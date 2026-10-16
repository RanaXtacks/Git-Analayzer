from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AnalysisRecord(Base):
    """Stores generated onboarding guides and repository metadata."""
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True)
    owner = Column(String(100), nullable=False, index=True)
    repo = Column(String(100), nullable=False, index=True)
    commit_sha = Column(String(64), nullable=True, index=True)
    model_name = Column(String(100), nullable=False)
    guide_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AnalysisRecord {self.owner}/{self.repo} @ {self.commit_sha}>"
