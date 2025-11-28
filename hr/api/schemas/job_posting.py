from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .department import DepartmentMinimalSchema


class JobPostingCreateSchema(BaseModel):
    """Schema for creating a new job posting"""
    job_title: str = Field(..., min_length=1, max_length=255)
    department_id: int = Field(..., description="ID of the department")
    location: str = Field(..., min_length=1, max_length=255)
    job_type: str = Field(..., description="Job type: Full-Time, Part-Time, Contract, Internship, Temporary")
    status: Optional[str] = Field(default="Draft", description="Status: Draft, Pending, Active, Closed, Cancelled")
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    salary_range: Optional[str] = Field(None, max_length=100)
    deadline: Optional[datetime] = None
    is_active: Optional[bool] = True


class JobPostingUpdateSchema(BaseModel):
    """Schema for updating a job posting"""
    job_title: Optional[str] = Field(None, min_length=1, max_length=255)
    department_id: Optional[int] = Field(None, description="ID of the department")
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    job_type: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    salary_range: Optional[str] = Field(None, max_length=100)
    deadline: Optional[datetime] = None
    is_active: Optional[bool] = None


class JobPostingStatusUpdateSchema(BaseModel):
    """Schema for updating only the status of a job posting"""
    status: str = Field(..., description="Status: Draft, Pending, Active, Closed, Cancelled")


class JobPostingResponseSchema(BaseModel):
    """Schema for job posting response"""
    id: int
    job_title: str
    department: DepartmentMinimalSchema
    location: str
    job_type: str
    status: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    salary_range: Optional[str] = None
    applicants_count: int
    deadline: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobPostingListItemSchema(BaseModel):
    """Schema for job posting in list view (minimal data)"""
    id: int
    job_title: str
    department: DepartmentMinimalSchema
    location: str
    job_type: str
    status: str
    applicants_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageSchema(BaseModel):
    """Generic message response schema"""
    message: str
