from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from hr.utils.validators import validate_employee_id


class DisciplinaryCase(models.Model):
    """
    Core model representing disciplinary actions taken against employees
    """
    
    # Action Type Choices
    VERBAL_WARNING = 'Verbal Warning'
    WRITTEN_WARNING = 'Written Warning'
    FINAL_WARNING = 'Final Warning'
    SUSPENSION = 'Suspension'
    TERMINATION = 'Termination'
    DEMOTION = 'Demotion'
    
    ACTION_TYPE_CHOICES = [
        (VERBAL_WARNING, 'Verbal Warning'),
        (WRITTEN_WARNING, 'Written Warning'),
        (SUSPENSION, 'Suspension'),
        (TERMINATION, 'Termination'),
        (FINAL_WARNING, 'Final Warning'),
        (DEMOTION, 'Demotion'),
    ]
    
    # Violation Category Choices
    ATTENDANCE_ISSUES = 'Attendance Issues'
    MISCONDUCT = 'Misconduct'
    POOR_PERFORMANCE = 'Poor Performance'
    INSUBORDINATION = 'Insubordination'
    DISHONESTY = 'Dishonesty'
    SAFETY_VIOLATION = 'Safety Violation'
    CONFIDENTIALITY_BREACH = 'Confidentiality Breach'
    HARASSMENT_DISCRIMINATION = 'Harassment/Discrimination'
    OTHER = 'Other'
    
    VIOLATION_CATEGORY_CHOICES = [
        (ATTENDANCE_ISSUES, 'Attendance Issues'),
        (MISCONDUCT, 'Misconduct'),
        (POOR_PERFORMANCE, 'Poor Performance'),
        (INSUBORDINATION, 'Insubordination'),
        (DISHONESTY, 'Dishonesty'),
        (SAFETY_VIOLATION, 'Safety Violation'),
        (CONFIDENTIALITY_BREACH, 'Confidentiality Breach'),
        (HARASSMENT_DISCRIMINATION, 'Harassment/Discrimination'),
        (OTHER, 'Other'),
    ]
    
    # Fields
    employee_id = models.CharField(
        max_length=100,
        help_text="Employee ID or identifier"
    )
    
    employee_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Employee full name"
    )
    
    action_type = models.CharField(
        max_length=50,
        choices=ACTION_TYPE_CHOICES,
        help_text="Type of disciplinary action"
    )
    
    violation_category = models.CharField(
        max_length=100,
        choices=VIOLATION_CATEGORY_CHOICES,
        help_text="Category of violation"
    )
    
    violation_title = models.CharField(
        max_length=255,
        help_text="Brief title of the violation"
    )
    
    violation_description = models.TextField(
        help_text="Detailed description of the violation"
    )
    
    date_of_violation = models.DateField(
        help_text="Date when the violation occurred"
    )
    
    action_date = models.DateField(
        default=timezone.now,
        help_text="Date when the action was taken"
    )
    
    investigation_details = models.TextField(
        blank=True,
        null=True,
        help_text="Optional investigation details"
    )
    
    severance_payment_due = models.BooleanField(
        default=False,
        help_text="Whether severance payment is due"
    )
    
    severance_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Severance payment amount if applicable"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'disciplinary_cases'
        ordering = ['-date_of_violation', '-created_at']
        verbose_name = 'Disciplinary Case'
        verbose_name_plural = 'Disciplinary Cases'
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['action_type']),
            models.Index(fields=['date_of_violation']),
            models.Index(fields=['action_date']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.employee_id} - {self.action_type} - {self.date_of_violation}"

    def clean(self):
        """Validate the model data"""
        from django.core.exceptions import ValidationError

        # Validate employee_id
        if self.employee_id:
            try:
                validate_employee_id(self.employee_id)
            except ValidationError as e:
                raise ValidationError({'employee_id': e.message})

        # Ensure date_of_violation is not in the future
        if self.date_of_violation and self.date_of_violation > timezone.now().date():
            raise ValidationError({
                'date_of_violation': 'Date of violation cannot be in the future.'
            })
        
        # Ensure action_date is on or after date_of_violation
        if self.date_of_violation and self.action_date and self.action_date < self.date_of_violation:
            raise ValidationError({
                'action_date': 'Action date cannot be before the violation date.'
            })
        
        # Validate severance amount if severance payment is due
        if self.severance_payment_due and not self.severance_amount:
            raise ValidationError({
                'severance_amount': 'Severance amount is required when severance payment is due.'
            })
        
        # Ensure severance amount is only set when severance_payment_due is True
        if self.severance_amount and not self.severance_payment_due:
            raise ValidationError({
                'severance_payment_due': 'Severance payment due must be checked when amount is specified.'
            })

    def save(self, *args, **kwargs):
        """Override save to perform validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def days_since_violation(self):
        """Calculate days since violation occurred"""
        if self.date_of_violation:
            return (timezone.now().date() - self.date_of_violation).days
        return None

    @property
    def is_severance_applicable(self):
        """Check if severance is applicable"""
        return self.severance_payment_due and self.severance_amount is not None
    
    @property
    def action_type_color(self):
        """Get color code for action type"""
        color_map = {
            self.VERBAL_WARNING: '#6B9BD1',      # Blue
            self.WRITTEN_WARNING: '#F5A623',     # Yellow
            self.FINAL_WARNING: '#F58220',       # Orange
            self.SUSPENSION: '#F58220',          # Orange
            self.TERMINATION: '#D0021B',         # Red
            self.DEMOTION: '#FF9800',            # Orange
        }
        return color_map.get(self.action_type, '#6B9BD1')
    

    def get_severity_level(self):
        """Get severity level for the action type"""
        severity_map = {
            self.VERBAL_WARNING: 1,
            self.WRITTEN_WARNING: 2,
            self.FINAL_WARNING: 3,
            self.DEMOTION: 4,
            self.SUSPENSION: 4,
            self.TERMINATION: 5,
        }
        return severity_map.get(self.action_type, 0)