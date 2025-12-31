"""
Auth Client for HR Service

This module provides utilities for communicating with the main auth backend.
It supports both REST API calls and gRPC (when proto files are compiled).

Configuration:
- Set AUTH_SERVICE_URL environment variable (default: http://localhost:8000)
- Set AUTH_SERVICE_GRPC_HOST and AUTH_SERVICE_GRPC_PORT for gRPC

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

import requests
from typing import Tuple, Optional, Dict, Any
from functools import lru_cache
from django.conf import settings


class AuthClientError(Exception):
    """Exception raised when auth client operations fail."""
    pass


class AuthClient:
    """
    Client for communicating with the main auth backend service.

    This client provides methods for:
    - Token verification
    - User information retrieval
    - Employee information retrieval
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 10
    ):
        """
        Initialize the auth client.

        Args:
            base_url: Base URL of the auth service (default from settings/env)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or getattr(
            settings, 'AUTH_SERVICE_URL',
            'http://localhost:8000'
        )
        self.timeout = timeout
        self._session = None

    @property
    def session(self) -> requests.Session:
        """Lazy-loaded requests session for connection pooling."""
        if self._session is None:
            self._session = requests.Session()
        return self._session

    def close(self):
        """Close the session."""
        if self._session:
            self._session.close()
            self._session = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def verify_token(self, token: str) -> Tuple[bool, Optional[int]]:
        """
        Verify a JWT token with the auth service.

        Args:
            token: JWT access token (without 'Bearer ' prefix)

        Returns:
            Tuple of (is_valid, user_id). user_id is None if invalid.
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/auth/verify-token",
                headers={"Authorization": f"Bearer {token}"},
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return True, data.get('user_id')
            return False, None

        except requests.RequestException:
            return False, None

    def get_current_user(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Get current user information from token.

        Args:
            token: JWT access token

        Returns:
            Tuple of (success, user_data, message)
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=self.timeout
            )

            if response.status_code == 200:
                return True, response.json(), "Success"
            elif response.status_code == 401:
                return False, None, "Invalid or expired token"
            else:
                return False, None, f"Error: {response.status_code}"

        except requests.RequestException as e:
            return False, None, f"Connection error: {str(e)}"

    def get_user_info(self, user_id: int, token: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by user ID.

        Note: This requires an authenticated request.

        Args:
            user_id: The user's ID
            token: JWT access token for authentication

        Returns:
            Dict with user info if found, None otherwise
        """
        try:
            # This endpoint may need to be implemented in the main backend
            response = self.session.get(
                f"{self.base_url}/api/v1/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            return None

        except requests.RequestException:
            return None

    def get_employee_info(
        self,
        employee_id: str,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get employee information by employee ID.

        Args:
            employee_id: The employee's ID (e.g., "EMP-001")
            token: JWT access token for authentication

        Returns:
            Dict with employee info if found, None otherwise
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/employees/{employee_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            return None

        except requests.RequestException:
            return None

    def validate_employee_id(self, employee_id: str, token: str) -> bool:
        """
        Check if an employee ID exists in the main backend.

        Args:
            employee_id: The employee ID to validate
            token: JWT access token for authentication

        Returns:
            True if employee exists, False otherwise
        """
        info = self.get_employee_info(employee_id, token)
        return info is not None


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
