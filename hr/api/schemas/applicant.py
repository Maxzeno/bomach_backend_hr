from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, EmailStr
from .job_posting import JobPostingListItemSchema


class ApplicantCreateSchema(BaseModel):
    """Schema for creating a new applicant"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=1, max_length=20)
    job_posting_id: int = Field(..., description="ID of the job posting")
    rating: Optional[Decimal] = Field(default=0.0, ge=0.0, le=5.0)
    stage: Optional[str] = Field(default="Applied", description="Stage: Applied, Screening, Interview, Offered, Rejected")
    status: Optional[str] = Field(default="New", description="Status: New, In Review, Shortlisted, Hired, Rejected")
    cover_letter: Optional[str] = None
    notes: Optional[str] = None


class ApplicantUpdateSchema(BaseModel):
    """Schema for updating an applicant"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=1, max_length=20)
    job_posting_id: Optional[int] = Field(None, description="ID of the job posting")
    rating: Optional[Decimal] = Field(None, ge=0.0, le=5.0)
    stage: Optional[str] = None
    status: Optional[str] = None
    cover_letter: Optional[str] = None
    notes: Optional[str] = None


class ApplicantStageUpdateSchema(BaseModel):
    """Schema for updating applicant stage"""
    stage: str = Field(..., description="Stage: Applied, Screening, Interview, Offered, Rejected")


class ApplicantStatusUpdateSchema(BaseModel):
    """Schema for updating applicant status"""
    status: str = Field(..., description="Status: New, In Review, Shortlisted, Hired, Rejected")


class ApplicantRatingUpdateSchema(BaseModel):
    """Schema for updating applicant rating"""
    rating: Decimal = Field(..., ge=0.0, le=5.0, description="Rating from 0.0 to 5.0")


class ApplicantMinimalSchema(BaseModel):
    """Minimal schema for applicant (used in nested responses)"""
    id: int
    application_id: str
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        from_attributes = True


class ApplicantResponseSchema(BaseModel):
    """Schema for applicant response"""
    id: int
    application_id: str
    first_name: str
    last_name: str
    email: EmailStr
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
    application_id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    job_posting: JobPostingListItemSchema
    rating: Decimal
    stage: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
