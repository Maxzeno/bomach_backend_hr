from typing import List
from ninja import Router
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from hr.models.leaderboard import PerformanceLeaderboard
from hr.api.schemas.leaderboard import LeaderboardSchema, LeaderboardSummarySchema

router = Router(tags=["Performance Leaderboard"])

@router.get("/", response=List[LeaderboardSchema])
def list_leaderboard(request, month: str = None, branch: str = None):
    qs = PerformanceLeaderboard.objects.select_related('associate', 'associate__department').all()
    if month:
        qs = qs.filter(month=month)
    if branch:
        # Assuming department name acts as branch for filtering
        qs = qs.filter(associate__department__name__icontains=branch)
    return qs

@router.get("/summary", response=LeaderboardSummarySchema)
def get_leaderboard_summary(request, month: str = None):
    qs = PerformanceLeaderboard.objects.select_related('associate', 'associate__department').all()
    if month:
        qs = qs.filter(month=month)

    top_performers = qs.order_by('rank')[:3]
    avg_score = qs.aggregate(Avg('score'))['score__avg'] or 0
    participants_count = qs.count()

    return {
        "top_performers": list(top_performers),
        "avg_score": avg_score,
        "participants_count": participants_count
    }

@router.post("/generate")
def generate_leaderboard(request, month: str):
    # Placeholder for logic to calculate and populate leaderboard from Scorecards
    # For now, this is a stub to allow manual triggering or future implementation
    return {"message": f"Leaderboard generation triggered for {month}"}
