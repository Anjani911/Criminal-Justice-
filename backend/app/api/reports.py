"""
Reports Router
==============
REST endpoints for generating structured investigation reports.

GET /api/v1/reports/case/{case_id}    → Full case investigation report
GET /api/v1/reports/district          → District crime summary report
GET /api/v1/reports/dashboard         → Complete dashboard data report
"""
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/case/{case_id}", summary="Case Investigation Report")
def case_report(
    case_id: int,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Generate a comprehensive investigation report for a single FIR case.
    Includes case metadata, crime classification, accused/victim lists,
    arrest details, criminal network sub-graph, and an AI summary placeholder.
    """
    try:
        return report_service.generate_case_report(db, case_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/district", summary="District Crime Summary Report")
def district_report(
    district: str = Query(..., min_length=2, description="District name"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter to a specific year"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Generate a crime statistics summary report for an entire district.
    Includes monthly trends, crime category breakdown, unit hotspots,
    and KPI summaries. Optionally filter statistics to a specific year.
    """
    return report_service.generate_district_report(db, district=district, year=year)


@router.get("/dashboard", summary="Dashboard Summary Report")
def dashboard_report(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Generate the complete dashboard data payload in a single call.
    Includes KPIs, trends, hotspots, crime type distribution,
    case status breakdowns, and network metrics.
    """
    return report_service.generate_dashboard_report(db)
