import re
from typing import List, Tuple

SENSITIVE_FILENAME_PATTERNS = [
    r"^\.env(?:\..+)?$",
    r".*\.pem$",
    r".*\.key$",
    r".*\.pfx$",
    r".*\.p12$",
    r".*id_rsa.*",
    r".*credentials.*",
    r".*secret.*\.ya?ml$",
    r".*secret.*\.json$",
]

SECRET_CONTENT_PATTERNS = [
    # AWS Access Key
    (re.compile(r"\b(AKIA[0-9A-Z]{16})\b"), "[REDACTED_AWS_KEY]"),
    # GitHub PAT
    (re.compile(r"\b(ghp_[a-zA-Z0-9]{36})\b"), "[REDACTED_GITHUB_PAT]"),
    # GitHub Fine-grained PAT
    (re.compile(r"\b(github_pat_[a-zA-Z0-9_]{82})\b"), "[REDACTED_GITHUB_FINE_PAT]"),
    # Generic Private Key header
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL), "[REDACTED_PRIVATE_KEY]"),
    # JWT Tokens
    (re.compile(r"\beyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b"), "[REDACTED_JWT]"),
    # Generic secret / password assignments in config or env
    (re.compile(r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|password|auth[_-]?token)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{8,})['\"]?"), r"\1=[REDACTED_SECRET]"),
]


class ContextSanitizer:
    """Sanitizes files and content before feeding to LLM or persisting."""

    def is_sensitive_file(self, filename: str) -> bool:
        """Check if file should be completely omitted from context."""
        fn = filename.lower().strip()
        for pattern in SENSITIVE_FILENAME_PATTERNS:
            if re.match(pattern, fn):
                return True
        return False

    def sanitize_content(self, content: str) -> Tuple[str, List[str]]:
        """Scrub secret patterns from text content and record warnings."""
        if not content:
            return "", []

        sanitized = content
        redactions: List[str] = []

        for pattern, replacement in SECRET_CONTENT_PATTERNS:
            matches = pattern.findall(sanitized)
            if matches:
                sanitized = pattern.sub(replacement, sanitized)
                redactions.append(f"Sanitized {len(matches)} potential secret match(es) matching {pattern.pattern[:30]}...")

        return sanitized, redactions
