from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.api.analytics import router as analytics_router
from app.api.prediction import router as prediction_router
from app.api.system import router as system_router
from app.api.cases import router as cases_router
from app.api.phase5 import router as phase5_router
from app.api.network import router as network_router
from app.api.people import router as people_router
from app.api.reports import router as reports_router
from app.api.audit import router as audit_router
from app.auth.dependencies import get_current_employee
from app.middleware.exceptions import request_validation_exception_handler, unhandled_exception_handler
from app.middleware.rate_limit import RateLimitMiddleware
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

app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Configure CORS (Cross-Origin Resource Sharing)
allowed_origins = [origin.strip() for origin in settings.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]
if allowed_origins == ["*"]:
    allowed_origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)

# Register Phase 5 API routers.
protected_dependencies = [Depends(get_current_employee)]

app.include_router(auth_router)
app.include_router(system_router)
app.include_router(prediction_router, dependencies=protected_dependencies)
app.include_router(cases_router, dependencies=protected_dependencies)
app.include_router(analytics_router, dependencies=protected_dependencies)
app.include_router(network_router, dependencies=protected_dependencies)
app.include_router(people_router, dependencies=protected_dependencies)
app.include_router(reports_router, dependencies=protected_dependencies)
app.include_router(phase5_router, dependencies=protected_dependencies)
app.include_router(audit_router, dependencies=protected_dependencies)


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


@app.get("/version", tags=["General"])
def version():
    return {
        "project": settings.PROJECT_NAME,
        "version": "1.0.0",
        "api_version": settings.API_V1_STR,
    }
