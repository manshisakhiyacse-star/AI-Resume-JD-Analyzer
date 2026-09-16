from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.analysis import Analysis

class AnalysisRepository:
    @staticmethod
    def create_analysis(db: Session, analysis_data: dict) -> Analysis:
        """
        Creates and stores a new Analysis record in the database.
        """
        db_analysis = Analysis(
            id=analysis_data.get("analysis_id"),
            resume_filename=analysis_data.get("resume_filename"),
            resume_text_hash=analysis_data.get("resume_text_hash"),
            job_description_hash=analysis_data.get("job_description_hash"),
            semantic_similarity_score=analysis_data.get("semantic_similarity_score"),
            skill_match_score=analysis_data.get("skill_match_score"),
            overall_score=analysis_data.get("overall_score"),
            matched_skills=analysis_data.get("matched_skills"),
            missing_skills=analysis_data.get("missing_skills"),
            additional_skills=analysis_data.get("additional_skills"),
            recommendations=analysis_data.get("recommendations"),
            explainable_matches=analysis_data.get("explainable_matches")
        )
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        return db_analysis

    @staticmethod
    def get_analysis(db: Session, analysis_id: str) -> Optional[Analysis]:
        """
        Retrieves a previously stored Analysis by its ID.
        """
        return db.query(Analysis).filter(Analysis.id == analysis_id).first()

    @staticmethod
    def get_analyses_by_hashes(
        db: Session, 
        resume_hash: str, 
        jd_hash: str
    ) -> Optional[Analysis]:
        """
        Retrieves a previous analysis matching both resume text hash and job description hash.
        Used for duplicate detection / caching.
        """
        return db.query(Analysis).filter(
            Analysis.resume_text_hash == resume_hash,
            Analysis.job_description_hash == jd_hash
        ).order_by(Analysis.created_at.desc()).first()
