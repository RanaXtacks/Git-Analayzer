from typing import List
from app.github.client import GitHubClient
from app.models.issue import GitHubIssue


async def extract_issues(client: GitHubClient, owner: str, repo: str, max_issues: int = 30) -> List[GitHubIssue]:
    """Retrieve open issues for a repository."""
    return await client.get_issues(owner, repo, max_count=max_issues)
