import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_ui_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "<title>AI Resume & Job Description Analyzer</title>" in response.text

def test_static_css_endpoint():
    with TestClient(app) as client:
        response = client.get("/static/style.css")
        assert response.status_code == 200
        assert "Obsidian Dark-Mode" in response.text

def test_static_js_endpoint():
    with TestClient(app) as client:
        response = client.get("/static/app.js")
        assert response.status_code == 200
        assert "DOMContentLoaded" in response.text
