from typing import Optional
from math import ceil
from ninja import Router
from django.shortcuts import get_object_or_404
from django.db.models import Q

from hr.models import Department
from hr.api.schemas import (
    DepartmentCreateSchema,
    DepartmentUpdateSchema,
    DepartmentResponseSchema,
    PaginatedResponse,
    MessageSchema,
)


router = Router(tags=['Departments'])


@router.get('/', response=PaginatedResponse[DepartmentResponseSchema])
def list_departments(
    request,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = 1,
    page_size: int = 10,
):
    """
    List all departments with optional filtering, search, and pagination.

    Query Parameters:
    - search: Search in department name and description
    - is_active: Filter by active status
    - page: Page number (default: 1)
    - page_size: Number of items per page (default: 10, max: 100)
    """
    # Validate and limit page_size
    page_size = min(page_size, 100)
    page = max(page, 1)

    queryset = Department.objects.all()

    # Search functionality
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    # Filters
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
        'has_next': total > 0 and page < total_pages,
        'has_previous': page > 1,
    }


@router.get('/{department_id}', response=DepartmentResponseSchema)
def get_department(request, department_id: int):
    """
    Get a single department by ID.
    """
    department = get_object_or_404(Department, id=department_id)
    return department


@router.post('/', response={201: DepartmentResponseSchema})
def create_department(request, payload: DepartmentCreateSchema):
    """
    Create a new department.
    """
    department = Department.objects.create(**payload.model_dump())
    return 201, department


@router.put('/{department_id}', response=DepartmentResponseSchema)
def update_department(request, department_id: int, payload: DepartmentUpdateSchema):
    """
    Update a department (full update).
    """
    department = get_object_or_404(Department, id=department_id)

    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(department, attr, value)

    department.save()
    return department


@router.patch('/{department_id}', response=DepartmentResponseSchema)
def partial_update_department(request, department_id: int, payload: DepartmentUpdateSchema):
    """
    Partially update a department.
    """
    department = get_object_or_404(Department, id=department_id)

    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(department, attr, value)

    department.save()
    return department


@router.delete('/{department_id}', response={200: MessageSchema, 400: MessageSchema})
def delete_department(request, department_id: int):
    """
    Delete a department.
    Note: This will fail if there are job postings associated with this department (protected).
    """
    from django.db.models import ProtectedError

    department = get_object_or_404(Department, id=department_id)
    department_name = department.name

    try:
        department.delete()
        return 200, {'message': f'Department "{department_name}" deleted successfully'}
    except ProtectedError:
        return 400, {'message': f'Cannot delete department "{department_name}" because it has associated job postings.'}


@router.get('/stats/summary', response=dict)
def get_departments_summary(request):
    """
    Get summary statistics for departments.
    """
    total = Department.objects.count()
    active = Department.objects.filter(is_active=True).count()

    return {
        'total': total,
        'active': active,
        'inactive': total - active,
    }
