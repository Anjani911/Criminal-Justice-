"""
Case schemas — CaseMaster request/response models.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import Field

from app.schemas.base import AppBaseModel
from app.schemas.crime_type import CrimeHeadOut, CrimeSubHeadOut
from app.schemas.employee import EmployeeOut
from app.schemas.people import AccusedOut, VictimOut


# ── Arrest ─────────────────────────────────────────────────────────────────────

class ArrestOut(AppBaseModel):
    id: int
    arrest_date: Optional[datetime]
    arrest_type: str
    court_name: Optional[str]
    remarks: Optional[str]
    accused_id: int
    arrest_by_employee_id: Optional[int]


# ── Create ─────────────────────────────────────────────────────────────────────

class CaseCreate(AppBaseModel):
    fir_number: str = Field(..., min_length=3, max_length=100)
    incident_date: datetime
    registered_date: datetime
    status: str = Field(
        default="Under Investigation",
        pattern="^(Under Investigation|Chargesheeted|Closed)$"
    )
    brief_facts: Optional[str] = None
    district: str = Field(..., min_length=2, max_length=100)
    unit_name: str = Field(..., min_length=2, max_length=100)
    crime_head_id: int
    crime_subhead_id: int
    investigating_officer_id: Optional[int] = None


# ── Status Update ──────────────────────────────────────────────────────────────

class CaseStatusUpdate(AppBaseModel):
    status: str = Field(
        ..., pattern="^(Under Investigation|Chargesheeted|Closed)$"
    )


# ── Summary (list view — lightweight) ─────────────────────────────────────────

class CaseSummaryOut(AppBaseModel):
    id: int
    fir_number: str
    status: str
    district: str
    unit_name: str
    incident_date: Optional[datetime]
    registered_date: Optional[datetime]
    crime_head_id: int
    crime_subhead_id: int


# ── Detail (full view — with all relations) ────────────────────────────────────

class CaseDetailOut(AppBaseModel):
    id: int
    fir_number: str
    status: str
    district: str
    unit_name: str
    brief_facts: Optional[str]
    incident_date: Optional[datetime]
    registered_date: Optional[datetime]
    crime_head: Optional[CrimeHeadOut]
    crime_sub_head: Optional[CrimeSubHeadOut]
    investigating_officer: Optional[EmployeeOut]
    accused_list: List[AccusedOut] = []
    victims: List[VictimOut] = []
    arrests: List[ArrestOut] = []


# ── Paginated List Response ────────────────────────────────────────────────────

class CaseListResponse(AppBaseModel):
    cases: List[CaseSummaryOut]
    total: int
    skip: int
    limit: int
