"""
Audit log model for tracking user actions and API usage.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    
    # User context
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True, index=True)
    username = Column(String(50), nullable=True, index=True)
    role = Column(String(50), nullable=True)
    ip_address = Column(String(50), nullable=True)

    # Action context
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(Integer, nullable=True, index=True)
    
    # Details
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, index=True)

    # Relationships
    employee = relationship("Employee", back_populates="audit_logs")
