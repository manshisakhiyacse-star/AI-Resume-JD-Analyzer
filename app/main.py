import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.api.routes import health, analyze, skills, jobs
from app.models.database import Base, engine
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import setup_logging

# Configure security-focused logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="REST API for analyzing candidate resumes against job descriptions, identifying matching/missing skills, and generating compatibility scores and actionable recommendations.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Register global exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(skills.router, prefix="/api/v1", tags=["Skills"])
app.include_router(jobs.router, prefix="/api/v1", tags=["Jobs"])

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("app/static/index.html")
