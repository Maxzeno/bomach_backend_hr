from typing import Optional, List
from ninja import Router
from ninja.pagination import paginate, LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q

from hr.models import JobPosting
from hr.api.schemas import (
    JobPostingCreateSchema,
    JobPostingUpdateSchema,
    JobPostingStatusUpdateSchema,
    JobPostingResponseSchema,
    JobPostingListItemSchema,
    MessageSchema,
)


router = Router(tags=['Job Postings'])


@router.get('/', response=List[JobPostingListItemSchema], auth=None)
@paginate(LimitOffsetPagination, page_size=10)
def list_job_postings(
    request,
    search: Optional[str] = None,
    branch_id: Optional[str] = None,
    status: Optional[str] = None,
    job_type: Optional[str] = None,
    department_id: Optional[int] = None,
    is_active: Optional[bool] = None,
):
    queryset = JobPosting.objects.all()

    # Search functionality
    if search:
        queryset = queryset.filter(
            Q(job_title__icontains=search)
        )

    # Filters
    if branch_id:
        queryset = queryset.filter(branch_id__iexact=branch_id)

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
    job_posting = get_object_or_404(JobPosting, id=job_posting_id)
    return job_posting


@router.post('/', response={201: JobPostingResponseSchema}, auth=None)
def create_job_posting(request, payload: JobPostingCreateSchema):
    """
    Create a new job posting.
    """
    data = payload.model_dump()
    job_posting = JobPosting.objects.create(**data)
    return 201, job_posting


@router.put('/{job_posting_id}', response=JobPostingResponseSchema)
def update_job_posting(request, job_posting_id: int, payload: JobPostingUpdateSchema):
    """
    Update a job posting (full update).
    """
    job_posting = get_object_or_404(JobPosting, id=job_posting_id)

    update_data = payload.model_dump(exclude_unset=True)

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

    update_data = payload.model_dump(exclude_unset=True)

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
