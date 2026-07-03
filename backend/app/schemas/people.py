"""
People schemas — Accused and Victim request/response models.
"""
from typing import Optional
from pydantic import Field
from app.schemas.base import AppBaseModel


# ── Accused ────────────────────────────────────────────────────────────────────

class AccusedCreate(AppBaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    status: str = Field(default="Suspect", pattern="^(Suspect|Arrested|Chargesheeted|Absconding)$")


class AccusedOut(AppBaseModel):
    id: int
    case_id: int
    name: str
    age: Optional[int]
    gender: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    status: str


# ── Victim ─────────────────────────────────────────────────────────────────────

class VictimCreate(AppBaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    injury_type: Optional[str] = Field(None, pattern="^(Grievous|Simple|Fatal|None)$")


class VictimOut(AppBaseModel):
    id: int
    case_id: int
    name: str
    age: Optional[int]
    gender: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    injury_type: Optional[str]
