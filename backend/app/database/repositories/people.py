from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.repositories.base import CRUDBase
from app.models.people import Accused, Victim


class AccusedRepository(CRUDBase[Accused]):
    """
    Repository for Accused entity database operations.
    Provides queries specific to suspects and accused individuals.
    """

    def get_by_case(self, db: Session, case_id: int) -> List[Accused]:
        """Fetch all accused persons linked to a specific case."""
        return (
            db.query(Accused)
            .filter(Accused.case_id == case_id)
            .all()
        )

    def get_by_status(
        self, db: Session, status: str, skip: int = 0, limit: int = 100
    ) -> List[Accused]:
        """
        Fetch accused persons by their current status.
        Status values: Suspect, Arrested, Chargesheeted, Absconding
        """
        return (
            db.query(Accused)
            .filter(Accused.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_by_name(self, db: Session, name: str) -> List[Accused]:
        """
        Search accused persons by partial name match (case-insensitive).
        Useful for cross-case criminal lookups.
        """
        return (
            db.query(Accused)
            .filter(Accused.name.ilike(f"%{name}%"))
            .all()
        )

    def count_by_case(self, db: Session, case_id: int) -> int:
        """Returns the count of accused persons for a specific case."""
        return db.query(Accused).filter(Accused.case_id == case_id).count()

    def get_absconding(self, db: Session, skip: int = 0, limit: int = 100) -> List[Accused]:
        """Fetch all accused with 'Absconding' status — useful for alerts."""
        return (
            db.query(Accused)
            .filter(Accused.status == "Absconding")
            .offset(skip)
            .limit(limit)
            .all()
        )


class VictimRepository(CRUDBase[Victim]):
    """
    Repository for Victim entity database operations.
    """

    def get_by_case(self, db: Session, case_id: int) -> List[Victim]:
        """Fetch all victims linked to a specific case."""
        return (
            db.query(Victim)
            .filter(Victim.case_id == case_id)
            .all()
        )

    def search_by_name(self, db: Session, name: str) -> List[Victim]:
        """Search victims by partial name match (case-insensitive)."""
        return (
            db.query(Victim)
            .filter(Victim.name.ilike(f"%{name}%"))
            .all()
        )

    def get_by_injury_type(
        self, db: Session, injury_type: str, skip: int = 0, limit: int = 100
    ) -> List[Victim]:
        """
        Filter victims by type of injury suffered.
        Injury types: Grievous, Simple, Fatal, None
        """
        return (
            db.query(Victim)
            .filter(Victim.injury_type == injury_type)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_case(self, db: Session, case_id: int) -> int:
        """Returns the count of victims for a specific case."""
        return db.query(Victim).filter(Victim.case_id == case_id).count()


# Singleton instances used across services
accused_repository = AccusedRepository(Accused)
victim_repository = VictimRepository(Victim)
