from typing import Optional, List
from datetime import date
from ninja import Router
from ninja.pagination import paginate, LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.exceptions import ValidationError

from hr.models import DailyWorkReport
from hr.api.schemas import (
    WorkReportCreate,
    WorkReportUpdate,
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
    queryset = DailyWorkReport.objects.all()

    if search:
        queryset = queryset.filter(
            Q(employee_id__icontains=search)
        )

    if employee_id:
        queryset = queryset.filter(employee_id=employee_id)

    if status:
        queryset = queryset.filter(status=status)

    if mood:
        queryset = queryset.filter(mood=mood)

    if date_from:
        queryset = queryset.filter(day__gte=date_from)

    if date_to:
        queryset = queryset.filter(day__lte=date_to)

    return queryset


@router.get('/{report_id}', response=WorkReportOut)
def get_work_report(request, report_id: int):
    """
    Get a single work report by ID.
    """
    report = get_object_or_404(DailyWorkReport, id=report_id)
    return report


@router.post('/', response={201: WorkReportOut, 400: MessageSchema})
def create_work_report(request, payload: WorkReportCreate):
    """
    Create a new daily work report.
    """
    try:
        data = payload.model_dump()
        report = DailyWorkReport.objects.create(**data)
        return 201, report
    except ValidationError as e:
        return 400, {'detail': e.messages[0]}


@router.put('/{report_id}', response={200: WorkReportOut, 400: MessageSchema})
def update_work_report(request, report_id: int, payload: WorkReportUpdate):
    """
    Update a work report (full update).
    """
    try:
        report = get_object_or_404(DailyWorkReport, id=report_id)
        update_data = payload.model_dump(exclude_unset=True)

        for attr, value in update_data.items():
            setattr(report, attr, value)

        report.save()
        return 200, report
    except ValidationError as e:
        return 400, {'detail': e.messages[0]}


@router.delete('/{report_id}', response={200: MessageSchema, 204: None, 400: MessageSchema})
def delete_work_report(request, report_id: int):
    """
    Delete a work report.
    """
    try:
        report = get_object_or_404(DailyWorkReport, id=report_id)
        report_date = report.day
        report.delete()
        return 200, {'detail': f'Work report on {report_date} deleted successfully'}
    except ValidationError as e:
        return 400, {'detail': e.messages[0]}
