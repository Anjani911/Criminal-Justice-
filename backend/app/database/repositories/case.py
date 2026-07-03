from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.database.repositories.base import CRUDBase
from app.models.case import CaseMaster


class CaseRepository(CRUDBase[CaseMaster]):
    """
    Repository for CaseMaster (FIR) database operations.
    Provides case-specific query methods beyond basic CRUD.
    """

    def get_by_fir_number(self, db: Session, fir_number: str) -> Optional[CaseMaster]:
        """
        Fetch a single case by its unique FIR number.
        Eagerly loads all related entities to avoid N+1 query problems.
        """
        return (
            db.query(CaseMaster)
            .options(
                joinedload(CaseMaster.crime_head),
                joinedload(CaseMaster.crime_sub_head),
                joinedload(CaseMaster.investigating_officer),
                joinedload(CaseMaster.accused_list),
                joinedload(CaseMaster.victims),
                joinedload(CaseMaster.arrests),
            )
            .filter(CaseMaster.fir_number == fir_number)
            .first()
        )

    def get_with_relations(self, db: Session, id: int) -> Optional[CaseMaster]:
        """
        Fetch a single case by ID with all related entities eagerly loaded.
        Used for detail views where complete case context is needed.
        """
        return (
            db.query(CaseMaster)
            .options(
                joinedload(CaseMaster.crime_head),
                joinedload(CaseMaster.crime_sub_head),
                joinedload(CaseMaster.investigating_officer),
                joinedload(CaseMaster.accused_list),
                joinedload(CaseMaster.victims),
                joinedload(CaseMaster.arrests),
            )
            .filter(CaseMaster.id == id)
            .first()
        )

    def list_with_filters(
        self,
        db: Session,
        *,
        district: Optional[str] = None,
        unit_name: Optional[str] = None,
        status: Optional[str] = None,
        crime_head_id: Optional[int] = None,
        crime_subhead_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CaseMaster]:
        """
        List cases with optional filtering by district, unit, status, and crime type.
        Supports pagination via skip/limit.
        """
        query = db.query(CaseMaster)

        # Apply filters dynamically only when they are provided
        if district:
            query = query.filter(CaseMaster.district.ilike(f"%{district}%"))
        if unit_name:
            query = query.filter(CaseMaster.unit_name.ilike(f"%{unit_name}%"))
        if status:
            query = query.filter(CaseMaster.status == status)
        if crime_head_id:
            query = query.filter(CaseMaster.crime_head_id == crime_head_id)
        if crime_subhead_id:
            query = query.filter(CaseMaster.crime_subhead_id == crime_subhead_id)

        return query.order_by(CaseMaster.registered_date.desc()).offset(skip).limit(limit).all()

    def count_with_filters(
        self,
        db: Session,
        *,
        district: Optional[str] = None,
        unit_name: Optional[str] = None,
        status: Optional[str] = None,
        crime_head_id: Optional[int] = None,
    ) -> int:
        """Returns the total count of matching cases for pagination metadata."""
        query = db.query(CaseMaster)
        if district:
            query = query.filter(CaseMaster.district.ilike(f"%{district}%"))
        if unit_name:
            query = query.filter(CaseMaster.unit_name.ilike(f"%{unit_name}%"))
        if status:
            query = query.filter(CaseMaster.status == status)
        if crime_head_id:
            query = query.filter(CaseMaster.crime_head_id == crime_head_id)
        return query.count()

    def get_by_district(self, db: Session, district: str, skip: int = 0, limit: int = 100) -> List[CaseMaster]:
        """Fetch all cases for a specific district, ordered by most recent."""
        return (
            db.query(CaseMaster)
            .filter(CaseMaster.district.ilike(f"%{district}%"))
            .order_by(CaseMaster.incident_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


# Singleton instance used across services
case_repository = CaseRepository(CaseMaster)
