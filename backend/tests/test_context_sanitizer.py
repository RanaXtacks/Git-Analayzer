from app.context.sanitizer import ContextSanitizer


def test_sensitive_file_detection():
    sanitizer = ContextSanitizer()
    assert sanitizer.is_sensitive_file(".env") is True
    assert sanitizer.is_sensitive_file(".env.local") is True
    assert sanitizer.is_sensitive_file("id_rsa") is True
    assert sanitizer.is_sensitive_file("server.key") is True
    assert sanitizer.is_sensitive_file("cert.pem") is True
    assert sanitizer.is_sensitive_file("package.json") is False
    assert sanitizer.is_sensitive_file("README.md") is False
    assert sanitizer.is_sensitive_file("src/main.py") is False


def test_secret_content_sanitization():
    sanitizer = ContextSanitizer()
    text = (
        "Here is my AWS key: AKIAIOSFODNN7EXAMPLE and "
        "GitHub token: ghp_1234567890abcdefghijklmnopqrstuvwxyz and "
        "database password: password='SuperSecretPassword123!'"
    )
    clean_text, warnings = sanitizer.sanitize_content(text)

    assert "AKIAIOSFODNN7EXAMPLE" not in clean_text
    assert "[REDACTED_AWS_KEY]" in clean_text
    assert "ghp_1234567890abcdefghijklmnopqrstuvwxyz" not in clean_text
    assert "[REDACTED_GITHUB_PAT]" in clean_text
    assert len(warnings) >= 2
