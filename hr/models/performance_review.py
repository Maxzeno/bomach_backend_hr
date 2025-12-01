from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base import BaseModel


class PerformanceReview(BaseModel):
    """Model for employee performance reviews"""

    # Rating Choices (1-5 stars)
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    # Employee Information
    employee_id = models.CharField(max_length=50, db_index=True)
    employee_name = models.CharField(max_length=255)
    employee_email = models.EmailField(max_length=255, blank=True, null=True)

    # Reviewer Information
    reviewer_id = models.CharField(max_length=50, db_index=True)
    reviewer_name = models.CharField(max_length=255)

    # Review Details
    review_date = models.DateField()
    review_period = models.CharField(
        max_length=50,
        help_text="e.g., Q1 2025, H1 2025, 2025, etc."
    )

    # Rating and Feedback
    overall_rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    strengths = models.TextField(
        help_text="Employee's key strengths and accomplishments"
    )
    areas_for_improvement = models.TextField(
        help_text="Areas where the employee can improve"
    )
    feedback = models.TextField(
        blank=True,
        null=True,
        help_text="Additional feedback and comments"
    )

    # Additional fields
    goals_met = models.BooleanField(
        default=True,
        help_text="Whether the employee met their goals"
    )
    next_review_date = models.DateField(
        blank=True,
        null=True,
        help_text="Scheduled date for next review"
    )

    class Meta:
        db_table = 'performance_reviews'
        ordering = ['-review_date', '-created_at']
        verbose_name = 'Performance Review'
        verbose_name_plural = 'Performance Reviews'
        indexes = [
            models.Index(fields=['employee_id', 'review_date']),
            models.Index(fields=['reviewer_id', 'review_date']),
            models.Index(fields=['review_period']),
        ]
        # Ensure one review per employee per period
        unique_together = [['employee_id', 'review_period']]

    def __str__(self):
        return f"{self.employee_name} - {self.review_period} ({self.overall_rating} stars)"

    @property
    def rating_display(self):
        """Get the rating as a display string"""
        return f"{self.overall_rating} Star{'s' if self.overall_rating != 1 else ''}"
