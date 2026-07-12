"""
Services package.
Exposes all service singleton instances for clean import in API routes.

Usage in routes:
    from app.services import crime_service, analytics_service
"""
from app.services.crime_service import crime_service, CrimeService
from app.services.analytics_service import analytics_service, AnalyticsService
from app.services.network_service import network_service, NetworkService
from app.services.report_service import report_service, ReportService
from app.services.prediction_service import prediction_service, PredictionService

__all__ = [
    "CrimeService", "crime_service",
    "AnalyticsService", "analytics_service",
    "NetworkService", "network_service",
    "ReportService", "report_service",
    "PredictionService", "prediction_service",
]
