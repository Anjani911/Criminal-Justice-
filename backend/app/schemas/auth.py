"""
Authentication schemas for JWT login and token responses.
"""
from typing import Literal, Optional

from pydantic import Field

from app.schemas.base import AppBaseModel
from app.schemas.employee import EmployeeOut


class LoginRequest(AppBaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(AppBaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    employee: EmployeeOut


class TokenData(AppBaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
