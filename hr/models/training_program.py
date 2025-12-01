from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .base import BaseModel


class TrainingProgram(BaseModel):
    """Model for employee training programs"""

    # Status Choices
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    # Target Audience Choices
    TARGET_AUDIENCE_CHOICES = [
        ('All Employees', 'All Employees'),
        ('Management', 'Management'),
        ('New Hires', 'New Hires'),
        ('Department Specific', 'Department Specific'),
        ('Leadership Team', 'Leadership Team'),
        ('Technical Staff', 'Technical Staff'),
        ('Sales Team', 'Sales Team'),
        ('Customer Service', 'Customer Service'),
    ]

    # Program Details
    program_name = models.CharField(max_length=255, db_index=True)
    provider = models.CharField(
        max_length=255,
        help_text="Training provider or organization"
    )
    description = models.TextField(
        help_text="Detailed description of the training program"
    )

    # Dates
    start_date = models.DateField()
    end_date = models.DateField()

    # Financial
    cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cost of the training program"
    )

    # Target Audience
    target_audience = models.CharField(
        max_length=100,
        choices=TARGET_AUDIENCE_CHOICES,
        default='All Employees'
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        db_index=True
    )

    class Meta:
        db_table = 'training_programs'
        ordering = ['-start_date', '-created_at']
        verbose_name = 'Training Program'
        verbose_name_plural = 'Training Programs'
        indexes = [
            models.Index(fields=['program_name', 'start_date']),
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['target_audience']),
        ]

    def __str__(self):
        return f"{self.program_name} - {self.start_date} to {self.end_date}"

    @property
    def duration_days(self):
        """Calculate the duration of the training program in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    @property
    def is_ongoing(self):
        """Check if the training program is currently ongoing"""
        from datetime import date
        today = date.today()
        return self.start_date <= today <= self.end_date and self.status == 'In Progress'

    @property
    def is_upcoming(self):
        """Check if the training program is upcoming"""
        from datetime import date
        today = date.today()
        return self.start_date > today and self.status == 'Pending'
