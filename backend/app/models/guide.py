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


class OnboardingGuide(BaseModel):
    project_summary: str
    prerequisites: List[str] = Field(default_factory=list)
    setup_steps: List[SetupStep] = Field(default_factory=list)
    run_instructions: List[SetupStep] = Field(default_factory=list)
    important_directories: List[DirectoryInfo] = Field(default_factory=list)
    where_to_start: str
    recommended_issues: List[RecommendedIssue] = Field(default_factory=list)
    first_contribution: FirstContribution
    contribution_workflow: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    confidence_score: int = Field(default=85, ge=0, le=100)
    confidence_level: str = Field(default="High")  # "High" | "Moderate" | "Low"
    confidence_breakdown: Optional[ConfidenceBreakdown] = None

