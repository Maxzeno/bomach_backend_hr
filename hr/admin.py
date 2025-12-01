from django.contrib import admin
from .models import Department, SubDepartment, JobPosting, Applicant, LeaveRequest


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']
    ordering = ['name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SubDepartment)
class SubDepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'is_active', 'created_at']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['name', 'description', 'department__name']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']
    ordering = ['department', 'name']
    autocomplete_fields = ['department']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'department', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = [
        'job_title',
        'department',
        'location',
        'job_type',
        'status',
        'applicants_count',
        'is_active',
        'created_at',
    ]
    list_filter = ['status', 'job_type', 'department', 'location', 'is_active', 'created_at']
    search_fields = ['job_title', 'department', 'location', 'description']
    readonly_fields = ['created_at', 'updated_at', 'applicants_count']
    list_editable = ['status', 'is_active']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('job_title', 'department', 'location', 'job_type', 'status', 'is_active')
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
