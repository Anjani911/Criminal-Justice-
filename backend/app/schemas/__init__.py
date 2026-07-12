"""
Schemas package — re-exports all Pydantic models.
"""
from app.schemas.base import AppBaseModel
from app.schemas.crime_type import CrimeHeadOut, CrimeSubHeadOut
from app.schemas.employee import EmployeeOut
from app.schemas.people import AccusedCreate, AccusedOut, VictimCreate, VictimOut
from app.schemas.case import (
    CaseCreate, CaseStatusUpdate,
    CaseSummaryOut, CaseDetailOut, CaseListResponse,
    ArrestOut,
)
from app.schemas.prediction import (
    HistoricalSummary,
    HotspotPredictionItem,
    HotspotPredictionResponse,
    TrendPredictionItem,
    TrendPredictionResponse,
    StationRiskItem,
    StationRiskResponse,
    WarningItem,
    WarningResponse,
    PredictionDashboardResponse,
)

__all__ = [
    "AppBaseModel",
    "CrimeHeadOut", "CrimeSubHeadOut",
    "EmployeeOut",
    "AccusedCreate", "AccusedOut",
    "VictimCreate", "VictimOut",
    "CaseCreate", "CaseStatusUpdate",
    "CaseSummaryOut", "CaseDetailOut", "CaseListResponse",
    "ArrestOut",
    "HistoricalSummary",
    "HotspotPredictionItem", "HotspotPredictionResponse",
    "TrendPredictionItem", "TrendPredictionResponse",
    "StationRiskItem", "StationRiskResponse",
    "WarningItem", "WarningResponse",
    "PredictionDashboardResponse",
]
