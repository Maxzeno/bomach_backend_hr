from typing import List
from ninja import Router
from ninja.pagination import paginate, LimitOffsetPagination
from django.shortcuts import get_object_or_404
from hr.models.award import Award
from hr.models.associate import Associate
from hr.api.schemas.award import AwardSchema, AwardCreateSchema, AwardUpdateSchema

router = Router(tags=["Awards"])

@router.post("/", response=AwardSchema)
def create_award(request, payload: AwardCreateSchema):
    associate = get_object_or_404(Associate, associate_id=payload.associate_id)
    award = Award.objects.create(
        associate=associate,
        title=payload.title,
        category=payload.category,
        date_awarded=payload.date_awarded,
        rank_level=payload.rank_level,
        description=payload.description
    )
    return award

@router.get("/", response=List[AwardSchema])
@paginate(LimitOffsetPagination, page_size=10)
def list_awards(request, year: int = None, associate_id: str = None):
    qs = Award.objects.all()
    if year:
        qs = qs.filter(date_awarded__year=year)
    if associate_id:
        qs = qs.filter(associate__associate_id=associate_id)
    return qs

@router.get("/{award_id}", response=AwardSchema)
def get_award(request, award_id: int):
    return get_object_or_404(Award, id=award_id)

@router.put("/{award_id}", response=AwardSchema)
def update_award(request, award_id: int, payload: AwardUpdateSchema):
    award = get_object_or_404(Award, id=award_id)
    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(award, attr, value)
    award.save()
    return award

@router.delete("/{award_id}")
def delete_award(request, award_id: int):
    award = get_object_or_404(Award, id=award_id)
    award.delete()
    return {"success": True}
