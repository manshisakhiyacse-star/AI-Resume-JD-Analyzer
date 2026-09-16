from pydantic import BaseModel
from typing import Dict, List

class SkillsListResponse(BaseModel):
    skills: List[str]

class SkillsCategoriesResponse(BaseModel):
    categories: Dict[str, List[str]]
