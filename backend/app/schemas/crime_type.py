"""
Crime type schemas — CrimeHead and CrimeSubHead.
"""
from app.schemas.base import AppBaseModel


class CrimeSubHeadOut(AppBaseModel):
    id: int
    code: str
    name: str
    crime_head_id: int


class CrimeHeadOut(AppBaseModel):
    id: int
    code: str
    name: str
    subheads: list[CrimeSubHeadOut] = []
