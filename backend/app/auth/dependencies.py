"""
FastAPI dependencies for authentication and role-based authorization.
"""
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.repositories.employee import employee_repository
from app.models.employee import Employee
from app.schemas.auth import TokenData
from app.utils.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_employee(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Employee:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        token_data = TokenData(
            username=payload.get("sub"),
            role=payload.get("role"),
        )
    except JWTError as exc:
        raise credentials_exception from exc

    if token_data.username is None:
        raise credentials_exception

    employee = employee_repository.get_by_username(db, token_data.username)
    if employee is None:
        raise credentials_exception

    return employee


def require_roles(*allowed_roles: str) -> Callable:
    allowed_set = set(allowed_roles)

    def role_guard(current_employee: Employee = Depends(get_current_employee)) -> Employee:
        if current_employee.role not in allowed_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )
        return current_employee

    return role_guard


require_investigator_or_higher = require_roles("Investigator", "Officer", "Administrator")
require_officer_or_higher = require_roles("Officer", "Administrator")
require_administrator = require_roles("Administrator")
