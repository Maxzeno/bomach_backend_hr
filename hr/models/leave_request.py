from django.db import models
from django.core.exceptions import ValidationError
from .base import BaseModel
from hr.utils.validators import validate_employee_id


class LeaveRequest(BaseModel):
    """Model for employee leave requests"""

    # Leave Type Choices
    LEAVE_TYPE_CHOICES = [
        ('Sick Leave', 'Sick Leave'),
        ('Annual Leave', 'Annual Leave'),
        ('Casual Leave', 'Casual Leave'),
        ('Maternity Leave', 'Maternity Leave'),
        ('Paternity Leave', 'Paternity Leave'),
        ('Unpaid Leave', 'Unpaid Leave'),
        ('Compassionate Leave', 'Compassionate Leave'),
    ]

    # Status Choices
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    ]

    # Employee Information
    employee_id = models.CharField(max_length=50, db_index=True)
    employee_name = models.CharField(max_length=255)
    employee_email = models.EmailField(max_length=255, blank=True, null=True)

    # Leave Details
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
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
        return f"{self.employee_name} - {self.leave_type} ({self.start_date} to {self.end_date})"

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

        # Validate approver_id (optional field)
        if self.approver_id:
            try:
                validate_employee_id(self.approver_id)
            except ValidationError as e:
                errors['approver_id'] = e.message

        # Validate date logic
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                errors['end_date'] = "End date cannot be before start date"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Override save to ensure validation happens.
        """
        # Skip validation if explicitly requested (for data migrations, etc.)
        if not kwargs.pop('skip_validation', False):
            self.full_clean()

        super().save(*args, **kwargs)
