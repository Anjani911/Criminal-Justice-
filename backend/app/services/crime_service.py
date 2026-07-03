"""
CrimeService
============
Core business logic for managing FIR cases, accused persons, victims,
and arrest records. Services call repositories; no raw SQL or ORM
sessions should appear in API routes.
"""
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.database.repositories import (
    case_repository,
    accused_repository,
    victim_repository,
    arrest_repository,
    crime_head_repository,
    crime_subhead_repository,
)
from app.models.case import CaseMaster
from app.models.people import Accused, Victim
from app.models.arrest import ArrestSurrender
from app.models.crime_type import CrimeHead, CrimeSubHead


class CrimeService:
    """
    Handles all business logic related to FIR cases, suspects,
    victims, and crime classification.

    Rules enforced here (NOT in the repository layer):
    - Pagination limits are capped at 200 records per request.
    - A case FIR number must be unique (validated before creation).
    - Status transitions are validated before persisting.
    """

    # Allowed status values for CaseMaster
    VALID_CASE_STATUSES = {"Under Investigation", "Chargesheeted", "Closed"}
    # Allowed status values for Accused
    VALID_ACCUSED_STATUSES = {"Suspect", "Arrested", "Chargesheeted", "Absconding"}

    # ------------------------------------------------------------------ #
    #  Case operations                                                     #
    # ------------------------------------------------------------------ #

    def get_case_by_id(self, db: Session, case_id: int) -> Optional[CaseMaster]:
        """Return a fully-loaded case by primary key, or None."""
        return case_repository.get_with_relations(db, case_id)

    def get_case_by_fir(self, db: Session, fir_number: str) -> Optional[CaseMaster]:
        """Return a fully-loaded case by FIR number, or None."""
        return case_repository.get_by_fir_number(db, fir_number)

    def list_cases(
        self,
        db: Session,
        *,
        district: Optional[str] = None,
        unit_name: Optional[str] = None,
        status: Optional[str] = None,
        crime_head_id: Optional[int] = None,
        crime_subhead_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Return a paginated list of cases with optional filters.
        Returns both the data list and total_count for frontend pagination.
        """
        # Cap page size to prevent expensive queries
        limit = min(limit, 200)

        cases = case_repository.list_with_filters(
            db,
            district=district,
            unit_name=unit_name,
            status=status,
            crime_head_id=crime_head_id,
            crime_subhead_id=crime_subhead_id,
            skip=skip,
            limit=limit,
        )
        total = case_repository.count_with_filters(
            db,
            district=district,
            unit_name=unit_name,
            status=status,
            crime_head_id=crime_head_id,
        )
        return {"cases": cases, "total": total, "skip": skip, "limit": limit}

    def create_case(self, db: Session, case_data: Dict[str, Any]) -> CaseMaster:
        """
        Create a new FIR case record.
        Validates:
        - FIR number uniqueness.
        - Status is a recognised value.
        """
        fir_number = case_data.get("fir_number", "").strip()
        if not fir_number:
            raise ValueError("FIR number is required.")

        if case_repository.get_by_fir_number(db, fir_number):
            raise ValueError(f"A case with FIR number '{fir_number}' already exists.")

        status = case_data.get("status", "Under Investigation")
        if status not in self.VALID_CASE_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of {self.VALID_CASE_STATUSES}.")

        return case_repository.create(db, obj_in=case_data)

    def update_case_status(
        self, db: Session, case_id: int, new_status: str
    ) -> CaseMaster:
        """
        Update only the status field of a case.
        Validates the status value before persisting.
        """
        if new_status not in self.VALID_CASE_STATUSES:
            raise ValueError(f"Invalid status '{new_status}'.")

        case = case_repository.get(db, case_id)
        if not case:
            raise LookupError(f"Case with ID {case_id} not found.")

        return case_repository.update(db, db_obj=case, obj_in={"status": new_status})

    # ------------------------------------------------------------------ #
    #  Accused operations                                                  #
    # ------------------------------------------------------------------ #

    def get_accused_for_case(self, db: Session, case_id: int) -> List[Accused]:
        """Return all accused persons linked to a case."""
        return accused_repository.get_by_case(db, case_id)

    def get_absconding_accused(self, db: Session, skip: int = 0, limit: int = 50) -> List[Accused]:
        """Return all accused persons with 'Absconding' status. Used for alerts."""
        return accused_repository.get_absconding(db, skip=skip, limit=min(limit, 200))

    def add_accused_to_case(
        self, db: Session, case_id: int, accused_data: Dict[str, Any]
    ) -> Accused:
        """
        Add an accused person to an existing case.
        Validates:
        - The referenced case exists.
        - The accused status is valid.
        """
        case = case_repository.get(db, case_id)
        if not case:
            raise LookupError(f"Case with ID {case_id} not found.")

        status = accused_data.get("status", "Suspect")
        if status not in self.VALID_ACCUSED_STATUSES:
            raise ValueError(f"Invalid accused status '{status}'.")

        accused_data["case_id"] = case_id
        return accused_repository.create(db, obj_in=accused_data)

    def search_accused(self, db: Session, name: str) -> List[Accused]:
        """Cross-case name search for accused persons (partial, case-insensitive)."""
        if len(name.strip()) < 2:
            raise ValueError("Search term must be at least 2 characters.")
        return accused_repository.search_by_name(db, name.strip())

    # ------------------------------------------------------------------ #
    #  Victim operations                                                   #
    # ------------------------------------------------------------------ #

    def get_victims_for_case(self, db: Session, case_id: int) -> List[Victim]:
        """Return all victims linked to a case."""
        return victim_repository.get_by_case(db, case_id)

    def add_victim_to_case(
        self, db: Session, case_id: int, victim_data: Dict[str, Any]
    ) -> Victim:
        """Add a victim to an existing case with validation."""
        case = case_repository.get(db, case_id)
        if not case:
            raise LookupError(f"Case with ID {case_id} not found.")
        victim_data["case_id"] = case_id
        return victim_repository.create(db, obj_in=victim_data)

    # ------------------------------------------------------------------ #
    #  Arrest operations                                                   #
    # ------------------------------------------------------------------ #

    def get_arrests_for_case(self, db: Session, case_id: int) -> List[ArrestSurrender]:
        """Return all arrest/surrender events for a case."""
        return arrest_repository.get_by_case(db, case_id)

    def record_arrest(
        self, db: Session, case_id: int, arrest_data: Dict[str, Any]
    ) -> ArrestSurrender:
        """
        Record a new arrest or surrender event.
        Validates:
        - The case exists.
        - The accused belongs to the case.
        """
        case = case_repository.get(db, case_id)
        if not case:
            raise LookupError(f"Case with ID {case_id} not found.")

        accused_id = arrest_data.get("accused_id")
        accused = accused_repository.get(db, accused_id)
        if not accused or accused.case_id != case_id:
            raise LookupError(f"Accused ID {accused_id} not found or not linked to case {case_id}.")

        arrest_data["case_id"] = case_id
        return arrest_repository.create(db, obj_in=arrest_data)

    # ------------------------------------------------------------------ #
    #  Crime classification                                                #
    # ------------------------------------------------------------------ #

    def get_all_crime_heads(self, db: Session) -> List[CrimeHead]:
        """Return all crime categories with their subheads (for dropdowns)."""
        return crime_head_repository.get_all_with_subheads(db)

    def get_subheads_for_head(self, db: Session, crime_head_id: int) -> List[CrimeSubHead]:
        """Return all sub-categories for a given major crime category."""
        return crime_subhead_repository.get_by_crime_head(db, crime_head_id)


# Singleton service instance
crime_service = CrimeService()
