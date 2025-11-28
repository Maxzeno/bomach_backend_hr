from django.contrib import admin
from .models import Department, SubDepartment, JobPosting


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
