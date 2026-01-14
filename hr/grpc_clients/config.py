"""
gRPC Client Configuration

Configure gRPC service endpoints here or via environment variables.
"""
import os

# Department Service Configuration
DEPARTMENT_SERVICE_HOST = os.getenv('DEPARTMENT_SERVICE_HOST', 'localhost')
DEPARTMENT_SERVICE_PORT = os.getenv('DEPARTMENT_SERVICE_PORT', '50051')
DEPARTMENT_SERVICE_ADDRESS = f'{DEPARTMENT_SERVICE_HOST}:{DEPARTMENT_SERVICE_PORT}'

# Auth Service Configuration
AUTH_SERVICE_HOST = os.getenv('AUTH_SERVICE_HOST', 'localhost')
AUTH_SERVICE_PORT = os.getenv('AUTH_SERVICE_PORT', '50052')
AUTH_SERVICE_ADDRESS = f'{AUTH_SERVICE_HOST}:{AUTH_SERVICE_PORT}'

# gRPC Configuration
GRPC_TIMEOUT = int(os.getenv('GRPC_TIMEOUT', '5'))  # seconds
GRPC_MAX_RETRIES = int(os.getenv('GRPC_MAX_RETRIES', '3'))
GRPC_RETRY_DELAY = float(os.getenv('GRPC_RETRY_DELAY', '0.5'))  # seconds

# Enable/Disable gRPC validation
ENABLE_GRPC_VALIDATION = os.getenv('ENABLE_GRPC_VALIDATION', 'True').lower() == 'true'
