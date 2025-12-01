from ninja import Schema, Field
from typing import Optional, List
from datetime import date
from uuid import UUID
from pydantic import validator

class PerformanceReviewCreateSchema(Schema):
    employee_id: str
    employee_name: str
    employee_email: Optional[str] = None
    reviewer_id: str
    reviewer_name: str
    review_date: date
    review_period: str
    overall_rating: int = Field(..., ge=1, le=5)
    strengths: str
    areas_for_improvement: str
    feedback: Optional[str] = None
    goals_met: bool = True
    next_review_date: Optional[date] = None

    @validator('overall_rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class PerformanceReviewUpdateSchema(Schema):
    employee_name: Optional[str] = None
    employee_email: Optional[str] = None
    reviewer_name: Optional[str] = None
    review_date: Optional[date] = None
    review_period: Optional[str] = None
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    feedback: Optional[str] = None
    goals_met: Optional[bool] = None
    next_review_date: Optional[date] = None

    @validator('overall_rating')
    def validate_rating(cls, v):
        if v is not None and not 1 <= v <= 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class PerformanceReviewResponseSchema(Schema):
    id: UUID
    employee_id: str
    employee_name: str
    employee_email: Optional[str] = None
    reviewer_id: str
    reviewer_name: str
    review_date: date
    review_period: str
    overall_rating: int
    rating_display: str
    strengths: str
    areas_for_improvement: str
    feedback: Optional[str] = None
    goals_met: bool
    next_review_date: Optional[date] = None
    created_at: str
    updated_at: str

    @staticmethod
    def resolve_created_at(obj):
        return obj.created_at.isoformat()

    @staticmethod
    def resolve_updated_at(obj):
        return obj.updated_at.isoformat()

class PerformanceReviewFilterSchema(Schema):
    employee_id: Optional[str] = None
    reviewer_id: Optional[str] = None
    review_period: Optional[str] = None
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
