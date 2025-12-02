from typing import List
from ninja import Router
from django.shortcuts import get_object_or_404
from hr.models.scorecard import Scorecard
from hr.models.associate import Associate
from hr.api.schemas.scorecard import ScorecardSchema, ScorecardCreateSchema, ScorecardUpdateSchema

router = Router(tags=["Scorecards"])

@router.post("/", response=ScorecardSchema)
def create_scorecard(request, payload: ScorecardCreateSchema):
    associate = get_object_or_404(Associate, associate_id=payload.associate_id)
    scorecard = Scorecard.objects.create(
        associate=associate,
        month=payload.month,
        overall_score=payload.overall_score,
        target_achievement=payload.target_achievement,
        branch_ranking=payload.branch_ranking,
        skill_update_progress=payload.skill_update_progress,
        attendance_score=payload.attendance_score,
        task_delivery_score=payload.task_delivery_score,
        report_accuracy_score=payload.report_accuracy_score,
        brand_contribution_score=payload.brand_contribution_score,
        training_progress_score=payload.training_progress_score
    )
    return scorecard

@router.get("/", response=List[ScorecardSchema])
def list_scorecards(request, month: str = None, associate_id: str = None):
    qs = Scorecard.objects.all()
    if month:
        qs = qs.filter(month=month)
    if associate_id:
        qs = qs.filter(associate__associate_id=associate_id)
    return qs

@router.get("/{scorecard_id}", response=ScorecardSchema)
def get_scorecard(request, scorecard_id: int):
    return get_object_or_404(Scorecard, id=scorecard_id)

@router.put("/{scorecard_id}", response=ScorecardSchema)
def update_scorecard(request, scorecard_id: int, payload: ScorecardUpdateSchema):
    scorecard = get_object_or_404(Scorecard, id=scorecard_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(scorecard, attr, value)
    scorecard.save()
    return scorecard

@router.delete("/{scorecard_id}")
def delete_scorecard(request, scorecard_id: int):
    scorecard = get_object_or_404(Scorecard, id=scorecard_id)
    scorecard.delete()
    return {"success": True}
