from django.contrib import admin
from .models import (
    JobPosting, Applicant, LeaveRequest,
    PerformanceReview, Payroll, TrainingProgram, Associate, Asset,
    DailyWorkReport, Scorecard, Award, PerformanceLeaderboard
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
        'application_id',
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
    search_fields = ['application_id', 'first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['application_id', 'created_at', 'updated_at']
    list_editable = ['stage', 'status', 'rating']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['job_posting']

    fieldsets = (
        ('Application Info', {
            'fields': ('application_id', 'job_posting')
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
        'employee_name',
        'leave_type',
        'start_date',
        'end_date',
        'status',
        'duration_days',
        'created_at',
    ]
    list_filter = ['status', 'leave_type', 'start_date', 'created_at']
    search_fields = ['employee_id', 'employee_name', 'employee_email', 'reason']
    readonly_fields = ['created_at', 'updated_at', 'duration_days']
    list_editable = ['status']
    ordering = ['-created_at']
    date_hierarchy = 'start_date'

    fieldsets = (
        ('Employee Information', {
            'fields': ('employee_id', 'employee_name', 'employee_email')
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
        'employee_name',
        'reviewer_name',
        'review_period',
        'overall_rating',
        'review_date',
        'goals_met',
        'created_at',
    ]
    list_filter = ['overall_rating', 'goals_met', 'review_date', 'review_period', 'created_at']
    search_fields = ['employee_id', 'employee_name', 'employee_email', 'reviewer_id', 'reviewer_name']
    readonly_fields = ['created_at', 'updated_at', 'rating_display']
    list_editable = ['goals_met']
    ordering = ['-review_date', '-created_at']
    date_hierarchy = 'review_date'

    fieldsets = (
        ('Employee Information', {
            'fields': ('employee_id', 'employee_name', 'employee_email')
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
        'employee_name',
        'payroll_period',
        'gross_salary',
        'net_salary',
        'disbursement_date',
        'status',
        'created_at',
    ]
    list_filter = ['status', 'payroll_period', 'disbursement_date', 'created_at']
    search_fields = ['employee_id', 'employee_name', 'employee_email']
    readonly_fields = ['created_at', 'updated_at', 'total_allowances', 'total_deductions', 'net_salary']
    list_editable = ['status']
    ordering = ['-disbursement_date', '-created_at']
    date_hierarchy = 'disbursement_date'

    fieldsets = (
        ('Employee Information', {
            'fields': ('employee_id', 'employee_name', 'employee_email')
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


@admin.register(Associate)
class AssociateAdmin(admin.ModelAdmin):
    list_display = [
        'associate_id',
        'full_name',
        'email',
        'role_position',
        'company_name',
        'phone_number',
        'contract_period',
        'status',
        'is_contract_active',
        'created_at',
    ]
    list_filter = ['status', 'role_position', 'company_name', 'contract_start_date', 'created_at']
    search_fields = ['associate_id', 'full_name', 'email', 'company_name', 'phone_number', 'role_position', 'department_id']
    readonly_fields = ['associate_id', 'created_at', 'updated_at', 'contract_period', 'contract_duration_days', 'is_contract_active', 'is_contract_expired']
    list_editable = ['status']
    ordering = ['-created_at']
    date_hierarchy = 'contract_start_date'

    fieldsets = (
        ('Associate ID', {
            'fields': ('associate_id',)
        }),
        ('Personal Information', {
            'fields': ('full_name', 'email', 'phone_number', 'address')
        }),
        ('Professional Information', {
            'fields': ('company_name', 'role_position', 'department_id', 'specialization')
        }),
        ('Contract Information', {
            'fields': (
                'contract_start_date',
                'contract_end_date',
                'contract_period',
                'contract_duration_days',
                'contract_value',
                'payment_terms',
                'supervisor_point_of_contact',
                'scope_of_work'
            )
        }),
        ('Documents', {
            'fields': ('documents',)
        }),
        ('Status', {
            'fields': ('status', 'is_contract_active', 'is_contract_expired')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = [
        'asset_id',
        'name',
        'asset_type',
        'branch',
        'status',
        'assigned_to_name',
        'value',
        'created_at',
    ]
    list_filter = ['status', 'asset_type', 'branch', 'created_at']
    search_fields = ['asset_id', 'name', 'serial_number', 'assigned_to_name']
    readonly_fields = ['asset_id', 'created_at', 'updated_at']
    list_editable = ['status']
    ordering = ['-created_at']


@admin.register(DailyWorkReport)
class DailyWorkReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee_name', 'employee_email', 'date', 'hours_worked', 'mood', 'status', 'created_at']
    list_filter = ['status', 'mood', 'date', 'created_at']
    search_fields = ['employee_name', 'employee_email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date', '-created_at']
    list_editable = ['status']


@admin.register(Scorecard)
class ScorecardAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'associate',
        'month',
        'overall_score',
        'target_achievement',
        'branch_ranking',
        'created_at',
    ]
    list_filter = ['month', 'created_at']
    search_fields = ['associate__full_name', 'associate__associate_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-month']
    autocomplete_fields = ['associate']


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'associate',
        'title',
        'category',
        'date_awarded',
        'rank_level',
        'created_at',
    ]
    list_filter = ['category', 'rank_level', 'date_awarded', 'created_at']
    search_fields = ['associate__full_name', 'associate__associate_id', 'title']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date_awarded']
    autocomplete_fields = ['associate']


@admin.register(PerformanceLeaderboard)
class PerformanceLeaderboardAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'associate',
        'month',
        'score',
        'rank',
        'created_at',
    ]
    list_filter = ['month', 'created_at']
    search_fields = ['associate__full_name', 'associate__associate_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-month', 'rank']
    autocomplete_fields = ['associate']
