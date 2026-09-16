import pytest
from app.services.embedding_service import EmbeddingService
from app.core.exceptions import EmbeddingError

@pytest.fixture(scope="module")
def embedding_service():
    return EmbeddingService()

def test_encode_text_success(embedding_service):
    text = "Python FastAPI Software Engineer"
    embedding = embedding_service.encode_text(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == 384  # all-MiniLM-L6-v2 has 384 dimensions
    assert all(isinstance(val, float) for val in embedding)

def test_encode_texts_success(embedding_service):
    texts = ["Python developer", "Machine learning practitioner"]
    embeddings = embedding_service.encode_texts(texts)
    
    assert isinstance(embeddings, list)
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384

def test_encode_empty_text_error(embedding_service):
    with pytest.raises(EmbeddingError):
        embedding_service.encode_text("")
        
    with pytest.raises(EmbeddingError):
        embedding_service.encode_text("   ")
