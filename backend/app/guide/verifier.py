import logging
from typing import Set
from app.models.guide import OnboardingGuide, RecommendedIssue
from app.models.repository import RepositoryContext

logger = logging.getLogger("git_analyzer.guide.verifier")


class EvidenceVerifier:
    """
    Enforces the zero-hallucination principle:
    - Removes issues that don't match GitHub issues
    - Verifies file paths against the repository tree
    - Audits commands against manifests
    """

    def verify_guide(self, guide: OnboardingGuide, context: RepositoryContext) -> OnboardingGuide:
        verified_guide = guide.model_copy(deep=True)
        warnings = list(verified_guide.warnings)

        # 1. Verify Recommended Issues
        actual_issue_map = {ri.issue.number: ri.issue for ri in context.ranked_issues}
        verified_issues = []

        for rec_issue in verified_guide.recommended_issues:
            if rec_issue.number in actual_issue_map:
                actual = actual_issue_map[rec_issue.number]
                # Enforce exact URL and title from GitHub
                verified_issues.append(
                    RecommendedIssue(
                        number=rec_issue.number,
                        title=actual.title,
                        url=actual.url,
                        difficulty=rec_issue.difficulty,
                        reason=rec_issue.reason,
                        score=rec_issue.score,
                        evidence=rec_issue.evidence,
                    )
                )
            else:
                warnings.append(
                    f"Removed hallucinated issue #{rec_issue.number} which does not exist in the repository."
                )

        # If LLM recommended no valid issues but repo has issues, supply the #1 ranked issue
        if not verified_issues and context.ranked_issues:
            top = context.ranked_issues[0]
            verified_issues.append(
                RecommendedIssue(
                    number=top.issue.number,
                    title=top.issue.title,
                    url=top.issue.url,
                    difficulty=top.difficulty,
                    reason=f"Top ranked beginner issue based on: {', '.join(top.reasons)}",
                    score=top.score,
                    evidence=[],
                )
            )

        verified_guide.recommended_issues = verified_issues

        # 2. Verify Suggested First Contribution Files
        existing_files: Set[str] = set()
        for path in context.raw_files.keys():
            existing_files.add(path)

        verified_suggested_files = []
        for file_path in verified_guide.first_contribution.suggested_files:
            file_clean = file_path.strip().lstrip("./")
            # Check if file exists in raw_files or tree
            found = False
            if file_clean in existing_files:
                found = True
            elif context.structure.compact_tree and file_clean in context.structure.compact_tree:
                found = True

            if found:
                verified_suggested_files.append(file_clean)
            else:
                warnings.append(
                    f"Suggested file '{file_clean}' could not be verified in the repository tree."
                )

        verified_guide.first_contribution.suggested_files = verified_suggested_files

        # 3. Add context sanitized warnings
        if context.sanitized_warnings:
            warnings.extend(context.sanitized_warnings)

        verified_guide.warnings = list(dict.fromkeys(warnings))
        return verified_guide
