import pytest
from app.services.recommendation_service import RecommendationService

def test_generate_recommendations_empty():
    recs = RecommendationService.generate_recommendations([])
    assert len(recs) == 1
    assert "matches all key technical skills" in recs[0]

def test_generate_recommendations_with_skills():
    missing_skills = ["aws", "kubernetes", "postgresql", "python"]
    recs = RecommendationService.generate_recommendations(missing_skills)
    
    assert len(recs) == 4
    
    # Check that AWS is formatted uppercase, and templates match expected categories
    assert any("AWS" in r and "cloud infrastructure" in r for r in recs)
    assert any("Kubernetes" in r and "containerization" in r for r in recs)
    assert any("PostgreSQL" in r and "database modeling" in r for r in recs)
    assert any("Python" in r and "software development projects" in r for r in recs)

def test_format_skill_display():
    assert RecommendationService.format_skill_display("aws") == "AWS"
    assert RecommendationService.format_skill_display("postgresql") == "PostgreSQL"
    assert RecommendationService.format_skill_display("spring boot") == "Spring Boot"
    assert RecommendationService.format_skill_display("nextjs") == "Next.js"
    assert RecommendationService.format_skill_display("nodejs") == "Node.js"
    assert RecommendationService.format_skill_display("rest api") == "REST API"
