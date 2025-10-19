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

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

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
