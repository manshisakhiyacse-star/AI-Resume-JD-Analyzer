from fastapi import APIRouter, Depends
from app.schemas.skills import SkillsListResponse, SkillsCategoriesResponse
from app.services.skill_extractor import SkillExtractor

router = APIRouter()

# Dependency to get SkillExtractor
def get_skill_extractor() -> SkillExtractor:
    return SkillExtractor()

@router.get("/skills", response_model=SkillsListResponse, summary="Get Canonical Skills", description="Returns a flat, sorted list of all canonical skills supported by the system.")
async def get_skills(extractor: SkillExtractor = Depends(get_skill_extractor)):
    # extractor.canonical_skills is a set, convert to sorted list
    return {"skills": sorted(list(extractor.canonical_skills))}

@router.get("/skills/categories", response_model=SkillsCategoriesResponse, summary="Get Skills by Categories", description="Returns all supported canonical skills grouped by their respective categories (e.g., databases, programming_languages).")
async def get_skills_categories(extractor: SkillExtractor = Depends(get_skill_extractor)):
    return {"categories": extractor.categories}
