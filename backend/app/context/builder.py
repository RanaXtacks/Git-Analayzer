import asyncio
import logging
from typing import Callable, Coroutine, Dict, List, Optional

from app.github.client import GitHubClient
from app.github.files import extract_readme, extract_contributing, extract_priority_files
from app.github.issues import extract_issues
from app.analyzer.repository import RepositoryAnalyzer
from app.context.sanitizer import ContextSanitizer
from app.context.selector import ContextSelector
from app.models.repository import RepositoryContext, RepositoryMetadata

logger = logging.getLogger("git_analyzer.context.builder")

ProgressCallback = Optional[Callable[[str, str, Dict], Coroutine]]


class ContextBuilder:
    """Orchestrates repository extraction, deterministic analysis, sanitization, and packaging."""

    def __init__(
        self,
        github_client: GitHubClient,
        analyzer: RepositoryAnalyzer,
        max_readme_size: int = 100000,
        max_file_size: int = 200000,
        max_issues: int = 30,
    ):
        self.client = github_client
        self.analyzer = analyzer
        self.sanitizer = ContextSanitizer()
        self.selector = ContextSelector(max_readme_size, max_file_size)
        self.max_issues = max_issues

    async def build(
        self,
        owner: str,
        repo: str,
        progress_cb: ProgressCallback = None,
    ) -> RepositoryContext:
        sanitized_warnings: List[str] = []

        async def notify(stage: str, status: str, detail: str = ""):
            if progress_cb:
                try:
                    await progress_cb(stage, status, {"detail": detail})
                except Exception as e:
                    logger.debug(f"Progress callback error: {e}")

        # 1. Repository metadata
        await notify("metadata", "running", "Fetching repository metadata...")
        metadata = await self.client.get_repository(owner, repo)
        await notify("metadata", "complete", f"Found {metadata.full_name} ({metadata.stars} stars)")

        # 2. Parallel Extraction: README, CONTRIBUTING, Git Tree, and Issues
        await notify("readme", "running", "Retrieving repository documentation, tree, and issues in parallel...")
        raw_readme, raw_contributing, tree_entries, raw_issues = await asyncio.gather(
            extract_readme(self.client, owner, repo),
            extract_contributing(self.client, owner, repo),
            self.client.get_tree(owner, repo, sha=metadata.default_branch),
            extract_issues(self.client, owner, repo, max_issues=self.max_issues),
        )

        # Process README
        sanitized_readme = None
        if raw_readme:
            clean_readme, warnings = self.sanitizer.sanitize_content(raw_readme)
            sanitized_readme = self.selector.prepare_readme(clean_readme)
            sanitized_warnings.extend(warnings)
            await notify("readme", "complete", "README extracted and sanitized")
        else:
            await notify("readme", "complete", "No README found (will note in onboarding guide)")

        # Process CONTRIBUTING
        sanitized_contributing = None
        if raw_contributing:
            clean_contrib, warnings = self.sanitizer.sanitize_content(raw_contributing)
            sanitized_contributing = self.selector.prepare_contributing(clean_contrib)
            sanitized_warnings.extend(warnings)
            await notify("contributing", "complete", "CONTRIBUTING.md processed")
        else:
            await notify("contributing", "complete", "No CONTRIBUTING.md found")

        # Process Structure (Tree)
        await notify("structure", "running", "Mapping Git tree structure...")
        structure_result = self.analyzer.analyze_structure(tree_entries)
        await notify("structure", "complete", f"Mapped {structure_result.total_files} files")

        # 5. Priority files & dependencies
        await notify("dependencies", "running", "Detecting dependencies and manifests...")
        raw_priority_files = await extract_priority_files(self.client, owner, repo, tree_entries)

        safe_priority_files: Dict[str, str] = {}
        for filename, content in raw_priority_files.items():
            if self.sanitizer.is_sensitive_file(filename):
                sanitized_warnings.append(f"Omitted sensitive file: {filename}")
                continue
            clean_content, warnings = self.sanitizer.sanitize_content(content)
            safe_priority_files[filename] = clean_content
            sanitized_warnings.extend(warnings)

        safe_priority_files = self.selector.prepare_raw_files(safe_priority_files)
        dependency_result = self.analyzer.analyze_dependencies(safe_priority_files)
        await notify("dependencies", "complete", f"Identified {dependency_result.language or 'general'} ecosystem")

        # 6. Configuration & CI
        await notify("configuration", "running", "Analyzing Docker, Makefile, and CI workflows...")
        config_result = self.analyzer.analyze_configuration(safe_priority_files)
        await notify("configuration", "complete", "Configuration and workflows cataloged")

        # 7. Rank Issues
        ranked_issues = self.analyzer.rank_issues(raw_issues)
        await notify("issues", "complete", f"Ranked {len(ranked_issues)} open issues for beginner fit")


        return RepositoryContext(
            metadata=metadata,
            readme=sanitized_readme,
            contributing=sanitized_contributing,
            structure=structure_result,
            dependencies=dependency_result,
            configuration=config_result,
            ranked_issues=ranked_issues,
            raw_files=safe_priority_files,
            sanitized_warnings=sanitized_warnings,
        )
