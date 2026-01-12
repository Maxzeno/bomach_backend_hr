from typing import Optional, List
from datetime import date
from ninja import Router
from ninja.pagination import paginate, LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q

from hr.models import DailyWorkReport
from hr.api.schemas import (
    WorkReportCreate,
    WorkReportUpdate,
    WorkReportStatusUpdate,
    WorkReportOut,
    WorkReportListItem,
    MessageSchema,
)


router = Router(tags=['Work Reports'])


@router.get('/', response=List[WorkReportListItem])
@paginate(LimitOffsetPagination, page_size=10)
def list_work_reports(
    request,
    search: Optional[str] = None,
    employee_id: Optional[str] = None,
    status: Optional[str] = None,
    mood: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    """
    List all daily work reports with optional filtering and search.

    Query Parameters:
    - search: Search by employee name, employee ID, or email
    - employee_id: Filter by specific employee ID
    - status: Filter by status (Draft, Submitted, Approved, Rejected)
    - mood: Filter by mood (Happy, Neutral, Sad, Stressed, Tired)
    - date_from: Filter by date (from)
    - date_to: Filter by date (to)
    - limit: Number of items per page (default: 10)
    - offset: Starting position
    """
    queryset = DailyWorkReport.objects.all()

    if search:
        queryset = queryset.filter(
            Q(employee_name__icontains=search) |
            Q(employee_id__icontains=search) |
            Q(employee_email__icontains=search)
        )

    if employee_id:
        queryset = queryset.filter(employee_id=employee_id)

    if status:
        queryset = queryset.filter(status=status)

    if mood:
        queryset = queryset.filter(mood=mood)

    if date_from:
        queryset = queryset.filter(date__gte=date_from)

    if date_to:
        queryset = queryset.filter(date__lte=date_to)

    return queryset


@router.get('/{report_id}', response=WorkReportOut)
def get_work_report(request, report_id: int):
    """
    Get a single work report by ID.
    """
    report = get_object_or_404(DailyWorkReport, id=report_id)
    return report


@router.post('/', response={201: WorkReportOut})
def create_work_report(request, payload: WorkReportCreate):
    """
    Create a new daily work report.
    """
    data = payload.model_dump()
    report = DailyWorkReport.objects.create(**data)
    return 201, report


@router.put('/{report_id}', response=WorkReportOut)
def update_work_report(request, report_id: int, payload: WorkReportUpdate):
    """
    Update a work report (full update).
    """
    report = get_object_or_404(DailyWorkReport, id=report_id)
    update_data = payload.model_dump(exclude_unset=True)

    for attr, value in update_data.items():
        setattr(report, attr, value)

    report.save()
    return report


@router.patch('/{report_id}', response=WorkReportOut)
def partial_update_work_report(request, report_id: int, payload: WorkReportUpdate):
    """
    Partially update a work report.
    """
    report = get_object_or_404(DailyWorkReport, id=report_id)
    update_data = payload.model_dump(exclude_unset=True)

    for attr, value in update_data.items():
        setattr(report, attr, value)

    report.save()
    return report


@router.patch('/{report_id}/status', response=WorkReportOut)
def update_work_report_status(request, report_id: int, payload: WorkReportStatusUpdate):
    """
    Update the status of a work report.
    Useful for submitting or approving work reports.
    """
    report = get_object_or_404(DailyWorkReport, id=report_id)
    report.status = payload.status
    report.save(update_fields=['status', 'updated_at'])
    return report


@router.delete('/{report_id}', response={200: MessageSchema, 204: None})
def delete_work_report(request, report_id: int):
    """
    Delete a work report.
    """
    report = get_object_or_404(DailyWorkReport, id=report_id)
    employee_name = report.employee_name
    report_date = report.date
    report.delete()
    return 200, {'message': f'Work report for "{employee_name}" on {report_date} deleted successfully'}


@router.get('/stats/summary', response=dict)
def get_work_reports_summary(request):
    """
    Get summary statistics for work reports.
    Returns counts by status and mood.
    """
    total = DailyWorkReport.objects.count()

    by_status = {
        'draft': DailyWorkReport.objects.filter(status='Draft').count(),
        'submitted': DailyWorkReport.objects.filter(status='Submitted').count(),
        'approved': DailyWorkReport.objects.filter(status='Approved').count(),
        'rejected': DailyWorkReport.objects.filter(status='Rejected').count(),
    }

    by_mood = {
        'happy': DailyWorkReport.objects.filter(mood='Happy').count(),
        'neutral': DailyWorkReport.objects.filter(mood='Neutral').count(),
        'sad': DailyWorkReport.objects.filter(mood='Sad').count(),
        'stressed': DailyWorkReport.objects.filter(mood='Stressed').count(),
        'tired': DailyWorkReport.objects.filter(mood='Tired').count(),
    }

    return {
        'total': total,
        'by_status': by_status,
        'by_mood': by_mood,
    }


@router.get('/stats/by-employee/{employee_id}', response=dict)
def get_employee_work_reports_stats(request, employee_id: str):
    """
    Get work report statistics for a specific employee.
    """
    reports = DailyWorkReport.objects.filter(employee_id=employee_id)
    total = reports.count()

    from django.db.models import Avg, Sum

    stats = reports.aggregate(
        avg_hours=Avg('hours_worked'),
        total_hours=Sum('hours_worked'),
    )

    by_status = {
        'draft': reports.filter(status='Draft').count(),
        'submitted': reports.filter(status='Submitted').count(),
        'approved': reports.filter(status='Approved').count(),
        'rejected': reports.filter(status='Rejected').count(),
    }

    return {
        'employee_id': employee_id,
        'total_reports': total,
        'average_hours_worked': float(stats['avg_hours']) if stats['avg_hours'] else 0,
        'total_hours_worked': float(stats['total_hours']) if stats['total_hours'] else 0,
        'by_status': by_status,
    }


@router.get('/filters/options', response=dict)
def get_filter_options(request):
    """
    Get available filter options for work reports.
    Returns unique values for statuses, moods, and employee IDs.
    """
    statuses = [choice[0] for choice in DailyWorkReport.STATUS_CHOICES]
    moods = [choice[0] for choice in DailyWorkReport.MOOD_CHOICES]

    employees = DailyWorkReport.objects.values('employee_id', 'employee_name').distinct()
    employees_list = [
        {'employee_id': emp['employee_id'], 'employee_name': emp['employee_name']}
        for emp in employees
    ]

    return {
        'statuses': statuses,
        'moods': moods,
        'employees': employees_list,
    }
