from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class LeaveRequestCreateSchema(BaseModel):
    """Schema for creating a new leave request"""
    employee_id: str = Field(..., min_length=1, max_length=50)
    leave_type: Literal[
        'Sick Leave',
        'Annual Leave',
        'Casual Leave',
        'Maternity Leave',
        'Paternity Leave',
        'Unpaid Leave',
        'Compassionate Leave'
    ] = Field(..., description="Type of leave")
    start_date: date = Field(..., description="Leave start date")
    end_date: date = Field(..., description="Leave end date")
    reason: str = Field(..., min_length=1, description="Reason for leave")
    # status: Optional[Literal['Pending', 'Approved', 'Rejected', 'Cancelled']] = Field(
    #     default='Pending',
    #     description="Leave request status"
    # )
    # approver_id: Optional[str] = Field(None, max_length=50)
    # approval_date: Optional[date] = None
    # rejection_reason: Optional[str] = None


class LeaveRequestUpdateSchema(BaseModel):
    """Schema for updating a leave request"""
    employee_id: Optional[str] = Field(None, min_length=1, max_length=50)
    leave_type: Optional[Literal[
        'Sick Leave',
        'Annual Leave',
        'Casual Leave',
        'Maternity Leave',
        'Paternity Leave',
        'Unpaid Leave',
        'Compassionate Leave'
    ]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = None
    status: Optional[Literal['Pending', 'Approved', 'Rejected', 'Cancelled']] = None
    approver_id: Optional[str] = Field(None, max_length=50)
    approval_date: Optional[date] = None
    rejection_reason: Optional[str] = None


class LeaveRequestStatusUpdateSchema(BaseModel):
    """Schema for updating leave request status"""
    status: Literal['Pending', 'Approved', 'Rejected', 'Cancelled'] = Field(
        ...,
        description="New status for the leave request"
    )
    approver_id: Optional[str] = Field(None, max_length=50, description="ID of the approver")
    approval_date: Optional[date] = Field(None, description="Date of approval/rejection")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection (if rejected)")


class LeaveRequestResponseSchema(BaseModel):
    """Schema for leave request response"""
    id: int
    employee_id: str
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    status: str
    approver_id: Optional[str] = None
    approval_date: Optional[date] = None
    rejection_reason: Optional[str] = None
    duration_days: int = Field(..., description="Number of days for the leave")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeaveRequestListItemSchema(BaseModel):
    """Schema for leave request in list view"""
    id: int
    employee_id: str
    leave_type: str
    start_date: date
    end_date: date
    status: str
    duration_days: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageSchema(BaseModel):
    """Generic message response schema"""
    message: str
