FROM python:3.11-slim

# Install system dependencies for TTS
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    espeak-ng \
    espeak-ng-data \
    libespeak-ng-dev \
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
COPY services/text-to-speech/ .

# Create directories for outputs
RUN mkdir -p /app/outputs /app/models

# Expose HTTP port
EXPOSE 8001

# Environment variables
ENV TTS_MODEL_NAME="tts_models/en/ljspeech/tacotron2-DDC"
ENV TTS_CACHE_DIR="/app/models"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Start the service
CMD ["python", "main.py"]
