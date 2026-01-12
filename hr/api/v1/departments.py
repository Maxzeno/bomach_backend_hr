from typing import Optional, List
from ninja import Router
from ninja.pagination import paginate, LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q

from hr.models import Department
from hr.api.schemas import (
    DepartmentCreateSchema,
    DepartmentUpdateSchema,
    DepartmentResponseSchema,
    MessageSchema,
)


router = Router(tags=['Departments'])


@router.get('/', response=List[DepartmentResponseSchema])
@paginate(LimitOffsetPagination, page_size=10)
def list_departments(
    request,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    """
    List all departments with optional filtering and search.

    Query Parameters:
    - search: Search in department name and description
    - is_active: Filter by active status
    - limit: Number of items per page (default: 10)
    - offset: Starting position
    """
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

    return queryset


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
