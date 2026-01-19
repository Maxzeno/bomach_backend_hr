from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field
from .job_posting import JobPostingListItemSchema


class ApplicantCreateSchema(BaseModel):
    """Schema for creating a new applicant"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str
    phone: str = Field(..., min_length=1, max_length=20)
    job_posting_id: int = Field(..., description="ID of the job posting")
    status: Optional[str] = Field(default="new", description="Status: new, in_review, shortlisted, hired, rejected")
    cover_letter: Optional[str] = None
    resume: Optional[str] = None
    linkedin_url: Optional[str] = None
    portolio_url: Optional[str] = None
    notes: Optional[str] = None


class ApplicantUpdateSchema(BaseModel):
    """Schema for updating an applicant"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = Field(None, min_length=1, max_length=20)
    job_posting_id: Optional[int] = Field(None, description="ID of the job posting")
    rating: Optional[Decimal] = Field(None, ge=0.0, le=5.0)
    stage: Optional[str] = None
    status: Optional[str] = None
    cover_letter: Optional[str] = None
    resume: Optional[str] = None
    linkedin_url: Optional[str] = None
    portolio_url: Optional[str] = None
    notes: Optional[str] = None


class ApplicantStageUpdateSchema(BaseModel):
    """Schema for updating applicant stage"""
    stage: str = Field(..., description="Stage: applied, screening, interview, offered, rejected")


class ApplicantStatusUpdateSchema(BaseModel):
    """Schema for updating applicant status"""
    status: str = Field(..., description="Status: new, in_review, shortlisted, hired, rejected")


class ApplicantRatingUpdateSchema(BaseModel):
    """Schema for updating applicant rating"""
    rating: Decimal = Field(..., ge=0.0, le=5.0, description="Rating from 0.0 to 5.0")


class ApplicantMinimalSchema(BaseModel):
    """Minimal schema for applicant (used in nested responses)"""
    id: int
    first_name: str
    last_name: str
    email: str

    class Config:
        from_attributes = True


class ApplicantResponseSchema(BaseModel):
    """Schema for applicant response"""
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    job_posting: JobPostingListItemSchema
    rating: Decimal
    stage: str
    status: str
    resume: Optional[str] = None
    cover_letter: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicantListItemSchema(BaseModel):
    """Schema for applicant in list view (minimal data)"""
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    job_posting: JobPostingListItemSchema
    rating: Decimal
    stage: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
