"""
Cases Router
============
REST endpoints for FIR case management.

GET    /api/v1/cases              → Paginated, filterable case list
GET    /api/v1/cases/{id}         → Full case detail with all relations
GET    /api/v1/cases/fir/{number} → Lookup by FIR number
POST   /api/v1/cases              → Create a new FIR case
PATCH  /api/v1/cases/{id}/status  → Update case status
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.case import (
    CaseCreate, CaseStatusUpdate,
    CaseSummaryOut, CaseDetailOut, CaseListResponse,
)
from app.services import crime_service

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.get("", response_model=CaseListResponse, summary="List FIR Cases")
def list_cases(
    district: Optional[str] = Query(None, description="Filter by district name"),
    unit_name: Optional[str] = Query(None, description="Filter by police station"),
    status: Optional[str] = Query(None, description="Filter by case status"),
    crime_head_id: Optional[int] = Query(None, description="Filter by crime category ID"),
    crime_subhead_id: Optional[int] = Query(None, description="Filter by crime sub-category ID"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Page size (max 200)"),
    db: Session = Depends(get_db),
):
    """
    Return a paginated list of FIR cases with optional filters.
    Supports filtering by district, unit, status, and crime classification.
    """
    result = crime_service.list_cases(
        db,
        district=district,
        unit_name=unit_name,
        status=status,
        crime_head_id=crime_head_id,
        crime_subhead_id=crime_subhead_id,
        skip=skip,
        limit=limit,
    )
    # Serialise ORM objects to summary schema
    result["cases"] = [CaseSummaryOut.model_validate(c) for c in result["cases"]]
    return result


@router.get("/fir/{fir_number}", response_model=CaseDetailOut, summary="Get Case by FIR Number")
def get_case_by_fir(fir_number: str, db: Session = Depends(get_db)):
    """Return full case details for the given FIR number."""
    case = crime_service.get_case_by_fir(db, fir_number)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with FIR number '{fir_number}' not found.",
        )
    return CaseDetailOut.model_validate(case)


@router.get("/{case_id}", response_model=CaseDetailOut, summary="Get Case by ID")
def get_case(case_id: int, db: Session = Depends(get_db)):
    """Return full case details including accused, victims, and arrests."""
    case = crime_service.get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case ID {case_id} not found.",
        )
    return CaseDetailOut.model_validate(case)


@router.post("", response_model=CaseDetailOut, status_code=status.HTTP_201_CREATED, summary="Create FIR Case")
def create_case(payload: CaseCreate, db: Session = Depends(get_db)):
    """
    Register a new FIR case.
    Returns HTTP 409 if a case with the same FIR number already exists.
    """
    try:
        case = crime_service.create_case(db, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    # Re-fetch with full relations for the response
    return CaseDetailOut.model_validate(
        crime_service.get_case_by_id(db, case.id)
    )


@router.patch("/{case_id}/status", response_model=CaseDetailOut, summary="Update Case Status")
def update_case_status(
    case_id: int, payload: CaseStatusUpdate, db: Session = Depends(get_db)
):
    """Update the status of an existing case (e.g., mark as Chargesheeted)."""
    try:
        case = crime_service.update_case_status(db, case_id, payload.status)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return CaseDetailOut.model_validate(
        crime_service.get_case_by_id(db, case.id)
    )
