from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .department import DepartmentMinimalSchema


class SubDepartmentCreateSchema(BaseModel):
    """Schema for creating a new sub-department"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    department_id: int = Field(..., description="ID of the parent department")
    is_active: Optional[bool] = True


class SubDepartmentUpdateSchema(BaseModel):
    """Schema for updating a sub-department"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    department_id: Optional[int] = Field(None, description="ID of the parent department")
    is_active: Optional[bool] = None


class SubDepartmentMinimalSchema(BaseModel):
    """Minimal schema for sub-department (used in nested responses)"""
    id: int
    name: str

    class Config:
        from_attributes = True


class SubDepartmentResponseSchema(BaseModel):
    """Schema for sub-department response"""
    id: int
    name: str
    description: Optional[str] = None
    department: DepartmentMinimalSchema
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
