from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional
from app.config import settings

class AnalysisTextRequest(BaseModel):
    resume_text: str = Field(..., description="The plain text content of the candidate resume.")
    job_description: str = Field(..., description="The plain text of the target job description.")

    @field_validator("resume_text", "job_description")
    @classmethod
    def validate_non_empty_and_length(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Text payload cannot be empty or just whitespace.")
        if len(cleaned) > settings.MAX_TEXT_LENGTH:
            raise ValueError(f"Text payload length exceeds the maximum allowed limit of {settings.MAX_TEXT_LENGTH} characters.")
        return cleaned

class ScoreBreakdown(BaseModel):
    skill_match_weight: float = Field(..., description="The weight applied to the skill match score.")
    semantic_similarity_weight: float = Field(..., description="The weight applied to the semantic similarity score.")

class SemanticMatchDetail(BaseModel):
    matched_to_resume_skill: str = Field(..., description="The actual candidate resume skill that matched.")
    similarity_score: float = Field(..., description="The similarity percentage between the two skills.")
    match_type: str = Field(..., description="Match type: 'exact' or 'semantic'.")

class AnalysisResponse(BaseModel):
    analysis_id: str = Field(..., description="Unique identifier for the analysis result.")
    semantic_similarity_score: float = Field(..., description="Semantic similarity score between resume and job description (0-100).")
    skill_match_score: float = Field(..., description="Score showing ratio of matched job required skills (0-100).")
    overall_score: float = Field(..., description="Weighted combination of skill match and semantic similarity (0-100).")
    resume_skills: List[str] = Field(..., description="List of canonical skills identified in the resume.")
    job_required_skills: List[str] = Field(..., description="List of canonical skills identified in the job description.")
    matched_skills: List[str] = Field(..., description="List of skills that successfully matched.")
    missing_skills: List[str] = Field(..., description="List of job required skills missing from the resume.")
    additional_skills: List[str] = Field(..., description="List of candidate skills that were not explicitly required.")
    recommendations: List[str] = Field(..., description="Actionable recommendations generated to bridge the skill gap.")
    score_breakdown: ScoreBreakdown = Field(..., description="The configuration weights used to compute the overall score.")
    explainable_matches: Dict[str, SemanticMatchDetail] = Field(..., description="Detailed breakdown of how each skill was matched (exact/semantic).")
