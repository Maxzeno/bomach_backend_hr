from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.core.validators import MinValueValidator
from .base import BaseModel
from hr.utils.validators import validate_employee_id
from django.core.validators import MinValueValidator, MaxValueValidator

class DailyWorkReport(BaseModel):
    """Model for tracking daily work reports from employees"""

    MOOD_CHOICES = [
        ('Happy', 'Happy'),
        ('Neutral', 'Neutral'),
        ('Sad', 'Sad'),
        ('Stressed', 'Stressed'),
        ('Tired', 'Tired'),
        ('Frustrated', 'Frustrated'),
    ]

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    # Employee Information (employee_id references main backend Employee)
    employee_id = models.CharField(max_length=50, db_index=True, default='', help_text="Employee ID from main backend")

    # Report Details
    day = models.DateField(db_index=True)
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

    rating = models.DecimalField(
        max_digits=1,
        decimal_places=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    feedback = models.TextField(blank=True, null=True, help_text="Feedback")


    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Draft',
        db_index=True
    )

    class Meta:
        db_table = 'daily_work_reports'
        ordering = ['-day', '-created_at']
        verbose_name = 'Daily Work Report'
        verbose_name_plural = 'Daily Work Reports'
        indexes = [
            models.Index(fields=['employee_id', 'day']),
            models.Index(fields=['status']),
        ]
        unique_together = ['employee_id', 'day']

    def __str__(self):
        return f"{self.employee_id} - {self.day}"

    def clean(self):
        """
        Validate cross-service references before saving.
        """
        super().clean()
        errors = {}

        # Validate employee_id
        if self.employee_id:
            try:
                employee_info = validate_employee_id(self.employee_id)                
            except ValidationError as e:
                errors['employee_id'] = e.message

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Override save to ensure validation happens.
        """
        if not kwargs.pop('skip_validation', False):
            self.full_clean()

        super().save(*args, **kwargs)
