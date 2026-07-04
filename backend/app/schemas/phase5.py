"""
Phase 5 request and response schemas.

These models validate the public REST payloads exposed by the API facade
for case lookup, analytics, network inspection, chat, and reporting.
"""
from typing import Any, Dict, Literal, Optional

from pydantic import Field, model_validator

from app.schemas.base import AppBaseModel


class ChatRequest(AppBaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    context: Optional[Dict[str, Any]] = None


class ChatResponse(AppBaseModel):
    status: Literal["not_available"]
    answer: str
    suggestions: list[str] = Field(default_factory=list)


class ReportRequest(AppBaseModel):
    report_type: Literal["case_investigation", "district_summary", "dashboard"]
    case_id: Optional[int] = Field(None, ge=1)
    district: Optional[str] = Field(None, min_length=2, max_length=100)
    year: Optional[int] = Field(None, ge=2000, le=2100)
    ai_summary: Optional[str] = None

    @model_validator(mode="after")
    def validate_required_fields(self):
        if self.report_type == "case_investigation" and self.case_id is None:
            raise ValueError("case_id is required for case_investigation reports.")
        if self.report_type == "district_summary" and not self.district:
            raise ValueError("district is required for district_summary reports.")
        return self
