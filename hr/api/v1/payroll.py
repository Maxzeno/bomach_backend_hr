from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ninja import Router, Query
from hr.models import Payroll
from hr.api.schemas import (
    PayrollCreateSchema,
    PayrollUpdateSchema,
    PayrollResponseSchema,
    PayrollListSchema,
    PayrollFilterSchema,
    PaginatedResponse,
)
from ninja.pagination import paginate, LimitOffsetPagination

router = Router(tags=['Payroll'])


@router.post("/", response={201: PayrollResponseSchema})
def create_payroll(request, payload: PayrollCreateSchema):
    """Create a new payroll record"""
    payroll = Payroll.objects.create(**payload.model_dump())
    return 201, payroll


@router.get("/", response=List[PayrollListSchema])
@paginate(LimitOffsetPagination, page_size=10)
def list_payroll(
    request,
    search: Optional[str] = Query(None, description="Search by employee name or ID"),
    filters: PayrollFilterSchema = Query(...)
):
    """List all payroll records with search and filters"""
    payroll_records = Payroll.objects.all()

    # Search functionality (by name or employee ID)
    if search:
        payroll_records = payroll_records.filter(
            Q(employee_name__icontains=search) | Q(employee_id__icontains=search)
        )

    # Filters from schema
    if filters.employee_id:
        payroll_records = payroll_records.filter(employee_id=filters.employee_id)
    if filters.employee_name:
        payroll_records = payroll_records.filter(employee_name__icontains=filters.employee_name)
    if filters.payroll_period:
        payroll_records = payroll_records.filter(payroll_period__icontains=filters.payroll_period)
    if filters.status:
        payroll_records = payroll_records.filter(status=filters.status)
    if filters.disbursement_date_from:
        payroll_records = payroll_records.filter(disbursement_date__gte=filters.disbursement_date_from)
    if filters.disbursement_date_to:
        payroll_records = payroll_records.filter(disbursement_date__lte=filters.disbursement_date_to)
    if filters.min_net_salary:
        payroll_records = payroll_records.filter(net_salary__gte=filters.min_net_salary)
    if filters.max_net_salary:
        payroll_records = payroll_records.filter(net_salary__lte=filters.max_net_salary)

    return payroll_records


@router.get("/{payroll_id}", response=PayrollResponseSchema)
def get_payroll(request, payroll_id: int):
    """Get a single payroll record by ID"""
    payroll = get_object_or_404(Payroll, id=payroll_id)
    return payroll


@router.put("/{payroll_id}", response=PayrollResponseSchema)
def update_payroll(request, payroll_id: int, payload: PayrollUpdateSchema):
    """Update a payroll record"""
    payroll = get_object_or_404(Payroll, id=payroll_id)

    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(payroll, attr, value)

    payroll.save()
    return payroll


@router.patch("/{payroll_id}/status", response=PayrollResponseSchema)
def update_payroll_status(request, payroll_id: int, status: str = Query(...)):
    """Update only the status of a payroll record"""
    payroll = get_object_or_404(Payroll, id=payroll_id)

    valid_statuses = ['Pending', 'Approved', 'Paid', 'Cancelled']
    if status not in valid_statuses:
        raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')

    payroll.status = status
    payroll.save()
    return payroll


@router.delete("/{payroll_id}", response={204: None})
def delete_payroll(request, payroll_id: int):
    """Delete a payroll record"""
    payroll = get_object_or_404(Payroll, id=payroll_id)
    payroll.delete()
    return 204, None
