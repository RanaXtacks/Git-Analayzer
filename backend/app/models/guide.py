from typing import List, Optional
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    source: str
    location: str
    detail: str


class SetupStep(BaseModel):
    step: int
    description: str
    command: Optional[str] = None
    evidence: List[Evidence] = Field(default_factory=list)


class DirectoryInfo(BaseModel):
    path: str
    description: str
    reason_to_care: str
    evidence: List[Evidence] = Field(default_factory=list)


class RecommendedIssue(BaseModel):
    number: int
    title: str
    url: str
    difficulty: str  # "Beginner" | "Intermediate" | "Advanced"
    reason: str
    score: int
    evidence: List[Evidence] = Field(default_factory=list)


class FirstContribution(BaseModel):
    title: str
    description: str
    suggested_files: List[str] = Field(default_factory=list)
    reasoning: str
    evidence: List[Evidence] = Field(default_factory=list)


class ConfidenceBreakdown(BaseModel):
    manifest_score: int = Field(default=80, ge=0, le=100)
    evidence_score: int = Field(default=80, ge=0, le=100)
    issue_score: int = Field(default=80, ge=0, le=100)
    doc_score: int = Field(default=80, ge=0, le=100)
    hallucination_penalty: int = Field(default=0)
    reasons: List[str] = Field(default_factory=list)


class ExecutionPlanStep(BaseModel):
    step: int
    action: str
    target_files: List[str] = Field(default_factory=list)
    command: Optional[str] = None
    verification: str


class ExecutionPlan(BaseModel):
    id: str  # "day_one" | "deep_architecture" | "bug_hunt" | "system_extender"
    title: str
    target_persona: str  # "30-Min Fast Track" | "System Architect" | "Bug Hunter" | "Feature Extender"
    time_estimate: str  # "~30 mins" | "~2-3 hrs" | "~1 hr" | "~1-2 days"
    difficulty: str  # "Beginner" | "Intermediate" | "Advanced"
    goal: str
    steps: List[ExecutionPlanStep] = Field(default_factory=list)
    key_files: List[str] = Field(default_factory=list)
    tips: List[str] = Field(default_factory=list)


class ArchitectureLifecycleStage(BaseModel):
    stage: int
    name: str
    description: str
    representative_files: List[str] = Field(default_factory=list)


class DeepArchitecture(BaseModel):
    pattern: str  # e.g. "Layered MVC / Microservices / Clean Architecture"
    explanation: str
    lifecycle_stages: List[ArchitectureLifecycleStage] = Field(default_factory=list)
    data_flow_summary: str
    hotspots_and_gotchas: List[str] = Field(default_factory=list)


class CopilotDiffPoint(BaseModel):
    feature: str
    copilot_approach: str
    git_analyzer_advantage: str
    technical_reason: str



class OnboardingGuide(BaseModel):
    project_summary: str
    what_is_it: Optional[str] = None
    why_it_exists: Optional[str] = None
    how_it_works: Optional[str] = None
    who_is_it_for: Optional[str] = None
    prerequisites: List[str] = Field(default_factory=list)

    setup_steps: List[SetupStep] = Field(default_factory=list)
    run_instructions: List[SetupStep] = Field(default_factory=list)
    important_directories: List[DirectoryInfo] = Field(default_factory=list)
    where_to_start: str
    recommended_issues: List[RecommendedIssue] = Field(default_factory=list)
    first_contribution: FirstContribution
    contribution_workflow: List[str] = Field(default_factory=list)
    execution_plans: List[ExecutionPlan] = Field(default_factory=list)
    deep_architecture: Optional[DeepArchitecture] = None
    differentiation_matrix: List[CopilotDiffPoint] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    confidence_score: int = Field(default=85, ge=0, le=100)
    confidence_level: str = Field(default="High")  # "High" | "Moderate" | "Low"
    confidence_breakdown: Optional[ConfidenceBreakdown] = None

