from typing import Dict, Optional


class ContextSelector:
    """Prioritizes and limits text blocks so that LLM context limits are never exceeded."""

    def __init__(self, max_readme_size: int = 100000, max_file_size: int = 200000):
        self.max_readme_size = max_readme_size
        self.max_file_size = max_file_size

    def truncate_text(self, text: Optional[str], max_len: int, label: str = "text") -> Optional[str]:
        if not text:
            return None
        if len(text) <= max_len:
            return text

        # Preserve the first 65% and last 35% of the allowance
        head_len = int(max_len * 0.65)
        tail_len = max_len - head_len

        truncated_notice = f"\n\n... [TRUNCATED {len(text) - max_len} CHARACTERS OF {label.upper()}] ...\n\n"
        return text[:head_len] + truncated_notice + text[-tail_len:]

    def prepare_readme(self, readme: Optional[str]) -> Optional[str]:
        return self.truncate_text(readme, self.max_readme_size, "README")

    def prepare_contributing(self, contributing: Optional[str]) -> Optional[str]:
        return self.truncate_text(contributing, self.max_readme_size, "CONTRIBUTING")

    def prepare_raw_files(self, raw_files: Dict[str, str]) -> Dict[str, str]:
        selected: Dict[str, str] = {}
        for path, content in raw_files.items():
            selected[path] = self.truncate_text(content, self.max_file_size, path) or ""
        return selected
