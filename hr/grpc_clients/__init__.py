"""
gRPC Clients for HR Service

This module provides singleton instances of gRPC clients for communicating
with the main backend services.

Usage:
    from hr.grpc_clients import auth_client, department_client

    # Validate an employee
    result = auth_client.validate_employee('EMP-001')

    # Validate a department
    result = department_client.validate_department('123')
"""

from .auth_client import AuthClient
from .department_client import DepartmentClient

# Singleton instances
auth_client = AuthClient()
department_client = DepartmentClient()

__all__ = ['auth_client', 'department_client', 'AuthClient', 'DepartmentClient']
