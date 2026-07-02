from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.utils.config import settings
from app.utils.logging_config import setup_logging
from app.database.database import get_db

# Initialize logging configuration
setup_logging()
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    Useful for initializing connection pools, caches, etc.
    """
    logger.info("Initializing Crime Intelligence Platform Backend...")
    yield
    logger.info("Shutting down Crime Intelligence Platform Backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="FastAPI Backend for SCRB Karnataka AI Crime Intelligence Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS (Cross-Origin Resource Sharing)
# In production, allow_origins should be loaded from environment variables
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
def read_root():
    """
    Root endpoint offering a simple welcome and links to interactive docs.
    """
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health",
    }


@app.get("/health", tags=["General"])
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to monitor application and database status.
    """
    try:
        # Perform a simple raw query to verify database connectivity
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check connection failure: {e}")
        db_status = "unhealthy"

    app_status = "healthy" if db_status == "healthy" else "degraded"

    return {
        "status": app_status,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
    }
