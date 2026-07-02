from app.database.database import Base
from app.models.crime_type import CrimeHead, CrimeSubHead
from app.models.employee import Employee
from app.models.people import Accused, Victim
from app.models.case import CaseMaster
from app.models.arrest import ArrestSurrender

# This list defines what is imported when from app.models import * is called.
# It also ensures that Alembic / SQLAlchemy metadata registers all models.
__all__ = [
    "Base",
    "CrimeHead",
    "CrimeSubHead",
    "Employee",
    "Accused",
    "Victim",
    "CaseMaster",
    "ArrestSurrender",
]
