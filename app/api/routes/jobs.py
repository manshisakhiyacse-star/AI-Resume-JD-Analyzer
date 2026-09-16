from fastapi import APIRouter

router = APIRouter()

# Placeholder for job-description management routes in future iterations
@router.get("/jobs/placeholder", include_in_schema=False)
async def jobs_placeholder():
    return {"message": "This is a placeholder for job posting management features."}
