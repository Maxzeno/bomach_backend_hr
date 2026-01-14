# gRPC Setup Guide for Microservices

This guide explains how to set up gRPC servers in your other microservices to communicate with the HR service.

## Overview

The HR microservice validates foreign keys (department_id, user_id, employee_id) by calling other microservices via gRPC. This ensures data integrity across services.

## Services Required

1. **Department Service** - Validates department_id and sub_department_id
2. **Auth Service** - Validates user_id and employee_id

---

## 1. Department Service Setup

### Step 1: Copy the Proto File

Copy `protos/department_service.proto` from this repository to your Department service project.

```bash
mkdir -p protos
cp /path/to/hr/protos/department_service.proto ./protos/
```

### Step 2: Install gRPC Dependencies

```bash
pip install grpcio grpcio-tools
```

### Step 3: Generate Python Code

Create a script `generate_grpc.sh`:

```bash
#!/bin/bash
python3 -m grpc_tools.protoc \
    -I./protos \
    --python_out=./department_service/grpc_server/generated \
    --grpc_python_out=./department_service/grpc_server/generated \
    ./protos/department_service.proto

touch department_service/grpc_server/__init__.py
touch department_service/grpc_server/generated/__init__.py
```

Make it executable and run:

```bash
chmod +x generate_grpc.sh
./generate_grpc.sh
```

### Step 4: Implement the gRPC Server

Create `department_service/grpc_server/server.py`:

```python
import grpc
from concurrent import futures
import logging

from django.core.exceptions import ObjectDoesNotExist
from .generated import department_service_pb2, department_service_pb2_grpc
from department_service.models import Department, SubDepartment

logger = logging.getLogger(__name__)


class DepartmentServiceServicer(department_service_pb2_grpc.DepartmentServiceServicer):
    """Implementation of DepartmentService gRPC service"""

    def ValidateDepartment(self, request, context):
        """Validate if a department exists"""
        try:
            department = Department.objects.get(id=request.department_id)

            return department_service_pb2.ValidateDepartmentResponse(
                exists=True,
                message="Department found",
                department=self._department_to_proto(department)
            )
        except ObjectDoesNotExist:
            return department_service_pb2.ValidateDepartmentResponse(
                exists=False,
                message=f"Department with ID '{request.department_id}' not found"
            )
        except Exception as e:
            logger.error(f"Error validating department: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return department_service_pb2.ValidateDepartmentResponse(
                exists=False,
                message="Internal error"
            )

    def GetDepartment(self, request, context):
        """Get department details"""
        try:
            department = Department.objects.get(id=request.department_id)
            return self._department_to_proto(department)
        except ObjectDoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Department with ID '{request.department_id}' not found")
            return department_service_pb2.Department()
        except Exception as e:
            logger.error(f"Error getting department: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return department_service_pb2.Department()

    def GetDepartments(self, request, context):
        """Get multiple departments"""
        try:
            departments = Department.objects.filter(id__in=request.department_ids)
            return department_service_pb2.GetDepartmentsResponse(
                departments=[self._department_to_proto(dept) for dept in departments]
            )
        except Exception as e:
            logger.error(f"Error getting departments: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return department_service_pb2.GetDepartmentsResponse(departments=[])

    def ValidateSubDepartment(self, request, context):
        """Validate if a sub-department exists"""
        try:
            sub_department = SubDepartment.objects.get(id=request.sub_department_id)

            return department_service_pb2.ValidateSubDepartmentResponse(
                exists=True,
                message="Sub-department found",
                sub_department=self._subdepartment_to_proto(sub_department)
            )
        except ObjectDoesNotExist:
            return department_service_pb2.ValidateSubDepartmentResponse(
                exists=False,
                message=f"Sub-department with ID '{request.sub_department_id}' not found"
            )
        except Exception as e:
            logger.error(f"Error validating sub-department: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return department_service_pb2.ValidateSubDepartmentResponse(
                exists=False,
                message="Internal error"
            )

    def GetSubDepartment(self, request, context):
        """Get sub-department details"""
        try:
            sub_department = SubDepartment.objects.get(id=request.sub_department_id)
            return self._subdepartment_to_proto(sub_department)
        except ObjectDoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Sub-department with ID '{request.sub_department_id}' not found")
            return department_service_pb2.SubDepartment()
        except Exception as e:
            logger.error(f"Error getting sub-department: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return department_service_pb2.SubDepartment()

    def _department_to_proto(self, department):
        """Convert Django model to protobuf message"""
        return department_service_pb2.Department(
            id=str(department.id),
            name=department.name,
            description=department.description or '',
            is_active=department.is_active,
            created_at=department.created_at.isoformat(),
            updated_at=department.updated_at.isoformat()
        )

    def _subdepartment_to_proto(self, sub_department):
        """Convert Django model to protobuf message"""
        return department_service_pb2.SubDepartment(
            id=str(sub_department.id),
            name=sub_department.name,
            description=sub_department.description or '',
            department_id=str(sub_department.department_id),
            is_active=sub_department.is_active,
            created_at=sub_department.created_at.isoformat(),
            updated_at=sub_department.updated_at.isoformat()
        )


def serve(port='50051'):
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    department_service_pb2_grpc.add_DepartmentServiceServicer_to_server(
        DepartmentServiceServicer(), server
    )
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logger.info(f"Department gRPC server started on port {port}")
    return server


if __name__ == '__main__':
    import django
    import os

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
    django.setup()

    server = serve()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)
```

### Step 5: Create Management Command

Create `department_service/management/commands/run_grpc_server.py`:

```python
from django.core.management.base import BaseCommand
from department_service.grpc_server.server import serve


class Command(BaseCommand):
    help = 'Run the gRPC server'

    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            type=str,
            default='50051',
            help='Port to run the gRPC server on'
        )

    def handle(self, *args, **options):
        port = options['port']
        self.stdout.write(f'Starting gRPC server on port {port}...')
        server = serve(port=port)
        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            server.stop(0)
            self.stdout.write('gRPC server stopped')
```

### Step 6: Run the Server

```bash
python manage.py run_grpc_server --port 50051
```

---

## 2. Auth Service Setup

Follow the same steps as Department Service, but use `protos/auth_service.proto` instead.

### Server Implementation

Create `auth_service/grpc_server/server.py`:

```python
import grpc
from concurrent import futures
import logging

from django.core.exceptions import ObjectDoesNotExist
from .generated import auth_service_pb2, auth_service_pb2_grpc
from auth_service.models import User, Employee

logger = logging.getLogger(__name__)


class AuthServiceServicer(auth_service_pb2_grpc.AuthServiceServicer):
    """Implementation of AuthService gRPC service"""

    def ValidateUser(self, request, context):
        """Validate if a user exists"""
        try:
            user = User.objects.get(id=request.user_id)

            return auth_service_pb2.ValidateUserResponse(
                exists=True,
                message="User found",
                user=self._user_to_proto(user)
            )
        except ObjectDoesNotExist:
            return auth_service_pb2.ValidateUserResponse(
                exists=False,
                message=f"User with ID '{request.user_id}' not found"
            )
        except Exception as e:
            logger.error(f"Error validating user: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return auth_service_pb2.ValidateUserResponse(
                exists=False,
                message="Internal error"
            )

    def GetUser(self, request, context):
        """Get user details"""
        try:
            user = User.objects.get(id=request.user_id)
            return self._user_to_proto(user)
        except ObjectDoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"User with ID '{request.user_id}' not found")
            return auth_service_pb2.User()
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return auth_service_pb2.User()

    def GetUsers(self, request, context):
        """Get multiple users"""
        try:
            users = User.objects.filter(id__in=request.user_ids)
            return auth_service_pb2.GetUsersResponse(
                users=[self._user_to_proto(user) for user in users]
            )
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return auth_service_pb2.GetUsersResponse(users=[])

    def ValidateEmployee(self, request, context):
        """Validate if an employee exists"""
        try:
            employee = Employee.objects.get(employee_id=request.employee_id)

            return auth_service_pb2.ValidateEmployeeResponse(
                exists=True,
                message="Employee found",
                employee=self._employee_to_proto(employee)
            )
        except ObjectDoesNotExist:
            return auth_service_pb2.ValidateEmployeeResponse(
                exists=False,
                message=f"Employee with ID '{request.employee_id}' not found"
            )
        except Exception as e:
            logger.error(f"Error validating employee: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return auth_service_pb2.ValidateEmployeeResponse(
                exists=False,
                message="Internal error"
            )

    def GetEmployee(self, request, context):
        """Get employee details"""
        try:
            employee = Employee.objects.get(employee_id=request.employee_id)
            return self._employee_to_proto(employee)
        except ObjectDoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Employee with ID '{request.employee_id}' not found")
            return auth_service_pb2.Employee()
        except Exception as e:
            logger.error(f"Error getting employee: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return auth_service_pb2.Employee()

    def _user_to_proto(self, user):
        """Convert Django model to protobuf message"""
        return auth_service_pb2.User(
            id=str(user.id),
            email=user.email,
            full_name=user.get_full_name(),
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if hasattr(user, 'created_at') else '',
            updated_at=user.updated_at.isoformat() if hasattr(user, 'updated_at') else ''
        )

    def _employee_to_proto(self, employee):
        """Convert Django model to protobuf message"""
        return auth_service_pb2.Employee(
            id=str(employee.id),
            employee_id=employee.employee_id,
            email=employee.email,
            full_name=employee.full_name,
            phone=employee.phone or '',
            department_id=str(employee.department_id) if employee.department_id else '',
            position=employee.position or '',
            is_active=employee.is_active,
            created_at=employee.created_at.isoformat(),
            updated_at=employee.updated_at.isoformat()
        )


def serve(port='50052'):
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_service_pb2_grpc.add_AuthServiceServicer_to_server(
        AuthServiceServicer(), server
    )
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logger.info(f"Auth gRPC server started on port {port}")
    return server


if __name__ == '__main__':
    import django
    import os

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
    django.setup()

    server = serve()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)
```

### Run the Server

```bash
python manage.py run_grpc_server --port 50052
```

---

## 3. Environment Configuration

### In HR Service

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
GRPC_MAX_RETRIES=3
GRPC_RETRY_DELAY=0.5
ENABLE_GRPC_VALIDATION=True
```

### In Production

For Docker/Kubernetes, use service names instead of localhost:

```bash
DEPARTMENT_SERVICE_HOST=department-service
AUTH_SERVICE_HOST=auth-service
```

---

## 4. Testing the Setup

### Test Department Service

```python
from hr.grpc_clients import department_client

# Validate a department
result = department_client.validate_department('dept-123')
print(result)  # {'exists': True, 'message': '...', 'department': {...}}

# Get department details
dept = department_client.get_department('dept-123')
print(dept)
```

### Test Auth Service

```python
from hr.grpc_clients import auth_client

# Validate an employee
result = auth_client.validate_employee('EMP-001')
print(result)  # {'exists': True, 'message': '...', 'employee': {...}}

# Get employee details
emp = auth_client.get_employee('EMP-001')
print(emp)
```

---

## 5. Production Considerations

### Security

For production, use TLS/SSL:

```python
# In the gRPC server
with open('server.key', 'rb') as f:
    private_key = f.read()
with open('server.crt', 'rb') as f:
    certificate_chain = f.read()

server_credentials = grpc.ssl_server_credentials(
    [(private_key, certificate_chain)]
)
server.add_secure_port(f'[::]:{port}', server_credentials)
```

### Load Balancing

Use a load balancer or service mesh (like Istio) for gRPC traffic.

### Monitoring

Add logging and metrics:

```python
import time

def log_request(method_name, start_time):
    duration = time.time() - start_time
    logger.info(f"gRPC {method_name} took {duration:.3f}s")
```

---

## 6. Docker Deployment

### Dockerfile for gRPC Server

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose gRPC port
EXPOSE 50051

CMD ["python", "manage.py", "run_grpc_server", "--port", "50051"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  department-grpc:
    build: ./department_service
    ports:
      - "50051:50051"
    environment:
      - DJANGO_SETTINGS_MODULE=department_service.settings
    networks:
      - microservices

  auth-grpc:
    build: ./auth_service
    ports:
      - "50052:50052"
    environment:
      - DJANGO_SETTINGS_MODULE=auth_service.settings
    networks:
      - microservices

  hr-service:
    build: ./hr_service
    ports:
      - "8000:8000"
    environment:
      - DEPARTMENT_SERVICE_HOST=department-grpc
      - DEPARTMENT_SERVICE_PORT=50051
      - AUTH_SERVICE_HOST=auth-grpc
      - AUTH_SERVICE_PORT=50052
    depends_on:
      - department-grpc
      - auth-grpc
    networks:
      - microservices

networks:
  microservices:
    driver: bridge
```

---

## Troubleshooting

### Connection Refused

- Ensure the gRPC server is running
- Check firewall settings
- Verify the correct host/port in environment variables

### Validation Disabled

If you see "Validation disabled" messages, check:
- `ENABLE_GRPC_VALIDATION=True` in .env
- gRPC servers are accessible

### Import Errors

Run `./generate_grpc.sh` to regenerate the gRPC code if you encounter import errors.

---

## Additional Resources

- [gRPC Python Documentation](https://grpc.io/docs/languages/python/)
- [Protocol Buffers Guide](https://developers.google.com/protocol-buffers)
- [Django gRPC Integration](https://github.com/gluk-w/django-grpc-framework)
