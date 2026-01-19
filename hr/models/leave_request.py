from django.db import models
from django.core.exceptions import ValidationError
from .base import BaseModel
from hr.utils.validators import validate_employee_id


class LeaveRequest(BaseModel):
    """Model for employee leave requests"""

    # Leave Type Choices
    LEAVE_TYPE_CHOICES = [
        ('sick_leave', 'Sick Leave'),
        ('annual_leave', 'Annual Leave'),
        ('casual_leave', 'Casual Leave'),
        ('maternity_leave', 'Maternity Leave'),
        ('paternity_leave', 'Paternity Leave'),
        ('unpaid_leave', 'Unpaid Leave'),
        ('compassionate_leave', 'Compassionate Leave'),
    ]

    # Status Choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    # Employee Information
    employee_id = models.CharField(max_length=50, db_index=True)

    # Leave Details
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    # Approval Information
    approver_id = models.CharField(max_length=50, blank=True, null=True)
    approval_date = models.DateField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'leave_requests'
        ordering = ['-created_at']
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'
        indexes = [
            models.Index(fields=['employee_id', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.leave_type} ({self.start_date} to {self.end_date})"

    @property
    def duration_days(self):
        """Calculate the number of days for the leave request"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def clean(self):
        """
        Validate cross-service references before saving.
        Called by full_clean() and save().
        """
        super().clean()

        # Validate employee_id
        if self.employee_id:
            try:
                validate_employee_id(self.employee_id)
            except ValidationError as e:
                raise ValidationError(e.message)
                
        # Validate approver_id (optional field)
        if self.approver_id:
            try:
                validate_employee_id(self.approver_id)
            except ValidationError as e:
                raise ValidationError(e.message)
                

        # Validate date logic
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({'end_date': 'End date cannot be before start date'})


    def save(self, *args, **kwargs):
        """
        Override save to ensure validation happens.
        """
        # Skip validation if explicitly requested (for data migrations, etc.)
        if not kwargs.pop('skip_validation', False):
            self.full_clean()

        super().save(*args, **kwargs)
