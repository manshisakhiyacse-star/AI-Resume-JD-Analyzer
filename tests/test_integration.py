import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_full_pipeline_integration(client):
    # 1. Load sample files
    with open("sample_data/sample_resume.pdf", "rb") as f:
        pdf_bytes = f.read()
        
    with open("sample_data/sample_job_description.txt", "r", encoding="utf-8") as f:
        job_desc = f.read()
        
    # 2. Call analyze endpoint
    response = client.post(
        "/api/v1/analyze",
        files={"resume_file": ("sample_resume.pdf", pdf_bytes, "application/pdf")},
        data={"job_description": job_desc}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # 3. Check response structure
    assert "analysis_id" in data
    analysis_id = data["analysis_id"]
    
    # Verify scores are correct
    assert 0 <= data["semantic_similarity_score"] <= 100
    assert 0 <= data["skill_match_score"] <= 100
    assert 0 <= data["overall_score"] <= 100
    
    # Verify matched skills
    # JD has Python, FastAPI, PostgreSQL, Docker, AWS, Machine Learning, NLP
    # Resume has Python, FastAPI, REST APIs, MySQL, Docker, Machine Learning, NLP (as NLP), Sentence Transformers
    # Matches: Python, FastAPI, Docker, Machine Learning, NLP (resolves to natural language processing)
    matched = data["matched_skills"]
    assert "python" in matched
    assert "fastapi" in matched
    assert "docker" in matched
    assert "machine learning" in matched
    assert "natural language processing" in matched
    
    # Missing: PostgreSQL, AWS (resolves to amazon web services)
    missing = data["missing_skills"]
    assert "postgresql" in missing
    assert "amazon web services" in missing
    
    # Additional: MySQL, REST API (resolves to rest api), Sentence Transformers
    additional = data["additional_skills"]
    assert "mysql" in additional
    assert "rest api" in additional
    assert "sentence transformers" in additional
    
    # 4. Verify recommendations generated for missing skills
    recs = data["recommendations"]
    assert len(recs) >= 2
    assert any("AWS" in r or "Amazon Web Services" in r for r in recs)
    assert any("PostgreSQL" in r for r in recs)
    
    # 5. Fetch from Database using the retrieved analysis ID
    get_response = client.get(f"/api/v1/analysis/{analysis_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["analysis_id"] == analysis_id
    assert get_data["overall_score"] == data["overall_score"]
    assert get_data["matched_skills"] == matched
