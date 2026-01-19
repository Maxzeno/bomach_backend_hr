"""
Model field validators for cross-service references.

These validators ensure that employee, client, user, and department IDs
referenced from other microservices actually exist before saving records.

Uses gRPC for efficient service-to-service communication.
"""

import logging
import grpc
from typing import Optional, Dict, List
from django.core.exceptions import ValidationError
from django.conf import settings

logger = logging.getLogger(__name__)


def validate_department_id(department_id: str) -> Dict:
    """
    Validate that a department ID exists in the department microservice using gRPC.

    Args:
        department_id: The department ID to validate

    Returns:
        dict: Department information if valid

    Raises:
        ValidationError: If department_id is invalid or not found
    """
    if not department_id:
        raise ValidationError("Department ID is required")

    try:
        from hr.grpc_clients import department_client

        result = department_client.validate_department(department_id)

        if not result['exists']:
            raise ValidationError(
                f"Department with ID '{department_id}' does not exist in the department service"
            )

        # Check if department is active
        if result['department'] and not result['department'].get('is_active', True):
            raise ValidationError(
                f"Department with ID '{department_id}' is not active"
            )

        return result['department']

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            logger.error(f"Department service is unavailable: {e.details()}")
            raise ValidationError(
                "Unable to validate department ID - Department service is unavailable"
            )
        else:
            logger.error(f"gRPC error validating department: {e.code()} - {e.details()}")
            raise ValidationError(
                f"{e.details()}"
            )
        
    except ValidationError as e:
        raise ValidationError(e.messages[0])

    except Exception as e:
        logger.error(f"Unexpected error validating department {department_id}: {str(e)}")
        raise ValidationError(f"{str(e)}")


def validate_sub_department_id(sub_department_id: str) -> Dict:
    """
    Validate that a sub-department ID exists in the department microservice using gRPC.

    Args:
        sub_department_id: The sub-department ID to validate

    Returns:
        dict: Sub-department information if valid

    Raises:
        ValidationError: If sub_department_id is invalid or not found
    """
    if not sub_department_id:
        raise ValidationError("Sub-department ID is required")

    try:
        from hr.grpc_clients import department_client

        result = department_client.validate_sub_department(sub_department_id)

        if not result['exists']:
            raise ValidationError(
                f"Sub-department with ID '{sub_department_id}' does not exist in the department service"
            )

        # Check if sub-department is active
        if result['sub_department'] and not result['sub_department'].get('is_active', True):
            raise ValidationError(
                f"Sub-department with ID '{sub_department_id}' is not active"
            )

        return result['sub_department']

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            logger.error(f"Department service is unavailable: {e.details()}")
            raise ValidationError(
                "Unable to validate sub-department ID - Department service is unavailable"
            )
        else:
            logger.error(f"gRPC error validating sub-department: {e.code()} - {e.details()}")
            raise ValidationError(
                f"{e.details()}"
            )
        
    except ValidationError as e:
        raise ValidationError(e.messages[0])

    except Exception as e:
        logger.error(f"Unexpected error validating sub-department {sub_department_id}: {str(e)}")
        raise ValidationError(f"{str(e)}")


def validate_employee_id(employee_id: str) -> Dict:
    """
    Validate that an employee ID exists in the auth microservice using gRPC.

    Args:
        employee_id: The employee ID to validate

    Returns:
        dict: Employee information if valid

    Raises:
        ValidationError: If employee_id is invalid or not found
    """
    if not employee_id:
        raise ValidationError("Employee ID is required")

    try:
        from hr.grpc_clients import auth_client

        result = auth_client.validate_employee(employee_id)

        if not result['exists']:
            raise ValidationError(
                f"Employee with ID '{employee_id}' does not exist in the auth service"
            )

        # Verify employee is active
        if result['employee'] and not result['employee'].get('is_active', True):
            raise ValidationError(
                f"Employee with ID '{employee_id}' is not active"
            )

        return result['employee']

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            logger.error(f"Auth service is unavailable: {e.details()}")
            raise ValidationError(
                "Unable to validate employee ID - Auth service is unavailable"
            )
        else:
            logger.error(f"gRPC error validating employee: {e.code()} - {e.details()}")
            raise ValidationError(
                f"{e.details()}"
            )
        
    except ValidationError as e:
        raise ValidationError(e.messages[0])

    except Exception as e:
        logger.error(f"Unexpected error validating employee {employee_id}: {str(e)}")
        raise ValidationError(f"{str(e)}")


def validate_user_id(user_id: str) -> Dict:
    """
    Validate that a user ID exists in the auth microservice using gRPC.

    Args:
        user_id: The user ID to validate

    Returns:
        dict: User information if valid

    Raises:
        ValidationError: If user_id is invalid or not found
    """
    if not user_id:
        raise ValidationError("User ID is required")

    try:
        from hr.grpc_clients import auth_client

        result = auth_client.validate_user(user_id)

        if not result['exists']:
            raise ValidationError(
                f"User with ID '{user_id}' does not exist in the auth service"
            )

        # Verify user is active
        if result['user'] and not result['user'].get('is_active', True):
            raise ValidationError(
                f"User with ID '{user_id}' is not active"
            )

        return result['user']

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            logger.error(f"Auth service is unavailable: {e.details()}")
            raise ValidationError(
                "Unable to validate user ID - Auth service is unavailable"
            )
        else:
            logger.error(f"gRPC error validating user: {e.code()} - {e.details()}")
            raise ValidationError(
                f"{e.details()}"
            )
        
    except ValidationError as e:
        raise ValidationError(e.messages[0])

    except Exception as e:
        logger.error(f"Unexpected error validating user {user_id}: {str(e)}")
        raise ValidationError(f"{str(e)}")


def validate_branch_id(branch_id: str) -> Dict:
    """
    Validate that a branch ID exists in the auth microservice using gRPC.

    Args:
        branch_id: The branch ID to validate

    Returns:
        dict: Branch information if valid

    Raises:
        ValidationError: If branch_id is invalid or not found
    """
    if not branch_id:
        raise ValidationError("Branch ID is required")

    try:
        from hr.grpc_clients import auth_client

        result = auth_client.validate_branch(branch_id)

        if not result['exists']:
            raise ValidationError(
                f"Branch with ID '{branch_id}' does not exist in the auth service"
            )

        # Check if branch is active
        if result['branch'] and not result['branch'].get('is_active', True):
            raise ValidationError(
                f"Branch with ID '{branch_id}' is not active"
            )

        return result['branch']

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            logger.error(f"Auth service is unavailable: {e.details()}")
            raise ValidationError(
                "Unable to validate branch ID - Auth service is unavailable"
            )
        else:
            logger.error(f"gRPC error validating branch: {e.code()} - {e.details()}")
            raise ValidationError(
                f"{e.details()}"
            )
        
    except ValidationError as e:
        logger.error(f"Unexpected error validating branch {branch_id}: {str(e)}")
        raise ValidationError(e.messages[0])

    except Exception as e:
        logger.error(f"Unexpected error validating branch {branch_id}: {str(e)}")
        raise ValidationError(f"{str(e)}")
