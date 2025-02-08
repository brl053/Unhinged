FROM ubuntu:22.04

# Install dependencies
RUN apt update && apt install -y curl && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Create a directory to store the model
RUN mkdir -p /models

# Expose Ollama API port
EXPOSE 11434

# Start Ollama in the background
CMD ["bash", "-c", "ollama pull openhermes || true && ollama serve --host 0.0.0.0"]
