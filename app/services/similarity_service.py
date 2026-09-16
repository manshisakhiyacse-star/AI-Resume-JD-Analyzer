import numpy as np
from typing import List
from app.core.exceptions import AnalysisError

class SimilarityService:
    @staticmethod
    def calculate_cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
        """
        Calculates the cosine similarity between two vectors and maps the output to a 0-100 range.
        
        Formula:
            similarity = (A . B) / (||A|| * ||B||)
            score = max(0.0, min(100.0, similarity * 100.0))
        """
        if not vector_a or not vector_b:
            raise AnalysisError("Cannot calculate similarity for empty embedding vectors.")
            
        if len(vector_a) != len(vector_b):
            raise AnalysisError(
                f"Dimension mismatch: Vector A has size {len(vector_a)} "
                f"but Vector B has size {len(vector_b)}."
            )
            
        array_a = np.array(vector_a)
        array_b = np.array(vector_b)
        
        norm_a = np.linalg.norm(array_a)
        norm_b = np.linalg.norm(array_b)
        
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
            
        dot_product = np.dot(array_a, array_b)
        similarity = float(dot_product / (norm_a * norm_b))
        
        # Normalize to 0-100 range
        score = max(0.0, min(100.0, similarity * 100.0))
        return round(score, 2)
