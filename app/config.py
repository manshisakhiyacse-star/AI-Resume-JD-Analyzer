import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "AI Resume & Job Description Analyzer"
    APP_ENV: str = "local"
    MODEL_NAME: str = "all-MiniLM-L6-v2"
    DATABASE_URL: str = "sqlite:///./data/resume_analyzer.db"
    MAX_FILE_SIZE_MB: int = 10
    MAX_TEXT_LENGTH: int = 50000
    SKILL_MATCH_WEIGHT: float = 0.60
    SEMANTIC_WEIGHT: float = 0.40
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
