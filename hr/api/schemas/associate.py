from ninja import Schema, Field
from typing import Optional
from datetime import date
from uuid import UUID
from decimal import Decimal
from pydantic import validator, EmailStr


class DepartmentMinimalSchema(Schema):
    """Minimal department info for nested responses"""
    id: UUID
    name: str


class AssociateCreateSchema(Schema):
    # Personal Information
    full_name: str
    email: EmailStr
    phone_number: str
    address: Optional[str] = None

    # Professional Information
    company_name: str
    role_position: str
    department_id: Optional[int] = None
    specialization: Optional[str] = None

    # Contract Information
    contract_start_date: date
    contract_end_date: date
    contract_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    payment_terms: str = "Monthly"
    supervisor_point_of_contact: Optional[str] = None
    scope_of_work: Optional[str] = None
    status: str = "Pending"

    @validator('contract_end_date')
    def validate_dates(cls, v, values):
        if 'contract_start_date' in values and v < values['contract_start_date']:
            raise ValueError('Contract end date must be after start date')
        return v

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['Active', 'Pending', 'Expired', 'Terminated']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @validator('payment_terms')
    def validate_payment_terms(cls, v):
        valid_terms = ['Monthly', 'Quarterly', 'Milestone-based', 'One-time', 'Hourly', 'Project-based']
        if v not in valid_terms:
            raise ValueError(f'Payment terms must be one of: {", ".join(valid_terms)}')
        return v

    @validator('role_position')
    def validate_role(cls, v):
        valid_roles = [
            'IT Consultant', 'UX Designer', 'Legal Advisor', 'Marketing Specialist',
            'Financial Analyst', 'HR Consultant', 'Software Developer', 'Project Manager',
            'Security Consultant', 'Business Analyst', 'Data Analyst', 'Content Writer',
            'Graphic Designer', 'Other'
        ]
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v


class AssociateUpdateSchema(Schema):
    # Personal Information
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

    # Professional Information
    company_name: Optional[str] = None
    role_position: Optional[str] = None
    department_id: Optional[int] = None
    specialization: Optional[str] = None

    # Contract Information
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    contract_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    payment_terms: Optional[str] = None
    supervisor_point_of_contact: Optional[str] = None
    scope_of_work: Optional[str] = None
    status: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['Active', 'Pending', 'Expired', 'Terminated']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @validator('payment_terms')
    def validate_payment_terms(cls, v):
        if v is not None:
            valid_terms = ['Monthly', 'Quarterly', 'Milestone-based', 'One-time', 'Hourly', 'Project-based']
            if v not in valid_terms:
                raise ValueError(f'Payment terms must be one of: {", ".join(valid_terms)}')
        return v

    @validator('role_position')
    def validate_role(cls, v):
        if v is not None:
            valid_roles = [
                'IT Consultant', 'UX Designer', 'Legal Advisor', 'Marketing Specialist',
                'Financial Analyst', 'HR Consultant', 'Software Developer', 'Project Manager',
                'Security Consultant', 'Business Analyst', 'Data Analyst', 'Content Writer',
                'Graphic Designer', 'Other'
            ]
            if v not in valid_roles:
                raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v


class AssociateResponseSchema(Schema):
    id: UUID
    associate_id: str

    # Personal Information
    full_name: str
    email: str
    phone_number: str
    address: Optional[str] = None

    # Professional Information
    company_name: str
    role_position: str
    department: Optional[DepartmentMinimalSchema] = None
    specialization: Optional[str] = None

    # Contract Information
    contract_start_date: date
    contract_end_date: date
    contract_value: Optional[Decimal] = None
    payment_terms: str
    supervisor_point_of_contact: Optional[str] = None
    scope_of_work: Optional[str] = None

    # Computed properties
    contract_period: str
    contract_duration_days: int
    is_contract_active: bool
    is_contract_expired: bool

    # Documents
    documents: Optional[str] = None

    # Status
    status: str

    # Timestamps
    created_at: str
    updated_at: str

    @staticmethod
    def resolve_created_at(obj):
        return obj.created_at.isoformat()

    @staticmethod
    def resolve_updated_at(obj):
        return obj.updated_at.isoformat()


class AssociateListSchema(Schema):
    """Simplified schema for list view"""
    id: UUID
    associate_id: str
    full_name: str
    email: str
    role_position: str
    company_name: str
    phone_number: str
    contract_period: str
    status: str


class AssociateFilterSchema(Schema):
    associate_id: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    company_name: Optional[str] = None
    role_position: Optional[str] = None
    status: Optional[str] = None
    department_id: Optional[int] = None
    contract_start_date_from: Optional[date] = None
    contract_start_date_to: Optional[date] = None
    contract_end_date_from: Optional[date] = None
    contract_end_date_to: Optional[date] = None
