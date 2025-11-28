from typing import Optional
from math import ceil
from ninja import Router
from django.shortcuts import get_object_or_404
from django.db.models import Q

from hr.models import SubDepartment, Department
from hr.api.schemas import (
    SubDepartmentCreateSchema,
    SubDepartmentUpdateSchema,
    SubDepartmentResponseSchema,
    PaginatedResponse,
    MessageSchema,
)


router = Router(tags=['Sub-Departments'])


@router.get('/', response=PaginatedResponse[SubDepartmentResponseSchema])
def list_sub_departments(
    request,
    search: Optional[str] = None,
    department_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    page: int = 1,
    page_size: int = 10,
):
    """
    List all sub-departments with optional filtering, search, and pagination.

    Query Parameters:
    - search: Search in sub-department name and description
    - department_id: Filter by parent department ID
    - is_active: Filter by active status
    - page: Page number (default: 1)
    - page_size: Number of items per page (default: 10, max: 100)
    """
    # Validate and limit page_size
    page_size = min(page_size, 100)
    page = max(page, 1)

    queryset = SubDepartment.objects.select_related('department').all()

    # Search functionality
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(department__name__icontains=search)
        )

    # Filters
    if department_id:
        queryset = queryset.filter(department_id=department_id)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    # Get total count
    total = queryset.count()
    total_pages = ceil(total / page_size) if page_size > 0 else 0

    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    items = list(queryset[start:end])

    return {
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_previous': page > 1,
    }


@router.get('/{sub_department_id}', response=SubDepartmentResponseSchema)
def get_sub_department(request, sub_department_id: int):
    """
    Get a single sub-department by ID.
    """
    sub_department = get_object_or_404(
        SubDepartment.objects.select_related('department'),
        id=sub_department_id
    )
    return sub_department


@router.post('/', response={201: SubDepartmentResponseSchema})
def create_sub_department(request, payload: SubDepartmentCreateSchema):
    """
    Create a new sub-department.
    """
    data = payload.model_dump(exclude={'department_id'})

    # Get the department
    department = get_object_or_404(Department, id=payload.department_id)
    data['department'] = department

    sub_department = SubDepartment.objects.create(**data)
    return 201, sub_department


@router.put('/{sub_department_id}', response=SubDepartmentResponseSchema)
def update_sub_department(request, sub_department_id: int, payload: SubDepartmentUpdateSchema):
    """
    Update a sub-department (full update).
    """
    sub_department = get_object_or_404(SubDepartment, id=sub_department_id)

    update_data = payload.model_dump(exclude_unset=True, exclude={'department_id'})

    # Handle department update if provided
    if 'department_id' in payload.model_dump(exclude_unset=True):
        department = get_object_or_404(Department, id=payload.department_id)
        sub_department.department = department

    for attr, value in update_data.items():
        setattr(sub_department, attr, value)

    sub_department.save()
    return sub_department


@router.patch('/{sub_department_id}', response=SubDepartmentResponseSchema)
def partial_update_sub_department(request, sub_department_id: int, payload: SubDepartmentUpdateSchema):
    """
    Partially update a sub-department.
    """
    sub_department = get_object_or_404(SubDepartment, id=sub_department_id)

    update_data = payload.model_dump(exclude_unset=True, exclude={'department_id'})

    # Handle department update if provided
    if 'department_id' in payload.model_dump(exclude_unset=True):
        department = get_object_or_404(Department, id=payload.department_id)
        sub_department.department = department

    for attr, value in update_data.items():
        setattr(sub_department, attr, value)

    sub_department.save()
    return sub_department


@router.delete('/{sub_department_id}', response={200: MessageSchema, 204: None})
def delete_sub_department(request, sub_department_id: int):
    """
    Delete a sub-department.
    """
    sub_department = get_object_or_404(SubDepartment, id=sub_department_id)
    sub_department_name = sub_department.name
    sub_department.delete()
    return 200, {'message': f'Sub-department "{sub_department_name}" deleted successfully'}


@router.get('/stats/summary', response=dict)
def get_sub_departments_summary(request):
    """
    Get summary statistics for sub-departments.
    """
    total = SubDepartment.objects.count()
    active = SubDepartment.objects.filter(is_active=True).count()

    # Count by department
    by_department = {}
    departments = Department.objects.all()
    for dept in departments:
        count = SubDepartment.objects.filter(department=dept).count()
        if count > 0:
            by_department[dept.name] = count

    return {
        'total': total,
        'active': active,
        'inactive': total - active,
        'by_department': by_department,
    }
