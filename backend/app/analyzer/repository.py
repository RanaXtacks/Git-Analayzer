from typing import Dict, List
from app.models.repository import (
    TreeEntry,
    DependencyAnalysisResult,
    StructureAnalysisResult,
    ConfigurationAnalysisResult,
)
from app.models.issue import GitHubIssue, RankedIssue
from app.analyzer.dependencies import DependencyAnalyzer
from app.analyzer.structure import StructureAnalyzer
from app.analyzer.configuration import ConfigurationAnalyzer
from app.analyzer.issues import IssueRanker


class RepositoryAnalyzer:
    """Coordinates deterministic analysis across structure, dependencies, configuration, and issues."""

    def __init__(self, max_tree_entries: int = 5000):
        self.dependency_analyzer = DependencyAnalyzer()
        self.structure_analyzer = StructureAnalyzer(max_entries=max_tree_entries)
        self.config_analyzer = ConfigurationAnalyzer()
        self.issue_ranker = IssueRanker()

    def analyze_structure(self, tree_entries: List[TreeEntry]) -> StructureAnalysisResult:
        return self.structure_analyzer.analyze(tree_entries)

    def analyze_dependencies(self, raw_files: Dict[str, str]) -> DependencyAnalysisResult:
        return self.dependency_analyzer.analyze(raw_files)

    def analyze_configuration(self, raw_files: Dict[str, str]) -> ConfigurationAnalysisResult:
        return self.config_analyzer.analyze(raw_files)

    def rank_issues(self, issues: List[GitHubIssue]) -> List[RankedIssue]:
        return self.issue_ranker.rank_issues(issues)
