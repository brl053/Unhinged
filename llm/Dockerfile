FROM ubuntu:22.04

# Install dependencies
RUN apt update && apt install -y curl && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Create a directory to store the models
RUN mkdir -p /models

# Expose Ollama API port
EXPOSE 11434

# Set environment variable
ENV OLLAMA_MODELS=/models
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_ORIGINS=*

# Start Ollama and pull the model once the container starts
CMD ["bash", "-c", "ollama serve & sleep 5 && ollama pull openhermes && tail -f /dev/null"]
