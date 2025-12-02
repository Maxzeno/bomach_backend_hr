from django.db import models
from .base import BaseModel
from .associate import Associate

class Award(BaseModel):
    """Model for Awards and Recognition"""

    associate = models.ForeignKey(
        Associate,
        on_delete=models.CASCADE,
        related_name='awards',
        help_text="Associate receiving the award"
    )
    title = models.CharField(
        max_length=255,
        help_text="Title of the award (e.g., Employee of the Month)"
    )
    category = models.CharField(
        max_length=100,
        help_text="Category of the award (e.g., Monthly Recognition, Excellence)"
    )
    date_awarded = models.DateField(
        help_text="Date the award was given"
    )
    rank_level = models.CharField(
        max_length=100,
        help_text="Rank or level of the award (e.g., Enugu State, Headquarters)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description or reason for the award"
    )

    class Meta:
        db_table = 'awards'
        ordering = ['-date_awarded']
        verbose_name = 'Award'
        verbose_name_plural = 'Awards'
        indexes = [
            models.Index(fields=['date_awarded']),
            models.Index(fields=['associate', 'date_awarded']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.title} - {self.associate.full_name} ({self.date_awarded})"
