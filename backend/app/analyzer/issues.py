import re
from typing import List, Tuple
from app.models.issue import GitHubIssue, RankedIssue

LABEL_POSITIVE_SCORES = {
    "good first issue": 30,
    "good-first-issue": 30,
    "first-timers-only": 25,
    "help wanted": 20,
    "help-wanted": 20,
    "documentation": 15,
    "docs": 15,
    "beginner": 15,
    "beginner-friendly": 15,
    "easy": 10,
    "starter": 10,
    "junior job": 10,
    "low hanging fruit": 10,
    "enhancement": 5,
    "bug": 5,
    "typo": 15,
}

NEGATIVE_KEYWORDS = [
    ("architecture", -20, "involves architectural changes"),
    ("breaking change", -20, "breaking change potential"),
    ("refactor", -15, "large refactoring required"),
    ("blocked by", -15, "issue is blocked by other tasks"),
    ("depends on", -15, "dependency on other unresolved issues"),
    ("epic", -15, "broad multi-part epic"),
    ("redesign", -15, "redesign requires wide consensus"),
    ("rfc", -10, "request for comments/discussion phase"),
]


class IssueRanker:
    """Ranks GitHub issues deterministically to recommend newcomer-friendly tasks."""

    def score_issue(self, issue: GitHubIssue) -> Tuple[int, str, List[str]]:
        score = 0
        reasons: List[str] = []
        labels_lower = [l.lower().strip() for l in issue.labels]

        # 1. Label scoring
        for label, weight in LABEL_POSITIVE_SCORES.items():
            if label in labels_lower:
                score += weight
                reasons.append(f"Label '{label}' (+{weight})")

        # 2. Body clarity & length
        body = (issue.body or "").strip()
        body_len = len(body)
        if body_len > 120:
            score += 10
            reasons.append("Detailed description provided (+10)")
        elif body_len < 40:
            score -= 15
            reasons.append("Very brief or unclear description (-15)")

        # 3. Low comment count (not bogged down in debate)
        if issue.comments <= 3:
            score += 5
            reasons.append(f"Low comment count ({issue.comments} comments) indicates open scope (+5)")
        elif issue.comments > 15:
            score -= 5
            reasons.append(f"High comment count ({issue.comments} comments) suggests ongoing contention (-5)")

        # 4. Scope size check
        if 80 <= body_len <= 1200:
            score += 5
            reasons.append("Focused, manageable scope (+5)")

        # 5. Check for checklist items / reproducibility steps
        if "- [ ]" in body or "1." in body:
            score += 5
            reasons.append("Actionable checklist/steps included (+5)")

        # 6. Negative keywords in title or body
        full_text = f"{issue.title} {body}".lower()
        for kw, weight, desc in NEGATIVE_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", full_text):
                score += weight  # weight is negative
                reasons.append(f"{desc} ({weight})")

        # Determine difficulty badge
        if score >= 35:
            difficulty = "Beginner"
        elif score >= 15:
            difficulty = "Intermediate"
        else:
            difficulty = "Advanced"

        return score, difficulty, reasons

    def rank_issues(self, issues: List[GitHubIssue]) -> List[RankedIssue]:
        ranked: List[RankedIssue] = []
        for issue in issues:
            score, difficulty, reasons = self.score_issue(issue)
            ranked.append(
                RankedIssue(
                    issue=issue,
                    score=score,
                    difficulty=difficulty,
                    reasons=reasons,
                )
            )

        # Sort descending by score, then ascending by number of comments
        ranked.sort(key=lambda x: (x.score, -x.issue.comments), reverse=True)
        return ranked
