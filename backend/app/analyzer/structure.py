from typing import List, Set
from app.models.repository import TreeEntry, StructureAnalysisResult

IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "vendor",
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".idea",
    ".vscode",
    "target",
    "coverage",
    ".systemlens",
}

IMPORTANT_DIR_KEYWORDS = {
    "src",
    "app",
    "lib",
    "packages",
    "components",
    "services",
    "api",
    "tests",
    "test",
    "docs",
    "documentation",
    "scripts",
    "examples",
    "config",
    "models",
    "routes",
    "hooks",
    "utils",
    "core",
}

ENTRY_POINT_CANDIDATES = {
    "src/index.ts",
    "src/index.tsx",
    "src/index.js",
    "src/main.ts",
    "src/main.tsx",
    "src/main.js",
    "src/App.tsx",
    "src/App.jsx",
    "main.py",
    "app/main.py",
    "src/main.py",
    "run.py",
    "src/main.rs",
    "src/lib.rs",
    "main.go",
    "cmd/main.go",
    "index.js",
    "index.ts",
}


class StructureAnalyzer:
    """Analyzes repository file tree, produces compact representation, and highlights key areas."""

    def __init__(self, max_entries: int = 5000):
        self.max_entries = max_entries

    def analyze(self, tree_entries: List[TreeEntry]) -> StructureAnalysisResult:
        if not tree_entries:
            return StructureAnalysisResult(
                compact_tree="(No repository tree available)",
                important_directories=[],
                likely_entry_points=[],
                total_files=0,
                total_directories=0,
                truncated=False,
            )

        total_files = 0
        total_directories = 0
        filtered_paths: List[str] = []
        important_dirs: Set[str] = set()
        entry_points: List[str] = []

        is_truncated = len(tree_entries) > self.max_entries
        sliced_entries = tree_entries[:self.max_entries]

        for entry in sliced_entries:
            path = entry.path.strip("/")
            parts = path.split("/")

            # Ignore noise directories
            if any(part in IGNORED_DIRECTORIES for part in parts):
                continue

            if entry.type == "tree":
                total_directories += 1
            else:
                total_files += 1

            filtered_paths.append(path)

            # Check for important directories (depth <= 2)
            if len(parts) >= 1:
                first_dir = parts[0]
                if first_dir in IMPORTANT_DIR_KEYWORDS:
                    important_dirs.add(first_dir)
            if len(parts) >= 2:
                second_dir = f"{parts[0]}/{parts[1]}"
                if parts[1] in IMPORTANT_DIR_KEYWORDS:
                    important_dirs.add(second_dir)

            # Check for candidate entry points
            if path in ENTRY_POINT_CANDIDATES:
                entry_points.append(path)

        # Build compact tree summary (up to 3 levels deep)
        tree_lines: List[str] = []
        shown_prefixes: Set[str] = set()

        for path in filtered_paths:
            parts = path.split("/")
            if len(parts) <= 3:
                # Direct file or shallow directory
                prefix = "/".join(parts[:-1]) if len(parts) > 1 else ""
                indent = "  " * (len(parts) - 1)
                tree_lines.append(f"{indent}{parts[-1]}")
            else:
                # Deeper file: group under top directory
                group_prefix = "/".join(parts[:2])
                if group_prefix not in shown_prefixes:
                    shown_prefixes.add(group_prefix)
                    tree_lines.append(f"  {parts[0]}/{parts[1]}/...")

        compact_tree_str = "\n".join(tree_lines[:200])
        if len(tree_lines) > 200:
            compact_tree_str += f"\n... [+{len(tree_lines) - 200} more items in tree]"

        return StructureAnalysisResult(
            compact_tree=compact_tree_str,
            important_directories=sorted(list(important_dirs))[:10],
            likely_entry_points=sorted(entry_points)[:5],
            total_files=total_files,
            total_directories=total_directories,
            truncated=is_truncated,
        )
