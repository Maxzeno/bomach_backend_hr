from django.contrib import admin
from .models import (
    JobPosting, Applicant, LeaveRequest,
    PerformanceReview, Payroll, TrainingProgram, Asset,
    DailyWorkReport, Award
)


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = [
        'job_title',
        'department_id',
        'branch_id',
        'job_type',
        'status',
        'applicants_count',
        'is_active',
        'created_at',
    ]
    list_filter = ['status', 'job_type', 'branch_id', 'is_active', 'created_at']
    search_fields = ['job_title', 'department_id', 'branch_id', 'description']
    readonly_fields = ['created_at', 'updated_at', 'applicants_count']
    list_editable = ['status', 'is_active']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('job_title', 'department_id', 'branch_id', 'job_type', 'status', 'is_active')
        }),
        ('Job Details', {
            'fields': ('description', 'requirements', 'responsibilities', 'salary_range', 'deadline')
        }),
        ('Statistics', {
            'fields': ('applicants_count',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'email',
        'phone',
        'job_posting',
        'rating',
        'stage',
        'status',
        'created_at',
    ]
    list_filter = ['stage', 'status', 'job_posting', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['stage', 'status', 'rating']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['job_posting']

    fieldsets = (
        ('Application Info', {
            'fields': ('job_posting',)
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Application Status', {
            'fields': ('stage', 'status', 'rating')
        }),
        ('Documents & Notes', {
            'fields': ('resume', 'cover_letter', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id',
        'leave_type',
        'start_date',
        'end_date',
        'status',
        'duration_days',
        'created_at',
    ]
    list_filter = ['status', 'leave_type', 'start_date', 'created_at']
    search_fields = ['employee_id', 'reason']
    readonly_fields = ['created_at', 'updated_at', 'duration_days']
    list_editable = ['status']
    ordering = ['-created_at']
    date_hierarchy = 'start_date'

    fieldsets = (
        ('Employee Information', {
            'fields': ('employee_id',)
        }),
        ('Leave Details', {
            'fields': ('leave_type', 'start_date', 'end_date', 'reason', 'duration_days')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Approval Information', {
            'fields': ('approver_id', 'approval_date', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id',
        'review_period',
        'overall_rating',
        'review_date',
        'created_at',
    ]
    list_filter = ['overall_rating', 'review_date', 'review_period', 'created_at']
    search_fields = ['employee_id', 'reviewer_id']
    readonly_fields = ['created_at', 'updated_at', 'rating_display']
    list_editable = []
    ordering = ['-review_date', '-created_at']
    date_hierarchy = 'review_date'

    fieldsets = (
        ('Employee Information', {
            'fields': ('employee_id',)
        }),
        ('Reviewer Information', {
            'fields': ('reviewer_id', 'reviewer_name')
        }),
        ('Review Details', {
            'fields': ('review_date', 'review_period', 'next_review_date')
        }),
        ('Rating & Feedback', {
            'fields': ('overall_rating', 'rating_display', 'goals_met', 'strengths', 'areas_for_improvement', 'feedback')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id',
        'payroll_period',
        'gross_salary',
        'net_salary',
        'disbursement_date',
        'status',
        'created_at',
    ]
    list_filter = ['status', 'payroll_period', 'disbursement_date', 'created_at']
    search_fields = ['employee_id']
    readonly_fields = ['created_at', 'updated_at', 'total_allowances', 'total_deductions', 'net_salary']
    list_editable = ['status']
    ordering = ['-disbursement_date', '-created_at']
    date_hierarchy = 'disbursement_date'

    fieldsets = (
        ('Employee Information', {
            'fields': ('employee_id',)
        }),
        ('Payroll Details', {
            'fields': ('payroll_period', 'gross_salary', 'disbursement_date', 'status')
        }),
        ('Allowances & Deductions', {
            'fields': ('allowances', 'total_allowances', 'deductions', 'total_deductions')
        }),
        ('Calculated Salary', {
            'fields': ('net_salary',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = [
        'program_name',
        'provider',
        'start_date',
        'end_date',
        'duration_days',
        'cost',
        'target_audience',
        'status',
        'is_ongoing',
        'created_at',
    ]
    list_filter = ['status', 'target_audience', 'start_date', 'end_date', 'created_at']
    search_fields = ['program_name', 'provider', 'description']
    readonly_fields = ['created_at', 'updated_at', 'duration_days', 'is_ongoing', 'is_upcoming']
    list_editable = ['status']
    ordering = ['-start_date', '-created_at']
    date_hierarchy = 'start_date'

    fieldsets = (
        ('Program Information', {
            'fields': ('program_name', 'provider', 'description')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'duration_days')
        }),
        ('Details', {
            'fields': ('cost', 'target_audience', 'status')
        }),
        ('Computed Fields', {
            'fields': ('is_ongoing', 'is_upcoming'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'asset_type',
        'branch',
        'status',
        'value',
        'created_at',
    ]
    list_filter = ['status', 'asset_type', 'branch', 'created_at']
    search_fields = ['name', 'serial_number']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    ordering = ['-created_at']


@admin.register(DailyWorkReport)
class DailyWorkReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'day', 'hours_worked', 'mood', 'status', 'created_at']
    list_filter = ['status', 'mood', 'day', 'created_at']
    search_fields = []
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-day', '-created_at']
    list_editable = ['status']

@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title',
        'category',
        'date_awarded',
        'rank_level',
        'created_at',
    ]
    list_filter = ['category', 'rank_level', 'date_awarded', 'created_at']
    search_fields = ['title']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date_awarded']
    autocomplete_fields = []
