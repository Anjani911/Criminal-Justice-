"""
Report generation response schemas.
"""
from typing import Any, Dict, Literal, Optional

from pydantic import Field

from app.schemas.base import AppBaseModel


class ReportGenerationResponse(AppBaseModel):
    report_type: Literal["case_investigation", "district_summary", "dashboard"]
    generated_at: str
    storage_provider: str
    storage_key: str
    file_name: str
    download_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
