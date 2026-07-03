"""
ReportService
=============
Assembles comprehensive investigation report data by orchestrating
CrimeService, AnalyticsService, and NetworkService.

Phase 10 will extend this to generate actual PDF files and
store them in Zoho Catalyst File Store. For now, this service
returns a structured dict representing the full report payload.
"""
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.services.crime_service import crime_service, CrimeService
from app.services.analytics_service import analytics_service, AnalyticsService
from app.services.network_service import network_service, NetworkService


class ReportService:
    """
    Orchestrates multi-service data aggregation to produce structured
    investigation reports for individual cases or district summaries.

    The AI summary field will be populated by the Gemini layer in Phase 9.
    """

    def __init__(
        self,
        _crime_svc: CrimeService = None,
        _analytics_svc: AnalyticsService = None,
        _network_svc: NetworkService = None,
    ):
        # Allow dependency injection for testing; fall back to singletons
        self._crime = _crime_svc or crime_service
        self._analytics = _analytics_svc or analytics_service
        self._network = _network_svc or network_service

    # ------------------------------------------------------------------ #
    #  Case-Level Report                                                   #
    # ------------------------------------------------------------------ #

    def generate_case_report(
        self, db: Session, case_id: int, ai_summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Assemble a full report for a single FIR case.

        Includes:
        - Case metadata (FIR number, dates, district, status)
        - Crime classification
        - Investigating officer details
        - Full accused list
        - Full victim list
        - Arrest/surrender events
        - Criminal network sub-graph
        - AI summary placeholder (populated by Gemini in Phase 9)
        - Report generation timestamp
        """
        case = self._crime.get_case_by_id(db, case_id)
        if not case:
            raise LookupError(f"Case ID {case_id} not found.")

        # Build network sub-graph for this case
        try:
            network = self._network.get_case_network(db, case_id)
        except Exception:
            network = {"nodes": [], "edges": [], "metadata": {}}

        return {
            "report_type": "case_investigation",
            "generated_at": datetime.utcnow().isoformat(),
            "ai_summary": ai_summary or "AI summary not yet generated.",
            "case": {
                "id": case.id,
                "fir_number": case.fir_number,
                "status": case.status,
                "district": case.district,
                "unit_name": case.unit_name,
                "incident_date": case.incident_date.isoformat() if case.incident_date else None,
                "registered_date": case.registered_date.isoformat() if case.registered_date else None,
                "brief_facts": case.brief_facts,
                "crime_head": case.crime_head.name if case.crime_head else None,
                "crime_sub_head": case.crime_sub_head.name if case.crime_sub_head else None,
            },
            "investigating_officer": (
                {
                    "name": case.investigating_officer.name,
                    "rank": case.investigating_officer.rank,
                    "badge_number": case.investigating_officer.badge_number,
                    "unit_name": case.investigating_officer.unit_name,
                }
                if case.investigating_officer
                else None
            ),
            "accused": [
                {
                    "id": a.id,
                    "name": a.name,
                    "age": a.age,
                    "gender": a.gender,
                    "status": a.status,
                    "address": a.address,
                }
                for a in case.accused_list
            ],
            "victims": [
                {
                    "id": v.id,
                    "name": v.name,
                    "age": v.age,
                    "gender": v.gender,
                    "injury_type": v.injury_type,
                }
                for v in case.victims
            ],
            "arrests": [
                {
                    "id": ar.id,
                    "arrest_date": ar.arrest_date.isoformat() if ar.arrest_date else None,
                    "arrest_type": ar.arrest_type,
                    "accused_name": ar.accused.name if ar.accused else None,
                    "arresting_officer": ar.arresting_officer.name if ar.arresting_officer else None,
                    "court_name": ar.court_name,
                    "remarks": ar.remarks,
                }
                for ar in case.arrests
            ],
            "criminal_network": {
                "node_count": network["metadata"].get("node_count", 0),
                "edge_count": network["metadata"].get("edge_count", 0),
                "nodes": network["nodes"],
                "edges": network["edges"],
            },
        }

    # ------------------------------------------------------------------ #
    #  District Summary Report                                             #
    # ------------------------------------------------------------------ #

    def generate_district_report(
        self, db: Session, district: str, year: int = None, ai_summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Assemble a crime statistics report for an entire district.

        Includes:
        - Monthly crime trends (filtered by year)
        - Crime category breakdown
        - Police station hotspots within the district
        - Case status summary
        - Accused status summary
        - Dashboard KPIs
        - AI summary placeholder
        """
        return {
            "report_type": "district_summary",
            "generated_at": datetime.utcnow().isoformat(),
            "district": district,
            "year": year,
            "ai_summary": ai_summary or "AI summary not yet generated.",
            "monthly_trends": self._analytics.get_monthly_trends(db, year=year),
            "crime_type_distribution": self._analytics.get_crime_type_distribution(db),
            "unit_hotspots": self._analytics.get_unit_hotspots(db, district=district),
            "case_status_summary": self._analytics.get_case_status_summary(db),
            "accused_status_summary": self._analytics.get_accused_status_summary(db),
            "dashboard_kpis": self._analytics.get_dashboard_summary(db),
        }

    # ------------------------------------------------------------------ #
    #  Dashboard Summary Report                                            #
    # ------------------------------------------------------------------ #

    def generate_dashboard_report(self, db: Session) -> Dict[str, Any]:
        """
        Fast summary report powering the main dashboard.
        Returns KPIs, trends, hotspots, and network metrics in one call.
        """
        try:
            network_metrics = self._network.get_network_metrics(db)
        except Exception:
            network_metrics = {}

        return {
            "report_type": "dashboard",
            "generated_at": datetime.utcnow().isoformat(),
            "kpis": self._analytics.get_dashboard_summary(db),
            "monthly_trends": self._analytics.get_monthly_trends(db),
            "district_hotspots": self._analytics.get_district_hotspots(db),
            "crime_type_distribution": self._analytics.get_crime_type_distribution(db),
            "case_status_summary": self._analytics.get_case_status_summary(db),
            "network_metrics": network_metrics,
        }


# Singleton service instance
report_service = ReportService()
