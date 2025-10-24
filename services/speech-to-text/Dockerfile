FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install only required dependencies for speech-to-text
RUN pip install --no-cache-dir \
    grpcio==1.60.0 \
    grpcio-tools==1.60.0 \
    protobuf==4.21.12 \
    openai-whisper==20231117 \
    torch==2.1.0 \
    "numpy<2.0.0"

# Copy proto files for generation
COPY proto/ /app/proto/

# Copy application code
COPY services/speech-to-text/ .

# Generate protobuf files with compatible version
RUN python generate_proto.py

# Create directories for uploads
RUN mkdir -p /app/uploads

# Expose HTTP port
EXPOSE 8000

# Environment variables for server configuration
ENV ENABLE_FLASK=true
ENV ENABLE_GRPC=true

# Health check (check both servers if enabled)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start both servers
CMD ["python", "main.py"]
