import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)

class ResumeAnalyzerException(Exception):
    """Base exception for AI Resume & Job Description Analyzer"""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code

class DocumentParsingError(ResumeAnalyzerException):
    """Raised when parsing a resume document fails"""
    def __init__(self, message: str):
        super().__init__(message, code="DOCUMENT_PARSING_FAILED")

class UnsupportedFileTypeError(ResumeAnalyzerException):
    """Raised when an unsupported file type is provided"""
    def __init__(self, message: str = "Only PDF, DOCX and TXT files are supported."):
        super().__init__(message, code="UNSUPPORTED_FILE_TYPE")

class EmptyDocumentError(ResumeAnalyzerException):
    """Raised when an uploaded document is empty"""
    def __init__(self, message: str = "The uploaded file is empty."):
        super().__init__(message, code="EMPTY_DOCUMENT")

class FileTooLargeError(ResumeAnalyzerException):
    """Raised when an uploaded file exceeds the configured size limit"""
    def __init__(self, message: str):
        super().__init__(message, code="FILE_TOO_LARGE")

class SkillExtractionError(ResumeAnalyzerException):
    """Raised when skill extraction fails"""
    def __init__(self, message: str):
        super().__init__(message, code="SKILL_EXTRACTION_FAILED")

class EmbeddingError(ResumeAnalyzerException):
    """Raised when generating embeddings fails"""
    def __init__(self, message: str):
        super().__init__(message, code="EMBEDDING_FAILED")

class AnalysisError(ResumeAnalyzerException):
    """Raised when resume analysis fails"""
    def __init__(self, message: str):
        super().__init__(message, code="ANALYSIS_FAILED")

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(ResumeAnalyzerException)
    async def resume_analyzer_exception_handler(request: Request, exc: ResumeAnalyzerException):
        logger.error(f"Application error: {exc.code} - {exc.message}")
        
        # Map error codes to HTTP status codes
        status_code = 400
        if exc.code == "UNSUPPORTED_FILE_TYPE":
            status_code = 415
        elif exc.code == "FILE_TOO_LARGE":
            status_code = 413
        elif exc.code == "EMPTY_DOCUMENT":
            status_code = 422
            
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation error: {str(exc.errors())}")
        errors = exc.errors()
        if errors:
            loc_str = " -> ".join([str(loc) for loc in errors[0].get("loc", [])])
            msg = f"Validation failed at '{loc_str}': {errors[0].get('msg')}"
        else:
            msg = "Validation failed for the request payload."
            
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": msg
                }
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled system exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred. Please try again later."
                }
            }
        )
