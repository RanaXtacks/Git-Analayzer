import base64
import logging
from typing import Any, Dict, List, Optional
import httpx

from app.models.repository import RepositoryMetadata, TreeEntry
from app.models.issue import GitHubIssue

logger = logging.getLogger("git_analyzer.github")


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class GitHubNotFoundError(GitHubAPIError):
    """Raised when repository or resource is not found (or private)."""
    pass


class GitHubRateLimitError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded."""
    def __init__(self, message: str, reset_time: Optional[int] = None):
        super().__init__(message, status_code=403)
        self.reset_time = reset_time


class GitHubAuthError(GitHubAPIError):
    """Raised when GitHub token is invalid."""
    pass


class GitHubClient:
    """
    Robust async HTTP client for the GitHub REST API.
    Handles authentication, error codes, rate limits, and safe timeouts.
    """
    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = "https://api.github.com",
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Git-Analyzer-OpenSource-Assistant",
        }
        if token and token.strip():
            headers["Authorization"] = f"Bearer {token.strip()}"

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        )

    async def close(self):
        await self._client.aclose()

    async def _handle_response(self, response: httpx.Response) -> Any:
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        elif response.status_code == 404:
            raise GitHubNotFoundError(
                "Repository not found. It may be private, deleted, or mistyped.",
                status_code=404,
            )
        elif response.status_code in (403, 429):
            remaining = response.headers.get("x-ratelimit-remaining")
            reset_ts = response.headers.get("x-ratelimit-reset")
            if remaining == "0" or "rate limit" in response.text.lower():
                raise GitHubRateLimitError(
                    "GitHub API rate limit exceeded. Please configure a server-side GITHUB_TOKEN or wait for the limit to reset.",
                    reset_time=int(reset_ts) if reset_ts and reset_ts.isdigit() else None,
                )
            raise GitHubAPIError(f"GitHub access forbidden (HTTP {response.status_code}): {response.text}", status_code=response.status_code)
        elif response.status_code == 401:
            raise GitHubAuthError("GitHub authentication failed. Check configured GITHUB_TOKEN.", status_code=401)
        else:
            raise GitHubAPIError(f"GitHub API returned unexpected status {response.status_code}: {response.text}", status_code=response.status_code)

    async def get_repository(self, owner: str, repo: str) -> RepositoryMetadata:
        """Fetch repository metadata and default branch."""
        try:
            resp = await self._client.get(f"/repos/{owner}/{repo}")
            data = await self._handle_response(resp)

            # Retrieve HEAD commit SHA of default branch
            default_branch = data.get("default_branch", "main")
            head_sha = None
            try:
                ref_resp = await self._client.get(f"/repos/{owner}/{repo}/commits/{default_branch}")
                if ref_resp.status_code == 200:
                    head_sha = ref_resp.json().get("sha")
            except Exception as e:
                logger.warning(f"Could not fetch commit SHA for {owner}/{repo}: {e}")

            license_name = None
            if data.get("license") and isinstance(data["license"], dict):
                license_name = data["license"].get("spdx_id") or data["license"].get("name")

            return RepositoryMetadata(
                owner=data["owner"]["login"],
                name=data["name"],
                full_name=data["full_name"],
                description=data.get("description") or "",
                language=data.get("language"),
                stars=data.get("stargazers_count", 0),
                forks=data.get("forks_count", 0),
                watchers=data.get("watchers_count", 0),
                default_branch=default_branch,
                license=license_name,
                open_issues_count=data.get("open_issues_count", 0),
                html_url=data.get("html_url", f"https://github.com/{owner}/{repo}"),
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at"),
                head_sha=head_sha,
            )
        except httpx.TimeoutException:
            raise GitHubAPIError(f"Connection timeout while reaching GitHub API for {owner}/{repo}")
        except httpx.RequestError as e:
            raise GitHubAPIError(f"Network error while connecting to GitHub: {str(e)}")

    async def get_readme(self, owner: str, repo: str) -> Optional[str]:
        """Fetch and decode the repository README content if available."""
        try:
            resp = await self._client.get(f"/repos/{owner}/{repo}/readme")
            if resp.status_code == 404:
                return None
            data = await self._handle_response(resp)
            content = data.get("content", "")
            encoding = data.get("encoding", "")
            if encoding == "base64" and content:
                return base64.b64decode(content).decode("utf-8", errors="replace")
            return content
        except GitHubNotFoundError:
            return None
        except Exception as e:
            logger.warning(f"Error fetching README for {owner}/{repo}: {e}")
            return None

    async def get_file_content(self, owner: str, repo: str, path: str, ref: Optional[str] = None) -> Optional[str]:
        """Fetch raw or base64-encoded file content for a given path."""
        try:
            params = {"ref": ref} if ref else {}
            resp = await self._client.get(f"/repos/{owner}/{repo}/contents/{path}", params=params)
            if resp.status_code == 404:
                return None
            data = await self._handle_response(resp)
            if isinstance(data, dict):
                content = data.get("content", "")
                encoding = data.get("encoding", "")
                if encoding == "base64" and content:
                    return base64.b64decode(content).decode("utf-8", errors="replace")
                return content
            return None
        except GitHubNotFoundError:
            return None
        except Exception as e:
            logger.warning(f"Error fetching file '{path}' for {owner}/{repo}: {e}")
            return None

    async def get_tree(self, owner: str, repo: str, sha: str = "HEAD", max_entries: int = 5000) -> List[TreeEntry]:
        """
        Fetch the repository git tree recursively.
        Returns a structured list of tree entries up to max_entries.
        """
        try:
            resp = await self._client.get(
                f"/repos/{owner}/{repo}/git/trees/{sha}",
                params={"recursive": "1"},
            )
            if resp.status_code == 404:
                return []
            data = await self._handle_response(resp)
            tree_data = data.get("tree", [])

            entries = []
            for item in tree_data[:max_entries]:
                entries.append(
                    TreeEntry(
                        path=item.get("path", ""),
                        type=item.get("type", "blob"),
                        size=item.get("size"),
                        sha=item.get("sha"),
                    )
                )
            return entries
        except Exception as e:
            logger.warning(f"Failed to fetch git tree for {owner}/{repo}: {e}")
            return []

    async def get_issues(self, owner: str, repo: str, max_count: int = 30) -> List[GitHubIssue]:
        """
        Fetch open issues from the repository, filtering out pull requests.
        """
        try:
            params = {
                "state": "open",
                "sort": "updated",
                "direction": "desc",
                "per_page": min(max_count, 100),
            }
            resp = await self._client.get(f"/repos/{owner}/{repo}/issues", params=params)
            if resp.status_code == 404:
                return []
            data = await self._handle_response(resp)

            issues: List[GitHubIssue] = []
            for item in data:
                # Exclude pull requests (GitHub issues API returns both issues and PRs)
                if "pull_request" in item:
                    continue

                labels = [l["name"] for l in item.get("labels", []) if isinstance(l, dict) and "name" in l]
                issues.append(
                    GitHubIssue(
                        number=item["number"],
                        title=item["title"],
                        body=item.get("body") or "",
                        labels=labels,
                        comments=item.get("comments", 0),
                        created_at=item.get("created_at", ""),
                        updated_at=item.get("updated_at"),
                        url=item.get("html_url", f"https://github.com/{owner}/{repo}/issues/{item['number']}"),
                        state="open",
                        is_pull_request=False,
                    )
                )
                if len(issues) >= max_count:
                    break

            return issues
        except Exception as e:
            logger.warning(f"Failed to fetch issues for {owner}/{repo}: {e}")
            return []
