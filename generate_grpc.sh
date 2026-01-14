#!/bin/bash

# Generate Python gRPC code from proto files

echo "Generating gRPC code from proto files..."

# Create output directory if it doesn't exist
mkdir -p hr/grpc_clients/generated

# Generate Python code for department service
python3 -m grpc_tools.protoc \
    -I./protos \
    --python_out=./hr/grpc_clients/generated \
    --grpc_python_out=./hr/grpc_clients/generated \
    ./protos/department_service.proto

# Generate Python code for auth service
python3 -m grpc_tools.protoc \
    -I./protos \
    --python_out=./hr/grpc_clients/generated \
    --grpc_python_out=./hr/grpc_clients/generated \
    ./protos/auth_service.proto

# Create __init__.py files
touch hr/grpc_clients/__init__.py
touch hr/grpc_clients/generated/__init__.py

echo "gRPC code generation complete!"
echo "Generated files:"
ls -la hr/grpc_clients/generated/
