"""
Predictive analytics API router.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_employee
from app.models.employee import Employee
from app.services.audit_service import audit_service
from app.database.database import get_db
from app.schemas.prediction import HotspotPredictionResponse, PredictionDashboardResponse, StationRiskResponse, TrendPredictionResponse, WarningResponse
from app.services.prediction_service import prediction_service
from app.utils.config import settings


logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.API_V1_STR}/predictions", tags=["Predictive Analytics"])


@router.get("/hotspots", response_model=HotspotPredictionResponse, summary="Forecast Future Crime Hotspots")
def hotspot_forecast(
    request: Request,
    district: Optional[str] = Query(None, description="District name"),
    police_station: Optional[str] = Query(None, description="Police station or unit name"),
    crime_head_id: Optional[int] = Query(None, ge=1, description="Crime head ID"),
    crime_subhead_id: Optional[int] = Query(None, ge=1, description="Crime subhead ID"),
    days_ahead: int = Query(7, ge=1, le=30, description="Forecast horizon in days"),
    top_k: int = Query(5, ge=1, le=20, description="Number of hotspot predictions to return"),
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
) -> HotspotPredictionResponse:
    ip_address = request.client.host if request.client else None
    audit_service.log_action(
        db=db,
        employee_id=current_employee.id,
        username=current_employee.username,
        role=current_employee.role,
        action="predict_hotspots",
        resource_type="prediction",
        description=f"Predicted hotspots for district={district}",
        status="Success",
        ip_address=ip_address,
    )
    try:
        logger.info(
            "Prediction hotspot request district=%s police_station=%s crime_head_id=%s crime_subhead_id=%s days_ahead=%s top_k=%s",
            district,
            police_station,
            crime_head_id,
            crime_subhead_id,
            days_ahead,
            top_k,
        )
        result = prediction_service.get_hotspot_forecast(db, district=district, police_station=police_station, crime_head_id=crime_head_id, crime_subhead_id=crime_subhead_id, days_ahead=days_ahead, top_k=top_k)
        return HotspotPredictionResponse.model_validate(result)
    except Exception as exc:
        logger.exception("Hotspot prediction failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/trends", response_model=TrendPredictionResponse, summary="Forecast Crime Trends")
def trend_forecast(
    request: Request,
    district: Optional[str] = Query(None, description="District name"),
    police_station: Optional[str] = Query(None, description="Police station or unit name"),
    crime_head_id: Optional[int] = Query(None, ge=1, description="Crime head ID"),
    crime_subhead_id: Optional[int] = Query(None, ge=1, description="Crime subhead ID"),
    period: str = Query("next_week", pattern="^(next_week|next_month)$", description="Forecast period"),
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
) -> TrendPredictionResponse:
    ip_address = request.client.host if request.client else None
    audit_service.log_action(
        db=db,
        employee_id=current_employee.id,
        username=current_employee.username,
        role=current_employee.role,
        action="predict_trends",
        resource_type="prediction",
        description=f"Predicted trends for period={period}",
        status="Success",
        ip_address=ip_address,
    )
    try:
        logger.info(
            "Prediction trend request district=%s police_station=%s crime_head_id=%s crime_subhead_id=%s period=%s",
            district,
            police_station,
            crime_head_id,
            crime_subhead_id,
            period,
        )
        result = prediction_service.get_trend_forecast(db, district=district, police_station=police_station, crime_head_id=crime_head_id, crime_subhead_id=crime_subhead_id, period=period)
        return TrendPredictionResponse.model_validate(result)
    except Exception as exc:
        logger.exception("Trend prediction failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/station-risk", response_model=StationRiskResponse, summary="Predict Police Station Risk Score")
def station_risk(
    request: Request,
    district: Optional[str] = Query(None, description="District name"),
    police_station: Optional[str] = Query(None, description="Police station or unit name"),
    top_k: int = Query(10, ge=1, le=20, description="Number of station risk rows to return"),
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
) -> StationRiskResponse:
    ip_address = request.client.host if request.client else None
    audit_service.log_action(
        db=db,
        employee_id=current_employee.id,
        username=current_employee.username,
        role=current_employee.role,
        action="predict_station_risk",
        resource_type="prediction",
        description=f"Predicted station risk for district={district}",
        status="Success",
        ip_address=ip_address,
    )
    try:
        logger.info("Prediction station-risk request district=%s police_station=%s top_k=%s", district, police_station, top_k)
        result = prediction_service.get_station_risk(db, district=district, police_station=police_station, top_k=top_k)
        return StationRiskResponse.model_validate(result)
    except Exception as exc:
        logger.exception("Station risk prediction failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/warnings", response_model=WarningResponse, summary="Generate Early Warnings")
def warnings(
    request: Request,
    district: Optional[str] = Query(None, description="District name"),
    police_station: Optional[str] = Query(None, description="Police station or unit name"),
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
) -> WarningResponse:
    ip_address = request.client.host if request.client else None
    audit_service.log_action(
        db=db,
        employee_id=current_employee.id,
        username=current_employee.username,
        role=current_employee.role,
        action="predict_warnings",
        resource_type="prediction",
        description=f"Generated early warnings for district={district}",
        status="Success",
        ip_address=ip_address,
    )
    try:
        logger.info("Prediction warnings request district=%s police_station=%s", district, police_station)
        result = prediction_service.get_warnings(db, district=district, police_station=police_station)
        return WarningResponse.model_validate(result)
    except Exception as exc:
        logger.exception("Warning prediction failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/dashboard", response_model=PredictionDashboardResponse, summary="Predictive Dashboard")
def dashboard(
    request: Request,
    district: Optional[str] = Query(None, description="District name"),
    police_station: Optional[str] = Query(None, description="Police station or unit name"),
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
) -> PredictionDashboardResponse:
    ip_address = request.client.host if request.client else None
    audit_service.log_action(
        db=db,
        employee_id=current_employee.id,
        username=current_employee.username,
        role=current_employee.role,
        action="predict_dashboard",
        resource_type="prediction",
        description="Generated prediction dashboard",
        status="Success",
        ip_address=ip_address,
    )
    try:
        logger.info("Prediction dashboard request district=%s police_station=%s", district, police_station)
        result = prediction_service.get_dashboard(db, district=district, police_station=police_station)
        return PredictionDashboardResponse.model_validate(result)
    except Exception as exc:
        logger.exception("Prediction dashboard failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
