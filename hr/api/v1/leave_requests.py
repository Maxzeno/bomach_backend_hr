from typing import Optional
from math import ceil
from datetime import date
from ninja import Router
from django.shortcuts import get_object_or_404
from django.db.models import Q

from hr.models import LeaveRequest
from hr.api.schemas import (
    LeaveRequestCreateSchema,
    LeaveRequestUpdateSchema,
    LeaveRequestStatusUpdateSchema,
    LeaveRequestResponseSchema,
    LeaveRequestListItemSchema,
    PaginatedResponse,
    MessageSchema,
)


router = Router(tags=['Leave Requests'])


@router.get('/', response=PaginatedResponse[LeaveRequestListItemSchema])
def list_leave_requests(
    request,
    search: Optional[str] = None,
    employee_id: Optional[str] = None,
    leave_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date_from: Optional[date] = None,
    start_date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = 10,
):
    """
    List all leave requests with optional filtering, search, and pagination.

    Query Parameters:
    - search: Search by employee name or employee ID
    - employee_id: Filter by specific employee ID
    - leave_type: Filter by leave type
    - status: Filter by status
    - start_date_from: Filter by start date (from)
    - start_date_to: Filter by start date (to)
    - page: Page number (default: 1)
    - page_size: Number of items per page (default: 10, max: 100)
    """
    # Validate and limit page_size
    page_size = min(page_size, 100)
    page = max(page, 1)

    queryset = LeaveRequest.objects.all()

    # Search functionality
    if search:
        queryset = queryset.filter(
            Q(employee_name__icontains=search) |
            Q(employee_id__icontains=search) |
            Q(employee_email__icontains=search)
        )

    # Filters
    if employee_id:
        queryset = queryset.filter(employee_id=employee_id)

    if leave_type:
        queryset = queryset.filter(leave_type=leave_type)

    if status:
        queryset = queryset.filter(status=status)

    if start_date_from:
        queryset = queryset.filter(start_date__gte=start_date_from)

    if start_date_to:
        queryset = queryset.filter(start_date__lte=start_date_to)

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


@router.get('/{leave_request_id}', response=LeaveRequestResponseSchema)
def get_leave_request(request, leave_request_id: int):
    """
    Get a single leave request by ID.
    """
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)
    return leave_request


@router.post('/', response={201: LeaveRequestResponseSchema})
def create_leave_request(request, payload: LeaveRequestCreateSchema):
    """
    Create a new leave request.
    """
    data = payload.model_dump()
    leave_request = LeaveRequest.objects.create(**data)
    return 201, leave_request


@router.put('/{leave_request_id}', response=LeaveRequestResponseSchema)
def update_leave_request(request, leave_request_id: int, payload: LeaveRequestUpdateSchema):
    """
    Update a leave request (full update).
    """
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)

    update_data = payload.model_dump(exclude_unset=True)

    for attr, value in update_data.items():
        setattr(leave_request, attr, value)

    leave_request.save()
    return leave_request


@router.patch('/{leave_request_id}', response=LeaveRequestResponseSchema)
def partial_update_leave_request(request, leave_request_id: int, payload: LeaveRequestUpdateSchema):
    """
    Partially update a leave request.
    """
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)

    update_data = payload.model_dump(exclude_unset=True)

    for attr, value in update_data.items():
        setattr(leave_request, attr, value)

    leave_request.save()
    return leave_request


@router.patch('/{leave_request_id}/status', response=LeaveRequestResponseSchema)
def update_leave_request_status(request, leave_request_id: int, payload: LeaveRequestStatusUpdateSchema):
    """
    Update the status of a leave request.
    Useful for approving or rejecting leave requests.
    """
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)

    update_data = payload.model_dump(exclude_unset=True)
    update_fields = ['status', 'updated_at']

    for attr, value in update_data.items():
        setattr(leave_request, attr, value)
        if attr not in update_fields:
            update_fields.append(attr)

    leave_request.save(update_fields=update_fields)
    return leave_request


@router.delete('/{leave_request_id}', response={200: MessageSchema, 204: None})
def delete_leave_request(request, leave_request_id: int):
    """
    Delete a leave request.
    """
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)
    employee_name = leave_request.employee_name
    leave_request.delete()
    return 200, {'message': f'Leave request for "{employee_name}" deleted successfully'}


@router.get('/stats/summary', response=dict)
def get_leave_requests_summary(request):
    """
    Get summary statistics for leave requests.
    Returns counts by status.
    """
    total = LeaveRequest.objects.count()
    pending = LeaveRequest.objects.filter(status='Pending').count()
    approved = LeaveRequest.objects.filter(status='Approved').count()
    rejected = LeaveRequest.objects.filter(status='Rejected').count()
    cancelled = LeaveRequest.objects.filter(status='Cancelled').count()

    return {
        'total': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'cancelled': cancelled,
    }


@router.get('/stats/by-employee/{employee_id}', response=dict)
def get_employee_leave_stats(request, employee_id: str):
    """
    Get leave request statistics for a specific employee.
    """
    total = LeaveRequest.objects.filter(employee_id=employee_id).count()
    pending = LeaveRequest.objects.filter(employee_id=employee_id, status='Pending').count()
    approved = LeaveRequest.objects.filter(employee_id=employee_id, status='Approved').count()
    rejected = LeaveRequest.objects.filter(employee_id=employee_id, status='Rejected').count()

    return {
        'employee_id': employee_id,
        'total': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
    }


@router.get('/filters/options', response=dict)
def get_filter_options(request):
    """
    Get available filter options for leave requests.
    Returns unique values for leave types, statuses, and employee IDs.
    """
    leave_types = [choice[0] for choice in LeaveRequest.LEAVE_TYPE_CHOICES]
    statuses = [choice[0] for choice in LeaveRequest.STATUS_CHOICES]

    # Get unique employee IDs and names
    employees = LeaveRequest.objects.values('employee_id', 'employee_name').distinct()
    employees_list = [
        {'employee_id': emp['employee_id'], 'employee_name': emp['employee_name']}
        for emp in employees
    ]

    return {
        'leave_types': leave_types,
        'statuses': statuses,
        'employees': employees_list,
    }
