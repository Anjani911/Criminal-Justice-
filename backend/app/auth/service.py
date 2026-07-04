"""
Authentication service layer.
"""
from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.auth.security import create_access_token, verify_password
from app.database.repositories.employee import employee_repository
from app.models.employee import Employee
from app.utils.config import settings


def authenticate_employee(db: Session, username: str, password: str) -> Optional[Employee]:
    employee = employee_repository.get_by_username(db, username)
    if not employee:
        return None
    if not verify_password(password, employee.hashed_password):
        return None
    return employee


def issue_access_token(employee: Employee) -> tuple[str, int]:
    expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    token = create_access_token(
        subject=employee.username,
        role=employee.role,
        extra_claims={
            "employee_id": employee.id,
            "badge_number": employee.badge_number,
            "unit_name": employee.unit_name,
        },
        expires_delta=timedelta(minutes=expires_minutes),
    )
    return token, expires_minutes * 60
