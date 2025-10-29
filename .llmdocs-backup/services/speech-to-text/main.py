#!/usr/bin/env python3
"""
@llm-type service-launcher
@llm-legend Speech-to-text service launcher with gRPC health.proto implementation
@llm-key Launches gRPC API for speech transcription with standardized health endpoints
@llm-map Main entry point for whisper-based speech-to-text service using health.proto
@llm-axiom Service must implement health.proto for service discovery and monitoring
@llm-contract Provides speech transcription via gRPC streaming API with health.proto compliance
@llm-token speech-service: Whisper-based speech-to-text with gRPC and health.proto

Speech-to-Text Service Main Entry Point

gRPC-only service with health.proto implementation:
- gRPC API: Streaming audio processing and real-time transcription
- Health checks: Implements unhinged.health.v1.HealthService
- Service discovery integration via health.proto
- Whisper model management and CUDA optimization
"""

import os
import sys
import signal
import time
from events import create_service_logger

# Initialize event logger
events = create_service_logger("speech-to-text", "1.0.0")

def run_grpc_server():
    """Run the gRPC server with health.proto implementation"""
    try:
        from grpc_server import serve
        events.info("gRPC server started", {"port": 9091})
        serve()
    except Exception as e:
        events.error("gRPC server failed", exception=e)
        sys.exit(1)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    events.info("Shutdown signal received", {"signal": signum})
    sys.exit(0)

def main():
    """Main entry point - gRPC only"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)



    try:
        run_grpc_server()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        events.error("Server error", exception=e)
        sys.exit(1)

if __name__ == '__main__':
    main()
