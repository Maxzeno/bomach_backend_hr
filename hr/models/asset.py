from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal
from .base import BaseModel
from hr.utils.validators import validate_employee_id, validate_department_id

class Asset(BaseModel):
    """Model for company assets"""

    ASSET_TYPE_CHOICES = [
        ('laptop', 'Laptop'),
        ('printer', 'Printer'),
        ('vehicle', 'Vehicle'),
        ('furniture', 'Furniture'),
        ('equipment', 'Equipment'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('in_use', 'In Use'),
        ('maintenance', 'Maintenance'),
        ('available', 'Available'),
        ('retired', 'Retired'),
        ('lost_stolen', 'Lost/Stolen'),
    ]

    name = models.CharField(max_length=255, help_text="Name of the asset")
    asset_type = models.CharField(
        max_length=50,
        choices=ASSET_TYPE_CHOICES,
        default='equipment'
    )
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)

    # Location & Assignment
    branch = models.CharField(
        max_length=100,
        help_text="Branch where the asset is located"
    )
    assigned_to_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_index=True,
        help_text="Employee ID from main auth service"
    )
    department_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="Department ID from department microservice"
    )

    # Financial Information
    purchase_date = models.DateField(blank=True, null=True)
    value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        blank=True,
        null=True
    )
    vendor = models.CharField(max_length=255, blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)

    # Status & Warranty
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='available',
        db_index=True
    )
    warranty_expiry_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    # Documents
    documents = models.URLField(
        blank=True,
        null=True,
        help_text="Upload invoice, warranty, manual, etc."
    )

    class Meta:
        db_table = 'assets'
        ordering = ['-created_at']
        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['asset_type']),
            models.Index(fields=['branch']),
            models.Index(fields=['assigned_to_id']),
        ]

    def __str__(self):
        return f"{self.name}"

    def clean(self):
        """
        Validate cross-service references before saving.
        """
        super().clean()
        errors = {}

        # Validate assigned_to_id (optional field)
        if self.assigned_to_id:
            try:
                employee_info = validate_employee_id(self.assigned_to_id)
            except ValidationError as e:
                errors['assigned_to_id'] = e.message

        # Validate department_id (optional field)
        if self.department_id:
            try:
                validate_department_id(self.department_id)
            except ValidationError as e:
                errors['department_id'] = e.message

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Validate unless explicitly skipped
        if not kwargs.pop('skip_validation', False):
            self.full_clean()

        super().save(*args, **kwargs)
