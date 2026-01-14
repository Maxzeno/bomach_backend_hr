"""
gRPC Client for Auth/User Service

Handles communication with the Auth/User microservice.
"""
import grpc
import logging
from typing import Optional, Dict, List
from django.core.cache import cache

from .generated import auth_service_pb2, auth_service_pb2_grpc
from .config import (
    AUTH_SERVICE_ADDRESS,
    GRPC_TIMEOUT,
    GRPC_MAX_RETRIES,
    GRPC_RETRY_DELAY,
    ENABLE_GRPC_VALIDATION
)

logger = logging.getLogger(__name__)


class AuthServiceClient:
    """Client for interacting with Auth/User gRPC service"""

    def __init__(self):
        self.address = AUTH_SERVICE_ADDRESS
        self.timeout = GRPC_TIMEOUT

    def _get_channel(self):
        """Create a gRPC channel"""
        return grpc.insecure_channel(self.address)

    def _get_stub(self, channel):
        """Get the service stub"""
        return auth_service_pb2_grpc.AuthServiceStub(channel)

    def validate_user(self, user_id: str) -> Dict:
        """
        Validate if a user exists.

        Args:
            user_id: The user ID to validate

        Returns:
            Dict with 'exists', 'message', and 'user' keys

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        if not ENABLE_GRPC_VALIDATION:
            logger.warning("gRPC validation is disabled. Skipping user validation.")
            return {
                'exists': True,
                'message': 'Validation disabled',
                'user': None
            }

        # Check cache first
        cache_key = f'user_valid_{user_id}'
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            with self._get_channel() as channel:
                stub = self._get_stub(channel)
                request = auth_service_pb2.ValidateUserRequest(user_id=user_id)
                response = stub.ValidateUser(request, timeout=self.timeout)

                result = {
                    'exists': response.exists,
                    'message': response.message,
                    'user': self._parse_user(response.user) if response.exists else None
                }

                # Cache valid results for 5 minutes
                if response.exists:
                    cache.set(cache_key, result, timeout=300)

                return result

        except grpc.RpcError as e:
            logger.error(f"gRPC error validating user {user_id}: {e.code()} - {e.details()}")
            raise

    def get_user(self, user_id: str) -> Optional[Dict]:
        """
        Get user details by ID.

        Args:
            user_id: The user ID

        Returns:
            User dict or None if not found

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        # Check cache first
        cache_key = f'user_{user_id}'
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            with self._get_channel() as channel:
                stub = self._get_stub(channel)
                request = auth_service_pb2.GetUserRequest(user_id=user_id)
                response = stub.GetUser(request, timeout=self.timeout)

                result = self._parse_user(response)

                # Cache for 5 minutes
                cache.set(cache_key, result, timeout=300)

                return result

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                logger.warning(f"User {user_id} not found")
                return None
            logger.error(f"gRPC error getting user {user_id}: {e.code()} - {e.details()}")
            raise

    def validate_employee(self, employee_id: str) -> Dict:
        """
        Validate if an employee exists.

        Args:
            employee_id: The employee ID to validate

        Returns:
            Dict with 'exists', 'message', and 'employee' keys

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        if not ENABLE_GRPC_VALIDATION:
            logger.warning("gRPC validation is disabled. Skipping employee validation.")
            return {
                'exists': True,
                'message': 'Validation disabled',
                'employee': None
            }

        # Check cache first
        cache_key = f'employee_valid_{employee_id}'
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            with self._get_channel() as channel:
                stub = self._get_stub(channel)
                request = auth_service_pb2.ValidateEmployeeRequest(
                    employee_id=employee_id
                )
                response = stub.ValidateEmployee(request, timeout=self.timeout)

                result = {
                    'exists': response.exists,
                    'message': response.message,
                    'employee': self._parse_employee(response.employee) if response.exists else None
                }

                # Cache valid results for 5 minutes
                if response.exists:
                    cache.set(cache_key, result, timeout=300)

                return result

        except grpc.RpcError as e:
            logger.error(f"gRPC error validating employee {employee_id}: {e.code()} - {e.details()}")
            raise

    def get_employee(self, employee_id: str) -> Optional[Dict]:
        """
        Get employee details by ID.

        Args:
            employee_id: The employee ID

        Returns:
            Employee dict or None if not found

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        # Check cache first
        cache_key = f'employee_{employee_id}'
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            with self._get_channel() as channel:
                stub = self._get_stub(channel)
                request = auth_service_pb2.GetEmployeeRequest(
                    employee_id=employee_id
                )
                response = stub.GetEmployee(request, timeout=self.timeout)

                result = self._parse_employee(response)

                # Cache for 5 minutes
                cache.set(cache_key, result, timeout=300)

                return result

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                logger.warning(f"Employee {employee_id} not found")
                return None
            logger.error(f"gRPC error getting employee {employee_id}: {e.code()} - {e.details()}")
            raise

    def get_users(self, user_ids: List[str]) -> List[Dict]:
        """
        Get multiple users by IDs.

        Args:
            user_ids: List of user IDs

        Returns:
            List of user dicts

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        try:
            with self._get_channel() as channel:
                stub = self._get_stub(channel)
                request = auth_service_pb2.GetUsersRequest(user_ids=user_ids)
                response = stub.GetUsers(request, timeout=self.timeout)

                return [self._parse_user(user) for user in response.users]

        except grpc.RpcError as e:
            logger.error(f"gRPC error getting users: {e.code()} - {e.details()}")
            raise

    def _parse_user(self, user_msg) -> Dict:
        """Parse user protobuf message to dict"""
        return {
            'id': user_msg.id,
            'email': user_msg.email,
            'full_name': user_msg.full_name,
            'username': user_msg.username,
            'is_active': user_msg.is_active,
            'created_at': user_msg.created_at,
            'updated_at': user_msg.updated_at,
        }

    def _parse_employee(self, employee_msg) -> Dict:
        """Parse employee protobuf message to dict"""
        return {
            'id': employee_msg.id,
            'employee_id': employee_msg.employee_id,
            'email': employee_msg.email,
            'full_name': employee_msg.full_name,
            'phone': employee_msg.phone,
            'department_id': employee_msg.department_id,
            'position': employee_msg.position,
            'is_active': employee_msg.is_active,
            'created_at': employee_msg.created_at,
            'updated_at': employee_msg.updated_at,
        }


# Singleton instance
auth_client = AuthServiceClient()
