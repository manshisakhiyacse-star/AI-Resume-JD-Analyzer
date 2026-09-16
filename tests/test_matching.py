import pytest
from app.services.matching_service import MatchingService
from app.core.exceptions import AnalysisError

class MockEmbeddingService:
    def encode_texts(self, texts):
        # 2D mock vectors to test cosine similarity logic in matching
        vectors = []
        for t in texts:
            t_lower = t.lower()
            if "aws" in t_lower or "amazon" in t_lower or "cloud" in t_lower:
                # AWS and Amazon Web Services will be close
                vectors.append([0.99, 0.01])
            elif "react" in t_lower:
                vectors.append([0.0, 1.0])
            elif "angular" in t_lower:
                # React and Angular similarity: dot([0.0, 1.0], [0.5, 0.866]) = 0.866
                # Under 0.90 threshold, but above 0.80
                vectors.append([0.5, 0.866])
            elif "docker" in t_lower:
                vectors.append([1.0, 0.0])
            elif "kubernetes" in t_lower:
                vectors.append([0.0, -1.0])
            else:
                vectors.append([0.1, 0.2])
        return vectors

def test_exact_skill_matching():
    resume_skills = ["Python", "FastAPI", "MySQL", "Docker"]
    job_skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"]
    
    result = MatchingService.match_skills(resume_skills, job_skills)
    
    assert result["matched_skills"] == ["docker", "fastapi", "python"]
    assert result["missing_skills"] == ["aws", "postgresql"]
    assert result["additional_skills"] == ["mysql"]
    
    # Check explanation structure
    assert result["explainable_matches"]["python"]["match_type"] == "exact"
    assert result["explainable_matches"]["python"]["similarity_score"] == 100.0

def test_semantic_skill_matching():
    # AWS (Job) and AWS Cloud (Resume) should match semantically
    resume_skills = ["AWS Cloud", "Docker"]
    job_skills = ["Amazon Web Services", "Kubernetes"]
    
    mock_embeddings = MockEmbeddingService()
    result = MatchingService.match_skills(
        resume_skills, 
        job_skills, 
        embedding_service=mock_embeddings,
        semantic_threshold=0.90
    )
    
    # AWS Cloud and Amazon Web Services similarity will be high (approx 100%)
    # Kubernetes and Docker similarity will be low
    assert "amazon web services" in result["matched_skills"]
    assert "kubernetes" in result["missing_skills"]
    
    # Explanations check
    explanation = result["explainable_matches"]["amazon web services"]
    assert explanation["match_type"] == "semantic"
    assert explanation["matched_to_resume_skill"] == "aws cloud"
    assert explanation["similarity_score"] > 90.0

def test_semantic_matching_below_threshold():
    # Angular and React similarity in mock is 0.866 (86.6%)
    # If threshold is set to 0.90, they should not match
    resume_skills = ["React"]
    job_skills = ["Angular"]
    
    mock_embeddings = MockEmbeddingService()
    result = MatchingService.match_skills(
        resume_skills,
        job_skills,
        embedding_service=mock_embeddings,
        semantic_threshold=0.90
    )
    
    assert "angular" in result["missing_skills"]
    assert "react" in result["additional_skills"]
    assert "angular" not in result["matched_skills"]
