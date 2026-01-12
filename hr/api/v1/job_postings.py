from typing import Optional, List
from ninja import Router
from ninja.pagination import paginate, LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q

from hr.models import JobPosting, Department
from hr.api.schemas import (
    JobPostingCreateSchema,
    JobPostingUpdateSchema,
    JobPostingStatusUpdateSchema,
    JobPostingResponseSchema,
    JobPostingListItemSchema,
    MessageSchema,
)


router = Router(tags=['Job Postings'])


@router.get('/', response=List[JobPostingListItemSchema])
@paginate(LimitOffsetPagination, page_size=10)
def list_job_postings(
    request,
    search: Optional[str] = None,
    location: Optional[str] = None,
    status: Optional[str] = None,
    job_type: Optional[str] = None,
    department_id: Optional[int] = None,
    is_active: Optional[bool] = None,
):
    """
    List all job postings with optional filtering and search.

    Query Parameters:
    - search: Search in job title, department name, and location
    - location: Filter by location
    - status: Filter by status
    - job_type: Filter by job type
    - department_id: Filter by department ID
    - is_active: Filter by active status
    - limit: Number of items per page (default: 10)
    - offset: Starting position
    """
    queryset = JobPosting.objects.select_related('department').all()

    # Search functionality
    if search:
        queryset = queryset.filter(
            Q(job_title__icontains=search) |
            Q(department__name__icontains=search) |
            Q(location__icontains=search)
        )

    # Filters
    if location:
        queryset = queryset.filter(location__iexact=location)

    if status:
        queryset = queryset.filter(status=status)

    if job_type:
        queryset = queryset.filter(job_type=job_type)

    if department_id:
        queryset = queryset.filter(department_id=department_id)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    return queryset


@router.get('/{job_posting_id}', response=JobPostingResponseSchema)
def get_job_posting(request, job_posting_id: int):
    """
    Get a single job posting by ID.
    """
    job_posting = get_object_or_404(
        JobPosting.objects.select_related('department'),
        id=job_posting_id
    )
    return job_posting


@router.post('/', response={201: JobPostingResponseSchema})
def create_job_posting(request, payload: JobPostingCreateSchema):
    """
    Create a new job posting.
    """
    data = payload.model_dump(exclude={'department_id'})

    # Get the department
    department = get_object_or_404(Department, id=payload.department_id)
    data['department'] = department

    job_posting = JobPosting.objects.create(**data)
    return 201, job_posting


@router.put('/{job_posting_id}', response=JobPostingResponseSchema)
def update_job_posting(request, job_posting_id: int, payload: JobPostingUpdateSchema):
    """
    Update a job posting (full update).
    """
    job_posting = get_object_or_404(JobPosting, id=job_posting_id)

    update_data = payload.model_dump(exclude_unset=True, exclude={'department_id'})

    # Handle department update if provided
    if 'department_id' in payload.model_dump(exclude_unset=True):
        department = get_object_or_404(Department, id=payload.department_id)
        job_posting.department = department

    for attr, value in update_data.items():
        setattr(job_posting, attr, value)

    job_posting.save()
    return job_posting


@router.patch('/{job_posting_id}', response=JobPostingResponseSchema)
def partial_update_job_posting(request, job_posting_id: int, payload: JobPostingUpdateSchema):
    """
    Partially update a job posting.
    """
    job_posting = get_object_or_404(JobPosting, id=job_posting_id)

    update_data = payload.model_dump(exclude_unset=True, exclude={'department_id'})

    # Handle department update if provided
    if 'department_id' in payload.model_dump(exclude_unset=True):
        department = get_object_or_404(Department, id=payload.department_id)
        job_posting.department = department

    for attr, value in update_data.items():
        setattr(job_posting, attr, value)

    job_posting.save()
    return job_posting


@router.patch('/{job_posting_id}/status', response=JobPostingResponseSchema)
def update_job_posting_status(request, job_posting_id: int, payload: JobPostingStatusUpdateSchema):
    """
    Update only the status of a job posting.
    """
    job_posting = get_object_or_404(JobPosting, id=job_posting_id)
    job_posting.status = payload.status
    job_posting.save(update_fields=['status', 'updated_at'])
    return job_posting


@router.delete('/{job_posting_id}', response={200: MessageSchema, 204: None})
def delete_job_posting(request, job_posting_id: int):
    """
    Delete a job posting.
    """
    job_posting = get_object_or_404(JobPosting, id=job_posting_id)
    job_posting.delete()
    return 200, {'message': f'Job posting "{job_posting.job_title}" deleted successfully'}


@router.get('/stats/summary', response=dict)
def get_job_postings_summary(request):
    """
    Get summary statistics for job postings.
    """
    total = JobPosting.objects.count()
    active = JobPosting.objects.filter(status='Active').count()
    pending = JobPosting.objects.filter(status='Pending').count()
    closed = JobPosting.objects.filter(status='Closed').count()
    draft = JobPosting.objects.filter(status='Draft').count()

    return {
        'total': total,
        'active': active,
        'pending': pending,
        'closed': closed,
        'draft': draft,
    }


@router.get('/filters/options', response=dict)
def get_filter_options(request):
    """
    Get available filter options for job postings.
    Returns unique values for locations, departments, and available choices for status and job_type.
    """
    locations = list(JobPosting.objects.values_list('location', flat=True).distinct())
    departments = Department.objects.filter(is_active=True).values('id', 'name')
    departments_list = [{'id': d['id'], 'name': d['name']} for d in departments]

    return {
        'locations': locations,
        'departments': departments_list,
        'statuses': [choice[0] for choice in JobPosting.Status.choices],
        'job_types': [choice[0] for choice in JobPosting.JobType.choices],
    }
