from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.crime_type import CrimeHead, CrimeSubHead
    from app.models.employee import Employee
    from app.models.people import Accused, Victim
    from app.models.arrest import ArrestSurrender


class CaseMaster(Base):
    """
    Represents the main FIR records in the police database.
    Mapped to 'case_master' table.
    """
    __tablename__ = "case_master"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fir_number: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    incident_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    registered_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    status: Mapped[str] = mapped_column(String(50), default="Under Investigation", index=True) # Under Investigation, Chargesheeted, Closed
    brief_facts: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    district: Mapped[str] = mapped_column(String(100), index=True)
    unit_name: Mapped[str] = mapped_column(String(100), index=True)  # e.g., "Koramangala Police Station"

    # Foreign Keys
    crime_head_id: Mapped[int] = mapped_column(ForeignKey("crime_heads.id", ondelete="RESTRICT"), nullable=False)
    crime_subhead_id: Mapped[int] = mapped_column(ForeignKey("crime_sub_heads.id", ondelete="RESTRICT"), nullable=False)
    investigating_officer_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    crime_head: Mapped["CrimeHead"] = relationship(back_populates="cases")
    crime_sub_head: Mapped["CrimeSubHead"] = relationship(back_populates="cases")
    investigating_officer: Mapped[Optional["Employee"]] = relationship(
        back_populates="cases_investigated"
    )
    accused_list: Mapped[List["Accused"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    victims: Mapped[List["Victim"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    arrests: Mapped[List["ArrestSurrender"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
