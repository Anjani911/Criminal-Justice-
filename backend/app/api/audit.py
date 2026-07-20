"""
Audit API routes.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_administrator
from app.database.database import get_db
from app.schemas.audit import AuditLogListResponse
from app.services.audit_service import audit_service
from app.utils.config import settings
from app.models.employee import Employee


router = APIRouter(prefix=f"{settings.API_V1_STR}/audit", tags=["Audit Trail"])


@router.get("", response_model=AuditLogListResponse, summary="Retrieve Audit Logs")
def get_audit_logs(
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    action: Optional[str] = Query(None, description="Filter by action name"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    start_date: Optional[str] = Query(None, description="Filter by start timestamp (ISO8601)"),
    end_date: Optional[str] = Query(None, description="Filter by end timestamp (ISO8601)"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Page size (max 200)"),
    current_employee: Employee = Depends(require_administrator),
    db: Session = Depends(get_db),
):
    result = audit_service.get_logs(
        db=db,
        employee_id=employee_id,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
    return AuditLogListResponse(**result)
