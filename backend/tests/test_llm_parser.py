import pytest
from app.llm.parser import extract_json_from_text, parse_guide_response, GuideParseError
from app.guide.verifier import EvidenceVerifier
from app.models.guide import OnboardingGuide, RecommendedIssue, FirstContribution, Evidence
from app.models.repository import RepositoryContext, RepositoryMetadata, StructureAnalysisResult, DependencyAnalysisResult, ConfigurationAnalysisResult
from app.models.issue import RankedIssue, GitHubIssue


def test_extract_json_from_markdown_block():
    text = """Here is the generated analysis:
```json
{
  "project_summary": "Test project",
  "prerequisites": ["Node.js"],
  "setup_steps": [],
  "run_instructions": [],
  "important_directories": [],
  "where_to_start": "src/",
  "recommended_issues": [],
  "first_contribution": {
    "title": "Fix docs",
    "description": "Fix typo",
    "suggested_files": [],
    "reasoning": "Simple",
    "evidence": []
  },
  "contribution_workflow": ["Fork", "PR"],
  "warnings": []
}
```
Hope this helps!"""
    data = extract_json_from_text(text)
    assert data["project_summary"] == "Test project"
    guide = parse_guide_response(text)
    assert guide.where_to_start == "src/"


def test_extract_json_invalid():
    with pytest.raises(GuideParseError):
        extract_json_from_text("This has no json brackets at all.")


def test_evidence_verifier_removes_hallucinated_issue():
    verifier = EvidenceVerifier()
    guide = OnboardingGuide(
        project_summary="A tool",
        prerequisites=[],
        setup_steps=[],
        run_instructions=[],
        important_directories=[],
        where_to_start="src/",
        recommended_issues=[
            RecommendedIssue(
                number=999,  # does NOT exist in context
                title="Invented issue",
                url="https://github.com/owner/repo/issues/999",
                difficulty="Beginner",
                reason="Made up",
                score=50,
                evidence=[],
            )
        ],
        first_contribution=FirstContribution(
            title="T", description="D", suggested_files=["nonexistent_file.py"], reasoning="R", evidence=[]
        ),
        contribution_workflow=[],
        warnings=[],
    )

    context = RepositoryContext(
        metadata=RepositoryMetadata(
            owner="owner", name="repo", full_name="owner/repo", html_url="https://github.com/owner/repo"
        ),
        structure=StructureAnalysisResult(compact_tree="src/main.py", total_files=1),
        dependencies=DependencyAnalysisResult(),
        configuration=ConfigurationAnalysisResult(),
        ranked_issues=[
            RankedIssue(
                issue=GitHubIssue(
                    number=42,
                    title="Real Issue",
                    body="Real body",
                    created_at="2026-01-01T00:00:00Z",
                    url="https://github.com/owner/repo/issues/42",
                ),
                score=40,
                difficulty="Beginner",
                reasons=["good first issue"],
            )
        ],
        raw_files={"src/main.py": "print('hello')"},
    )

    verified = verifier.verify_guide(guide, context)

    # Hallucinated issue #999 must be removed and replaced with actual issue #42
    assert not any(i.number == 999 for i in verified.recommended_issues)
    assert any(i.number == 42 for i in verified.recommended_issues)
    assert any("Removed hallucinated issue #999" in w for w in verified.warnings)
    # Nonexistent file must be removed from first contribution
    assert "nonexistent_file.py" not in verified.first_contribution.suggested_files


@pytest.mark.asyncio
async def test_deterministic_provider_generates_deep_plans_and_diff_matrix():
    from app.llm.deterministic import DeterministicProvider
    from app.llm.prompts import SYSTEM_PROMPT, build_user_prompt

    context = RepositoryContext(
        metadata=RepositoryMetadata(
            owner="facebook", name="react", full_name="facebook/react", html_url="https://github.com/facebook/react"
        ),
        structure=StructureAnalysisResult(
            compact_tree="packages/react/index.js\npackages/react-dom/index.js",
            total_files=2,
            important_directories=["packages/react", "packages/react-dom"],
            likely_entry_points=["packages/react/index.js"],
        ),
        dependencies=DependencyAnalysisResult(
            language="JavaScript",
            package_manager="yarn",
            install_command="yarn install",
            dev_command="yarn start",
            test_command="yarn test",
        ),
        configuration=ConfigurationAnalysisResult(),
        ranked_issues=[],
        raw_files={"packages/react/index.js": "// React index"},
    )

    user_prompt = build_user_prompt(context)
    provider = DeterministicProvider()
    raw = await provider.generate(SYSTEM_PROMPT, user_prompt)
    guide = parse_guide_response(raw)

    assert len(guide.execution_plans) == 4
    plan_ids = [p.id for p in guide.execution_plans]
    assert "day_one" in plan_ids
    assert "deep_architecture" in plan_ids
    assert "bug_hunt" in plan_ids
    assert "system_extender" in plan_ids

    assert guide.deep_architecture is not None
    assert len(guide.deep_architecture.lifecycle_stages) >= 4
    assert len(guide.differentiation_matrix) >= 5
    assert any("Zero-Hallucination" in d.feature for d in guide.differentiation_matrix)

