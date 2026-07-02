from typing import List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.case import CaseMaster


class CrimeHead(Base):
    """
    Represents the broad category of a crime (e.g., Homicide, Theft, Cybercrime).
    Mapped to 'crime_heads' table.
    """
    __tablename__ = "crime_heads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)

    # Relationships
    subheads: Mapped[List["CrimeSubHead"]] = relationship(
        back_populates="crime_head", cascade="all, delete-orphan"
    )
    cases: Mapped[List["CaseMaster"]] = relationship(
        back_populates="crime_head"
    )


class CrimeSubHead(Base):
    """
    Represents the subcategory of a crime (e.g., under Theft: Vehicle Theft, Chain Snatching).
    Mapped to 'crime_sub_heads' table.
    """
    __tablename__ = "crime_sub_heads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    crime_head_id: Mapped[int] = mapped_column(ForeignKey("crime_heads.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)

    # Relationships
    crime_head: Mapped["CrimeHead"] = relationship(back_populates="subheads")
    cases: Mapped[List["CaseMaster"]] = relationship(
        back_populates="crime_sub_head"
    )
