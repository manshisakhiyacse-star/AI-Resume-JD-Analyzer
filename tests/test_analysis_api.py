import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    # Using 'with' triggers the FastAPI lifespan events (which creates SQLite tables)
    with TestClient(app) as c:
        yield c

def test_get_skills(client):
    response = client.get("/api/v1/skills")
    assert response.status_code == 200
    data = response.json()
    assert "skills" in data
    assert isinstance(data["skills"], list)
    assert "python" in data["skills"]
    assert "fastapi" in data["skills"]

def test_get_skills_categories(client):
    response = client.get("/api/v1/skills/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "programming_languages" in data["categories"]
    assert "databases" in data["categories"]
    assert "python" in data["categories"]["programming_languages"]

def test_analyze_text_endpoint(client):
    payload = {
        "resume_text": "Experienced Python developer working with FastAPI and Docker containers.",
        "job_description": "Seeking a Software Engineer with skills in Python, FastAPI, and Kubernetes."
    }
    
    response = client.post("/api/v1/analyze/text", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "analysis_id" in data
    assert "overall_score" in data
    assert "skill_match_score" in data
    assert "semantic_similarity_score" in data
    
    # Python and FastAPI are matched
    assert "python" in data["matched_skills"]
    assert "fastapi" in data["matched_skills"]
    # Kubernetes is required but missing
    assert "kubernetes" in data["missing_skills"]
    # Docker is additional (not required by JD)
    assert "docker" in data["additional_skills"]
    
    assert len(data["recommendations"]) > 0
    assert data["score_breakdown"]["skill_match_weight"] == 0.60

def test_analyze_file_endpoint(client):
    # Test uploading a text resume
    file_content = b"Candidate skills: Machine Learning, Python, PostgreSQL, Git."
    job_desc = "We need a machine learning developer with Python and MySQL."
    
    response = client.post(
        "/api/v1/analyze",
        files={"resume_file": ("resume.txt", file_content, "text/plain")},
        data={"job_description": job_desc}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert "machine learning" in data["matched_skills"]
    assert "mysql" in data["missing_skills"]
    assert "postgresql" in data["additional_skills"]

def test_get_stored_analysis(client):
    # First analyze
    payload = {
        "resume_text": "Python developer specialized in MySQL.",
        "job_description": "Developer with Python and PostgreSQL."
    }
    post_resp = client.post("/api/v1/analyze/text", json=payload)
    assert post_resp.status_code == 200
    analysis_id = post_resp.json()["analysis_id"]
    
    # Retrieve
    get_resp = client.get(f"/api/v1/analysis/{analysis_id}")
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["analysis_id"] == analysis_id
    assert "python" in get_data["matched_skills"]

def test_get_analysis_not_found(client):
    response = client.get("/api/v1/analysis/non-existent-uuid")
    assert response.status_code == 404
