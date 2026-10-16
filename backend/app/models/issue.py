from typing import List, Optional
from pydantic import BaseModel, Field


class GitHubIssue(BaseModel):
    number: int
    title: str
    body: Optional[str] = ""
    labels: List[str] = Field(default_factory=list)
    comments: int = 0
    created_at: str
    updated_at: Optional[str] = None
    url: str
    state: str = "open"
    is_pull_request: bool = False


class RankedIssue(BaseModel):
    issue: GitHubIssue
    score: int
    difficulty: str = "Beginner"
    reasons: List[str] = Field(default_factory=list)
