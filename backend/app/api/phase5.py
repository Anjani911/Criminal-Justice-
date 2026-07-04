"""
Phase 5 API facade.

This router exposes the public REST endpoints required by the phase 5
roadmap while reusing the existing service layer.
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.ai import ai_service
from app.database.database import get_db
from app.schemas.ai import AIChatResponse
from app.schemas.report import ReportGenerationResponse
from app.schemas.case import (
    CaseCreate,
    CaseDetailOut,
    CaseListResponse,
    CaseStatusUpdate,
    CaseSummaryOut,
)
from app.schemas.phase5 import ChatRequest, ReportRequest
from app.reports import report_engine
from app.services import analytics_service, crime_service, network_service, report_service
from app.utils.config import settings


router = APIRouter(prefix=settings.API_V1_STR, tags=["Phase 5 API"])


@router.get("/cases", response_model=CaseListResponse, summary="List FIR Cases")
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
    result["cases"] = [CaseSummaryOut.model_validate(case) for case in result["cases"]]
    return result


@router.get("/cases/{case_id}", response_model=CaseDetailOut, summary="Get Case by ID")
@router.get("/case/{case_id}", response_model=CaseDetailOut, summary="Get Case by ID Alias")
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = crime_service.get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case ID {case_id} not found.")
    return CaseDetailOut.model_validate(case)


@router.get("/cases/fir/{fir_number}", response_model=CaseDetailOut, summary="Get Case by FIR Number")
def get_case_by_fir(fir_number: str, db: Session = Depends(get_db)):
    case = crime_service.get_case_by_fir(db, fir_number)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with FIR number '{fir_number}' not found.",
        )
    return CaseDetailOut.model_validate(case)


@router.post("/cases", response_model=CaseDetailOut, status_code=status.HTTP_201_CREATED, summary="Create FIR Case")
def create_case(payload: CaseCreate, db: Session = Depends(get_db)):
    try:
        case = crime_service.create_case(db, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return CaseDetailOut.model_validate(crime_service.get_case_by_id(db, case.id))


@router.patch("/cases/{case_id}/status", response_model=CaseDetailOut, summary="Update Case Status")
def update_case_status(case_id: int, payload: CaseStatusUpdate, db: Session = Depends(get_db)):
    try:
        case = crime_service.update_case_status(db, case_id, payload.status)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return CaseDetailOut.model_validate(crime_service.get_case_by_id(db, case.id))


@router.get("/crime-trends", summary="Monthly Crime Trends")
def crime_trends(
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter trends to a specific year"),
    db: Session = Depends(get_db),
) -> list[Dict[str, Any]]:
    return analytics_service.get_monthly_trends(db, year=year)


@router.get("/crime-types", summary="Crime Type Distribution")
def crime_types(
    crime_head_id: Optional[int] = Query(None, description="Filter to subheads of a specific crime category"),
    db: Session = Depends(get_db),
) -> list[Dict[str, Any]]:
    if crime_head_id:
        return analytics_service.get_crime_subtype_distribution(db, crime_head_id=crime_head_id)
    return analytics_service.get_crime_type_distribution(db)


@router.get("/hotspots", summary="Crime Hotspot Analysis")
def hotspots(
    district: Optional[str] = Query(None, description="Drill into a specific district's police stations"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    return {
        "district_hotspots": analytics_service.get_district_hotspots(db),
        "unit_hotspots": analytics_service.get_unit_hotspots(db, district=district),
    }


@router.get("/network", summary="Full Criminal Network Graph")
def network(db: Session = Depends(get_db)) -> Dict[str, Any]:
    return network_service.get_full_network(db)


@router.get("/network/metrics", summary="Network Centrality Metrics")
def network_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    return network_service.get_network_metrics(db)


@router.get("/network/case/{case_id}", summary="Case-Centric Sub-Graph")
def network_case(case_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        return network_service.get_case_network(db, case_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/network/accused/{accused_id}", summary="Accused-Centric Sub-Graph")
def network_accused(accused_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        return network_service.get_accused_network(db, accused_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/chat", response_model=AIChatResponse, summary="Validated AI Chat")
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> AIChatResponse:
    return ai_service.answer(db, payload.question, payload.context)


@router.post("/report", response_model=ReportGenerationResponse, summary="Generate Professional PDF Report")
def report(payload: ReportRequest, db: Session = Depends(get_db)) -> ReportGenerationResponse:
    if payload.report_type == "case_investigation":
        result = report_engine.generate_case_report(db, payload.case_id, ai_summary=payload.ai_summary)
        return ReportGenerationResponse.model_validate(result)

    if payload.report_type == "district_summary":
        result = report_engine.generate_district_report(
            db,
            district=payload.district,
            year=payload.year,
            ai_summary=payload.ai_summary,
        )
        return ReportGenerationResponse.model_validate(result)

    result = report_engine.generate_dashboard_report(db, ai_summary=payload.ai_summary)
    return ReportGenerationResponse.model_validate(result)
