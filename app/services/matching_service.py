from typing import Dict, List, Set
from app.services.embedding_service import EmbeddingService
from app.services.similarity_service import SimilarityService

class MatchingService:
    @staticmethod
    def match_skills(
        resume_skills: List[str],
        job_skills: List[str],
        embedding_service: EmbeddingService = None,
        semantic_threshold: float = 0.85
    ) -> Dict[str, any]:
        """
        Matches resume skills against job description skills.
        
        Performs:
        1. Exact (canonicalized) matching.
        2. Semantic matching for remaining unmatched skills (if embedding_service is provided).
        
        Returns:
            Dict containing:
            - matched_skills: List of skills matched (exact + semantic)
            - missing_skills: List of job skills not found in resume
            - additional_skills: List of resume skills not required by job
            - explainable_matches: Dict mapping semantic matches to their similarity details
        """
        # Lowercase and clean for matching
        r_skills = {s.lower().strip() for s in resume_skills if s.strip()}
        j_skills = {s.lower().strip() for s in job_skills if s.strip()}
        
        # 1. Exact Matching
        matched_exact = r_skills.intersection(j_skills)
        unmatched_resume = r_skills - matched_exact
        unmatched_job = j_skills - matched_exact
        
        matched_skills = set(matched_exact)
        explainable_matches = {}
        
        # 2. Semantic Matching (Optional)
        if embedding_service and unmatched_resume and unmatched_job:
            try:
                # Convert sets to lists for ordered indexing
                unmatched_resume_list = list(unmatched_resume)
                unmatched_job_list = list(unmatched_job)
                
                # Get embeddings
                resume_embeddings = embedding_service.encode_texts(unmatched_resume_list)
                job_embeddings = embedding_service.encode_texts(unmatched_job_list)
                
                # Compare all pairs
                used_resume_indices = set()
                for j_idx, job_skill in enumerate(unmatched_job_list):
                    job_emb = job_embeddings[j_idx]
                    best_score = 0.0
                    best_r_idx = -1
                    
                    for r_idx, resume_skill in enumerate(unmatched_resume_list):
                        if r_idx in used_resume_indices:
                            continue
                        res_emb = resume_embeddings[r_idx]
                        
                        score = SimilarityService.calculate_cosine_similarity(job_emb, res_emb)
                        # Cosine similarity returns 0-100 score in our SimilarityService
                        normalized_score = score / 100.0
                        
                        if normalized_score >= semantic_threshold and normalized_score > best_score:
                            best_score = normalized_score
                            best_r_idx = r_idx
                            
                    if best_r_idx != -1:
                        matched_resume_skill = unmatched_resume_list[best_r_idx]
                        used_resume_indices.add(best_r_idx)
                        
                        # Add to matched sets
                        matched_skills.add(job_skill)
                        # Map explanation: job skill -> what resume skill it matched
                        explainable_matches[job_skill] = {
                            "matched_to_resume_skill": matched_resume_skill,
                            "similarity_score": round(best_score * 100, 2),
                            "match_type": "semantic"
                        }
                        
                # Update unmatched sets based on semantic matches
                matched_resume_skills = {unmatched_resume_list[i] for i in used_resume_indices}
                matched_job_skills = set(explainable_matches.keys())
                
                unmatched_resume = unmatched_resume - matched_resume_skills
                unmatched_job = unmatched_job - matched_job_skills
                
            except Exception:
                # Fallback to pure exact matching if embedding fails
                pass
                
        # Populate explanations for exact matches too
        for skill in matched_exact:
            explainable_matches[skill] = {
                "matched_to_resume_skill": skill,
                "similarity_score": 100.0,
                "match_type": "exact"
            }
            
        return {
            "matched_skills": sorted(list(matched_skills)),
            "missing_skills": sorted(list(unmatched_job)),
            "additional_skills": sorted(list(unmatched_resume)),
            "explainable_matches": explainable_matches
        }
