FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy local events package source (from project root context)
COPY libs/event-framework/python/ /tmp/events-package/

# Install local events package first
RUN cd /tmp/events-package && pip install --no-cache-dir .

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy centralized protobuf clients and add to Python path
COPY generated/python/clients/ /app/generated/python/clients/
ENV PYTHONPATH="/app/generated/python/clients:${PYTHONPATH}"

# Copy application code
COPY services/vision-ai/ .

# Create directories for uploads
RUN mkdir -p /app/uploads

# Expose both HTTP and gRPC ports
EXPOSE 8001 9092

# Environment variables for server configuration
ENV ENABLE_FLASK=true
ENV ENABLE_GRPC=true
ENV VISION_MODEL=openai/clip-vit-base-patch32

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Start both servers
CMD ["python", "main.py"]
