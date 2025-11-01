# @llm-type config.build
# @llm-does Dockerfile for chat service with embedded session management

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy shared Python libraries
COPY libs/python /app/libs/python

# Copy generated proto clients
COPY generated/python/clients /app/generated/python/clients

# Copy service code
COPY services/chat-with-sessions /app/services/chat-with-sessions

# Copy proto definitions (for reference)
COPY proto /app/proto

# Install Python dependencies (aligned with speech-to-text service versions)
RUN pip install --no-cache-dir \
    grpcio>=1.75.1 \
    grpcio-tools>=1.75.1 \
    grpcio-health-checking>=1.60.0 \
    protobuf>=4.21.12 \
    redis==5.0.1 \
    psycopg2-binary==2.9.9 \
    pyyaml==6.0.1

# Set Python path to include libs
ENV PYTHONPATH=/app:/app/libs/python:/app/services/chat-with-sessions

# Expose gRPC port
EXPOSE 9095

# Health check using grpc_health_probe
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import grpc; from grpc_health.v1 import health_pb2, health_pb2_grpc; \
    channel = grpc.insecure_channel('localhost:9095'); \
    stub = health_pb2_grpc.HealthStub(channel); \
    stub.Check(health_pb2.HealthCheckRequest())"

# Run the service
CMD ["python", "/app/services/chat-with-sessions/main.py"]

