"""
System and status endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.utils.config import settings


router = APIRouter(prefix=settings.API_V1_STR, tags=["System"])


@router.get("/health", summary="Health Check")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        database = "healthy"
    except Exception:
        database = "unhealthy"

    status = "healthy" if database == "healthy" else "degraded"
    return {
        "status": status,
        "environment": settings.ENVIRONMENT,
        "database": database,
        "api_version": settings.API_V1_STR,
    }


@router.get("/version", summary="API Version")
def api_version():
    return {
        "project": settings.PROJECT_NAME,
        "version": "1.0.0",
        "api_version": settings.API_V1_STR,
    }
