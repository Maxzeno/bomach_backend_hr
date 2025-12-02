from ninja import Schema
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

class WorkReportCreate(Schema):
    employee_name: str
    employee_email: str
    date: date
    hours_worked: Optional[Decimal] = Decimal('0.0')
    mood: Optional[str] = 'Neutral'
    challenges: Optional[str] = None
    achievements: Optional[str] = None
    plan_next_day: Optional[str] = None
    status: Optional[str] = 'Draft'

class WorkReportUpdate(Schema):
    employee_name: Optional[str] = None
    employee_email: Optional[str] = None
    date: Optional[date] = None
    hours_worked: Optional[Decimal] = None
    mood: Optional[str] = None
    challenges: Optional[str] = None
    achievements: Optional[str] = None
    plan_next_day: Optional[str] = None
    status: Optional[str] = None

class WorkReportOut(Schema):
    id: UUID
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
