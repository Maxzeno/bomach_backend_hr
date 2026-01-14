from django.db import models
from .base import BaseModel


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
    location = models.CharField(max_length=255)
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

    def increment_applicants(self):
        """Increment the applicants count"""
        self.applicants_count += 1
        self.save(update_fields=['applicants_count'])

    def decrement_applicants(self):
        """Decrement the applicants count"""
        if self.applicants_count > 0:
            self.applicants_count -= 1
            self.save(update_fields=['applicants_count'])
