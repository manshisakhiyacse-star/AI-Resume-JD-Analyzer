import logging
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.core.exceptions import EmbeddingError

logger = logging.getLogger(__name__)

class EmbeddingService:
    _model: SentenceTransformer = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            logger.info(f"Initializing SentenceTransformer model: {settings.MODEL_NAME}")
            try:
                # Load model
                cls._model = SentenceTransformer(settings.MODEL_NAME)
            except Exception as e:
                logger.error(f"Failed to load embedding model: {str(e)}")
                raise EmbeddingError(f"Failed to initialize embedding model: {str(e)}")
        return cls._model

    def __init__(self):
        # Trigger initialization if not already done
        self.get_model()

    def encode_text(self, text: str) -> List[float]:
        """
        Encodes a single text block into a dense vector representation.
        """
        if not text.strip():
            raise EmbeddingError("Cannot encode empty text.")
        try:
            model = self.get_model()
            embedding = model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            raise EmbeddingError(f"Error generating embedding: {str(e)}")

    def encode_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Encodes a list of text blocks.
        """
        if not texts:
            return []
        try:
            model = self.get_model()
            embeddings = model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            raise EmbeddingError(f"Error generating embeddings: {str(e)}")

    def calculate_embedding(self, text: str) -> List[float]:
        """
        Alias for encode_text.
        """
        return self.encode_text(text)
