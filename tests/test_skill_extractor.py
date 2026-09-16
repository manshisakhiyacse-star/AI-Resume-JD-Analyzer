import pytest
from app.services.skill_extractor import SkillExtractor

@pytest.fixture
def extractor():
    return SkillExtractor()

def test_extract_basic_skills(extractor):
    text = "I am a Python developer with experience in FastAPI, Docker, and PostgreSQL."
    result = extractor.extract_skills(text)
    
    assert "python" in result["skills"]
    assert "fastapi" in result["skills"]
    assert "docker" in result["skills"]
    assert "postgresql" in result["skills"]
    
    # Categorization check
    assert "python" in result["categories"]["programming_languages"]
    assert "fastapi" in result["categories"]["frameworks"]
    assert "docker" in result["categories"]["devops"]
    assert "postgresql" in result["categories"]["databases"]

def test_alias_normalization(extractor):
    text = "We use py, postgres, js, and ts. Also we build restful apis and springboot apps."
    result = extractor.extract_skills(text)
    
    assert "python" in result["skills"]
    assert "postgresql" in result["skills"]
    assert "javascript" in result["skills"]
    assert "typescript" in result["skills"]
    assert "rest api" in result["skills"]
    assert "spring boot" in result["skills"]

def test_no_false_positives(extractor):
    # 'py' in 'happy', 'js' in 'logs', 'ts' in 'its' should not trigger skill match
    text = "I am happy with its logs."
    result = extractor.extract_skills(text)
    
    assert "python" not in result["skills"]
    assert "javascript" not in result["skills"]
    assert "typescript" not in result["skills"]

def test_special_characters_matching(extractor):
    text = "Skills: C++, C#, .NET, Node.js."
    # Since .NET and Node.js have punctuation, let's verify if they match correctly
    # Note: text preprocessor normalizes Node.js to nodejs or preserves it depending on rules.
    # In TextPreprocessor: node.js -> nodejs, and in skills.json aliases: nodejs -> node.js.
    # Let's verify how it behaves.
    result = extractor.extract_skills(text)
    
    assert "c++" in result["skills"]
    # Let's check node.js matching
    # Node.js -> TextPreprocessor normalizes node.js to nodejs -> SkillExtractor matches nodejs and resolves to node.js (canonical)
    assert "node.js" in result["skills"]
