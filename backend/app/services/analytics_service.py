"""
AnalyticsService
================
Implements the SQL-based analytics engine.
Generates crime trends, monthly statistics, hotspot data,
station-level breakdowns, and category distributions.

No AI is used here — pure SQL aggregations via SQLAlchemy.
The AI layer (Phase 9) will call these methods for data
before passing results to the Gemini summariser.
"""
from typing import Any, Dict, List
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.models.case import CaseMaster
from app.models.crime_type import CrimeHead, CrimeSubHead
from app.models.people import Accused, Victim
from app.models.arrest import ArrestSurrender


class AnalyticsService:
    """
    Provides aggregated statistical insights over the FIR database.
    All methods return plain Python dicts/lists — ready for JSON serialisation.
    """

    # ------------------------------------------------------------------ #
    #  Crime Trends                                                        #
    # ------------------------------------------------------------------ #

    def get_monthly_trends(
        self, db: Session, year: int = None
    ) -> List[Dict[str, Any]]:
        """
        Return the number of cases registered per month.
        Optionally filter by year; defaults to all available years.
        Returns data sorted chronologically.
        """
        query = (
            db.query(
                extract("year", CaseMaster.registered_date).label("year"),
                extract("month", CaseMaster.registered_date).label("month"),
                func.count(CaseMaster.id).label("case_count"),
            )
            .group_by("year", "month")
            .order_by("year", "month")
        )
        if year:
            query = query.filter(
                extract("year", CaseMaster.registered_date) == year
            )

        rows = query.all()
        return [
            {
                "year": int(r.year),
                "month": int(r.month),
                "month_name": _month_name(int(r.month)),
                "case_count": r.case_count,
            }
            for r in rows
        ]

    def get_yearly_summary(self, db: Session) -> List[Dict[str, Any]]:
        """Return total cases per year across all years in the database."""
        rows = (
            db.query(
                extract("year", CaseMaster.registered_date).label("year"),
                func.count(CaseMaster.id).label("case_count"),
            )
            .group_by("year")
            .order_by("year")
            .all()
        )
        return [{"year": int(r.year), "case_count": r.case_count} for r in rows]

    # ------------------------------------------------------------------ #
    #  Crime Category Distribution                                         #
    # ------------------------------------------------------------------ #

    def get_crime_type_distribution(self, db: Session) -> List[Dict[str, Any]]:
        """
        Return case counts grouped by major crime category (CrimeHead).
        Useful for pie/donut charts on the dashboard.
        """
        rows = (
            db.query(
                CrimeHead.name.label("crime_head"),
                func.count(CaseMaster.id).label("case_count"),
            )
            .join(CaseMaster, CaseMaster.crime_head_id == CrimeHead.id)
            .group_by(CrimeHead.name)
            .order_by(func.count(CaseMaster.id).desc())
            .all()
        )
        return [{"crime_head": r.crime_head, "case_count": r.case_count} for r in rows]

    def get_crime_subtype_distribution(
        self, db: Session, crime_head_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        Return case counts grouped by crime sub-category.
        Optionally filter to subheads of a specific CrimeHead.
        """
        query = (
            db.query(
                CrimeHead.name.label("crime_head"),
                CrimeSubHead.name.label("crime_subhead"),
                func.count(CaseMaster.id).label("case_count"),
            )
            .join(CrimeSubHead, CaseMaster.crime_subhead_id == CrimeSubHead.id)
            .join(CrimeHead, CaseMaster.crime_head_id == CrimeHead.id)
            .group_by(CrimeHead.name, CrimeSubHead.name)
            .order_by(func.count(CaseMaster.id).desc())
        )
        if crime_head_id:
            query = query.filter(CaseMaster.crime_head_id == crime_head_id)

        rows = query.all()
        return [
            {
                "crime_head": r.crime_head,
                "crime_subhead": r.crime_subhead,
                "case_count": r.case_count,
            }
            for r in rows
        ]

    # ------------------------------------------------------------------ #
    #  Hotspot Analysis                                                    #
    # ------------------------------------------------------------------ #

    def get_district_hotspots(self, db: Session) -> List[Dict[str, Any]]:
        """
        Return case counts per district, ordered by highest crime rate.
        Drives the geographic hotspot view on the dashboard.
        """
        rows = (
            db.query(
                CaseMaster.district.label("district"),
                func.count(CaseMaster.id).label("case_count"),
            )
            .group_by(CaseMaster.district)
            .order_by(func.count(CaseMaster.id).desc())
            .all()
        )
        return [{"district": r.district, "case_count": r.case_count} for r in rows]

    def get_unit_hotspots(
        self, db: Session, district: str = None
    ) -> List[Dict[str, Any]]:
        """
        Return case counts per police station/unit.
        Optionally filter by district to drill down.
        """
        query = (
            db.query(
                CaseMaster.unit_name.label("unit"),
                CaseMaster.district.label("district"),
                func.count(CaseMaster.id).label("case_count"),
            )
            .group_by(CaseMaster.unit_name, CaseMaster.district)
            .order_by(func.count(CaseMaster.id).desc())
        )
        if district:
            query = query.filter(CaseMaster.district.ilike(f"%{district}%"))

        rows = query.all()
        return [
            {"unit": r.unit, "district": r.district, "case_count": r.case_count}
            for r in rows
        ]

    # ------------------------------------------------------------------ #
    #  Status & Clearance                                                  #
    # ------------------------------------------------------------------ #

    def get_case_status_summary(self, db: Session) -> List[Dict[str, Any]]:
        """
        Return case counts grouped by case status.
        Shows how many cases are Under Investigation vs Chargesheeted vs Closed.
        """
        rows = (
            db.query(
                CaseMaster.status.label("status"),
                func.count(CaseMaster.id).label("case_count"),
            )
            .group_by(CaseMaster.status)
            .all()
        )
        return [{"status": r.status, "case_count": r.case_count} for r in rows]

    def get_accused_status_summary(self, db: Session) -> List[Dict[str, Any]]:
        """Return accused persons grouped by their current status."""
        rows = (
            db.query(
                Accused.status.label("status"),
                func.count(Accused.id).label("count"),
            )
            .group_by(Accused.status)
            .all()
        )
        return [{"status": r.status, "count": r.count} for r in rows]

    # ------------------------------------------------------------------ #
    #  Summary Dashboard Stats                                             #
    # ------------------------------------------------------------------ #

    def get_dashboard_summary(self, db: Session) -> Dict[str, Any]:
        """
        Return a high-level summary of key statistics for the dashboard.
        Single call to power the top-level KPI cards on the frontend.
        """
        total_cases = db.query(func.count(CaseMaster.id)).scalar() or 0
        total_accused = db.query(func.count(Accused.id)).scalar() or 0
        total_victims = db.query(func.count(Victim.id)).scalar() or 0
        total_arrests = db.query(func.count(ArrestSurrender.id)).scalar() or 0
        absconding = (
            db.query(func.count(Accused.id))
            .filter(Accused.status == "Absconding")
            .scalar()
            or 0
        )
        under_investigation = (
            db.query(func.count(CaseMaster.id))
            .filter(CaseMaster.status == "Under Investigation")
            .scalar()
            or 0
        )

        return {
            "total_cases": total_cases,
            "total_accused": total_accused,
            "total_victims": total_victims,
            "total_arrests": total_arrests,
            "absconding_accused": absconding,
            "cases_under_investigation": under_investigation,
        }


# ------------------------------------------------------------------ #
#  Helper                                                              #
# ------------------------------------------------------------------ #

_MONTHS = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

def _month_name(month_num: int) -> str:
    return _MONTHS[month_num] if 1 <= month_num <= 12 else "Unknown"


# Singleton service instance
analytics_service = AnalyticsService()
