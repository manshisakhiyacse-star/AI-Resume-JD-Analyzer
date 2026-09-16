from fastapi import APIRouter

router = APIRouter()

@router.get("/health", summary="Health Check", description="Returns the status of the service to verify it is running.")
async def health_check():
    return {
        "status": "healthy",
        "service": "resume-job-analyzer"
    }
