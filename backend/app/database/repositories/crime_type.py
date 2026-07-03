from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.repositories.base import CRUDBase
from app.models.crime_type import CrimeHead, CrimeSubHead


class CrimeHeadRepository(CRUDBase[CrimeHead]):
    """
    Repository for CrimeHead (major crime category) database operations.
    """

    def get_by_code(self, db: Session, code: str) -> Optional[CrimeHead]:
        """Fetch a crime head by its unique code (e.g., 'CYBER', 'THEFT')."""
        return db.query(CrimeHead).filter(CrimeHead.code == code).first()

    def search_by_name(self, db: Session, name: str) -> List[CrimeHead]:
        """Search crime heads by partial name match."""
        return db.query(CrimeHead).filter(CrimeHead.name.ilike(f"%{name}%")).all()

    def get_all_with_subheads(self, db: Session) -> List[CrimeHead]:
        """Fetch all crime heads along with their subheads. Used for dropdown population."""
        from sqlalchemy.orm import joinedload
        return db.query(CrimeHead).options(joinedload(CrimeHead.subheads)).all()


class CrimeSubHeadRepository(CRUDBase[CrimeSubHead]):
    """
    Repository for CrimeSubHead (specific crime category) database operations.
    """

    def get_by_code(self, db: Session, code: str) -> Optional[CrimeSubHead]:
        """Fetch a crime sub-head by its unique code (e.g., 'PHISH')."""
        return db.query(CrimeSubHead).filter(CrimeSubHead.code == code).first()

    def get_by_crime_head(
        self, db: Session, crime_head_id: int
    ) -> List[CrimeSubHead]:
        """Fetch all sub-categories belonging to a specific crime head."""
        return (
            db.query(CrimeSubHead)
            .filter(CrimeSubHead.crime_head_id == crime_head_id)
            .all()
        )

    def search_by_name(self, db: Session, name: str) -> List[CrimeSubHead]:
        """Search crime sub-heads by partial name match."""
        return (
            db.query(CrimeSubHead)
            .filter(CrimeSubHead.name.ilike(f"%{name}%"))
            .all()
        )


# Singleton instances
crime_head_repository = CrimeHeadRepository(CrimeHead)
crime_subhead_repository = CrimeSubHeadRepository(CrimeSubHead)
