"""
Prediction orchestration layer for hotspot forecasting, trend forecasting,
station risk scoring, and dashboard synthesis.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional, Tuple

from sqlalchemy.orm import Session

from app.analytics.feature_engineering import feature_engineer
from app.analytics.forecasting import forecaster
from app.analytics.warning_engine import warning_engine

logger = logging.getLogger(__name__)


class PredictionEngine:
    """Combines feature engineering, forecasting, and warning logic."""

    def __init__(self) -> None:
        self._cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
        self._cache_ttl_seconds = 300

    def predict_hotspots(
        self,
        db: Session,
        *,
        district: Optional[str] = None,
        police_station: Optional[str] = None,
        crime_head_id: Optional[int] = None,
        crime_subhead_id: Optional[int] = None,
        days_ahead: int = 7,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        cache_key = self._cache_key(
            "hotspots",
            district=district,
            police_station=police_station,
            crime_head_id=crime_head_id,
            crime_subhead_id=crime_subhead_id,
            days_ahead=days_ahead,
            top_k=top_k,
        )
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        profiles = feature_engineer.build_grouped_daily_series(
            db,
            district=district,
            police_station=police_station,
            crime_head_id=crime_head_id,
            crime_subhead_id=crime_subhead_id,
            lookback_days=180,
        )

        if not profiles:
            result = {
                "status": "no_data",
                "generated_at": self._now_iso(),
                "scope": self._scope_payload(district, police_station, crime_head_id, crime_subhead_id, days_ahead),
                "predictions": [],
                "prediction": None,
                "explanation": "No historical records were found for the requested scope.",
            }
            self._set_cache(cache_key, result)
            return result

        rows = []
        for profile in profiles:
            forecast = forecaster.forecast_series(profile.series, days_ahead)
            historical_summary = feature_engineer.summarize_series(profile.series)
            risk_percentage = self._risk_from_forecast(forecast.total_predicted, profile, days_ahead)
            rows.append(
                {
                    "district": profile.district,
                    "police_station": profile.police_station,
                    "crime_type": self._dominant_crime_type(profile),
                    "predicted_hotspot": f"{profile.district} - {profile.police_station}",
                    "expected_crime_count": forecast.total_predicted,
                    "risk_percentage": risk_percentage,
                    "confidence": forecast.confidence,
                    "model_name": forecast.model_name,
                    "explanation": self._hotspot_explanation(profile, forecast, risk_percentage),
                    "features_used": {
                        "recent_7d": profile.recent_7d,
                        "previous_7d": profile.previous_7d,
                        "growth_pct": profile.growth_pct,
                        "violent_share": profile.violent_share,
                        "repeat_offender_ratio": profile.repeat_offender_ratio,
                        "days_ahead": days_ahead,
                    },
                    "historical_data_summary": historical_summary,
                }
            )

        rows = sorted(rows, key=lambda item: (item["risk_percentage"], item["expected_crime_count"]), reverse=True)
        status = "insufficient_data" if any(item["confidence"] < 0.5 for item in rows) else "success"
        result = {
            "status": status,
            "generated_at": self._now_iso(),
            "scope": self._scope_payload(district, police_station, crime_head_id, crime_subhead_id, days_ahead),
            "prediction": rows[0],
            "predictions": rows[:top_k],
            "explanation": "Hotspot forecasts were derived from historical daily counts, trend strength, and recent spike pressure.",
        }
        self._set_cache(cache_key, result)
        return result

    def predict_trends(
        self,
        db: Session,
        *,
        district: Optional[str] = None,
        police_station: Optional[str] = None,
        crime_head_id: Optional[int] = None,
        crime_subhead_id: Optional[int] = None,
        period: str = "next_week",
    ) -> Dict[str, Any]:
        days_ahead = 30 if period == "next_month" else 7
        cache_key = self._cache_key(
            "trends",
            district=district,
            police_station=police_station,
            crime_head_id=crime_head_id,
            crime_subhead_id=crime_subhead_id,
            period=period,
        )
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        series = feature_engineer.build_daily_series(
            db,
            district=district,
            police_station=police_station,
            crime_head_id=crime_head_id,
            crime_subhead_id=crime_subhead_id,
            lookback_days=365,
        )

        if not series:
            result = {
                "status": "no_data",
                "generated_at": self._now_iso(),
                "scope": self._scope_payload(district, police_station, crime_head_id, crime_subhead_id, period),
                "prediction": None,
                "explanation": "No historical records were found for the requested scope.",
            }
            self._set_cache(cache_key, result)
            return result

        forecast = forecaster.forecast_series(series, days_ahead)
        historical_summary = feature_engineer.summarize_series(series)
        result = {
            "status": "insufficient_data" if forecast.confidence < 0.5 else "success",
            "generated_at": self._now_iso(),
            "scope": self._scope_payload(district, police_station, crime_head_id, crime_subhead_id, period),
            "prediction": {
                "period": period,
                "predicted_value": forecast.total_predicted,
                "trend_direction": forecast.trend_direction,
                "confidence": forecast.confidence,
                "model_name": forecast.model_name,
                "explanation": forecast.explanation,
                "features_used": {
                    "days_ahead": days_ahead,
                    "sample_size": len(series),
                    "recent_7d": historical_summary["recent_7d"],
                    "previous_7d": historical_summary["previous_7d"],
                    "growth_pct": historical_summary["growth_pct"],
                },
                "historical_data_summary": historical_summary,
            },
            "explanation": f"Forecast generated for {period.replace('_', ' ')} using {forecast.model_name}.",
        }
        self._set_cache(cache_key, result)
        return result

    def predict_station_risk(
        self,
        db: Session,
        *,
        district: Optional[str] = None,
        police_station: Optional[str] = None,
        top_k: int = 10,
    ) -> Dict[str, Any]:
        cache_key = self._cache_key("station_risk", district=district, police_station=police_station, top_k=top_k)
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        profiles = feature_engineer.build_grouped_daily_series(
            db,
            district=district,
            police_station=police_station,
            lookback_days=180,
        )

        if not profiles:
            result = {
                "status": "no_data",
                "generated_at": self._now_iso(),
                "scope": self._scope_payload(district, police_station, None, None, top_k),
                "predictions": [],
                "prediction": None,
                "explanation": "No historical records were found for the requested scope.",
            }
            self._set_cache(cache_key, result)
            return result

        rows = []
        for profile in profiles:
            risk = forecaster.score_station_risk(
                {
                    "recent_7d": profile.recent_7d,
                    "previous_7d": profile.previous_7d,
                    "growth_pct": profile.growth_pct,
                    "average_daily_count": profile.average_daily_count,
                    "violent_share": profile.violent_share,
                    "repeat_offender_ratio": profile.repeat_offender_ratio,
                    "total_records": profile.total_records,
                }
            )
            rows.append(
                {
                    "district": profile.district,
                    "police_station": profile.police_station,
                    **risk,
                    "historical_data_summary": feature_engineer.summarize_series(profile.series),
                }
            )

        rows = sorted(rows, key=lambda item: item["risk_score"], reverse=True)
        result = {
            "status": "insufficient_data" if any(item["confidence"] < 0.5 for item in rows) else "success",
            "generated_at": self._now_iso(),
            "scope": self._scope_payload(district, police_station, None, None, top_k),
            "prediction": rows[0],
            "predictions": rows[:top_k],
            "explanation": "Station risk scores were derived from recent volume, increase rate, violent crime share, and repeat offender pressure.",
        }
        self._set_cache(cache_key, result)
        return result

    def predict_warnings(
        self,
        db: Session,
        *,
        district: Optional[str] = None,
        police_station: Optional[str] = None,
    ) -> Dict[str, Any]:
        cache_key = self._cache_key("warnings", district=district, police_station=police_station)
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        result = warning_engine.generate_warnings(db, district=district, police_station=police_station)
        result = {**result, "scope": self._scope_payload(district, police_station, None, None)}
        self._set_cache(cache_key, result)
        return result

    def predict_dashboard(
        self,
        db: Session,
        *,
        district: Optional[str] = None,
        police_station: Optional[str] = None,
    ) -> Dict[str, Any]:
        cache_key = self._cache_key("dashboard", district=district, police_station=police_station)
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        result = {
            "status": "success",
            "generated_at": self._now_iso(),
            "scope": self._scope_payload(district, police_station, None, None),
            "hotspot_forecast": self.predict_hotspots(db, district=district, police_station=police_station),
            "trend_forecast": self.predict_trends(db, district=district, police_station=police_station),
            "station_risk": self.predict_station_risk(db, district=district, police_station=police_station),
            "warnings": self.predict_warnings(db, district=district, police_station=police_station),
        }
        self._set_cache(cache_key, result)
        return result

    def _risk_from_forecast(self, predicted_total: int, profile, days_ahead: int) -> float:
        baseline = max(profile.average_daily_count * days_ahead, 1.0)
        ratio = predicted_total / baseline
        spike_component = max(0.0, profile.growth_pct) / 2.0
        violent_component = profile.violent_share * 20.0
        repeat_component = profile.repeat_offender_ratio * 20.0
        raw = (ratio * 45.0) + spike_component + violent_component + repeat_component
        return round(min(100.0, max(0.0, raw)), 2)

    def _dominant_crime_type(self, profile) -> str:
        if not profile.crime_mix:
            return "All Crime Types"
        return profile.crime_mix[0]["crime_label"]

    def _hotspot_explanation(self, profile, forecast, risk_percentage: float) -> str:
        return (
            f"{profile.police_station} in {profile.district} shows a {forecast.trend_direction} trend with "
            f"{forecast.total_predicted} predicted incidents over the next forecast window and a risk score of {risk_percentage:.1f}%."
        )

    def _scope_payload(self, district, police_station, crime_head_id, crime_subhead_id, period=None) -> Dict[str, Any]:
        return {
            "district": district,
            "police_station": police_station,
            "crime_head_id": crime_head_id,
            "crime_subhead_id": crime_subhead_id,
            "period": period,
        }

    def _cache_key(self, name: str, **kwargs: Any) -> str:
        payload = json.dumps({k: kwargs[k] for k in sorted(kwargs)}, sort_keys=True, default=str)
        digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()
        return f"{name}:{digest}"

    def _get_cache(self, key: str) -> Optional[Dict[str, Any]]:
        cached = self._cache.get(key)
        if not cached:
            return None
        timestamp, payload = cached
        if time.time() - timestamp > self._cache_ttl_seconds:
            self._cache.pop(key, None)
            return None
        return payload

    def _set_cache(self, key: str, payload: Dict[str, Any]) -> None:
        self._cache[key] = (time.time(), payload)

    def _now_iso(self) -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()


prediction_engine = PredictionEngine()
