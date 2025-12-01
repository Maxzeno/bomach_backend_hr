from typing import List
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ninja import Router, Query
from hr.models.performance_review import PerformanceReview
from hr.api.schemas import (
    PerformanceReviewCreateSchema,
    PerformanceReviewUpdateSchema,
    PerformanceReviewResponseSchema,
    PerformanceReviewFilterSchema,
    PaginatedResponse,
)
from ninja.pagination import paginate

router = Router(tags=['Performance Reviews'])

@router.post("/", response={201: PerformanceReviewResponseSchema})
def create_performance_review(request, payload: PerformanceReviewCreateSchema):
    review = PerformanceReview.objects.create(**payload.model_dump())
    return 201, review

@router.get("/", response=List[PerformanceReviewResponseSchema])
@paginate
def list_performance_reviews(request, filters: PerformanceReviewFilterSchema = Query(...)):
    reviews = PerformanceReview.objects.all()

    if filters.employee_id:
        reviews = reviews.filter(employee_id=filters.employee_id)
    if filters.reviewer_id:
        reviews = reviews.filter(reviewer_id=filters.reviewer_id)
    if filters.review_period:
        reviews = reviews.filter(review_period__icontains=filters.review_period)
    if filters.min_rating:
        reviews = reviews.filter(overall_rating__gte=filters.min_rating)
    if filters.max_rating:
        reviews = reviews.filter(overall_rating__lte=filters.max_rating)
    if filters.date_from:
        reviews = reviews.filter(review_date__gte=filters.date_from)
    if filters.date_to:
        reviews = reviews.filter(review_date__lte=filters.date_to)

    return reviews

@router.get("/{review_id}", response=PerformanceReviewResponseSchema)
def get_performance_review(request, review_id: str):
    review = get_object_or_404(PerformanceReview, id=review_id)
    return review

@router.put("/{review_id}", response=PerformanceReviewResponseSchema)
def update_performance_review(request, review_id: str, payload: PerformanceReviewUpdateSchema):
    review = get_object_or_404(PerformanceReview, id=review_id)

    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(review, attr, value)

    review.save()
    return review

@router.delete("/{review_id}", response={204: None})
def delete_performance_review(request, review_id: str):
    review = get_object_or_404(PerformanceReview, id=review_id)
    review.delete()
    return 204, None
