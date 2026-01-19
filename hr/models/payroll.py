from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal
from .base import BaseModel
from hr.utils.validators import validate_employee_id


class Payroll(BaseModel):
    """Model for employee payroll records"""

    # Status Choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    # Employee Information
    employee_id = models.CharField(max_length=50, db_index=True)

    # Payroll Details
    payroll_period = models.CharField(
        max_length=50,
        help_text="e.g., July 2025, Q1 2025, etc."
    )
    gross_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Allowances (stored as JSON)
    # Example: {"housing": 5000, "car": 3000, "transport": 1000, ...}
    allowances = models.JSONField(
        default=dict,
        blank=True,
        help_text="Allowances breakdown as key-value pairs"
    )

    # Deductions (stored as JSON)
    # Example: {"tax": 2000, "pension": 1500, "loan": 500}
    deductions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Deductions breakdown as key-value pairs"
    )

    # Calculated Salary
    net_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Payment Details
    disbursement_date = models.DateField()

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    class Meta:
        db_table = 'payroll'
        ordering = ['-disbursement_date', '-created_at']
        verbose_name = 'Payroll'
        verbose_name_plural = 'Payroll Records'
        indexes = [
            models.Index(fields=['employee_id', 'payroll_period']),
            models.Index(fields=['disbursement_date']),
            models.Index(fields=['status']),
        ]
        # Ensure one payroll record per employee per period
        unique_together = [['employee_id', 'payroll_period']]

    def __str__(self):
        return f"{self.payroll_period} (Net: {self.net_salary})"

    @property
    def total_allowances(self):
        """Calculate total allowances"""
        if not self.allowances:
            return Decimal('0.00')
        return Decimal(str(sum(float(v) for v in self.allowances.values() if v)))

    @property
    def total_deductions(self):
        """Calculate total deductions"""
        if not self.deductions:
            return Decimal('0.00')
        return Decimal(str(sum(float(v) for v in self.deductions.values() if v)))

    def calculate_net_salary(self):
        """Calculate net salary based on gross salary, allowances, and deductions"""
        total_allowances = self.total_allowances
        total_deductions = self.total_deductions
        return self.gross_salary + total_allowances - total_deductions

    def clean(self):
        super().clean()

        if self.employee_id:
            try:
                employee_info = validate_employee_id(self.employee_id)
            except ValidationError as e:
                raise ValidationError({'employee_id': e.message})

    def save(self, *args, **kwargs):
        """Override save to validate and auto-calculate net salary"""
        # Validate employee_id unless explicitly skipped
        if not kwargs.pop('skip_validation', False):
            self.full_clean()

        # Auto-calculate net salary before saving
        self.net_salary = self.calculate_net_salary()
        super().save(*args, **kwargs)
