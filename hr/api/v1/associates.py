from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ninja import Router, Query
from hr.models import Associate, Department
from hr.api.schemas import (
    AssociateCreateSchema,
    AssociateUpdateSchema,
    AssociateResponseSchema,
    AssociateListSchema,
    AssociateFilterSchema,
)
from ninja.pagination import paginate

router = Router(tags=['Associates'])


@router.post("/", response={201: AssociateResponseSchema})
def create_associate(request, payload: AssociateCreateSchema):
    """Create a new associate"""
    data = payload.model_dump(exclude={'department_id'})

    # Handle department relationship
    if payload.department_id:
        department = get_object_or_404(Department, id=payload.department_id)
        data['department'] = department

    associate = Associate.objects.create(**data)
    return 201, associate


@router.get("/", response=List[AssociateListSchema])
@paginate
def list_associates(
    request,
    search: Optional[str] = Query(None, description="Search by name, role, or company"),
    filters: AssociateFilterSchema = Query(...)
):
    """List all associates with search and filters"""
    associates = Associate.objects.select_related('department').all()

    # Search functionality (by name, role, or company)
    if search:
        associates = associates.filter(
            Q(full_name__icontains=search) |
            Q(role_position__icontains=search) |
            Q(company_name__icontains=search) |
            Q(associate_id__icontains=search)
        )

    # Filters from schema
    if filters.associate_id:
        associates = associates.filter(associate_id__icontains=filters.associate_id)
    if filters.full_name:
        associates = associates.filter(full_name__icontains=filters.full_name)
    if filters.email:
        associates = associates.filter(email__icontains=filters.email)
    if filters.company_name:
        associates = associates.filter(company_name__icontains=filters.company_name)
    if filters.role_position:
        associates = associates.filter(role_position=filters.role_position)
    if filters.status:
        associates = associates.filter(status=filters.status)
    if filters.department_id:
        associates = associates.filter(department_id=filters.department_id)
    if filters.contract_start_date_from:
        associates = associates.filter(contract_start_date__gte=filters.contract_start_date_from)
    if filters.contract_start_date_to:
        associates = associates.filter(contract_start_date__lte=filters.contract_start_date_to)
    if filters.contract_end_date_from:
        associates = associates.filter(contract_end_date__gte=filters.contract_end_date_from)
    if filters.contract_end_date_to:
        associates = associates.filter(contract_end_date__lte=filters.contract_end_date_to)

    return associates


@router.get("/{associate_id}", response=AssociateResponseSchema)
def get_associate(request, associate_id: int):
    """Get a single associate by ID"""
    associate = get_object_or_404(Associate.objects.select_related('department'), id=associate_id)
    return associate


@router.put("/{associate_id}", response=AssociateResponseSchema)
def update_associate(request, associate_id: int, payload: AssociateUpdateSchema):
    """Update an associate"""
    associate = get_object_or_404(Associate, id=associate_id)

    update_data = payload.model_dump(exclude_unset=True, exclude={'department_id'})

    # Handle department relationship
    if 'department_id' in payload.model_dump(exclude_unset=True):
        dept_id = payload.department_id
        if dept_id:
            department = get_object_or_404(Department, id=dept_id)
            update_data['department'] = department
        else:
            update_data['department'] = None

    # Validate date logic if both dates are being updated
    start_date = update_data.get('contract_start_date', associate.contract_start_date)
    end_date = update_data.get('contract_end_date', associate.contract_end_date)

    if start_date and end_date and end_date < start_date:
        raise ValueError('Contract end date must be after start date')

    for attr, value in update_data.items():
        setattr(associate, attr, value)

    associate.save()
    return associate


@router.patch("/{associate_id}/status", response=AssociateResponseSchema)
def update_associate_status(request, associate_id: int, status: str = Query(...)):
    """Update only the status of an associate"""
    associate = get_object_or_404(Associate, id=associate_id)

    valid_statuses = ['Active', 'Pending', 'Expired', 'Terminated']
    if status not in valid_statuses:
        raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')

    associate.status = status
    associate.save()
    return associate


@router.delete("/{associate_id}", response={204: None})
def delete_associate(request, associate_id: int):
    """Delete an associate"""
    associate = get_object_or_404(Associate, id=associate_id)
    associate.delete()
    return 204, None
