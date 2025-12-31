from ninja import Schema
from typing import Optional, Literal
from datetime import date, datetime
from decimal import Decimal


class WorkReportCreate(Schema):
    employee_id: str
    employee_name: str
    employee_email: str
    date: date
    hours_worked: Optional[Decimal] = Decimal('0.0')
    mood: Optional[Literal['Happy', 'Neutral', 'Sad', 'Stressed', 'Tired']] = 'Neutral'
    challenges: Optional[str] = None
    achievements: Optional[str] = None
    plan_next_day: Optional[str] = None
    status: Optional[Literal['Draft', 'Submitted', 'Approved', 'Rejected']] = 'Draft'


class WorkReportUpdate(Schema):
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    employee_email: Optional[str] = None
    date: Optional[date] = None
    hours_worked: Optional[Decimal] = None
    mood: Optional[Literal['Happy', 'Neutral', 'Sad', 'Stressed', 'Tired']] = None
    challenges: Optional[str] = None
    achievements: Optional[str] = None
    plan_next_day: Optional[str] = None
    status: Optional[Literal['Draft', 'Submitted', 'Approved', 'Rejected']] = None


class WorkReportStatusUpdate(Schema):
    status: Literal['Draft', 'Submitted', 'Approved', 'Rejected']


class WorkReportOut(Schema):
    id: int
    employee_id: str
    employee_name: str
    employee_email: str
    date: date
    hours_worked: Decimal
    mood: str
    challenges: Optional[str] = None
    achievements: Optional[str] = None
    plan_next_day: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime


class WorkReportListItem(Schema):
    id: int
    employee_id: str
    employee_name: str
    employee_email: str
    date: date
    hours_worked: Decimal
    mood: str
    status: str
    created_at: datetime
    updated_at: datetime
