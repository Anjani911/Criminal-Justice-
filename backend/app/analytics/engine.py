"""
SQL-based analytics engine.

This module contains the pure data aggregation layer used by the service
and API layers. It performs no business orchestration and no AI work.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import case, extract, func
from sqlalchemy.orm import Session

from app.models.arrest import ArrestSurrender
from app.models.case import CaseMaster
from app.models.crime_type import CrimeHead, CrimeSubHead
from app.models.people import Accused, Victim


_MONTHS = [
    "",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


class AnalyticsEngine:
    """
    Executes SQL aggregations over the FIR database.
    The methods return JSON-ready dictionaries and lists.
    """

    def get_monthly_trends(self, db: Session, year: Optional[int] = None) -> List[Dict[str, Any]]:
        query = (
            db.query(
                extract("year", CaseMaster.registered_date).label("year"),
                extract("month", CaseMaster.registered_date).label("month"),
                func.count(CaseMaster.id).label("case_count"),
            )
            .group_by("year", "month")
            .order_by("year", "month")
        )
        if year is not None:
            query = query.filter(extract("year", CaseMaster.registered_date) == year)

        rows = query.all()
        return [
            {
                "year": int(row.year),
                "month": int(row.month),
                "month_name": _MONTHS[int(row.month)] if 1 <= int(row.month) <= 12 else "Unknown",
                "case_count": int(row.case_count),
            }
            for row in rows
        ]

    def get_monthly_statistics(self, db: Session, year: Optional[int] = None) -> List[Dict[str, Any]]:
        query = (
            db.query(
                extract("year", CaseMaster.registered_date).label("year"),
                extract("month", CaseMaster.registered_date).label("month"),
                func.count(CaseMaster.id).label("case_count"),
                func.sum(case((CaseMaster.status == "Under Investigation", 1), else_=0)).label("under_investigation_count"),
                func.sum(case((CaseMaster.status == "Chargesheeted", 1), else_=0)).label("chargesheeted_count"),
                func.sum(case((CaseMaster.status == "Closed", 1), else_=0)).label("closed_count"),
            )
            .group_by("year", "month")
            .order_by("year", "month")
        )
        if year is not None:
            query = query.filter(extract("year", CaseMaster.registered_date) == year)

        rows = query.all()
        return [
            {
                "year": int(row.year),
                "month": int(row.month),
                "month_name": _MONTHS[int(row.month)] if 1 <= int(row.month) <= 12 else "Unknown",
                "case_count": int(row.case_count),
                "under_investigation_count": int(row.under_investigation_count or 0),
                "chargesheeted_count": int(row.chargesheeted_count or 0),
                "closed_count": int(row.closed_count or 0),
            }
            for row in rows
        ]

    def get_yearly_summary(self, db: Session) -> List[Dict[str, Any]]:
        rows = (
            db.query(
                extract("year", CaseMaster.registered_date).label("year"),
                func.count(CaseMaster.id).label("case_count"),
            )
            .group_by("year")
            .order_by("year")
            .all()
        )
        return [{"year": int(row.year), "case_count": int(row.case_count)} for row in rows]

    def get_crime_type_distribution(self, db: Session) -> List[Dict[str, Any]]:
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
        return [{"crime_head": row.crime_head, "case_count": int(row.case_count)} for row in rows]

    def get_crime_subtype_distribution(self, db: Session, crime_head_id: Optional[int] = None) -> List[Dict[str, Any]]:
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
        if crime_head_id is not None:
            query = query.filter(CaseMaster.crime_head_id == crime_head_id)

        rows = query.all()
        return [
            {
                "crime_head": row.crime_head,
                "crime_subhead": row.crime_subhead,
                "case_count": int(row.case_count),
            }
            for row in rows
        ]

    def get_district_hotspots(self, db: Session) -> List[Dict[str, Any]]:
        rows = (
            db.query(
                CaseMaster.district.label("district"),
                func.count(CaseMaster.id).label("case_count"),
            )
            .group_by(CaseMaster.district)
            .order_by(func.count(CaseMaster.id).desc())
            .all()
        )
        return [{"district": row.district, "case_count": int(row.case_count)} for row in rows]

    def get_unit_hotspots(self, db: Session, district: Optional[str] = None) -> List[Dict[str, Any]]:
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
            {"unit": row.unit, "district": row.district, "case_count": int(row.case_count)}
            for row in rows
        ]

    def get_police_station_statistics(self, db: Session, district: Optional[str] = None) -> List[Dict[str, Any]]:
        query = (
            db.query(
                CaseMaster.district.label("district"),
                CaseMaster.unit_name.label("unit"),
                func.count(CaseMaster.id).label("case_count"),
                func.sum(case((CaseMaster.status == "Under Investigation", 1), else_=0)).label("under_investigation_count"),
                func.sum(case((CaseMaster.status == "Chargesheeted", 1), else_=0)).label("chargesheeted_count"),
                func.sum(case((CaseMaster.status == "Closed", 1), else_=0)).label("closed_count"),
            )
            .group_by(CaseMaster.district, CaseMaster.unit_name)
            .order_by(func.count(CaseMaster.id).desc())
        )
        if district:
            query = query.filter(CaseMaster.district.ilike(f"%{district}%"))

        rows = query.all()
        return [
            {
                "district": row.district,
                "unit": row.unit,
                "case_count": int(row.case_count),
                "under_investigation_count": int(row.under_investigation_count or 0),
                "chargesheeted_count": int(row.chargesheeted_count or 0),
                "closed_count": int(row.closed_count or 0),
            }
            for row in rows
        ]

    def get_case_status_summary(self, db: Session) -> List[Dict[str, Any]]:
        rows = (
            db.query(
                CaseMaster.status.label("status"),
                func.count(CaseMaster.id).label("case_count"),
            )
            .group_by(CaseMaster.status)
            .all()
        )
        return [{"status": row.status, "case_count": int(row.case_count)} for row in rows]

    def get_accused_status_summary(self, db: Session) -> List[Dict[str, Any]]:
        rows = (
            db.query(
                Accused.status.label("status"),
                func.count(Accused.id).label("count"),
            )
            .group_by(Accused.status)
            .all()
        )
        return [{"status": row.status, "count": int(row.count)} for row in rows]

    def get_dashboard_summary(self, db: Session) -> Dict[str, Any]:
        total_cases = db.query(func.count(CaseMaster.id)).scalar() or 0
        total_accused = db.query(func.count(Accused.id)).scalar() or 0
        total_victims = db.query(func.count(Victim.id)).scalar() or 0
        total_arrests = db.query(func.count(ArrestSurrender.id)).scalar() or 0
        absconding = db.query(func.count(Accused.id)).filter(Accused.status == "Absconding").scalar() or 0
        under_investigation = (
            db.query(func.count(CaseMaster.id))
            .filter(CaseMaster.status == "Under Investigation")
            .scalar()
            or 0
        )

        return {
            "total_cases": int(total_cases),
            "total_accused": int(total_accused),
            "total_victims": int(total_victims),
            "total_arrests": int(total_arrests),
            "absconding_accused": int(absconding),
            "cases_under_investigation": int(under_investigation),
        }


analytics_engine = AnalyticsEngine()
