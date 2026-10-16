import pytest
from app.github.repository import parse_and_validate_github_url


def test_valid_github_url():
    owner, repo = parse_and_validate_github_url("https://github.com/facebook/react")
    assert owner == "facebook"
    assert repo == "react"


def test_valid_github_url_trailing_slash():
    owner, repo = parse_and_validate_github_url("https://github.com/fastapi/fastapi/")
    assert owner == "fastapi"
    assert repo == "fastapi"


def test_valid_github_url_with_git_suffix():
    owner, repo = parse_and_validate_github_url("https://github.com/torvalds/linux.git")
    assert owner == "torvalds"
    assert repo == "linux"


def test_reject_invalid_domain():
    with pytest.raises(ValueError, match="Only public GitHub repositories"):
        parse_and_validate_github_url("https://gitlab.com/owner/repo")


def test_reject_user_profile():
    with pytest.raises(ValueError, match="URL points to a GitHub user or organization"):
        parse_and_validate_github_url("https://github.com/torvalds")


def test_reject_subpath():
    with pytest.raises(ValueError, match="URL points to a subpath"):
        parse_and_validate_github_url("https://github.com/facebook/react/pull/123")


def test_reject_reserved_route():
    with pytest.raises(ValueError, match="reserved GitHub route"):
        parse_and_validate_github_url("https://github.com/marketplace/actions")


def test_reject_empty_or_malformed():
    with pytest.raises(ValueError):
        parse_and_validate_github_url("")
    with pytest.raises(ValueError):
        parse_and_validate_github_url("not a url")
