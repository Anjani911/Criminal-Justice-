"""
Network Router
==============
REST endpoints for the criminal network graph engine.

GET /api/v1/network                      → Full network graph (Cytoscape JSON)
GET /api/v1/network/metrics              → Centrality metrics & top criminal nodes
GET /api/v1/network/case/{case_id}       → Sub-graph centred on a specific case
GET /api/v1/network/accused/{accused_id} → All cases connected to one accused
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services import network_service

router = APIRouter(prefix="/network", tags=["Criminal Network"])


@router.get("", summary="Full Criminal Network Graph")
def full_network(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Return the complete Case → Accused criminal network graph as
    Cytoscape.js compatible JSON (nodes + edges + metadata).
    Note: For large databases this may be slow; filtered endpoints are preferred.
    """
    return network_service.get_full_network(db)


@router.get("/metrics", summary="Network Centrality Metrics")
def network_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Compute and return network centrality metrics:
    - Degree centrality: nodes with the most connections
    - Betweenness centrality: nodes acting as bridges between criminal clusters
    - Top 10 most connected accused persons
    - Top 10 most connected cases
    """
    return network_service.get_network_metrics(db)


@router.get("/case/{case_id}", summary="Case-Centric Sub-Graph")
def case_network(case_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Return a localised network graph centred on the specified case,
    including all accused and any other cases they are linked to.
    Ideal for the investigation detail view.
    """
    try:
        return network_service.get_case_network(db, case_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/accused/{accused_id}", summary="Accused-Centric Sub-Graph")
def accused_network(accused_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Return all cases and co-accused connected to a specific individual.
    Useful for building a criminal profile and history.
    """
    try:
        return network_service.get_accused_network(db, accused_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
