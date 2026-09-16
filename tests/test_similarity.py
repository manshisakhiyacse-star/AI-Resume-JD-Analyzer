import pytest
from app.services.similarity_service import SimilarityService
from app.core.exceptions import AnalysisError

def test_similarity_exact_match():
    vec_a = [1.0, 2.0, 3.0]
    vec_b = [1.0, 2.0, 3.0]
    
    score = SimilarityService.calculate_cosine_similarity(vec_a, vec_b)
    assert score == 100.0

def test_similarity_orthogonal():
    vec_a = [1.0, 0.0]
    vec_b = [0.0, 1.0]
    
    score = SimilarityService.calculate_cosine_similarity(vec_a, vec_b)
    assert score == 0.0

def test_similarity_partial_match():
    vec_a = [1.0, 1.0]
    # 45 degrees angle: cosine is approx 0.7071
    vec_b = [1.0, 0.0]
    
    score = SimilarityService.calculate_cosine_similarity(vec_a, vec_b)
    assert pytest.approx(score, 0.01) == 70.71

def test_similarity_dimension_mismatch():
    with pytest.raises(AnalysisError):
        SimilarityService.calculate_cosine_similarity([1.0, 2.0], [1.0, 2.0, 3.0])

def test_similarity_empty_vectors():
    with pytest.raises(AnalysisError):
        SimilarityService.calculate_cosine_similarity([], [1.0])
