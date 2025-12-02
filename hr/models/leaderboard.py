from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from .base import BaseModel
from .associate import Associate

class PerformanceLeaderboard(BaseModel):
    """Model for Monthly Performance Leaderboard"""

    associate = models.ForeignKey(
        Associate,
        on_delete=models.CASCADE,
        related_name='leaderboard_entries',
        help_text="Associate in the leaderboard"
    )
    month = models.DateField(
        help_text="The month this ranking represents (stored as first day of month)"
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Performance score for the month"
    )
    rank = models.IntegerField(
        help_text="Rank position in the leaderboard"
    )
    status = models.CharField(
        max_length=100,
        help_text="Performance status label (e.g., Rising Star, Consistent Performer)"
    )
    awards_summary = models.TextField(
        blank=True,
        null=True,
        help_text="Snapshot of awards received this month"
    )

    class Meta:
        db_table = 'performance_leaderboard'
        ordering = ['-month', 'rank']
        verbose_name = 'Performance Leaderboard Entry'
        verbose_name_plural = 'Performance Leaderboard Entries'
        unique_together = ['associate', 'month']
        indexes = [
            models.Index(fields=['month']),
            models.Index(fields=['month', 'rank']),
        ]

    def __str__(self):
        return f"#{self.rank} {self.associate.full_name} - {self.month.strftime('%B %Y')}"
