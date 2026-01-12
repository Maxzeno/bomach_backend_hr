from typing import Optional, List
from ninja import Router
from ninja.pagination import paginate, LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q

from hr.models import Applicant, JobPosting
from hr.api.schemas import (
    ApplicantCreateSchema,
    ApplicantUpdateSchema,
    ApplicantStageUpdateSchema,
    ApplicantStatusUpdateSchema,
    ApplicantRatingUpdateSchema,
    ApplicantResponseSchema,
    ApplicantListItemSchema,
    MessageSchema,
)


router = Router(tags=['Applicants'])


@router.get('/', response=List[ApplicantListItemSchema])
@paginate(LimitOffsetPagination, page_size=10)
def list_applicants(
    request,
    search: Optional[str] = None,
    job_posting_id: Optional[int] = None,
    stage: Optional[str] = None,
    status: Optional[str] = None,
):
    """
    List all applicants with optional filtering and search.

    Query Parameters:
    - search: Search in applicant name, email, phone, or application ID
    - job_posting_id: Filter by job posting ID
    - stage: Filter by application stage
    - status: Filter by application status
    - limit: Number of items per page (default: 10)
    - offset: Starting position
    """
    queryset = Applicant.objects.select_related('job_posting', 'job_posting__department').all()

    # Search functionality
    if search:
        queryset = queryset.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search) |
            Q(application_id__icontains=search) |
            Q(job_posting__job_title__icontains=search)
        )

    # Filters
    if job_posting_id:
        queryset = queryset.filter(job_posting_id=job_posting_id)

    if stage:
        queryset = queryset.filter(stage=stage)

    if status:
        queryset = queryset.filter(status=status)

    return queryset


@router.get('/{applicant_id}', response=ApplicantResponseSchema)
def get_applicant(request, applicant_id: int):
    """
    Get a single applicant by ID.
    """
    applicant = get_object_or_404(
        Applicant.objects.select_related('job_posting', 'job_posting__department'),
        id=applicant_id
    )
    return applicant


@router.post('/', response={201: ApplicantResponseSchema})
def create_applicant(request, payload: ApplicantCreateSchema):
    """
    Create a new applicant.
    """
    data = payload.model_dump(exclude={'job_posting_id'})

    # Get the job posting
    job_posting = get_object_or_404(JobPosting, id=payload.job_posting_id)
    data['job_posting'] = job_posting

    applicant = Applicant.objects.create(**data)

    # Increment job posting applicants count
    job_posting.increment_applicants()

    return 201, applicant


@router.put('/{applicant_id}', response=ApplicantResponseSchema)
def update_applicant(request, applicant_id: int, payload: ApplicantUpdateSchema):
    """
    Update an applicant (full update).
    """
    applicant = get_object_or_404(Applicant, id=applicant_id)

    update_data = payload.model_dump(exclude_unset=True, exclude={'job_posting_id'})

    # Handle job posting update if provided
    if 'job_posting_id' in payload.model_dump(exclude_unset=True):
        old_job_posting = applicant.job_posting
        new_job_posting = get_object_or_404(JobPosting, id=payload.job_posting_id)

        if old_job_posting.id != new_job_posting.id:
            # Update counts
            old_job_posting.decrement_applicants()
            new_job_posting.increment_applicants()
            applicant.job_posting = new_job_posting

    for attr, value in update_data.items():
        setattr(applicant, attr, value)

    applicant.save()
    return applicant


@router.patch('/{applicant_id}', response=ApplicantResponseSchema)
def partial_update_applicant(request, applicant_id: int, payload: ApplicantUpdateSchema):
    """
    Partially update an applicant.
    """
    applicant = get_object_or_404(Applicant, id=applicant_id)

    update_data = payload.model_dump(exclude_unset=True, exclude={'job_posting_id'})

    # Handle job posting update if provided
    if 'job_posting_id' in payload.model_dump(exclude_unset=True):
        old_job_posting = applicant.job_posting
        new_job_posting = get_object_or_404(JobPosting, id=payload.job_posting_id)

        if old_job_posting.id != new_job_posting.id:
            # Update counts
            old_job_posting.decrement_applicants()
            new_job_posting.increment_applicants()
            applicant.job_posting = new_job_posting

    for attr, value in update_data.items():
        setattr(applicant, attr, value)

    applicant.save()
    return applicant


@router.patch('/{applicant_id}/stage', response=ApplicantResponseSchema)
def update_applicant_stage(request, applicant_id: int, payload: ApplicantStageUpdateSchema):
    """
    Update only the stage of an applicant.
    """
    applicant = get_object_or_404(Applicant, id=applicant_id)
    applicant.stage = payload.stage
    applicant.save(update_fields=['stage', 'updated_at'])
    return applicant


@router.patch('/{applicant_id}/status', response=ApplicantResponseSchema)
def update_applicant_status(request, applicant_id: int, payload: ApplicantStatusUpdateSchema):
    """
    Update only the status of an applicant.
    """
    applicant = get_object_or_404(Applicant, id=applicant_id)
    applicant.status = payload.status
    applicant.save(update_fields=['status', 'updated_at'])
    return applicant


@router.patch('/{applicant_id}/rating', response=ApplicantResponseSchema)
def update_applicant_rating(request, applicant_id: int, payload: ApplicantRatingUpdateSchema):
    """
    Update only the rating of an applicant.
    """
    applicant = get_object_or_404(Applicant, id=applicant_id)
    applicant.rating = payload.rating
    applicant.save(update_fields=['rating', 'updated_at'])
    return applicant


@router.delete('/{applicant_id}', response={200: MessageSchema, 204: None})
def delete_applicant(request, applicant_id: int):
    """
    Delete an applicant.
    """
    applicant = get_object_or_404(Applicant, id=applicant_id)
    job_posting = applicant.job_posting
    applicant_name = applicant.full_name

    applicant.delete()

    # Decrement job posting applicants count
    job_posting.decrement_applicants()

    return 200, {'message': f'Applicant "{applicant_name}" deleted successfully'}


@router.get('/stats/summary', response=dict)
def get_applicants_summary(request):
    """
    Get summary statistics for applicants.
    """
    total = Applicant.objects.count()

    # Count by stage
    applied = Applicant.objects.filter(stage='Applied').count()
    screening = Applicant.objects.filter(stage='Screening').count()
    interview = Applicant.objects.filter(stage='Interview').count()
    offered = Applicant.objects.filter(stage='Offered').count()
    rejected = Applicant.objects.filter(stage='Rejected').count()

    # Count by status
    new = Applicant.objects.filter(status='New').count()
    in_review = Applicant.objects.filter(status='In Review').count()
    shortlisted = Applicant.objects.filter(status='Shortlisted').count()
    hired = Applicant.objects.filter(status='Hired').count()
    rejected_status = Applicant.objects.filter(status='Rejected').count()

    return {
        'total': total,
        'by_stage': {
            'applied': applied,
            'screening': screening,
            'interview': interview,
            'offered': offered,
            'rejected': rejected,
        },
        'by_status': {
            'new': new,
            'in_review': in_review,
            'shortlisted': shortlisted,
            'hired': hired,
            'rejected': rejected_status,
        },
    }


@router.get('/filters/options', response=dict)
def get_filter_options(request):
    """
    Get available filter options for applicants.
    Returns available choices for stage and status, and active job postings.
    """
    from hr.models import JobPosting

    job_postings = JobPosting.objects.filter(is_active=True).values('id', 'job_title')
    job_postings_list = [{'id': jp['id'], 'job_title': jp['job_title']} for jp in job_postings]

    return {
        'job_postings': job_postings_list,
        'stages': [choice[0] for choice in Applicant.Stage.choices],
        'statuses': [choice[0] for choice in Applicant.Status.choices],
    }
