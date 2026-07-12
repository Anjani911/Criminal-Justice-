"""
Prediction service layer.
"""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.analytics.prediction_engine import prediction_engine

logger = logging.getLogger(__name__)


class PredictionService:
    """Thin orchestration layer for predictive analytics endpoints."""

    def get_hotspot_forecast(self, db: Session, *, district: Optional[str] = None, police_station: Optional[str] = None, crime_head_id: Optional[int] = None, crime_subhead_id: Optional[int] = None, days_ahead: int = 7, top_k: int = 5):
        logger.info("Predict hotspot forecast requested district=%s police_station=%s crime_head_id=%s crime_subhead_id=%s days_ahead=%s", district, police_station, crime_head_id, crime_subhead_id, days_ahead)
        return prediction_engine.predict_hotspots(db, district=district, police_station=police_station, crime_head_id=crime_head_id, crime_subhead_id=crime_subhead_id, days_ahead=days_ahead, top_k=top_k)

    def get_trend_forecast(self, db: Session, *, district: Optional[str] = None, police_station: Optional[str] = None, crime_head_id: Optional[int] = None, crime_subhead_id: Optional[int] = None, period: str = "next_week"):
        logger.info("Predict trend forecast requested district=%s police_station=%s crime_head_id=%s crime_subhead_id=%s period=%s", district, police_station, crime_head_id, crime_subhead_id, period)
        return prediction_engine.predict_trends(db, district=district, police_station=police_station, crime_head_id=crime_head_id, crime_subhead_id=crime_subhead_id, period=period)

    def get_station_risk(self, db: Session, *, district: Optional[str] = None, police_station: Optional[str] = None, top_k: int = 10):
        logger.info("Predict station risk requested district=%s police_station=%s top_k=%s", district, police_station, top_k)
        return prediction_engine.predict_station_risk(db, district=district, police_station=police_station, top_k=top_k)

    def get_warnings(self, db: Session, *, district: Optional[str] = None, police_station: Optional[str] = None):
        logger.info("Predict warning requested district=%s police_station=%s", district, police_station)
        return prediction_engine.predict_warnings(db, district=district, police_station=police_station)

    def get_dashboard(self, db: Session, *, district: Optional[str] = None, police_station: Optional[str] = None):
        logger.info("Predict dashboard requested district=%s police_station=%s", district, police_station)
        return prediction_engine.predict_dashboard(db, district=district, police_station=police_station)


prediction_service = PredictionService()
