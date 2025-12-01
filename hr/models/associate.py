from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .base import BaseModel
from .department import Department


class Associate(BaseModel):
    """Model for external associates and contractors"""

    # Status Choices
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Pending', 'Pending'),
        ('Expired', 'Expired'),
        ('Terminated', 'Terminated'),
    ]

    # Payment Terms Choices
    PAYMENT_TERMS_CHOICES = [
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Milestone-based', 'Milestone-based'),
        ('One-time', 'One-time'),
        ('Hourly', 'Hourly'),
        ('Project-based', 'Project-based'),
    ]

    # Role/Position Choices
    ROLE_CHOICES = [
        ('IT Consultant', 'IT Consultant'),
        ('UX Designer', 'UX Designer'),
        ('Legal Advisor', 'Legal Advisor'),
        ('Marketing Specialist', 'Marketing Specialist'),
        ('Financial Analyst', 'Financial Analyst'),
        ('HR Consultant', 'HR Consultant'),
        ('Software Developer', 'Software Developer'),
        ('Project Manager', 'Project Manager'),
        ('Security Consultant', 'Security Consultant'),
        ('Business Analyst', 'Business Analyst'),
        ('Data Analyst', 'Data Analyst'),
        ('Content Writer', 'Content Writer'),
        ('Graphic Designer', 'Graphic Designer'),
        ('Other', 'Other'),
    ]

    # Associate ID (auto-generated)
    associate_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Auto-generated associate ID (e.g., ASC-001)"
    )

    # Personal Information
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, db_index=True)
    phone_number = models.CharField(max_length=50)
    address = models.TextField(blank=True, null=True)

    # Professional Information
    company_name = models.CharField(max_length=255, db_index=True)
    role_position = models.CharField(
        max_length=100,
        choices=ROLE_CHOICES,
        default='Other'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='associates',
        help_text="Associated department"
    )
    specialization = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Area of specialization or expertise"
    )

    # Contract Information
    contract_start_date = models.DateField()
    contract_end_date = models.DateField()
    contract_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        blank=True,
        null=True,
        help_text="Total value of the contract"
    )
    payment_terms = models.CharField(
        max_length=50,
        choices=PAYMENT_TERMS_CHOICES,
        default='Monthly'
    )
    supervisor_point_of_contact = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Internal supervisor or point of contact"
    )
    scope_of_work = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of work scope"
    )

    # Documents
    documents = models.FileField(
        upload_to='associates/documents/',
        blank=True,
        null=True,
        help_text="Upload contract, resume, or relevant documents"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        db_index=True
    )

    class Meta:
        db_table = 'associates'
        ordering = ['-created_at']
        verbose_name = 'Associate'
        verbose_name_plural = 'Associates'
        indexes = [
            models.Index(fields=['associate_id']),
            models.Index(fields=['email', 'status']),
            models.Index(fields=['company_name', 'role_position']),
            models.Index(fields=['contract_start_date', 'contract_end_date']),
        ]

    def __str__(self):
        return f"{self.associate_id} - {self.full_name} ({self.company_name})"

    def save(self, *args, **kwargs):
        """Override save to auto-generate associate_id"""
        if not self.associate_id:
            # Get the last associate ID
            last_associate = Associate.objects.order_by('-id').first()
            if last_associate and last_associate.associate_id:
                # Extract number from last ID (e.g., ASC-001 -> 001)
                try:
                    last_number = int(last_associate.associate_id.split('-')[1])
                    new_number = last_number + 1
                except (IndexError, ValueError):
                    new_number = 1
            else:
                new_number = 1

            # Format as ASC-001, ASC-002, etc.
            self.associate_id = f"ASC-{new_number:03d}"

        super().save(*args, **kwargs)

    @property
    def contract_period(self):
        """Return formatted contract period"""
        start = self.contract_start_date.strftime('%b %Y')
        end = self.contract_end_date.strftime('%b %Y')
        return f"{start} to {end}"

    @property
    def contract_duration_days(self):
        """Calculate contract duration in days"""
        if self.contract_start_date and self.contract_end_date:
            return (self.contract_end_date - self.contract_start_date).days + 1
        return 0

    @property
    def is_contract_active(self):
        """Check if contract is currently active"""
        from datetime import date
        today = date.today()
        return (
            self.contract_start_date <= today <= self.contract_end_date
            and self.status == 'Active'
        )

    @property
    def is_contract_expired(self):
        """Check if contract has expired"""
        from datetime import date
        today = date.today()
        return self.contract_end_date < today
