from ninja import Schema
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

class AssetCreate(Schema):
    name: str
    asset_type: str
    branch: str
    assigned_to_name: Optional[str] = None
    assigned_to_email: Optional[str] = None
    department_id: Optional[UUID] = None
    purchase_date: Optional[date] = None
    value: Optional[Decimal] = None
    vendor: Optional[str] = None
    invoice_number: Optional[str] = None
    status: Optional[str] = 'Available'
    warranty_expiry_date: Optional[date] = None
    notes: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None

class AssetUpdate(Schema):
    name: Optional[str] = None
    asset_type: Optional[str] = None
    branch: Optional[str] = None
    assigned_to_name: Optional[str] = None
    assigned_to_email: Optional[str] = None
    department_id: Optional[UUID] = None
    purchase_date: Optional[date] = None
    value: Optional[Decimal] = None
    vendor: Optional[str] = None
    invoice_number: Optional[str] = None
    status: Optional[str] = None
    warranty_expiry_date: Optional[date] = None
    notes: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None

class AssetOut(Schema):
    id: UUID
    asset_id: str
    name: str
    asset_type: str
    branch: str
    assigned_to_name: Optional[str] = None
    assigned_to_email: Optional[str] = None
    department_id: Optional[UUID] = None
    purchase_date: Optional[date] = None
    value: Optional[Decimal] = None
    vendor: Optional[str] = None
    invoice_number: Optional[str] = None
    status: str
    warranty_expiry_date: Optional[date] = None
    notes: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    documents: Optional[str] = None
    created_at: datetime
    updated_at: datetime
