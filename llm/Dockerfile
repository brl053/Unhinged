# =============================================================================
# Ollama LLM Service Dockerfile
# =============================================================================
#
# Provides local LLM capabilities using Ollama for the voice-first platform
# Supports offline operation and independent architecture principles
#

FROM ollama/ollama:latest

# Set environment variables
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_PORT=11434

# Create models directory
RUN mkdir -p /models
VOLUME ["/models"]

# Expose Ollama API port
EXPOSE 11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:11434/api/tags || exit 1

# Start Ollama service
CMD ["serve"]
