import logging
from typing import Dict
from app.config import settings

logger = logging.getLogger(__name__)

class ScoringService:
    @staticmethod
    def calculate_scores(
        matched_skills_count: int,
        total_required_skills: int,
        semantic_similarity_score: float,
        skill_match_weight: float = None,
        semantic_weight: float = None
    ) -> Dict[str, float]:
        """
        Calculates the skill match score, semantic similarity score, and overall compatibility score.
        
        Formula:
            skill_match_score = (matched_skills / total_required_skills) * 100
            overall_score = (skill_match_score * skill_match_weight) + (semantic_similarity_score * semantic_weight)
        
        Handles edge cases such as zero required skills.
        """
        # Load weights from config if not provided
        if skill_match_weight is None:
            skill_match_weight = settings.SKILL_MATCH_WEIGHT
        if semantic_weight is None:
            semantic_weight = settings.SEMANTIC_WEIGHT
            
        # Ensure weights sum to 1.0; otherwise normalize them
        weight_sum = skill_match_weight + semantic_weight
        if weight_sum <= 0:
            logger.warning("Weights sum to 0. Falling back to default weights: 0.60 / 0.40.")
            skill_match_weight = 0.60
            semantic_weight = 0.40
            weight_sum = 1.0
            
        w_skill = skill_match_weight / weight_sum
        w_semantic = semantic_weight / weight_sum
        
        # Calculate skill match score
        if total_required_skills == 0:
            # Edge case: job description contains no detectable skills.
            # In this case, we default the skill match score to 100.0 or 0.0?
            # 100.0 makes sense because there are no unsatisfied requirements.
            skill_match_score = 100.0
            logger.info("Job description has no detectable skills. Setting skill match score to 100.0.")
        else:
            skill_match_score = (matched_skills_count / total_required_skills) * 100.0
            
        # Calculate overall score
        overall_score = (skill_match_score * w_skill) + (semantic_similarity_score * w_semantic)
        
        # Bounding
        skill_match_score = max(0.0, min(100.0, skill_match_score))
        overall_score = max(0.0, min(100.0, overall_score))
        
        return {
            "skill_match_score": round(skill_match_score, 2),
            "semantic_similarity_score": round(semantic_similarity_score, 2),
            "overall_score": round(overall_score, 2),
            "skill_match_weight": round(w_skill, 2),
            "semantic_similarity_weight": round(w_semantic, 2)
        }
