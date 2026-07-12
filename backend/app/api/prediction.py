"""
Predictive analytics API router.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.prediction import HotspotPredictionResponse, PredictionDashboardResponse, StationRiskResponse, TrendPredictionResponse, WarningResponse
from app.services.prediction_service import prediction_service
from app.utils.config import settings


logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.API_V1_STR}/predictions", tags=["Predictive Analytics"])


@router.get("/hotspots", response_model=HotspotPredictionResponse, summary="Forecast Future Crime Hotspots")
def hotspot_forecast(
    district: Optional[str] = Query(None, description="District name"),
    police_station: Optional[str] = Query(None, description="Police station or unit name"),
    crime_head_id: Optional[int] = Query(None, ge=1, description="Crime head ID"),
    crime_subhead_id: Optional[int] = Query(None, ge=1, description="Crime subhead ID"),
    days_ahead: int = Query(7, ge=1, le=30, description="Forecast horizon in days"),
    top_k: int = Query(5, ge=1, le=20, description="Number of hotspot predictions to return"),
    db: Session = Depends(get_db),
) -> HotspotPredictionResponse:
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
    district: Optional[str] = Query(None, description="District name"),
    police_station: Optional[str] = Query(None, description="Police station or unit name"),
    crime_head_id: Optional[int] = Query(None, ge=1, description="Crime head ID"),
    crime_subhead_id: Optional[int] = Query(None, ge=1, description="Crime subhead ID"),
    period: str = Query("next_week", pattern="^(next_week|next_month)$", description="Forecast period"),
    db: Session = Depends(get_db),
) -> TrendPredictionResponse:
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
    district: Optional[str] = Query(None, description="District name"),
    police_station: Optional[str] = Query(None, description="Police station or unit name"),
    top_k: int = Query(10, ge=1, le=20, description="Number of station risk rows to return"),
    db: Session = Depends(get_db),
) -> StationRiskResponse:
    try:
        logger.info("Prediction station-risk request district=%s police_station=%s top_k=%s", district, police_station, top_k)
        result = prediction_service.get_station_risk(db, district=district, police_station=police_station, top_k=top_k)
        return StationRiskResponse.model_validate(result)
    except Exception as exc:
        logger.exception("Station risk prediction failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/warnings", response_model=WarningResponse, summary="Generate Early Warnings")
def warnings(
    district: Optional[str] = Query(None, description="District name"),
    police_station: Optional[str] = Query(None, description="Police station or unit name"),
    db: Session = Depends(get_db),
) -> WarningResponse:
    try:
        logger.info("Prediction warnings request district=%s police_station=%s", district, police_station)
        result = prediction_service.get_warnings(db, district=district, police_station=police_station)
        return WarningResponse.model_validate(result)
    except Exception as exc:
        logger.exception("Warning prediction failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/dashboard", response_model=PredictionDashboardResponse, summary="Predictive Dashboard")
def dashboard(
    district: Optional[str] = Query(None, description="District name"),
    police_station: Optional[str] = Query(None, description="Police station or unit name"),
    db: Session = Depends(get_db),
) -> PredictionDashboardResponse:
    try:
        logger.info("Prediction dashboard request district=%s police_station=%s", district, police_station)
        result = prediction_service.get_dashboard(db, district=district, police_station=police_station)
        return PredictionDashboardResponse.model_validate(result)
    except Exception as exc:
        logger.exception("Prediction dashboard failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
