from ninja import Schema
from datetime import date
from typing import Optional
from decimal import Decimal
from pydantic import Field

class ScorecardSchema(Schema):
    id: int
    associate_id: str
    associate_name: str = Field(..., alias='associate.full_name')
    month: date
    overall_score: Decimal
    target_achievement: Decimal
    branch_ranking: int
    skill_update_progress: Decimal
    attendance_score: Decimal
    task_delivery_score: Decimal
    report_accuracy_score: Decimal
    brand_contribution_score: Decimal
    training_progress_score: Decimal
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True

class ScorecardCreateSchema(Schema):
    associate_id: str
    month: date
    overall_score: Decimal
    target_achievement: Decimal
    branch_ranking: int
    skill_update_progress: Decimal
    attendance_score: Decimal
    task_delivery_score: Decimal
    report_accuracy_score: Decimal
    brand_contribution_score: Decimal
    training_progress_score: Decimal

class ScorecardUpdateSchema(Schema):
    month: Optional[date] = None
    overall_score: Optional[Decimal] = None
    target_achievement: Optional[Decimal] = None
    branch_ranking: Optional[int] = None
    skill_update_progress: Optional[Decimal] = None
    attendance_score: Optional[Decimal] = None
    task_delivery_score: Optional[Decimal] = None
    report_accuracy_score: Optional[Decimal] = None
    brand_contribution_score: Optional[Decimal] = None
    training_progress_score: Optional[Decimal] = None
