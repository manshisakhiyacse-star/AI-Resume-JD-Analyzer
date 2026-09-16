import uuid
import logging
from sqlalchemy.orm import Session
from app.utils.text_utils import calculate_hash
from app.services.text_preprocessor import TextPreprocessor
from app.services.skill_extractor import SkillExtractor
from app.services.embedding_service import EmbeddingService
from app.services.matching_service import MatchingService
from app.services.similarity_service import SimilarityService
from app.services.scoring_service import ScoringService
from app.services.recommendation_service import RecommendationService
from app.repositories.analysis_repository import AnalysisRepository
from app.config import settings
from app.core.exceptions import AnalysisError

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(
        self,
        skill_extractor: SkillExtractor = None,
        embedding_service: EmbeddingService = None
    ):
        self.skill_extractor = skill_extractor or SkillExtractor()
        self.embedding_service = embedding_service or EmbeddingService()

    def analyze_resume(
        self,
        db: Session,
        resume_text: str,
        job_description: str,
        resume_filename: str = None
    ) -> dict:
        """
        Coordinates the full resume analysis pipeline:
        1. Preprocessing and cleaning.
        2. Duplicate check using SHA-256 hashes.
        3. Skill extraction.
        4. Exact & semantic matching.
        5. Document level semantic similarity.
        6. Combined compatibility scoring.
        7. Grounded recommendation generation.
        8. Database storage.
        """
        if not resume_text.strip():
            raise AnalysisError("Resume text cannot be empty.")
        if not job_description.strip():
            raise AnalysisError("Job description cannot be empty.")
            
        # 1. Clean texts
        clean_resume = TextPreprocessor.clean_text(resume_text)
        clean_jd = TextPreprocessor.clean_text(job_description)
        
        # Calculate content hashes
        resume_hash = calculate_hash(clean_resume)
        jd_hash = calculate_hash(clean_jd)
        
        # 2. Check for duplicate analysis in database
        cached = AnalysisRepository.get_analyses_by_hashes(db, resume_hash, jd_hash)
        if cached:
            logger.info(f"Duplicate match found. Returning cached analysis: {cached.id}")
            result = cached.to_dict()
            # Reconstitute resume_skills & job_required_skills
            result["resume_skills"] = sorted(list(set(cached.matched_skills + cached.additional_skills)))
            result["job_required_skills"] = sorted(list(set(cached.matched_skills + cached.missing_skills)))
            result["score_breakdown"] = {
                "skill_match_weight": settings.SKILL_MATCH_WEIGHT,
                "semantic_similarity_weight": settings.SEMANTIC_WEIGHT
            }
            return result
            
        # 3. Extract skills
        resume_skills_data = self.skill_extractor.extract_skills(clean_resume)
        jd_skills_data = self.skill_extractor.extract_skills(clean_jd)
        
        resume_skills = resume_skills_data["skills"]
        job_skills = jd_skills_data["skills"]
        
        # 4. Perform skill matching (exact + semantic)
        # Use semantic threshold of 0.85 (conservative)
        matching_res = MatchingService.match_skills(
            resume_skills=resume_skills,
            job_skills=job_skills,
            embedding_service=self.embedding_service,
            semantic_threshold=0.85
        )
        
        matched_skills = matching_res["matched_skills"]
        missing_skills = matching_res["missing_skills"]
        additional_skills = matching_res["additional_skills"]
        explainable_matches = matching_res["explainable_matches"]
        
        # 5. Document-level semantic embedding & similarity
        try:
            resume_vector = self.embedding_service.encode_text(clean_resume)
            jd_vector = self.embedding_service.encode_text(clean_jd)
            semantic_sim = SimilarityService.calculate_cosine_similarity(resume_vector, jd_vector)
        except Exception as e:
            logger.error(f"Semantic similarity encoding failed: {str(e)}")
            # Fallback score if embedding fails
            semantic_sim = 0.0
            
        # 6. Compatibility scoring
        scores = ScoringService.calculate_scores(
            matched_skills_count=len(matched_skills),
            total_required_skills=len(job_skills),
            semantic_similarity_score=semantic_sim
        )
        
        # 7. Recommendation generation
        recommendations = RecommendationService.generate_recommendations(missing_skills)
        
        # 8. Persistence
        analysis_id = str(uuid.uuid4())
        analysis_dict = {
            "analysis_id": analysis_id,
            "resume_filename": resume_filename,
            "resume_text_hash": resume_hash,
            "job_description_hash": jd_hash,
            "semantic_similarity_score": scores["semantic_similarity_score"],
            "skill_match_score": scores["skill_match_score"],
            "overall_score": scores["overall_score"],
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "additional_skills": additional_skills,
            "recommendations": recommendations,
            "explainable_matches": explainable_matches
        }
        
        # Save record
        AnalysisRepository.create_analysis(db, analysis_dict)
        
        # Build API response schema dictionary
        analysis_dict["resume_skills"] = resume_skills
        analysis_dict["job_required_skills"] = job_skills
        analysis_dict["score_breakdown"] = {
            "skill_match_weight": scores["skill_match_weight"],
            "semantic_similarity_weight": scores["semantic_similarity_weight"]
        }
        
        return analysis_dict
