from ninja import Schema
from typing import Optional, Literal
from datetime import date, datetime
from decimal import Decimal


class WorkReportCreate(Schema):
    employee_id: str
    day: date
    hours_worked: Optional[Decimal] = Decimal('0.0')
    mood: Optional[Literal['happy', 'neutral', 'sad', 'stressed', 'tired', 'frustrated']] = 'neutral'
    challenges: Optional[str] = None
    achievements: Optional[str] = None
    plan_next_day: Optional[str] = None
    status: Optional[Literal['draft', 'submitted', 'approved', 'rejected']] = 'draft'


class WorkReportUpdate(Schema):
    employee_id: Optional[str] = None
    day: Optional[date] = None
    hours_worked: Optional[Decimal] = None
    mood: Optional[Literal['happy', 'neutral', 'sad', 'stressed', 'tired', 'frustrated']] = None
    challenges: Optional[str] = None
    achievements: Optional[str] = None
    plan_next_day: Optional[str] = None
    status: Optional[Literal['draft', 'submitted', 'approved', 'rejected']] = None
    feedback: Optional[str] = None
    rating: Optional[int] = None

class WorkReportOut(Schema):
    id: int
    employee_id: str
    day: date
    hours_worked: Decimal
    mood: str
    challenges: Optional[str] = None
    achievements: Optional[str] = None
    plan_next_day: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    feedback: Optional[str] = None
    rating: Optional[int] = None

class WorkReportListItem(Schema):
    id: int
    employee_id: str
    day: date
    hours_worked: Decimal
    mood: str
    status: str
    created_at: datetime
    updated_at: datetime
    feedback: Optional[str] = None
    rating: Optional[int] = None
