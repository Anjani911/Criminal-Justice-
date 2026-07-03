"""
Shared Pydantic base configuration and common schema utilities.
"""
from pydantic import BaseModel, ConfigDict


class AppBaseModel(BaseModel):
    """
    Base class for all Pydantic schemas.
    - orm_mode (model_config) allows reading data directly from SQLAlchemy ORM objects.
    - populate_by_name allows using both alias and field name.
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
