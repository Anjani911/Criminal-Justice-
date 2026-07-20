"""
AI response schemas.
"""
from typing import Any, Dict, Literal

from pydantic import Field, confloat

from app.schemas.base import AppBaseModel


class AIChatResponse(AppBaseModel):
    status: Literal["success", "partial", "error"]
    intent: str
    confidence: confloat(ge=0.0, le=1.0)
    query_kind: str
    detected_language: str
    response_language: str
    answer: str
    data: Dict[str, Any] = Field(default_factory=dict)
    suggestions: list[str] = Field(default_factory=list)
