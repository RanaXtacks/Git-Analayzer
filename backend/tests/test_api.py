import pytest
from unittest.mock import AsyncMock, patch
from starlette.testclient import TestClient
from app.main import app
from app.models.repository import RepositoryMetadata, TreeEntry
from app.models.issue import GitHubIssue
from app.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        return """{
            "project_summary": "Test repository summary",
            "prerequisites": ["Python 3.12"],
            "setup_steps": [
                {"step": 1, "description": "Install deps", "command": "pip install -r requirements.txt", "evidence": []}
            ],
            "run_instructions": [
                {"step": 1, "description": "Run server", "command": "uvicorn app.main:app", "evidence": []}
            ],
            "important_directories": [
                {"path": "app/", "description": "App code", "reason_to_care": "Core logic", "evidence": []}
            ],
            "where_to_start": "Check app/main.py",
            "recommended_issues": [
                {"number": 1, "title": "First issue", "url": "https://github.com/mock/repo/issues/1", "difficulty": "Beginner", "reason": "Good", "score": 30, "evidence": []}
            ],
            "first_contribution": {
                "title": "Fix doc",
                "description": "Improve README",
                "suggested_files": ["README.md"],
                "reasoning": "Simple",
                "evidence": []
            },
            "contribution_workflow": ["Fork", "PR"],
            "warnings": []
        }"""

    async def health_check(self) -> bool:
        return True


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "Git-Analyzer"


def test_analyze_rejects_invalid_url(client):
    response = client.post("/api/analyze/sync", json={"url": "https://notgithub.com/a/b"})
    assert response.status_code == 400
    assert "Only public GitHub repositories" in response.json()["detail"]


@patch("app.api.routes.get_llm_provider")
@patch("app.api.routes.get_github_client")
def test_analyze_sync_success(mock_get_gh, mock_get_llm, client):
    mock_llm = MockLLMProvider()
    mock_get_llm.return_value = mock_llm

    mock_gh = AsyncMock()
    mock_gh.get_repository.return_value = RepositoryMetadata(
        owner="mock",
        name="repo",
        full_name="mock/repo",
        html_url="https://github.com/mock/repo",
        default_branch="main",
        head_sha="sha123",
    )
    mock_gh.get_readme.return_value = "# Mock Repo\nRun `pip install -r requirements.txt`"
    mock_gh.get_tree.return_value = [
        TreeEntry(path="README.md", type="blob"),
        TreeEntry(path="requirements.txt", type="blob"),
        TreeEntry(path="app/main.py", type="blob"),
    ]
    mock_gh.get_file_content.side_effect = lambda owner, repo, path: "fastapi==0.115.0" if path == "requirements.txt" else None
    mock_gh.get_issues.return_value = [
        GitHubIssue(
            number=1,
            title="First issue",
            body="Help wanted",
            labels=["good first issue"],
            comments=0,
            created_at="2026-01-01T00:00:00Z",
            url="https://github.com/mock/repo/issues/1",
        )
    ]
    mock_get_gh.return_value = mock_gh

    response = client.post("/api/analyze/sync", json={"url": "https://github.com/mock/repo"})
    assert response.status_code == 200
    data = response.json()
    assert data["repository"]["full_name"] == "mock/repo"
    assert data["guide"]["project_summary"] == "Test repository summary"
    assert len(data["guide"]["setup_steps"]) == 1
    assert data["guide"]["recommended_issues"][0]["number"] == 1
