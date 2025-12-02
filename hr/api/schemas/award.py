from ninja import Schema
from datetime import date
from typing import Optional
from pydantic import Field

class AwardSchema(Schema):
    id: int
    associate_id: str
    associate_name: str = Field(..., alias='associate.full_name')
    title: str
    category: str
    date_awarded: date
    rank_level: str
    description: Optional[str]
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True

class AwardCreateSchema(Schema):
    associate_id: str
    title: str
    category: str
    date_awarded: date
    rank_level: str
    description: Optional[str] = None

class AwardUpdateSchema(Schema):
    title: Optional[str] = None
    category: Optional[str] = None
    date_awarded: Optional[date] = None
    rank_level: Optional[str] = None
    description: Optional[str] = None
