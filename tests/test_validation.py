import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_unsupported_file_type(client):
    response = client.post(
        "/api/v1/analyze",
        files={"resume_file": ("resume.png", b"fake png bytes", "image/png")},
        data={"job_description": "We need a python developer."}
    )
    
    assert response.status_code == 415
    data = response.json()
    assert data["error"]["code"] == "UNSUPPORTED_FILE_TYPE"
    assert "Only PDF, DOCX and TXT" in data["error"]["message"]

def test_file_too_large(client, monkeypatch):
    # Temporarily set max file size to 0 to trigger file too large error
    monkeypatch.setattr(settings, "MAX_FILE_SIZE_MB", 0)
    
    response = client.post(
        "/api/v1/analyze",
        files={"resume_file": ("resume.txt", b"some resume content", "text/plain")},
        data={"job_description": "We need a python developer."}
    )
    
    assert response.status_code == 413
    data = response.json()
    assert data["error"]["code"] == "FILE_TOO_LARGE"
    assert "File size exceeds the limit" in data["error"]["message"]

def test_empty_file_upload(client):
    response = client.post(
        "/api/v1/analyze",
        files={"resume_file": ("resume.txt", b"", "text/plain")},
        data={"job_description": "We need a python developer."}
    )
    
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "EMPTY_DOCUMENT"

def test_missing_payload_field(client):
    # Missing job_description
    response = client.post(
        "/api/v1/analyze/text",
        json={"resume_text": "Python developer"}
    )
    
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "Field required" in data["error"]["message"]

def test_empty_payload_text(client):
    response = client.post(
        "/api/v1/analyze/text",
        json={"resume_text": "", "job_description": "We need python"}
    )
    
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "cannot be empty" in data["error"]["message"]

def test_excessive_payload_length(client, monkeypatch):
    monkeypatch.setattr(settings, "MAX_TEXT_LENGTH", 10)
    response = client.post(
        "/api/v1/analyze/text",
        json={"resume_text": "Too long text here", "job_description": "We need python"}
    )
    
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "exceeds the maximum allowed limit" in data["error"]["message"]
