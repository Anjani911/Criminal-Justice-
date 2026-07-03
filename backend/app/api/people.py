"""
People Router
=============
REST endpoints for accused persons and victims.

GET  /api/v1/accused                     → List accused (filterable by status)
GET  /api/v1/accused/absconding          → All absconding suspects (alert list)
GET  /api/v1/accused/search              → Cross-case name search
GET  /api/v1/cases/{case_id}/accused     → All accused for a case
POST /api/v1/cases/{case_id}/accused     → Add accused to a case
GET  /api/v1/cases/{case_id}/victims     → All victims for a case
POST /api/v1/cases/{case_id}/victims     → Add victim to a case
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.people import AccusedCreate, AccusedOut, VictimCreate, VictimOut
from app.services import crime_service

router = APIRouter(tags=["People"])


# ── Accused endpoints ──────────────────────────────────────────────────────────

@router.get("/accused/absconding", response_model=List[AccusedOut], summary="List Absconding Accused")
def get_absconding(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Return all accused persons currently marked as Absconding. Used for alert dashboards."""
    return crime_service.get_absconding_accused(db, skip=skip, limit=limit)


@router.get("/accused/search", response_model=List[AccusedOut], summary="Search Accused by Name")
def search_accused(
    name: str = Query(..., min_length=2, description="Partial or full name to search"),
    db: Session = Depends(get_db),
):
    """Cross-case search for accused persons by name (case-insensitive partial match)."""
    try:
        return crime_service.search_accused(db, name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/cases/{case_id}/accused", response_model=List[AccusedOut], summary="List Accused for Case")
def get_accused_for_case(case_id: int, db: Session = Depends(get_db)):
    """Return all accused persons linked to the specified case."""
    return crime_service.get_accused_for_case(db, case_id)


@router.post(
    "/cases/{case_id}/accused",
    response_model=AccusedOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add Accused to Case",
)
def add_accused(case_id: int, payload: AccusedCreate, db: Session = Depends(get_db)):
    """Add a new accused person to an existing case."""
    try:
        return crime_service.add_accused_to_case(db, case_id, payload.model_dump())
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


# ── Victim endpoints ───────────────────────────────────────────────────────────

@router.get("/cases/{case_id}/victims", response_model=List[VictimOut], summary="List Victims for Case")
def get_victims_for_case(case_id: int, db: Session = Depends(get_db)):
    """Return all victims linked to the specified case."""
    return crime_service.get_victims_for_case(db, case_id)


@router.post(
    "/cases/{case_id}/victims",
    response_model=VictimOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add Victim to Case",
)
def add_victim(case_id: int, payload: VictimCreate, db: Session = Depends(get_db)):
    """Add a new victim to an existing case."""
    try:
        return crime_service.add_victim_to_case(db, case_id, payload.model_dump())
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
