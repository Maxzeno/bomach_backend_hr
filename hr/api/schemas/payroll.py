from ninja import Schema, Field
from typing import Optional, Dict
from datetime import date
from decimal import Decimal
from pydantic import validator


class PayrollCreateSchema(Schema):
    employee_id: str
    employee_name: str
    employee_email: Optional[str] = None
    payroll_period: str
    gross_salary: Decimal = Field(..., gt=0, decimal_places=2)
    allowances: Optional[Dict[str, float]] = Field(default_factory=dict)
    deductions: Optional[Dict[str, float]] = Field(default_factory=dict)
    disbursement_date: date
    status: str = "Pending"

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['Pending', 'Approved', 'Paid', 'Cancelled']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @validator('allowances', 'deductions')
    def validate_amounts(cls, v):
        if v:
            for key, value in v.items():
                if value < 0:
                    raise ValueError(f'Amount for {key} cannot be negative')
        return v


class PayrollUpdateSchema(Schema):
    employee_name: Optional[str] = None
    employee_email: Optional[str] = None
    payroll_period: Optional[str] = None
    gross_salary: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    allowances: Optional[Dict[str, float]] = None
    deductions: Optional[Dict[str, float]] = None
    disbursement_date: Optional[date] = None
    status: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['Pending', 'Approved', 'Paid', 'Cancelled']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @validator('allowances', 'deductions')
    def validate_amounts(cls, v):
        if v:
            for key, value in v.items():
                if value < 0:
                    raise ValueError(f'Amount for {key} cannot be negative')
        return v


class PayrollResponseSchema(Schema):
    id: int
    employee_id: str
    employee_name: str
    employee_email: Optional[str] = None
    payroll_period: str
    gross_salary: Decimal
    allowances: Dict[str, float]
    deductions: Dict[str, float]
    total_allowances: Decimal
    total_deductions: Decimal
    net_salary: Decimal
    disbursement_date: date
    status: str
    created_at: str
    updated_at: str

    @staticmethod
    def resolve_created_at(obj):
        return obj.created_at.isoformat()

    @staticmethod
    def resolve_updated_at(obj):
        return obj.updated_at.isoformat()


class PayrollListSchema(Schema):
    """Simplified schema for list view"""
    id: int
    employee_id: str
    employee_name: str
    employee_email: Optional[str] = None
    payroll_period: str
    net_salary: Decimal
    disbursement_date: date
    status: str


class PayrollFilterSchema(Schema):
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    payroll_period: Optional[str] = None
    status: Optional[str] = None
    disbursement_date_from: Optional[date] = None
    disbursement_date_to: Optional[date] = None
    min_net_salary: Optional[Decimal] = None
    max_net_salary: Optional[Decimal] = None
