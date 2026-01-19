"""
Department gRPC Client

This module provides a client for communicating with the Department gRPC server
in the main backend to validate departments and sub-departments.
"""

import logging
import grpc
from typing import Dict, Optional, List
from django.conf import settings

from . import department_service_pb2
from . import department_service_pb2_grpc

logger = logging.getLogger(__name__)


class DepartmentClient:
    """
    Client for communicating with the Department gRPC server.

    This client provides methods for:
    - Validating department IDs
    - Getting department details
    - Validating sub-department IDs
    - Getting sub-department details
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[str] = None,
        timeout: int = 5
    ):
        """
        Initialize the department gRPC client.

        Args:
            host: gRPC server host (default from settings or 'localhost')
            port: gRPC server port (default from settings or '50053')
            timeout: Request timeout in seconds
        """
        self.host = host or getattr(settings, 'GRPC_SERVICE_HOST', 'localhost')
        self.port = port or getattr(settings, 'GRPC_SERVICE_PORT', '50052')
        self.timeout = timeout
        self._channel = None
        self._stub = None

    @property
    def channel(self):
        """Lazy-loaded gRPC channel."""
        if self._channel is None:
            self._channel = grpc.insecure_channel(f'{self.host}:{self.port}')
        return self._channel

    @property
    def stub(self):
        """Lazy-loaded gRPC stub."""
        if self._stub is None:
            self._stub = department_service_pb2_grpc.DepartmentServiceStub(self.channel)
        return self._stub

    def close(self):
        """Close the gRPC channel."""
        if self._channel:
            self._channel.close()
            self._channel = None
            self._stub = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def validate_department(self, department_id: str) -> Dict:
        """
        Validate that a department ID exists and is active.

        Args:
            department_id: The department ID to validate

        Returns:
            dict: {
                'exists': bool,
                'department': dict or None,
                'message': str
            }

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        try:
            request = department_service_pb2.ValidateDepartmentRequest(
                department_id=department_id
            )

            response = self.stub.ValidateDepartment(request, timeout=self.timeout)

            department_data = None
            if response.department and response.exists:
                department_data = {
                    'id': response.department.id,
                    'name': response.department.name,
                    'description': response.department.description,
                    'is_active': response.department.is_active,
                    'created_at': response.department.created_at,
                    'updated_at': response.department.updated_at,
                }

            logger.info(f"Department validation result for {department_id}: {response.exists}")

            return {
                'exists': response.exists,
                'department': department_data,
                'message': response.message
            }

        except grpc.RpcError as e:
            logger.error(f"gRPC error validating department {department_id}: {e.code()} - {e.details()}")
            raise

    def get_department(self, department_id: str) -> Optional[Dict]:
        """
        Get department details by department ID.

        Args:
            department_id: The department ID to fetch

        Returns:
            dict: Department details or None if not found
        """
        try:
            request = department_service_pb2.GetDepartmentRequest(
                department_id=department_id
            )
            response = self.stub.GetDepartment(request, timeout=self.timeout)

            return {
                'id': response.id,
                'name': response.name,
                'description': response.description,
                'is_active': response.is_active,
                'created_at': response.created_at,
                'updated_at': response.updated_at,
            }

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            logger.error(f"gRPC error getting department {department_id}: {e.code()} - {e.details()}")
            raise

    def get_departments(self, department_ids: List[str]) -> List[Dict]:
        """
        Get multiple departments by their IDs.

        Args:
            department_ids: List of department IDs to fetch

        Returns:
            list: List of department details
        """
        try:
            request = department_service_pb2.GetDepartmentsRequest(
                department_ids=department_ids
            )
            response = self.stub.GetDepartments(request, timeout=self.timeout)

            departments = []
            for dept in response.departments:
                departments.append({
                    'id': dept.id,
                    'name': dept.name,
                    'description': dept.description,
                    'is_active': dept.is_active,
                    'created_at': dept.created_at,
                    'updated_at': dept.updated_at,
                })

            return departments

        except grpc.RpcError as e:
            logger.error(f"gRPC error getting departments: {e.code()} - {e.details()}")
            raise

    def validate_sub_department(self, sub_department_id: str) -> Dict:
        """
        Validate that a sub-department (unit) ID exists and is active.

        Args:
            sub_department_id: The sub-department ID to validate

        Returns:
            dict: {
                'exists': bool,
                'sub_department': dict or None,
                'message': str
            }

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        try:
            request = department_service_pb2.ValidateSubDepartmentRequest(
                sub_department_id=sub_department_id
            )

            response = self.stub.ValidateSubDepartment(request, timeout=self.timeout)

            sub_dept_data = None
            if response.sub_department and response.exists:
                sub_dept_data = {
                    'id': response.sub_department.id,
                    'name': response.sub_department.name,
                    'description': response.sub_department.description,
                    'department_id': response.sub_department.department_id,
                    'is_active': response.sub_department.is_active,
                    'created_at': response.sub_department.created_at,
                    'updated_at': response.sub_department.updated_at,
                }

            logger.info(f"Sub-department validation result for {sub_department_id}: {response.exists}")

            return {
                'exists': response.exists,
                'sub_department': sub_dept_data,
                'message': response.message
            }

        except grpc.RpcError as e:
            logger.error(f"gRPC error validating sub-department {sub_department_id}: {e.code()} - {e.details()}")
            raise

    def get_sub_department(self, sub_department_id: str) -> Optional[Dict]:
        """
        Get sub-department (unit) details by ID.

        Args:
            sub_department_id: The sub-department ID to fetch

        Returns:
            dict: Sub-department details or None if not found
        """
        try:
            request = department_service_pb2.GetSubDepartmentRequest(
                sub_department_id=sub_department_id
            )
            response = self.stub.GetSubDepartment(request, timeout=self.timeout)

            return {
                'id': response.id,
                'name': response.name,
                'description': response.description,
                'department_id': response.department_id,
                'is_active': response.is_active,
                'created_at': response.created_at,
                'updated_at': response.updated_at,
            }

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            logger.error(f"gRPC error getting sub-department {sub_department_id}: {e.code()} - {e.details()}")
            raise
