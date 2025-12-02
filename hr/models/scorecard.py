from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from .base import BaseModel
from .associate import Associate

class Scorecard(BaseModel):
    """Model for Monthly Scorecard"""

    associate = models.ForeignKey(
        Associate,
        on_delete=models.CASCADE,
        related_name='scorecards',
        help_text="Associate this scorecard belongs to"
    )
    month = models.DateField(
        help_text="The month this scorecard represents (stored as first day of month)"
    )
    
    # Overall Metrics
    overall_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Overall score out of 100"
    )
    target_achievement = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Target achievement percentage"
    )
    branch_ranking = models.IntegerField(
        help_text="Ranking within the branch for the month"
    )
    skill_update_progress = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Skill update progress percentage"
    )

    # Performance Metrics
    attendance_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Attendance score percentage"
    )
    task_delivery_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Task delivery score percentage"
    )
    report_accuracy_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Report accuracy score percentage"
    )
    brand_contribution_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Brand contribution score percentage"
    )
    training_progress_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Training progress score percentage"
    )

    class Meta:
        db_table = 'scorecards'
        ordering = ['-month', '-overall_score']
        verbose_name = 'Scorecard'
        verbose_name_plural = 'Scorecards'
        unique_together = ['associate', 'month']
        indexes = [
            models.Index(fields=['month']),
            models.Index(fields=['associate', 'month']),
        ]

    def __str__(self):
        return f"{self.associate.full_name} - {self.month.strftime('%B %Y')}"
