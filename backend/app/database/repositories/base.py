from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from app.database.database import Base

# Generic type variable bound to SQLAlchemy Base models
ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    """
    Generic CRUD base class that provides standard database operations.
    All specific repositories inherit from this class to avoid code duplication.

    This class follows the Repository pattern:
    - It ONLY performs database operations.
    - No business logic is placed here.
    - Services (Phase 4) will call these methods to implement business rules.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize the repository with the SQLAlchemy model class.
        :param model: The SQLAlchemy model class (e.g., CaseMaster, Accused).
        """
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Fetch a single record by its primary key ID."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Fetch multiple records with pagination support."""
        return db.query(self.model).offset(skip).limit(limit).all()

    def get_count(self, db: Session) -> int:
        """Returns the total count of records in the table."""
        return db.query(self.model).count()

    def create(self, db: Session, *, obj_in: Dict[str, Any]) -> ModelType:
        """
        Create and persist a new record from a dictionary of field values.
        :param obj_in: Dictionary of field names to values.
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record.
        :param db_obj: The existing SQLAlchemy ORM object to update.
        :param obj_in: Dictionary of updated field values.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        """Delete a record by its primary key ID."""
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
