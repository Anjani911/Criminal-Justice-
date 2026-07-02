from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.case import CaseMaster
    from app.models.people import Accused
    from app.models.employee import Employee


class ArrestSurrender(Base):
    """
    Represents the arrest or surrender details of an accused person in a case.
    Mapped to 'arrest_surrenders' table.
    """
    __tablename__ = "arrest_surrenders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("case_master.id", ondelete="CASCADE"), nullable=False)
    accused_id: Mapped[int] = mapped_column(ForeignKey("accused.id", ondelete="CASCADE"), nullable=False)
    arrest_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    arrest_type: Mapped[str] = mapped_column(String(50), default="Arrested")  # Arrested, Surrendered in Court, Surrendered to Police
    arrest_by_employee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    court_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # Populated if surrendered in court
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    case: Mapped["CaseMaster"] = relationship(back_populates="arrests")
    accused: Mapped["Accused"] = relationship(back_populates="arrests")
    arresting_officer: Mapped[Optional["Employee"]] = relationship(
        back_populates="arrests_made"
    )
