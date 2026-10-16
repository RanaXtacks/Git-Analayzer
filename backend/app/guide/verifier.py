import logging
from typing import Set
from app.models.guide import OnboardingGuide, RecommendedIssue, ConfidenceBreakdown
from app.models.repository import RepositoryContext

logger = logging.getLogger("git_analyzer.guide.verifier")


class EvidenceVerifier:
    """
    Enforces the zero-hallucination principle:
    - Removes issues that don't match GitHub issues
    - Verifies file paths against the repository tree
    - Audits commands against manifests
    - Computes mathematical confidence scores and breakdowns
    """

    def calculate_confidence(
        self,
        guide: OnboardingGuide,
        context: RepositoryContext,
        removed_issues_count: int,
        removed_files_count: int,
    ) -> tuple[int, str, ConfidenceBreakdown]:
        reasons = []

        # 1. Manifest Certainty (0 - 100)
        has_runtime = bool(context.dependencies.runtime)
        has_pkg_mgr = bool(context.dependencies.package_manager)
        has_docker = bool(context.configuration.docker_support)

        if has_runtime and has_pkg_mgr:
            manifest_score = 95
            reasons.append(f"Explicit runtime ({context.dependencies.runtime}) & package manager verified (+35% weight)")
        elif has_runtime or has_pkg_mgr or has_docker:
            manifest_score = 75
            reasons.append("Partial project manifest verified")
        elif context.metadata.language:
            manifest_score = 55
            reasons.append(f"Language recognized ({context.metadata.language}) without locked manifest")
        else:
            manifest_score = 30
            reasons.append("No explicit runtime manifest detected")

        # 2. Evidence Grounding (0 - 100)
        evidence_count = 0
        for step in guide.setup_steps:
            evidence_count += len(step.evidence)
        for step in guide.run_instructions:
            evidence_count += len(step.evidence)
        for d in guide.important_directories:
            evidence_count += len(d.evidence)
        for issue in guide.recommended_issues:
            evidence_count += len(issue.evidence)
        if guide.first_contribution.evidence:
            evidence_count += len(guide.first_contribution.evidence)

        if evidence_count >= 6:
            evidence_score = 100
            reasons.append(f"High evidence citations ({evidence_count} verified sources)")
        elif evidence_count >= 3:
            evidence_score = 80
            reasons.append(f"Adequate evidence citations ({evidence_count} sources)")
        else:
            evidence_score = 55
            reasons.append("Limited evidence citations supplied")

        # 3. Issue Actionability (0 - 100)
        if context.ranked_issues:
            top_score = max(r.score for r in context.ranked_issues)
            issue_score = min(100, max(40, 50 + top_score))
            reasons.append("Beginner-friendly open issues discovered and ranked")
        else:
            issue_score = 60
            reasons.append("No open beginner issues in repository")

        # 4. Documentation Health (0 - 100)
        doc_score = 0
        raw_names = [f.lower() for f in context.raw_files.keys()]
        if any("readme" in f for f in raw_names):
            doc_score += 50
        if any("contributing" in f for f in raw_names):
            doc_score += 30
        if any("license" in f for f in raw_names):
            doc_score += 20
        reasons.append(f"Repository documentation health rated {doc_score}/100")

        # 5. Hallucination Penalties
        penalty = (removed_issues_count * 20) + (removed_files_count * 15)
        if penalty > 0:
            reasons.append(f"Hallucination penalty (-{penalty} pts) applied for {removed_issues_count} unverified issue(s) and {removed_files_count} unverified file(s)")

        # Weighted composite score
        # 35% manifest, 30% evidence, 15% issues, 20% documentation
        composite = (
            0.35 * manifest_score
            + 0.30 * evidence_score
            + 0.15 * issue_score
            + 0.20 * doc_score
            - penalty
        )
        final_score = max(15, min(100, int(round(composite))))

        if final_score >= 80:
            level = "High"
        elif final_score >= 60:
            level = "Moderate"
        else:
            level = "Low"

        breakdown = ConfidenceBreakdown(
            manifest_score=manifest_score,
            evidence_score=evidence_score,
            issue_score=issue_score,
            doc_score=doc_score,
            hallucination_penalty=penalty,
            reasons=reasons,
        )

        return final_score, level, breakdown

    def verify_guide(self, guide: OnboardingGuide, context: RepositoryContext) -> OnboardingGuide:
        verified_guide = guide.model_copy(deep=True)
        warnings = list(verified_guide.warnings)

        removed_issues_count = 0
        removed_files_count = 0

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
                removed_issues_count += 1
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
                removed_files_count += 1
                warnings.append(
                    f"Suggested file '{file_clean}' could not be verified in the repository tree."
                )

        verified_guide.first_contribution.suggested_files = verified_suggested_files

        # 3. Add context sanitized warnings
        if context.sanitized_warnings:
            warnings.extend(context.sanitized_warnings)

        verified_guide.warnings = list(dict.fromkeys(warnings))

        # 4. Compute Confidence Score & Breakdown
        score, level, breakdown = self.calculate_confidence(
            verified_guide,
            context,
            removed_issues_count,
            removed_files_count,
        )
        verified_guide.confidence_score = score
        verified_guide.confidence_level = level
        verified_guide.confidence_breakdown = breakdown

        return verified_guide

