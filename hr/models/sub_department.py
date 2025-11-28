from django.db import models
from .base import BaseModel
from .department import Department


class SubDepartment(BaseModel):
    """
    Model for managing sub-departments under main departments.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='sub_departments'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'sub_departments'
        ordering = ['department', 'name']
        verbose_name = 'Sub-Department'
        verbose_name_plural = 'Sub-Departments'
        unique_together = [['name', 'department']]

    def __str__(self):
        return f"{self.department.name} - {self.name}"

    def get_hierarchy_path(self):
        """Get the full hierarchy path of the sub-department"""
        return f"{self.department.name} > {self.name}"
