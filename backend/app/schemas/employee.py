"""
Employee schemas — read/create for police personnel.
"""
from typing import Optional
from app.schemas.base import AppBaseModel


class EmployeeOut(AppBaseModel):
    id: int
    name: str
    rank: str
    role: str
    badge_number: str
    unit_name: str
    username: str
