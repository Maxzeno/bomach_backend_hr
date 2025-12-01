from django.db import models
from .base import BaseModel


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
