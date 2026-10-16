from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from app.models.guide import OnboardingGuide
from app.models.issue import RankedIssue


class RepositoryMetadata(BaseModel):
    owner: str
    name: str
    full_name: str
    description: Optional[str] = ""
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    default_branch: str = "main"
    license: Optional[str] = None
    open_issues_count: int = 0
    html_url: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    head_sha: Optional[str] = None


class TreeEntry(BaseModel):
    path: str
    type: str  # "blob" or "tree"
    size: Optional[int] = None
    sha: Optional[str] = None


class DependencyAnalysisResult(BaseModel):
    language: Optional[str] = None
    runtime: Optional[str] = None
    package_manager: Optional[str] = None
    install_command: Optional[str] = None
    dev_command: Optional[str] = None
    start_command: Optional[str] = None
    build_command: Optional[str] = None
    test_command: Optional[str] = None
    lint_command: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    dev_dependencies: List[str] = Field(default_factory=list)
    engines: Dict[str, str] = Field(default_factory=dict)
    raw_manifests_found: List[str] = Field(default_factory=list)


class StructureAnalysisResult(BaseModel):
    compact_tree: str
    important_directories: List[str] = Field(default_factory=list)
    likely_entry_points: List[str] = Field(default_factory=list)
    total_files: int = 0
    total_directories: int = 0
    truncated: bool = False


class ConfigurationAnalysisResult(BaseModel):
    docker_support: bool = False
    dockerfile_found: bool = False
    docker_compose_found: bool = False
    makefile_found: bool = False
    env_example_found: bool = False
    env_variables: List[str] = Field(default_factory=list)
    ci_workflows: List[str] = Field(default_factory=list)
    ci_commands: List[str] = Field(default_factory=list)


class RepositoryContext(BaseModel):
    metadata: RepositoryMetadata
    readme: Optional[str] = None
    contributing: Optional[str] = None
    structure: StructureAnalysisResult
    dependencies: DependencyAnalysisResult
    configuration: ConfigurationAnalysisResult
    ranked_issues: List[RankedIssue] = Field(default_factory=list)
    raw_files: Dict[str, str] = Field(default_factory=dict)
    sanitized_warnings: List[str] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    url: str


class AnalysisMetadata(BaseModel):
    commit_sha: Optional[str] = None
    model: str
    provider: str
    generated_at: str
    cached: bool = False
    duration_seconds: Optional[float] = None


class AnalysisResponse(BaseModel):
    repository: RepositoryMetadata
    guide: OnboardingGuide
    metadata: AnalysisMetadata
