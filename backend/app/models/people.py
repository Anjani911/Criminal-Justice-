from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.case import CaseMaster
    from app.models.arrest import ArrestSurrender


class Accused(Base):
    """
    Represents an accused person associated with a case.
    Mapped to 'accused' table.
    """
    __tablename__ = "accused"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("case_master.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), index=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Suspect")  # Suspect, Arrested, Chargesheeted, Absconding

    # Relationships
    case: Mapped["CaseMaster"] = relationship(back_populates="accused_list")
    arrests: Mapped[List["ArrestSurrender"]] = relationship(
        back_populates="accused", cascade="all, delete-orphan"
    )


class Victim(Base):
    """
    Represents a victim associated with a case.
    Mapped to 'victims' table.
    """
    __tablename__ = "victims"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("case_master.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), index=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    injury_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Grievous, Simple, Fatal, None

    # Relationships
    case: Mapped["CaseMaster"] = relationship(back_populates="victims")
