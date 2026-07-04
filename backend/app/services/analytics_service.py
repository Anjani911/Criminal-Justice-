"""
AnalyticsService
================
Thin orchestration layer over the SQL analytics engine.

This keeps the API/service boundary stable while the actual aggregation
logic lives in app.analytics.engine.
"""
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.analytics.engine import analytics_engine


class AnalyticsService:
    """
    Provides aggregated statistical insights over the FIR database.
    All methods return plain Python dicts/lists — ready for JSON serialisation.
    """

    # ------------------------------------------------------------------ #
    #  Crime Trends                                                        #
    # ------------------------------------------------------------------ #

    def get_monthly_trends(self, db: Session, year: Optional[int] = None) -> List[Dict[str, Any]]:
        return analytics_engine.get_monthly_trends(db, year=year)

    def get_monthly_statistics(self, db: Session, year: Optional[int] = None) -> List[Dict[str, Any]]:
        return analytics_engine.get_monthly_statistics(db, year=year)

    def get_yearly_summary(self, db: Session) -> List[Dict[str, Any]]:
        return analytics_engine.get_yearly_summary(db)

    # ------------------------------------------------------------------ #
    #  Crime Category Distribution                                         #
    # ------------------------------------------------------------------ #

    def get_crime_type_distribution(self, db: Session) -> List[Dict[str, Any]]:
        return analytics_engine.get_crime_type_distribution(db)

    def get_crime_subtype_distribution(self, db: Session, crime_head_id: Optional[int] = None) -> List[Dict[str, Any]]:
        return analytics_engine.get_crime_subtype_distribution(db, crime_head_id=crime_head_id)

    # ------------------------------------------------------------------ #
    #  Hotspot Analysis                                                    #
    # ------------------------------------------------------------------ #

    def get_district_hotspots(self, db: Session) -> List[Dict[str, Any]]:
        return analytics_engine.get_district_hotspots(db)

    def get_unit_hotspots(self, db: Session, district: Optional[str] = None) -> List[Dict[str, Any]]:
        return analytics_engine.get_unit_hotspots(db, district=district)

    def get_police_station_statistics(self, db: Session, district: Optional[str] = None) -> List[Dict[str, Any]]:
        return analytics_engine.get_police_station_statistics(db, district=district)

    # ------------------------------------------------------------------ #
    #  Status & Clearance                                                  #
    # ------------------------------------------------------------------ #

    def get_case_status_summary(self, db: Session) -> List[Dict[str, Any]]:
        return analytics_engine.get_case_status_summary(db)

    def get_accused_status_summary(self, db: Session) -> List[Dict[str, Any]]:
        return analytics_engine.get_accused_status_summary(db)

    # ------------------------------------------------------------------ #
    #  Summary Dashboard Stats                                             #
    # ------------------------------------------------------------------ #

    def get_dashboard_summary(self, db: Session) -> Dict[str, Any]:
        return analytics_engine.get_dashboard_summary(db)


# Singleton service instance
analytics_service = AnalyticsService()
