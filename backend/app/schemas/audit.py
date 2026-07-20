"""
Pydantic schemas for Audit Trail.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AuditLogBase(BaseModel):
    employee_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
    action: str = Field(..., max_length=100)
    resource_type: str = Field(..., max_length=100)
    resource_id: Optional[int] = None
    description: Optional[str] = None
    status: str = Field(..., max_length=50)
    ip_address: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogOut(AuditLogBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    logs: List[AuditLogOut]
