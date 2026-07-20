from typing import List, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.arrest import ArrestSurrender
    from app.models.case import CaseMaster


class Employee(Base):
    """
    Represents the police personnel utilizing the platform.
    Mapped to 'employees' table.
    """
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(100), index=True)
    rank: Mapped[str] = mapped_column(String(50), index=True)  # Constable, Inspector, SP, etc.
    role: Mapped[str] = mapped_column(String(50), default="Investigator")  # Investigator, Officer, Administrator
    badge_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    unit_name: Mapped[str] = mapped_column(String(100), index=True)  # Name of their Police Station / Unit

    # Relationships
    arrests_made: Mapped[List["ArrestSurrender"]] = relationship(
        back_populates="arresting_officer"
    )
    cases_investigated: Mapped[List["CaseMaster"]] = relationship(
        back_populates="investigating_officer"
    )
    audit_logs = relationship(
        "AuditLog", back_populates="employee", cascade="all, delete-orphan"
    )
