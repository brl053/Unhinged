#!/bin/bash
# Generate chat protobuf clients for production deployment

set -e

echo "🔧 Generating chat protobuf clients..."

# Create output directory
mkdir -p ../generated/python/clients/unhinged_proto_clients

# Generate chat protobuf files
python3 -m grpc_tools.protoc \
    --proto_path=. \
    --python_out=../generated/python/clients/unhinged_proto_clients \
    --grpc_python_out=../generated/python/clients/unhinged_proto_clients \
    chat.proto common.proto

echo "✅ Chat protobuf clients generated successfully"
echo "📁 Output: ../generated/python/clients/unhinged_proto_clients/"
ls -la ../generated/python/clients/unhinged_proto_clients/*chat*
