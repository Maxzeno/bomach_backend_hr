from ninja import Schema
from datetime import date
from typing import Optional, List
from decimal import Decimal
from pydantic import Field

class LeaderboardSchema(Schema):
    id: int
    associate_id: str
    associate_name: str = Field(..., alias='associate.full_name')
    branch: Optional[str] = Field(None, alias='associate.department.name') # Assuming department maps to branch for now
    month: date
    score: Decimal
    rank: int
    status: str
    awards_summary: Optional[str]

    class Config:
        from_attributes = True

class LeaderboardSummarySchema(Schema):
    top_performers: List[LeaderboardSchema]
    avg_score: Decimal
    participants_count: int
    # Trend data could be added here if needed, keeping it simple for now
