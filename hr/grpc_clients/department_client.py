"""
gRPC Client for Department Service

Handles communication with the Department microservice.
"""
import grpc
import logging
from typing import Optional, Dict, List
from django.core.cache import cache

from .generated import department_service_pb2, department_service_pb2_grpc
from .config import (
    DEPARTMENT_SERVICE_ADDRESS,
    GRPC_TIMEOUT,
    GRPC_MAX_RETRIES,
    GRPC_RETRY_DELAY,
    ENABLE_GRPC_VALIDATION
)

logger = logging.getLogger(__name__)


class DepartmentServiceClient:
    """Client for interacting with Department gRPC service"""

    def __init__(self):
        self.address = DEPARTMENT_SERVICE_ADDRESS
        self.timeout = GRPC_TIMEOUT

    def _get_channel(self):
        """Create a gRPC channel"""
        return grpc.insecure_channel(self.address)

    def _get_stub(self, channel):
        """Get the service stub"""
        return department_service_pb2_grpc.DepartmentServiceStub(channel)

    def validate_department(self, department_id: str) -> Dict:
        """
        Validate if a department exists.

        Args:
            department_id: The department ID to validate

        Returns:
            Dict with 'exists', 'message', and 'department' keys

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        if not ENABLE_GRPC_VALIDATION:
            logger.warning("gRPC validation is disabled. Skipping department validation.")
            return {
                'exists': True,
                'message': 'Validation disabled',
                'department': None
            }

        # Check cache first
        cache_key = f'department_valid_{department_id}'
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            with self._get_channel() as channel:
                stub = self._get_stub(channel)
                request = department_service_pb2.ValidateDepartmentRequest(
                    department_id=department_id
                )
                response = stub.ValidateDepartment(request, timeout=self.timeout)

                result = {
                    'exists': response.exists,
                    'message': response.message,
                    'department': self._parse_department(response.department) if response.exists else None
                }

                # Cache valid results for 5 minutes
                if response.exists:
                    cache.set(cache_key, result, timeout=300)

                return result

        except grpc.RpcError as e:
            logger.error(f"gRPC error validating department {department_id}: {e.code()} - {e.details()}")
            raise

    def get_department(self, department_id: str) -> Optional[Dict]:
        """
        Get department details by ID.

        Args:
            department_id: The department ID

        Returns:
            Department dict or None if not found

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        # Check cache first
        cache_key = f'department_{department_id}'
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            with self._get_channel() as channel:
                stub = self._get_stub(channel)
                request = department_service_pb2.GetDepartmentRequest(
                    department_id=department_id
                )
                response = stub.GetDepartment(request, timeout=self.timeout)

                result = self._parse_department(response)

                # Cache for 5 minutes
                cache.set(cache_key, result, timeout=300)

                return result

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                logger.warning(f"Department {department_id} not found")
                return None
            logger.error(f"gRPC error getting department {department_id}: {e.code()} - {e.details()}")
            raise

    def get_departments(self, department_ids: List[str]) -> List[Dict]:
        """
        Get multiple departments by IDs.

        Args:
            department_ids: List of department IDs

        Returns:
            List of department dicts

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        try:
            with self._get_channel() as channel:
                stub = self._get_stub(channel)
                request = department_service_pb2.GetDepartmentsRequest(
                    department_ids=department_ids
                )
                response = stub.GetDepartments(request, timeout=self.timeout)

                return [self._parse_department(dept) for dept in response.departments]

        except grpc.RpcError as e:
            logger.error(f"gRPC error getting departments: {e.code()} - {e.details()}")
            raise

    def validate_sub_department(self, sub_department_id: str) -> Dict:
        """
        Validate if a sub-department exists.

        Args:
            sub_department_id: The sub-department ID to validate

        Returns:
            Dict with 'exists', 'message', and 'sub_department' keys

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        if not ENABLE_GRPC_VALIDATION:
            logger.warning("gRPC validation is disabled. Skipping sub-department validation.")
            return {
                'exists': True,
                'message': 'Validation disabled',
                'sub_department': None
            }

        # Check cache first
        cache_key = f'subdept_valid_{sub_department_id}'
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            with self._get_channel() as channel:
                stub = self._get_stub(channel)
                request = department_service_pb2.ValidateSubDepartmentRequest(
                    sub_department_id=sub_department_id
                )
                response = stub.ValidateSubDepartment(request, timeout=self.timeout)

                result = {
                    'exists': response.exists,
                    'message': response.message,
                    'sub_department': self._parse_sub_department(response.sub_department) if response.exists else None
                }

                # Cache valid results for 5 minutes
                if response.exists:
                    cache.set(cache_key, result, timeout=300)

                return result

        except grpc.RpcError as e:
            logger.error(f"gRPC error validating sub-department {sub_department_id}: {e.code()} - {e.details()}")
            raise

    def _parse_department(self, dept_msg) -> Dict:
        """Parse department protobuf message to dict"""
        return {
            'id': dept_msg.id,
            'name': dept_msg.name,
            'description': dept_msg.description,
            'is_active': dept_msg.is_active,
            'created_at': dept_msg.created_at,
            'updated_at': dept_msg.updated_at,
        }

    def _parse_sub_department(self, subdept_msg) -> Dict:
        """Parse sub-department protobuf message to dict"""
        return {
            'id': subdept_msg.id,
            'name': subdept_msg.name,
            'description': subdept_msg.description,
            'department_id': subdept_msg.department_id,
            'is_active': subdept_msg.is_active,
            'created_at': subdept_msg.created_at,
            'updated_at': subdept_msg.updated_at,
        }


# Singleton instance
department_client = DepartmentServiceClient()
