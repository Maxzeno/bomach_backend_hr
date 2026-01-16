"""
Auth gRPC Client

This module provides a client for communicating with the Auth gRPC server
in the main backend to validate employees, users, and branches.
"""

import logging
import grpc
from typing import Dict, Optional
from django.conf import settings

from hr.grpc_compiled import auth_service_pb2
from hr.grpc_compiled import auth_service_pb2_grpc

logger = logging.getLogger(__name__)


class AuthClient:
    """
    Client for communicating with the Auth gRPC server.

    This client provides methods for:
    - Validating employee IDs
    - Getting employee details
    - Validating user IDs
    - Getting user details
    - Validating branch IDs
    - Getting branch details
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[str] = None,
        timeout: int = 5
    ):
        """
        Initialize the auth gRPC client.

        Args:
            host: gRPC server host (default from settings or 'localhost')
            port: gRPC server port (default from settings or '50052')
            timeout: Request timeout in seconds
        """
        self.host = host or getattr(settings, 'GRPC_SERVICE_HOST', 'localhost')
        self.port = port or getattr(settings, 'GRPC_SERVICE_PORT', '50051')
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
            self._stub = auth_service_pb2_grpc.AuthServiceStub(self.channel)
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

    def validate_employee(self, employee_id: str) -> Dict:
        """
        Validate that an employee ID exists and is active.

        Args:
            employee_id: The employee ID to validate

        Returns:
            dict: {
                'exists': bool,
                'employee': dict or None,
                'message': str
            }

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        try:
            request = auth_service_pb2.ValidateEmployeeRequest(
                employee_id=employee_id
            )

            response = self.stub.ValidateEmployee(request, timeout=self.timeout)

            employee_data = None
            if response.employee and response.exists:
                employee_data = {
                    'id': response.employee.id,
                    'employee_id': response.employee.employee_id,
                    'email': response.employee.email,
                    'full_name': response.employee.full_name,
                    'phone': response.employee.phone,
                    'department_id': response.employee.department_id,
                    'position': response.employee.position,
                    'is_active': response.employee.is_active,
                    'created_at': response.employee.created_at,
                    'updated_at': response.employee.updated_at,
                }

            logger.info(f"Employee validation result for {employee_id}: {response.exists}")

            return {
                'exists': response.exists,
                'employee': employee_data,
                'message': response.message
            }

        except grpc.RpcError as e:
            logger.error(f"gRPC error validating employee {employee_id}: {e.code()} - {e.details()}")
            raise

    def get_employee(self, employee_id: str) -> Optional[Dict]:
        """
        Get employee details by employee ID.

        Args:
            employee_id: The employee ID to fetch

        Returns:
            dict: Employee details or None if not found
        """
        try:
            request = auth_service_pb2.GetEmployeeRequest(employee_id=employee_id)
            response = self.stub.GetEmployee(request, timeout=self.timeout)

            return {
                'id': response.id,
                'employee_id': response.employee_id,
                'email': response.email,
                'full_name': response.full_name,
                'phone': response.phone,
                'department_id': response.department_id,
                'position': response.position,
                'is_active': response.is_active,
                'created_at': response.created_at,
                'updated_at': response.updated_at,
            }

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            logger.error(f"gRPC error getting employee {employee_id}: {e.code()} - {e.details()}")
            raise

    def validate_user(self, user_id: str) -> Dict:
        """
        Validate that a user ID exists and is active.

        Args:
            user_id: The user ID to validate

        Returns:
            dict: {
                'exists': bool,
                'user': dict or None,
                'message': str
            }

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        try:
            request = auth_service_pb2.ValidateUserRequest(user_id=user_id)
            response = self.stub.ValidateUser(request, timeout=self.timeout)

            user_data = None
            if response.user and response.exists:
                user_data = {
                    'id': response.user.id,
                    'email': response.user.email,
                    'full_name': response.user.full_name,
                    'username': response.user.username,
                    'is_active': response.user.is_active,
                    'created_at': response.user.created_at,
                    'updated_at': response.user.updated_at,
                }

            logger.info(f"User validation result for {user_id}: {response.exists}")

            return {
                'exists': response.exists,
                'user': user_data,
                'message': response.message
            }

        except grpc.RpcError as e:
            logger.error(f"gRPC error validating user {user_id}: {e.code()} - {e.details()}")
            raise

    def get_user(self, user_id: str) -> Optional[Dict]:
        """
        Get user details by user ID.

        Args:
            user_id: The user ID to fetch

        Returns:
            dict: User details or None if not found
        """
        try:
            request = auth_service_pb2.GetUserRequest(user_id=user_id)
            response = self.stub.GetUser(request, timeout=self.timeout)

            return {
                'id': response.id,
                'email': response.email,
                'full_name': response.full_name,
                'username': response.username,
                'is_active': response.is_active,
                'created_at': response.created_at,
                'updated_at': response.updated_at,
            }

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            logger.error(f"gRPC error getting user {user_id}: {e.code()} - {e.details()}")
            raise

    def validate_branch(self, branch_id: str) -> Dict:
        """
        Validate that a branch ID exists and is active.

        Args:
            branch_id: The branch ID to validate

        Returns:
            dict: {
                'exists': bool,
                'branch': dict or None,
                'message': str
            }

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        try:
            request = auth_service_pb2.ValidateBranchRequest(branch_id=branch_id)
            response = self.stub.ValidateBranch(request, timeout=self.timeout)

            branch_data = None
            if response.branch and response.exists:
                branch_data = {
                    'id': response.branch.id,
                    'branch_id': response.branch.branch_id,
                    'branch_name': response.branch.branch_name,
                    'country': response.branch.country,
                    'state': response.branch.state,
                    'office_address': response.branch.office_address,
                    'operational_status': response.branch.operational_status,
                    'is_active': response.branch.is_active,
                    'created_at': response.branch.created_at,
                    'updated_at': response.branch.updated_at,
                }

            logger.info(f"Branch validation result for {branch_id}: {response.exists}")

            return {
                'exists': response.exists,
                'branch': branch_data,
                'message': response.message
            }

        except grpc.RpcError as e:
            logger.error(f"gRPC error validating branch {branch_id}: {e.code()} - {e.details()}")
            raise

    def get_branch(self, branch_id: str) -> Optional[Dict]:
        """
        Get branch details by branch ID.

        Args:
            branch_id: The branch ID to fetch

        Returns:
            dict: Branch details or None if not found
        """
        try:
            request = auth_service_pb2.GetBranchRequest(branch_id=branch_id)
            response = self.stub.GetBranch(request, timeout=self.timeout)

            return {
                'id': response.id,
                'branch_id': response.branch_id,
                'branch_name': response.branch_name,
                'country': response.country,
                'state': response.state,
                'office_address': response.office_address,
                'operational_status': response.operational_status,
                'is_active': response.is_active,
                'created_at': response.created_at,
                'updated_at': response.updated_at,
            }

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            logger.error(f"gRPC error getting branch {branch_id}: {e.code()} - {e.details()}")
            raise
