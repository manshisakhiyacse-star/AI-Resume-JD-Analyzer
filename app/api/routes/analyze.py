from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.schemas.analysis import AnalysisTextRequest, AnalysisResponse
from app.services.document_parser import extract_text
from app.services.skill_extractor import SkillExtractor
from app.services.embedding_service import EmbeddingService
from app.services.analysis_service import AnalysisService
from app.repositories.analysis_repository import AnalysisRepository
from app.config import settings
import logging
from app.core.exceptions import ResumeAnalyzerException

logger = logging.getLogger(__name__)

router = APIRouter()

# Singletons for extractor/embeddings to prevent reloading
_skill_extractor = None
_embedding_service = None
_analysis_service = None

def get_skill_extractor() -> SkillExtractor:
    global _skill_extractor
    if _skill_extractor is None:
        _skill_extractor = SkillExtractor()
    return _skill_extractor

def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

def get_analysis_service(
    extractor: SkillExtractor = Depends(get_skill_extractor),
    embeddings: EmbeddingService = Depends(get_embedding_service)
) -> AnalysisService:
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService(
            skill_extractor=extractor,
            embedding_service=embeddings
        )
    return _analysis_service

@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze Resume File against Job Description",
    description="Upload a resume file (PDF, DOCX, or TXT) and provide the job description text to execute compatibility analysis."
)
async def analyze_file(
    resume_file: UploadFile = File(..., description="The candidate's resume file (PDF, DOCX, or TXT)."),
    job_description: str = Form(..., description="The job description text to analyze against."),
    db: Session = Depends(get_db),
    service: AnalysisService = Depends(get_analysis_service)
):
    try:
        # Validate job_description length
        if not job_description.strip():
            raise HTTPException(status_code=400, detail="Job description text cannot be empty.")
        if len(job_description) > settings.MAX_TEXT_LENGTH:
            raise HTTPException(status_code=400, detail=f"Job description exceeds character limit of {settings.MAX_TEXT_LENGTH}.")
            
        file_bytes = await resume_file.read()
        
        # Parse document
        resume_text = extract_text(file_bytes, resume_file.filename)
        
        # Execute analysis
        result = service.analyze_resume(
            db=db,
            resume_text=resume_text,
            job_description=job_description,
            resume_filename=resume_file.filename
        )
        return result
    except HTTPException:
        raise
    except ResumeAnalyzerException:
        raise
    except Exception as e:
        logger.error(f"Error in /analyze file upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred during processing.")

@router.post(
    "/analyze/text",
    response_model=AnalysisResponse,
    summary="Analyze Resume Text against Job Description",
    description="Analyze resume text and job description text directly via JSON payloads."
)
async def analyze_text(
    payload: AnalysisTextRequest,
    db: Session = Depends(get_db),
    service: AnalysisService = Depends(get_analysis_service)
):
    try:
        result = service.analyze_resume(
            db=db,
            resume_text=payload.resume_text,
            job_description=payload.job_description,
            resume_filename="text_payload"
        )
        return result
    except ResumeAnalyzerException:
        raise
    except Exception as e:
        logger.error(f"Error in /analyze/text: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred during processing.")

@router.get(
    "/analysis/{analysis_id}",
    response_model=AnalysisResponse,
    summary="Retrieve Previous Analysis",
    description="Fetch the results of a previously executed analysis by its unique UUID."
)
async def get_analysis(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    db_analysis = AnalysisRepository.get_analysis(db, analysis_id)
    if not db_analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
        
    result = db_analysis.to_dict()
    # Reconstitute resume_skills & job_required_skills
    result["resume_skills"] = sorted(list(set(db_analysis.matched_skills + db_analysis.additional_skills)))
    result["job_required_skills"] = sorted(list(set(db_analysis.matched_skills + db_analysis.missing_skills)))
    result["score_breakdown"] = {
        "skill_match_weight": settings.SKILL_MATCH_WEIGHT,
        "semantic_similarity_weight": settings.SEMANTIC_WEIGHT
    }
    return result
