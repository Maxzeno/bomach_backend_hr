from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DepartmentCreateSchema(BaseModel):
    """Schema for creating a new department"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = True


class DepartmentUpdateSchema(BaseModel):
    """Schema for updating a department"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentMinimalSchema(BaseModel):
    """Minimal schema for department (used in nested responses)"""
    id: int
    name: str

    class Config:
        from_attributes = True


class DepartmentResponseSchema(BaseModel):
    """Schema for department response"""
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
