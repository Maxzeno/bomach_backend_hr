from django.db import models
from django.core.exceptions import ValidationError
from .base import BaseModel
from hr.utils.validators import validate_department_id, validate_branch_id


class JobPosting(BaseModel):
    """
    Model for managing job postings in the HR system.
    """

    class JobType(models.TextChoices):
        FULL_TIME = 'Full-Time', 'Full-Time'
        PART_TIME = 'Part-Time', 'Part-Time'
        CONTRACT = 'Contract', 'Contract'
        INTERNSHIP = 'Internship', 'Internship'
        TEMPORARY = 'Temporary', 'Temporary'

    class Status(models.TextChoices):
        DRAFT = 'Draft', 'Draft'
        PENDING = 'Pending', 'Pending'
        ACTIVE = 'Active', 'Active'
        CLOSED = 'Closed', 'Closed'
        CANCELLED = 'Cancelled', 'Cancelled'

    job_title = models.CharField(max_length=255)
    department_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="Department ID from department microservice"
    )
    branch_id = models.CharField(max_length=255)
    job_type = models.CharField(
        max_length=50,
        choices=JobType.choices,
        default=JobType.FULL_TIME
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.DRAFT
    )
    description = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    applicants_count = models.IntegerField(default=0)
    deadline = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'job_postings'
        ordering = ['-created_at']
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'

    def __str__(self):
        return f"{self.job_title} - {self.department_id}"

    def clean(self):
        """Validate cross-service references before saving."""
        super().clean()
        errors = {}

        # Validate department_id (optional field)
        if self.department_id:
            try:
                validate_department_id(self.department_id)
            except ValidationError as e:
                errors['department_id'] = e.message

        # Validate branch_id (required field)
        if self.branch_id:
            try:
                validate_branch_id(self.branch_id)
            except ValidationError as e:
                errors['branch_id'] = e.message

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Override save to ensure validation happens."""
        if not kwargs.pop('skip_validation', False):
            self.full_clean()
        super().save(*args, **kwargs)

    def increment_applicants(self):
        """Increment the applicants count"""
        self.applicants_count += 1
        self.save(update_fields=['applicants_count'])

    def decrement_applicants(self):
        """Decrement the applicants count"""
        if self.applicants_count > 0:
            self.applicants_count -= 1
            self.save(update_fields=['applicants_count'])
