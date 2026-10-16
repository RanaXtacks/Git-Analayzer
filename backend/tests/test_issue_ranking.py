from app.analyzer.issues import IssueRanker
from app.models.issue import GitHubIssue


def test_issue_ranking_scores_beginner_higher_than_architectural():
    ranker = IssueRanker()

    beginner_issue = GitHubIssue(
        number=101,
        title="Fix typo in README installation commands",
        body="There is a small typo in the install section: npm instll should be npm install. - [ ] Fix typo",
        labels=["good first issue", "documentation"],
        comments=1,
        created_at="2026-01-01T00:00:00Z",
        url="https://github.com/owner/repo/issues/101",
    )

    complex_issue = GitHubIssue(
        number=102,
        title="Complete architectural redesign of authentication pipeline",
        body="We need to rewrite the entire security subsystem. This is a breaking change and epic.",
        labels=["architecture", "breaking change"],
        comments=20,
        created_at="2026-01-01T00:00:00Z",
        url="https://github.com/owner/repo/issues/102",
    )

    ranked = ranker.rank_issues([complex_issue, beginner_issue])

    assert len(ranked) == 2
    assert ranked[0].issue.number == 101
    assert ranked[0].score > ranked[1].score
    assert ranked[0].difficulty == "Beginner"
    assert "Label 'good first issue' (+30)" in ranked[0].reasons
    assert ranked[1].difficulty == "Advanced"
