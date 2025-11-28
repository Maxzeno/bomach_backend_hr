from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base import BaseModel
from .job_posting import JobPosting
import random
import string


class Applicant(BaseModel):
    """
    Model for managing job applicants.
    """

    class Stage(models.TextChoices):
        APPLIED = 'Applied', 'Applied'
        SCREENING = 'Screening', 'Screening'
        INTERVIEW = 'Interview', 'Interview'
        OFFERED = 'Offered', 'Offered'
        REJECTED = 'Rejected', 'Rejected'

    class Status(models.TextChoices):
        NEW = 'New', 'New'
        IN_REVIEW = 'In Review', 'In Review'
        SHORTLISTED = 'Shortlisted', 'Shortlisted'
        HIRED = 'Hired', 'Hired'
        REJECTED = 'Rejected', 'Rejected'

    application_id = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    job_posting = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='applicants'
    )
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        default=0.0
    )
    stage = models.CharField(
        max_length=50,
        choices=Stage.choices,
        default=Stage.APPLIED
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.NEW
    )
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'applicants'
        ordering = ['-created_at']
        verbose_name = 'Applicant'
        verbose_name_plural = 'Applicants'
        indexes = [
            models.Index(fields=['application_id']),
            models.Index(fields=['email']),
            models.Index(fields=['stage']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.job_posting.job_title}"

    def save(self, *args, **kwargs):
        # Generate application_id if not exists
        if not self.application_id:
            self.application_id = self.generate_application_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_application_id():
        """Generate a unique application ID like K987KD"""
        while True:
            # Generate 6 character alphanumeric ID
            app_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Applicant.objects.filter(application_id=app_id).exists():
                return app_id

    @property
    def full_name(self):
        """Return full name of applicant"""
        return f"{self.first_name} {self.last_name}"
