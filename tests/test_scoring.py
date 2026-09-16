import pytest
from app.services.scoring_service import ScoringService

def test_calculate_scores_basic():
    # 3 matched out of 4 required, similarity of 80.0
    # Weights: 0.60 / 0.40
    # skill_match_score = 75.0
    # overall_score = 0.60 * 75 + 0.40 * 80 = 45 + 32 = 77.0
    scores = ScoringService.calculate_scores(
        matched_skills_count=3,
        total_required_skills=4,
        semantic_similarity_score=80.0,
        skill_match_weight=0.60,
        semantic_weight=0.40
    )
    
    assert scores["skill_match_score"] == 75.0
    assert scores["semantic_similarity_score"] == 80.0
    assert scores["overall_score"] == 77.0
    assert scores["skill_match_weight"] == 0.60
    assert scores["semantic_similarity_weight"] == 0.40

def test_calculate_scores_no_skills_jd():
    # Edge case: Job description has 0 skills
    scores = ScoringService.calculate_scores(
        matched_skills_count=0,
        total_required_skills=0,
        semantic_similarity_score=50.0,
        skill_match_weight=0.60,
        semantic_weight=0.40
    )
    
    assert scores["skill_match_score"] == 100.0
    # overall = 0.6 * 100 + 0.4 * 50 = 60 + 20 = 80.0
    assert scores["overall_score"] == 80.0

def test_calculate_scores_weight_normalization():
    # Weights sum to 2.0 (1.5 and 0.5)
    # Normalized weights: 1.5/2.0 = 0.75, 0.5/2.0 = 0.25
    # skill_match = 100.0, semantic = 80.0
    # overall = 0.75 * 100 + 0.25 * 80 = 75 + 20 = 95.0
    scores = ScoringService.calculate_scores(
        matched_skills_count=1,
        total_required_skills=1,
        semantic_similarity_score=80.0,
        skill_match_weight=1.5,
        semantic_weight=0.5
    )
    
    assert scores["skill_match_weight"] == 0.75
    assert scores["semantic_similarity_weight"] == 0.25
    assert scores["overall_score"] == 95.0
