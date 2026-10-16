import logging
from typing import Dict, List, Optional
from app.github.client import GitHubClient
from app.models.repository import TreeEntry

logger = logging.getLogger("git_analyzer.github.files")

README_CANDIDATES = [
    "README.md",
    "README",
    "README.rst",
    "README.txt",
    "readme.md",
]

CONTRIBUTING_CANDIDATES = [
    "CONTRIBUTING.md",
    "CONTRIBUTING",
    ".github/CONTRIBUTING.md",
    "docs/CONTRIBUTING.md",
    "docs/contributing.md",
    "contributing.md",
]

HIGH_PRIORITY_FILES = {
    # Node / JS
    "package.json",
    # Python
    "requirements.txt",
    "pyproject.toml",
    "Pipfile",
    "setup.py",
    # Rust
    "Cargo.toml",
    # Go
    "go.mod",
    # Java / Kotlin
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    # Ruby
    "Gemfile",
    # PHP
    "composer.json",
    # Containers & Config
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yaml",
    "Makefile",
    ".env.example",
}


async def extract_readme(client: GitHubClient, owner: str, repo: str) -> Optional[str]:
    """Fetch README content using the GitHub /readme endpoint or falling back to file paths."""
    readme_content = await client.get_readme(owner, repo)
    if readme_content:
        return readme_content

    for candidate in README_CANDIDATES:
        content = await client.get_file_content(owner, repo, candidate)
        if content:
            return content

    return None


async def extract_contributing(client: GitHubClient, owner: str, repo: str) -> Optional[str]:
    """Search for CONTRIBUTING guidelines across standard locations."""
    for candidate in CONTRIBUTING_CANDIDATES:
        content = await client.get_file_content(owner, repo, candidate)
        if content:
            return content
    return None


async def extract_priority_files(
    client: GitHubClient,
    owner: str,
    repo: str,
    tree_entries: List[TreeEntry],
    max_file_size: int = 200000,
) -> Dict[str, str]:
    """
    Fetch contents for manifests, Docker configs, environment examples, and CI workflows
    that exist in the repository tree.
    """
    existing_paths = {entry.path for entry in tree_entries if entry.type == "blob"}
    files_to_fetch: List[str] = []

    # Priority manifests in root or packages
    for path in existing_paths:
        if path in HIGH_PRIORITY_FILES:
            files_to_fetch.append(path)
        elif path.startswith(".github/workflows/") and (path.endswith(".yml") or path.endswith(".yaml")):
            files_to_fetch.append(path)

    fetched_files: Dict[str, str] = {}
    for path in files_to_fetch:
        try:
            content = await client.get_file_content(owner, repo, path)
            if content:
                # Check size limit
                if len(content) > max_file_size:
                    content = content[:max_file_size] + "\n...[TRUNCATED FILE CONTENT]..."
                fetched_files[path] = content
        except Exception as e:
            logger.warning(f"Could not fetch priority file '{path}' for {owner}/{repo}: {e}")

    return fetched_files
