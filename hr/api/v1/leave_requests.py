from typing import Optional, List
from datetime import date
from ninja import Router
from ninja.pagination import paginate, LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.exceptions import ValidationError

from hr.models import LeaveRequest
from hr.api.schemas import (
    LeaveRequestCreateSchema,
    LeaveRequestUpdateSchema,
    LeaveRequestStatusUpdateSchema,
    LeaveRequestResponseSchema,
    LeaveRequestListItemSchema,
    MessageSchema,
)


router = Router(tags=['Leave Requests'])


@router.get('/', response=List[LeaveRequestListItemSchema])
@paginate(LimitOffsetPagination, page_size=10)
def list_leave_requests(
    request,
    search: Optional[str] = None,
    employee_id: Optional[str] = None,
    leave_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date_from: Optional[date] = None,
    start_date_to: Optional[date] = None,
):
    queryset = LeaveRequest.objects.all()

    # Search functionality
    if search:
        queryset = queryset.filter(
            Q(employee_id__icontains=search)
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

    return queryset


@router.get('/{leave_request_id}', response=LeaveRequestResponseSchema)
def get_leave_request(request, leave_request_id: int):
    """
    Get a single leave request by ID.
    """
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)
    return leave_request


@router.post('/', response={201: LeaveRequestResponseSchema, 400: MessageSchema})
def create_leave_request(request, payload: LeaveRequestCreateSchema):
    """
    Create a new leave request.
    """
    try:
        data = payload.model_dump()
        leave_request = LeaveRequest.objects.create(**data)
        return 201, leave_request
    except ValidationError as e:
        return 400, {'detail': e.messages[0]}


@router.put('/{leave_request_id}', response={200: LeaveRequestResponseSchema, 400: MessageSchema})
def update_leave_request(request, leave_request_id: int, payload: LeaveRequestUpdateSchema):
    """
    Update a leave request (full update).
    """
    try:
        leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)

        update_data = payload.model_dump(exclude_unset=True)

        for attr, value in update_data.items():
            setattr(leave_request, attr, value)

        leave_request.save()
        return 200, leave_request
    except ValidationError as e:
        return 400, {'detail': e.messages[0]}


@router.patch('/{leave_request_id}/status', response={200: LeaveRequestResponseSchema, 400: MessageSchema})
def update_leave_request_status(request, leave_request_id: int, payload: LeaveRequestStatusUpdateSchema):
    """
    Update the status of a leave request.
    Useful for approving or rejecting leave requests.
    """
    try:
        leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)

        update_data = payload.model_dump(exclude_unset=True)
        update_fields = ['status', 'updated_at']

        for attr, value in update_data.items():
            setattr(leave_request, attr, value)
            if attr not in update_fields:
                update_fields.append(attr)

        leave_request.save(update_fields=update_fields)
        return 200, leave_request
    except ValidationError as e:
        return 400, {'detail': e.messages[0]}


@router.delete('/{leave_request_id}', response={200: MessageSchema, 204: None, 400: MessageSchema})
def delete_leave_request(request, leave_request_id: int):
    """
    Delete a leave request.
    """
    try:
        leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)
        leave_request.delete()
        return 200, {'detail': f'Leave request deleted successfully'}
    except ValidationError as e:
        return 400, {'detail': e.messages[0]}


@router.get('/stats/summary', response=dict)
def get_leave_requests_summary(request):
    """
    Get summary statistics for leave requests.
    Returns counts by status.
    """
    total = LeaveRequest.objects.count()
    pending = LeaveRequest.objects.filter(status='pending').count()
    approved = LeaveRequest.objects.filter(status='approved').count()
    rejected = LeaveRequest.objects.filter(status='rejected').count()
    cancelled = LeaveRequest.objects.filter(status='cancelled').count()

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
    pending = LeaveRequest.objects.filter(employee_id=employee_id, status='pending').count()
    approved = LeaveRequest.objects.filter(employee_id=employee_id, status='approved').count()
    rejected = LeaveRequest.objects.filter(employee_id=employee_id, status='rejected').count()

    return {
        'employee_id': employee_id,
        'total': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
    }
