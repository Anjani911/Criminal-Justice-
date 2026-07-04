"""
Analytics Router
================
REST endpoints serving the SQL-based analytics engine.

GET /api/v1/analytics/dashboard        → KPI summary cards
GET /api/v1/analytics/crime-trends     → Monthly / yearly case trends
GET /api/v1/analytics/monthly-statistics → Monthly case, status, and clearance stats
GET /api/v1/analytics/crime-types      → Distribution by crime category
GET /api/v1/analytics/hotspots         → District and unit-level hotspots
GET /api/v1/analytics/police-stations   → District/unit investigation statistics
GET /api/v1/analytics/status           → Case status breakdown
GET /api/v1/analytics/accused-status   → Accused status breakdown
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", summary="Dashboard KPI Summary")
def dashboard_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Return high-level KPIs for the main dashboard:
    total cases, accused, victims, arrests, absconding suspects,
    and cases currently under investigation.
    """
    return analytics_service.get_dashboard_summary(db)


@router.get("/crime-trends", summary="Monthly Crime Trends")
def crime_trends(
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter trends to a specific year"),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Return case registrations grouped by month.
    Optionally filter by year. Returns chronologically sorted data
    suitable for line charts.
    """
    return analytics_service.get_monthly_trends(db, year=year)


@router.get("/monthly-statistics", summary="Monthly Statistics")
def monthly_statistics(
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter statistics to a specific year"),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Return month-wise case volume with investigation and clearance breakdown.
    Suitable for stacked charts and monthly operational reporting.
    """
    return analytics_service.get_monthly_statistics(db, year=year)


@router.get("/yearly-summary", summary="Yearly Case Summary")
def yearly_summary(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Return total cases registered per calendar year."""
    return analytics_service.get_yearly_summary(db)


@router.get("/crime-types", summary="Crime Type Distribution")
def crime_type_distribution(
    crime_head_id: Optional[int] = Query(None, description="Filter to subheads of a specific crime category"),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Return case counts grouped by crime category.
    Optionally drill down into sub-categories by providing crime_head_id.
    Suitable for pie/donut and bar charts.
    """
    if crime_head_id:
        return analytics_service.get_crime_subtype_distribution(db, crime_head_id=crime_head_id)
    return analytics_service.get_crime_type_distribution(db)


@router.get("/hotspots", summary="Crime Hotspot Analysis")
def hotspots(
    district: Optional[str] = Query(None, description="Drill into a specific district's police stations"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Return crime hotspot data at district and station level.
    If district is provided, returns police-station-level breakdown within it.
    Drives the geographic heatmap on the dashboard.
    """
    return {
        "district_hotspots": analytics_service.get_district_hotspots(db),
        "unit_hotspots": analytics_service.get_unit_hotspots(db, district=district),
    }


@router.get("/police-stations", summary="Police Station Statistics")
def police_station_statistics(
    district: Optional[str] = Query(None, description="Filter to a district"),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Return police-station level workload statistics for operational dashboards.
    """
    return analytics_service.get_police_station_statistics(db, district=district)


@router.get("/status", summary="Case Status Breakdown")
def case_status(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Return case counts grouped by investigation status."""
    return analytics_service.get_case_status_summary(db)


@router.get("/accused-status", summary="Accused Status Breakdown")
def accused_status(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Return accused counts grouped by their current status (Arrested, Absconding, etc.)."""
    return analytics_service.get_accused_status_summary(db)
