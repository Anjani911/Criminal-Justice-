"""
Repositories package.
Exposes all repository singleton instances for easy import across the service layer.

Usage in services:
    from app.database.repositories import case_repository, accused_repository
"""
from app.database.repositories.case import case_repository, CaseRepository
from app.database.repositories.people import (
    accused_repository,
    victim_repository,
    AccusedRepository,
    VictimRepository,
)
from app.database.repositories.employee import employee_repository, EmployeeRepository
from app.database.repositories.crime_type import (
    crime_head_repository,
    crime_subhead_repository,
    CrimeHeadRepository,
    CrimeSubHeadRepository,
)
from app.database.repositories.arrest import arrest_repository, ArrestRepository

__all__ = [
    "CaseRepository", "case_repository",
    "AccusedRepository", "accused_repository",
    "VictimRepository", "victim_repository",
    "EmployeeRepository", "employee_repository",
    "CrimeHeadRepository", "crime_head_repository",
    "CrimeSubHeadRepository", "crime_subhead_repository",
    "ArrestRepository", "arrest_repository",
]
