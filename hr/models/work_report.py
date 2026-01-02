from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.core.validators import MinValueValidator
from .base import BaseModel
from hr.utils.validators import validate_employee_id

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

    # Employee Information (employee_id references main backend Employee)
    employee_id = models.CharField(max_length=50, db_index=True, default='', help_text="Employee ID from main backend")
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
            models.Index(fields=['employee_id', 'date']),
            models.Index(fields=['employee_email', 'date']),
            models.Index(fields=['status']),
        ]
        unique_together = ['employee_id', 'date']

    def __str__(self):
        return f"{self.employee_name} - {self.date}"

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
                # Update cached fields with validated data
                if employee_info:
                    self.employee_name = employee_info.get('full_name', self.employee_name)
                    self.employee_email = employee_info.get('email', self.employee_email)
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
