"""
Auth Client for HR Service

This module provides utilities for communicating with the main auth backend
using gRPC for token validation and user information.

Configuration:
- Set GRPC_SERVICE_HOST environment variable (default: localhost)
- Set GRPC_SERVICE_PORT environment variable (default: 50052)

Usage:
    from hr.utils.auth_client import AuthClient

    # Verify a JWT token
    client = AuthClient()
    is_valid, user_id = client.verify_token(token)

    # Get user info
    user_info = client.get_user_info(user_id)

    # Get employee info
    employee_info = client.get_employee_info(employee_id)
"""

import logging
from typing import Tuple, Optional, Dict, Any
from django.conf import settings

from hr.grpc_clients.auth_client import AuthClient as GrpcAuthClient
import grpc

logger = logging.getLogger(__name__)


class AuthClientError(Exception):
    """Exception raised when auth client operations fail."""
    pass


class AuthClient:
    """
    Client for communicating with the main auth backend service using gRPC.

    This client provides methods for:
    - Token verification
    - User information retrieval
    - Employee information retrieval
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[str] = None,
        timeout: int = 5
    ):
        """
        Initialize the auth client.

        Args:
            host: gRPC server host (default from settings or 'localhost')
            port: gRPC server port (default from settings or '50052')
            timeout: Request timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self._grpc_client = None

    @property
    def grpc_client(self) -> GrpcAuthClient:
        """Lazy-loaded gRPC client."""
        if self._grpc_client is None:
            self._grpc_client = GrpcAuthClient(
                host=self.host,
                port=self.port,
                timeout=self.timeout
            )
        return self._grpc_client

    def close(self):
        """Close the gRPC client."""
        if self._grpc_client:
            self._grpc_client.close()
            self._grpc_client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def verify_token(self, token: str) -> Tuple[bool, Optional[int]]:
        """
        Verify a JWT token with the auth service using gRPC.

        Args:
            token: JWT access token (without 'Bearer ' prefix)

        Returns:
            Tuple of (is_valid, user_id). user_id is None if invalid.
        """
        try:
            result = self.grpc_client.verify_token(token)
            is_valid = result.get('valid', False)
            user_id = result.get('user_id')

            # Convert user_id to int if it's a string
            if user_id and isinstance(user_id, str):
                try:
                    user_id = int(user_id)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert user_id to int: {user_id}")
                    return False, None

            return is_valid, user_id

        except grpc.RpcError as e:
            logger.error(f"gRPC error verifying token: {e.code()} - {e.details()}")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {str(e)}")
            return False, None

    def get_current_user(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Get current user information from token using gRPC.

        Args:
            token: JWT access token

        Returns:
            Tuple of (success, user_data, message)
        """
        try:
            result = self.grpc_client.verify_token(token)
            is_valid = result.get('valid', False)

            if is_valid:
                user_data = result.get('user')
                if user_data:
                    return True, user_data, "Success"
                else:
                    return False, None, "User data not available"
            else:
                message = result.get('message', 'Invalid or expired token')
                return False, None, message

        except grpc.RpcError as e:
            logger.error(f"gRPC error getting current user: {e.code()} - {e.details()}")
            return False, None, f"gRPC error: {e.details()}"
        except Exception as e:
            logger.error(f"Unexpected error getting current user: {str(e)}")
            return False, None, f"Error: {str(e)}"

    def get_user_info(self, user_id: int, token: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by user ID using gRPC.

        Args:
            user_id: The user's ID
            token: JWT access token for authentication (not used in gRPC call)

        Returns:
            Dict with user info if found, None otherwise
        """
        try:
            user_data = self.grpc_client.get_user(str(user_id))
            return user_data

        except grpc.RpcError as e:
            logger.error(f"gRPC error getting user info: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting user info: {str(e)}")
            return None

    def get_employee_info(
        self,
        employee_id: str,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get employee information by employee ID using gRPC.

        Args:
            employee_id: The employee's ID (e.g., "EMP-001" or user ID)
            token: JWT access token for authentication (not used in gRPC call)

        Returns:
            Dict with employee info if found, None otherwise
        """
        try:
            employee_data = self.grpc_client.get_employee(employee_id)
            return employee_data

        except grpc.RpcError as e:
            logger.error(f"gRPC error getting employee info: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting employee info: {str(e)}")
            return None

    def validate_employee_id(self, employee_id: str, token: str) -> bool:
        """
        Check if an employee ID exists in the main backend using gRPC.

        Args:
            employee_id: The employee ID to validate
            token: JWT access token for authentication (not used in gRPC call)

        Returns:
            True if employee exists, False otherwise
        """
        try:
            result = self.grpc_client.validate_employee(employee_id)
            return result.get('exists', False)

        except grpc.RpcError as e:
            logger.error(f"gRPC error validating employee: {e.code()} - {e.details()}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error validating employee: {str(e)}")
            return False


# Singleton instance for convenience
_default_client: Optional[AuthClient] = None


def get_auth_client() -> AuthClient:
    """Get the default auth client instance."""
    global _default_client
    if _default_client is None:
        _default_client = AuthClient()
    return _default_client


# Utility functions for common operations

def verify_request_token(request) -> Tuple[bool, Optional[int], str]:
    """
    Verify the token from a Django request.

    Args:
        request: Django request object

    Returns:
        Tuple of (is_valid, user_id, error_message)
    """
    auth_header = request.headers.get('Authorization', '')

    if not auth_header:
        return False, None, "No authorization header"

    if not auth_header.startswith('Bearer '):
        return False, None, "Invalid authorization header format"

    token = auth_header[7:]  # Remove 'Bearer ' prefix
    client = get_auth_client()
    is_valid, user_id = client.verify_token(token)

    if not is_valid:
        return False, None, "Invalid or expired token"

    return True, user_id, ""


def get_request_user(request) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Get user information from request token.

    Args:
        request: Django request object

    Returns:
        Tuple of (success, user_data, error_message)
    """
    auth_header = request.headers.get('Authorization', '')

    if not auth_header or not auth_header.startswith('Bearer '):
        return False, None, "Invalid authorization"

    token = auth_header[7:]
    client = get_auth_client()
    return client.get_current_user(token)
