"""
Audit service for tracking system actions.
"""
from typing import Any, Dict, List, Optional
import logging

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.audit import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    def log_action(
        self,
        db: Session,
        action: str,
        resource_type: str,
        status: str,
        employee_id: Optional[int] = None,
        username: Optional[str] = None,
        role: Optional[str] = None,
        resource_id: Optional[int] = None,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """
        Create a new audit log entry.
        """
        try:
            audit_log = AuditLog(
                employee_id=employee_id,
                username=username,
                role=role,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                description=description,
                status=status,
                ip_address=ip_address,
            )
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            return audit_log
        except Exception as e:
            db.rollback()
            logger.error("Failed to write audit log: %s", e)
            # We don't raise the exception because audit logging should not break the main workflow
            return None

    def get_logs(
        self,
        db: Session,
        employee_id: Optional[int] = None,
        username: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Retrieve and filter audit logs for administrators.
        """
        query = db.query(AuditLog)

        if employee_id is not None:
            query = query.filter(AuditLog.employee_id == employee_id)
            
        if username:
            query = query.filter(AuditLog.username == username)
        
        if action:
            query = query.filter(AuditLog.action == action)
            
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)

        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
            
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)

        total = query.count()
        logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "logs": logs
        }


audit_service = AuditService()
