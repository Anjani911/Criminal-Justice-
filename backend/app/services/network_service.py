"""
NetworkService
==============
Thin orchestration layer over the criminal network engine.

This preserves the service boundary used by the API layer while the graph
construction logic itself lives in app.analytics.network_engine.
"""
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.analytics.network_engine import network_engine


class NetworkService:
    def get_full_network(self, db: Session) -> Dict[str, Any]:
        return network_engine.build_full_payload(db)

    def get_case_network(self, db: Session, case_id: int) -> Dict[str, Any]:
        return network_engine.build_case_payload(db, case_id)

    def get_accused_network(self, db: Session, accused_id: int) -> Dict[str, Any]:
        return network_engine.build_accused_payload(db, accused_id)

    def get_network_metrics(self, db: Session) -> Dict[str, Any]:
        return network_engine.graph_metrics(db)


# Singleton service instance
network_service = NetworkService()
