from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from .base import BaseModel

class DailyWorkReport(BaseModel):
    """Model for tracking daily work reports from employees"""

    MOOD_CHOICES = [
        ('Happy', 'Happy'),
        ('Neutral', 'Neutral'),
        ('Sad', 'Sad'),
        ('Stressed', 'Stressed'),
        ('Tired', 'Tired'),
    ]

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    # Employee Information (Using CharFields as Employee model is missing/not confirmed)
    employee_name = models.CharField(max_length=255, db_index=True)
    employee_email = models.EmailField(max_length=255, db_index=True)

    # Report Details
    date = models.DateField(db_index=True)
    hours_worked = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0.0'))],
        default=Decimal('0.0'),
        help_text="Total hours worked for the day"
    )
    mood = models.CharField(
        max_length=20,
        choices=MOOD_CHOICES,
        default='Neutral'
    )
    
    # Content
    challenges = models.TextField(blank=True, null=True, help_text="Challenges faced today")
    achievements = models.TextField(blank=True, null=True, help_text="Accomplishments today")
    plan_next_day = models.TextField(blank=True, null=True, help_text="Plan for tomorrow")

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Draft',
        db_index=True
    )

    class Meta:
        db_table = 'daily_work_reports'
        ordering = ['-date', '-created_at']
        verbose_name = 'Daily Work Report'
        verbose_name_plural = 'Daily Work Reports'
        indexes = [
            models.Index(fields=['employee_email', 'date']),
            models.Index(fields=['status']),
        ]
        unique_together = ['employee_email', 'date']

    def __str__(self):
        return f"{self.employee_name} - {self.date}"
