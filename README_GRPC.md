# HR Service - gRPC Integration

This document explains how the HR service uses gRPC to validate foreign key references from other microservices.

## Overview

The HR service validates the following fields via gRPC:
- `department_id` - Validated against Department microservice
- `employee_id` / `assigned_to_id` - Validated against Auth microservice
- `user_id` - Validated against Auth microservice

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_grpc.txt
```

### 2. Generate gRPC Code

```bash
./generate_grpc.sh
```

This will generate Python code from the `.proto` files in the `hr/grpc_clients/generated/` directory.

### 3. Configure Environment

Create/update `.env`:

```bash
# Department Service
DEPARTMENT_SERVICE_HOST=localhost
DEPARTMENT_SERVICE_PORT=50051

# Auth Service
AUTH_SERVICE_HOST=localhost
AUTH_SERVICE_PORT=50052

# gRPC Settings
GRPC_TIMEOUT=5
ENABLE_GRPC_VALIDATION=True
```

### 4. Start Other Services

Make sure the Department and Auth gRPC servers are running. See `GRPC_SETUP_GUIDE.md` for details on setting those up.

```bash
# In Department service
python manage.py run_grpc_server --port 50051

# In Auth service
python manage.py run_grpc_server --port 50052
```

### 5. Start HR Service

```bash
python manage.py runserver
```

## How It Works

### Automatic Validation

When you create or update models with foreign key IDs, they are automatically validated:

```python
from hr.models import Associate

# This will validate department_id via gRPC
associate = Associate.objects.create(
    full_name="John Doe",
    email="john@example.com",
    phone_number="+1234567890",
    company_name="Acme Corp",
    role_position="IT Consultant",
    department_id="dept-123",  # Validated via gRPC!
    contract_start_date="2024-01-01",
    contract_end_date="2024-12-31"
)
```

If the `department_id` doesn't exist in the Department service, you'll get a `ValidationError`:

```python
ValidationError: Department with ID 'dept-123' does not exist in the department service
```

### Manual Validation

You can also validate IDs manually:

```python
from hr.utils.validators import (
    validate_department_id,
    validate_employee_id,
    validate_user_id
)

# Validate a department
dept_info = validate_department_id('dept-123')
print(dept_info)  # {'id': 'dept-123', 'name': 'Engineering', ...}

# Validate an employee
emp_info = validate_employee_id('EMP-001')
print(emp_info)  # {'id': '...', 'employee_id': 'EMP-001', ...}

# Validate a user
user_info = validate_user_id('user-456')
print(user_info)  # {'id': 'user-456', 'email': '...', ...}
```

### Caching

Validation results are cached for 5 minutes to improve performance. The cache is automatically invalidated when validation fails.

## gRPC Clients

The HR service provides two gRPC clients:

### Department Client

```python
from hr.grpc_clients import department_client

# Validate department
result = department_client.validate_department('dept-123')
print(result)  # {'exists': True, 'message': '...', 'department': {...}}

# Get department details
dept = department_client.get_department('dept-123')
print(dept)  # {'id': 'dept-123', 'name': 'Engineering', ...}

# Get multiple departments
depts = department_client.get_departments(['dept-123', 'dept-456'])
print(depts)  # [{'id': 'dept-123', ...}, {'id': 'dept-456', ...}]

# Validate sub-department
result = department_client.validate_sub_department('subdept-789')
```

### Auth Client

```python
from hr.grpc_clients import auth_client

# Validate employee
result = auth_client.validate_employee('EMP-001')
print(result)  # {'exists': True, 'message': '...', 'employee': {...}}

# Get employee details
emp = auth_client.get_employee('EMP-001')
print(emp)  # {'id': '...', 'employee_id': 'EMP-001', ...}

# Validate user
result = auth_client.validate_user('user-456')

# Get user details
user = auth_client.get_user('user-456')

# Get multiple users
users = auth_client.get_users(['user-123', 'user-456'])
```

## Models with Validation

The following models automatically validate foreign keys via gRPC:

### Associate Model
- `department_id` - Validated against Department service

### JobPosting Model
- `department_id` - Validated against Department service (optional)

### Asset Model
- `department_id` - Validated against Department service (optional)
- `assigned_to_id` - Validated against Auth service (optional)

### LeaveRequest, PerformanceReview, Payroll Models
- `employee_id` - Validated against Auth service

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEPARTMENT_SERVICE_HOST` | `localhost` | Department service hostname |
| `DEPARTMENT_SERVICE_PORT` | `50051` | Department service port |
| `AUTH_SERVICE_HOST` | `localhost` | Auth service hostname |
| `AUTH_SERVICE_PORT` | `50052` | Auth service port |
| `GRPC_TIMEOUT` | `5` | Request timeout in seconds |
| `GRPC_MAX_RETRIES` | `3` | Maximum retry attempts |
| `GRPC_RETRY_DELAY` | `0.5` | Delay between retries in seconds |
| `ENABLE_GRPC_VALIDATION` | `True` | Enable/disable gRPC validation |

### Disabling Validation

For development or testing, you can disable gRPC validation:

```bash
ENABLE_GRPC_VALIDATION=False
```

Or in Python:

```python
from hr.grpc_clients.config import ENABLE_GRPC_VALIDATION
# Validation will be skipped if ENABLE_GRPC_VALIDATION is False
```

## Error Handling

### Service Unavailable

If a gRPC service is unavailable, you'll get a descriptive error:

```python
ValidationError: Unable to validate department ID - Department service is unavailable
```

### Invalid IDs

If an ID doesn't exist:

```python
ValidationError: Department with ID 'dept-999' does not exist in the department service
```

### Inactive Entities

If an entity is inactive:

```python
ValidationError: Department with ID 'dept-123' is not active
```

## Testing

### Unit Tests

```python
from django.test import TestCase
from unittest.mock import patch
from hr.models import Associate

class AssociateTestCase(TestCase):
    @patch('hr.grpc_clients.department_client.validate_department')
    def test_create_associate_with_valid_department(self, mock_validate):
        # Mock the gRPC response
        mock_validate.return_value = {
            'exists': True,
            'message': 'Department found',
            'department': {
                'id': 'dept-123',
                'name': 'Engineering',
                'is_active': True
            }
        }

        associate = Associate.objects.create(
            full_name="John Doe",
            email="john@example.com",
            phone_number="+1234567890",
            company_name="Acme Corp",
            role_position="IT Consultant",
            department_id="dept-123",
            contract_start_date="2024-01-01",
            contract_end_date="2024-12-31"
        )

        self.assertEqual(associate.department_id, "dept-123")
        mock_validate.assert_called_once_with("dept-123")
```

## Production Deployment

### Docker Compose

See `GRPC_SETUP_GUIDE.md` for Docker Compose configuration.

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hr-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: hr-service
        image: hr-service:latest
        env:
        - name: DEPARTMENT_SERVICE_HOST
          value: "department-service.default.svc.cluster.local"
        - name: DEPARTMENT_SERVICE_PORT
          value: "50051"
        - name: AUTH_SERVICE_HOST
          value: "auth-service.default.svc.cluster.local"
        - name: AUTH_SERVICE_PORT
          value: "50052"
```

## Troubleshooting

### Connection Issues

1. Check if gRPC servers are running:
   ```bash
   # Test Department service
   grpcurl -plaintext localhost:50051 list

   # Test Auth service
   grpcurl -plaintext localhost:50052 list
   ```

2. Verify environment variables:
   ```python
   from hr.grpc_clients.config import (
       DEPARTMENT_SERVICE_ADDRESS,
       AUTH_SERVICE_ADDRESS
   )
   print(f"Department: {DEPARTMENT_SERVICE_ADDRESS}")
   print(f"Auth: {AUTH_SERVICE_ADDRESS}")
   ```

3. Check firewall/network settings

### Import Errors

If you see import errors for generated proto files:

```bash
# Regenerate gRPC code
./generate_grpc.sh

# Restart Django
python manage.py runserver
```

### Performance Issues

1. Check cache configuration (Redis recommended for production)
2. Increase `GRPC_TIMEOUT` if requests are timing out
3. Monitor gRPC server resource usage

## Additional Resources

- [gRPC Setup Guide](./GRPC_SETUP_GUIDE.md) - How to set up gRPC servers in other microservices
- [Proto Files](./protos/) - Protocol Buffer definitions
- [gRPC Python Documentation](https://grpc.io/docs/languages/python/)
