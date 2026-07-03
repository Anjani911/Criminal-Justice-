from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.database.repositories.base import CRUDBase
from app.models.arrest import ArrestSurrender


class ArrestRepository(CRUDBase[ArrestSurrender]):
    """
    Repository for ArrestSurrender database operations.
    Provides queries to retrieve arrest and surrender events.
    """

    def get_by_case(self, db: Session, case_id: int) -> List[ArrestSurrender]:
        """Fetch all arrest/surrender events linked to a case."""
        return (
            db.query(ArrestSurrender)
            .options(
                joinedload(ArrestSurrender.accused),
                joinedload(ArrestSurrender.arresting_officer),
            )
            .filter(ArrestSurrender.case_id == case_id)
            .all()
        )

    def get_by_accused(self, db: Session, accused_id: int) -> List[ArrestSurrender]:
        """Fetch all arrest events for a specific accused person."""
        return (
            db.query(ArrestSurrender)
            .filter(ArrestSurrender.accused_id == accused_id)
            .all()
        )

    def get_by_officer(
        self, db: Session, employee_id: int, skip: int = 0, limit: int = 100
    ) -> List[ArrestSurrender]:
        """Fetch all arrests performed by a specific officer."""
        return (
            db.query(ArrestSurrender)
            .filter(ArrestSurrender.arrest_by_employee_id == employee_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_arrest_type(
        self, db: Session, arrest_type: str, skip: int = 0, limit: int = 100
    ) -> List[ArrestSurrender]:
        """
        Fetch arrests/surrenders filtered by type.
        Types: Arrested, Surrendered in Court, Surrendered to Police
        """
        return (
            db.query(ArrestSurrender)
            .filter(ArrestSurrender.arrest_type == arrest_type)
            .offset(skip)
            .limit(limit)
            .all()
        )


# Singleton instance
arrest_repository = ArrestRepository(ArrestSurrender)
