"""
Predictive analytics response schemas.
"""
from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from pydantic import Field, confloat, conint

from app.schemas.base import AppBaseModel


PredictionStatus = Literal["success", "insufficient_data", "no_data"]


class HistoricalSummary(AppBaseModel):
    total_records: int = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    recent_7d: int = 0
    previous_7d: int = 0
    growth_pct: confloat(ge=-1000.0, le=1000.0) = 0
    average_daily_count: confloat(ge=0.0, le=100000.0) = 0


class HotspotPredictionItem(AppBaseModel):
    district: str
    police_station: str
    crime_type: str = "All Crime Types"
    predicted_hotspot: str
    expected_crime_count: conint(ge=0)
    risk_percentage: confloat(ge=0.0, le=100.0)
    confidence: confloat(ge=0.0, le=1.0)
    model_name: str
    explanation: str
    features_used: Dict[str, Any] = Field(default_factory=dict)
    historical_data_summary: HistoricalSummary


class HotspotPredictionResponse(AppBaseModel):
    status: PredictionStatus
    generated_at: str
    scope: Dict[str, Any] = Field(default_factory=dict)
    prediction: Optional[HotspotPredictionItem] = None
    predictions: list[HotspotPredictionItem] = Field(default_factory=list)
    explanation: str


class TrendPredictionItem(AppBaseModel):
    period: Literal["next_week", "next_month"]
    predicted_value: conint(ge=0)
    trend_direction: Literal["upward", "downward", "stable"]
    confidence: confloat(ge=0.0, le=1.0)
    model_name: str
    explanation: str
    features_used: Dict[str, Any] = Field(default_factory=dict)
    historical_data_summary: HistoricalSummary


class TrendPredictionResponse(AppBaseModel):
    status: PredictionStatus
    generated_at: str
    scope: Dict[str, Any] = Field(default_factory=dict)
    prediction: Optional[TrendPredictionItem] = None
    explanation: str


class StationRiskItem(AppBaseModel):
    district: str
    police_station: str
    risk_score: confloat(ge=0.0, le=100.0)
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    confidence: confloat(ge=0.0, le=1.0)
    model_name: str
    explanation: str
    features_used: Dict[str, Any] = Field(default_factory=dict)
    historical_data_summary: HistoricalSummary


class StationRiskResponse(AppBaseModel):
    status: PredictionStatus
    generated_at: str
    scope: Dict[str, Any] = Field(default_factory=dict)
    prediction: Optional[StationRiskItem] = None
    predictions: list[StationRiskItem] = Field(default_factory=list)
    explanation: str


class WarningItem(AppBaseModel):
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    title: str
    category: str
    district: Optional[str] = None
    police_station: Optional[str] = None
    reason: str
    supporting_statistics: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str
    confidence: confloat(ge=0.0, le=1.0) = 0.5


class WarningResponse(AppBaseModel):
    status: PredictionStatus
    generated_at: str
    scope: Dict[str, Any] = Field(default_factory=dict)
    warnings: list[WarningItem] = Field(default_factory=list)
    explanation: str


class PredictionDashboardResponse(AppBaseModel):
    status: PredictionStatus
    generated_at: str
    scope: Dict[str, Any] = Field(default_factory=dict)
    hotspot_forecast: Optional[HotspotPredictionResponse] = None
    trend_forecast: Optional[TrendPredictionResponse] = None
    station_risk: Optional[StationRiskResponse] = None
    warnings: Optional[WarningResponse] = None
