"""
Model field validators for cross-service references.

These validators ensure that employee, client, and user IDs referenced
from other microservices actually exist before saving records.
"""

from typing import Optional
from django.core.exceptions import ValidationError
from django.conf import settings
from hr.utils.auth_client import AuthClient


class ServiceValidator:
    """
    Base validator for cross-service entity validation.
    Uses the auth client to validate entities from the main backend.
    """

    def __init__(self):
        self.client = AuthClient()

    def __del__(self):
        """Clean up the HTTP session when validator is destroyed."""
        if hasattr(self, 'client'):
            self.client.close()


def validate_employee_id(employee_id: str, service_token: Optional[str] = None) -> dict:
    """
    Validate that an employee ID exists in the main backend.

    Args:
        employee_id: The employee ID to validate
        service_token: Optional service authentication token.
                      If not provided, uses settings.SERVICE_AUTH_TOKEN

    Returns:
        dict: Employee information if valid

    Raises:
        ValidationError: If employee_id is invalid or not found
    """
    if not employee_id:
        raise ValidationError("Employee ID is required")

    # Get service token from settings or parameter
    token = service_token or getattr(
        settings,
        'SERVICE_AUTH_TOKEN',
        getattr(settings, 'MAIN_BACKEND_SERVICE_TOKEN', None)
    )

    if not token:
        # If no service token configured, log warning but don't block
        # This allows gradual rollout of validation
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"No SERVICE_AUTH_TOKEN configured - skipping validation for employee_id: {employee_id}"
        )
        return {'employee_id': employee_id}

    client = AuthClient()
    try:
        employee_info = client.get_employee_info(employee_id, token)

        if not employee_info:
            raise ValidationError(
                f"Employee with ID '{employee_id}' does not exist in the main backend"
            )

        # Verify employee is active
        if not employee_info.get('is_active', True):
            raise ValidationError(
                f"Employee with ID '{employee_id}' is not active"
            )

        return employee_info

    finally:
        client.close()


def validate_client_id(client_id: str, service_token: Optional[str] = None) -> dict:
    """
    Validate that a client ID exists in the main backend.

    Args:
        client_id: The client ID to validate
        service_token: Optional service authentication token

    Returns:
        dict: Client information if valid

    Raises:
        ValidationError: If client_id is invalid or not found
    """
    if not client_id:
        raise ValidationError("Client ID is required")

    token = service_token or getattr(
        settings,
        'SERVICE_AUTH_TOKEN',
        getattr(settings, 'MAIN_BACKEND_SERVICE_TOKEN', None)
    )

    if not token:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"No SERVICE_AUTH_TOKEN configured - skipping validation for client_id: {client_id}"
        )
        return {'client_id': client_id}

    client = AuthClient()
    try:
        # Note: auth_client may need get_client_info method
        # For now, we'll use a generic approach
        client_info = getattr(client, 'get_client_info', lambda cid, tok: None)(client_id, token)

        if not client_info:
            raise ValidationError(
                f"Client with ID '{client_id}' does not exist in the main backend"
            )

        return client_info

    finally:
        client.close()


def validate_user_id(user_id: int, service_token: Optional[str] = None) -> dict:
    """
    Validate that a user ID exists in the main backend.

    Args:
        user_id: The user ID to validate
        service_token: Optional service authentication token

    Returns:
        dict: User information if valid

    Raises:
        ValidationError: If user_id is invalid or not found
    """
    if not user_id:
        raise ValidationError("User ID is required")

    token = service_token or getattr(
        settings,
        'SERVICE_AUTH_TOKEN',
        getattr(settings, 'MAIN_BACKEND_SERVICE_TOKEN', None)
    )

    if not token:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"No SERVICE_AUTH_TOKEN configured - skipping validation for user_id: {user_id}"
        )
        return {'id': user_id}

    client = AuthClient()
    try:
        user_info = client.get_user_info(user_id, token)

        if not user_info:
            raise ValidationError(
                f"User with ID '{user_id}' does not exist in the main backend"
            )

        # Verify user is active
        if not user_info.get('is_active', True):
            raise ValidationError(
                f"User with ID '{user_id}' is not active"
            )

        return user_info

    finally:
        client.close()


def validate_employee_ids_bulk(employee_ids: list, service_token: Optional[str] = None) -> dict:
    """
    Validate multiple employee IDs at once (for JSONField lists).

    Args:
        employee_ids: List of employee IDs to validate
        service_token: Optional service authentication token

    Returns:
        dict: Mapping of employee_id -> employee_info

    Raises:
        ValidationError: If any employee_id is invalid
    """
    if not employee_ids:
        return {}

    token = service_token or getattr(
        settings,
        'SERVICE_AUTH_TOKEN',
        getattr(settings, 'MAIN_BACKEND_SERVICE_TOKEN', None)
    )

    if not token:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"No SERVICE_AUTH_TOKEN configured - skipping validation for {len(employee_ids)} employee IDs"
        )
        return {eid: {'employee_id': eid} for eid in employee_ids}

    client = AuthClient()
    results = {}
    invalid_ids = []

    try:
        for employee_id in employee_ids:
            employee_info = client.get_employee_info(employee_id, token)
            if employee_info and employee_info.get('is_active', True):
                results[employee_id] = employee_info
            else:
                invalid_ids.append(employee_id)

        if invalid_ids:
            raise ValidationError(
                f"The following employee IDs are invalid or inactive: {', '.join(invalid_ids)}"
            )

        return results

    finally:
        client.close()
