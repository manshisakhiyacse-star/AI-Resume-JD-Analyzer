import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
from app.models.analysis import Analysis
from app.repositories.analysis_repository import AnalysisRepository
import uuid

@pytest.fixture
def db_session():
    # Setup in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_database_crud(db_session):
    analysis_id = str(uuid.uuid4())
    data = {
        "analysis_id": analysis_id,
        "resume_filename": "resume.pdf",
        "resume_text_hash": "hash_resume_123",
        "job_description_hash": "hash_jd_456",
        "semantic_similarity_score": 85.5,
        "skill_match_score": 75.0,
        "overall_score": 81.3,
        "matched_skills": ["python", "fastapi"],
        "missing_skills": ["aws"],
        "additional_skills": ["mysql"],
        "recommendations": ["Learn AWS."],
        "explainable_matches": {"python": {"match_type": "exact"}}
    }
    
    # Create
    created = AnalysisRepository.create_analysis(db_session, data)
    assert created.id == analysis_id
    assert created.overall_score == 81.3
    
    # Retrieve
    retrieved = AnalysisRepository.get_analysis(db_session, analysis_id)
    assert retrieved is not None
    assert retrieved.resume_filename == "resume.pdf"
    assert retrieved.matched_skills == ["python", "fastapi"]
    
    # Get by hashes
    by_hashes = AnalysisRepository.get_analyses_by_hashes(
        db_session, "hash_resume_123", "hash_jd_456"
    )
    assert by_hashes is not None
    assert by_hashes.id == analysis_id
