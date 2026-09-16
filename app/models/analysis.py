import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON
from app.models.database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resume_filename = Column(String(255), nullable=True)
    resume_text_hash = Column(String(64), nullable=False)
    job_description_hash = Column(String(64), nullable=False)
    
    semantic_similarity_score = Column(Float, nullable=False)
    skill_match_score = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    
    # Store lists and complex nested dicts as JSON
    matched_skills = Column(JSON, nullable=False)
    missing_skills = Column(JSON, nullable=False)
    additional_skills = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=False)
    explainable_matches = Column(JSON, nullable=False)

    def to_dict(self):
        """Converts SQLAlchemy model instance to dictionary representation."""
        return {
            "analysis_id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resume_filename": self.resume_filename,
            "resume_text_hash": self.resume_text_hash,
            "job_description_hash": self.job_description_hash,
            "semantic_similarity_score": self.semantic_similarity_score,
            "skill_match_score": self.skill_match_score,
            "overall_score": self.overall_score,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "additional_skills": self.additional_skills,
            "recommendations": self.recommendations,
            "explainable_matches": self.explainable_matches
        }
