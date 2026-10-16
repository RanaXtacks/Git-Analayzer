import re
from urllib.parse import urlparse
from typing import Tuple


GITHUB_URL_REGEX = re.compile(
    r"^https?://(?:www\.)?github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+?)(?:/)?(?:\.git)?$"
)

# Reserved words on GitHub that are not repositories
RESERVED_GITHUB_NAMES = {
    "features", "pricing", "marketplace", "login", "join", "signup",
    "settings", "notifications", "search", "explore", "trending",
    "stars", "topics", "collections", "events", "about", "contact",
    "security", "terms", "privacy", "organizations", "orgs"
}


def parse_and_validate_github_url(url: str) -> Tuple[str, str]:
    """
    Validates a GitHub repository URL and extracts (owner, repo).
    Rejects:
      - non-GitHub domains
      - user profiles or organizations only
      - arbitrary subpaths (/pulls, /issues, /tree, etc.)
      - empty or malformed URLs
    Returns (owner, repo) in normalized lower/canonical casing.
    Raises ValueError with descriptive message on failure.
    """
    if not url or not isinstance(url, str):
        raise ValueError("A valid repository URL is required.")

    cleaned_url = url.strip()
    # Remove git+ or git:// prefix if user provided it
    if cleaned_url.startswith("git@github.com:"):
        cleaned_url = "https://github.com/" + cleaned_url.split("git@github.com:")[1]

    parsed = urlparse(cleaned_url)
    if parsed.netloc not in ("github.com", "www.github.com"):
        raise ValueError("Only public GitHub repositories (https://github.com/owner/repo) are supported.")

    path = parsed.path.strip("/")
    parts = [p for p in path.split("/") if p]

    if len(parts) != 2:
        if len(parts) == 1:
            raise ValueError("URL points to a GitHub user or organization profile, not a repository.")
        elif len(parts) > 2:
            raise ValueError("URL points to a subpath inside a repository (such as an issue, PR, or file tree). Please provide the repository root URL.")
        else:
            raise ValueError("Invalid GitHub URL format. Expected: https://github.com/owner/repository")

    owner, repo = parts[0], parts[1]

    # Strip .git suffix if present
    if repo.endswith(".git"):
        repo = repo[:-4]

    # Validate characters
    if not re.match(r"^[a-zA-Z0-9_.-]+$", owner) or not re.match(r"^[a-zA-Z0-9_.-]+$", repo):
        raise ValueError("Repository URL contains invalid characters in owner or repository name.")

    if owner.lower() in RESERVED_GITHUB_NAMES:
        raise ValueError(f"'{owner}' is a reserved GitHub route, not a repository owner.")

    return owner, repo
