from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.repositories.base import CRUDBase
from app.models.employee import Employee


class EmployeeRepository(CRUDBase[Employee]):
    """
    Repository for Employee (police personnel) database operations.
    Provides authentication and role-based lookup methods.
    """

    def get_by_username(self, db: Session, username: str) -> Optional[Employee]:
        """
        Fetch an employee by their username.
        This is the primary lookup method used during JWT authentication.
        """
        return (
            db.query(Employee)
            .filter(Employee.username == username)
            .first()
        )

    def get_by_badge_number(self, db: Session, badge_number: str) -> Optional[Employee]:
        """Fetch an employee by their unique police badge number."""
        return (
            db.query(Employee)
            .filter(Employee.badge_number == badge_number)
            .first()
        )

    def get_by_role(
        self, db: Session, role: str, skip: int = 0, limit: int = 100
    ) -> List[Employee]:
        """
        Fetch all employees assigned a specific role.
        Roles: Investigator, Officer, Administrator
        """
        return (
            db.query(Employee)
            .filter(Employee.role == role)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_unit(
        self, db: Session, unit_name: str, skip: int = 0, limit: int = 100
    ) -> List[Employee]:
        """Fetch all employees belonging to a specific unit or police station."""
        return (
            db.query(Employee)
            .filter(Employee.unit_name.ilike(f"%{unit_name}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_by_name(self, db: Session, name: str) -> List[Employee]:
        """Search employees by partial name match (case-insensitive)."""
        return (
            db.query(Employee)
            .filter(Employee.name.ilike(f"%{name}%"))
            .all()
        )


# Singleton instance used across services
employee_repository = EmployeeRepository(Employee)
