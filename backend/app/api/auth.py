"""
Authentication API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_employee
from app.auth.service import authenticate_employee, issue_access_token
from app.database.database import get_db
from app.models.employee import Employee
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.employee import EmployeeOut
from app.services.audit_service import audit_service
from app.utils.config import settings


router = APIRouter(prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, summary="JWT Login")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    ip_address = request.client.host if request.client else None
    employee = authenticate_employee(db, payload.username, payload.password)
    if employee is None:
        audit_service.log_action(
            db=db,
            action="login",
            resource_type="auth",
            status="Failed",
            username=payload.username,
            description="Failed login attempt due to invalid credentials",
            ip_address=ip_address,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, expires_in = issue_access_token(employee)
    
    audit_service.log_action(
        db=db,
        employee_id=employee.id,
        username=employee.username,
        role=employee.role,
        action="login",
        resource_type="auth",
        status="Success",
        description="Successful login",
        ip_address=ip_address,
    )
    
    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        employee=EmployeeOut.model_validate(employee),
    )


@router.get("/me", response_model=EmployeeOut, summary="Current Employee Profile")
def read_current_employee(current_employee: Employee = Depends(get_current_employee)) -> EmployeeOut:
    return EmployeeOut.model_validate(current_employee)
