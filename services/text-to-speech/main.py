#!/usr/bin/env python3
"""
@llm-type service-launcher
@llm-legend Text-to-speech service launcher with gRPC health.proto implementation
@llm-key Launches gRPC API for text-to-speech with standardized health endpoints
@llm-map Main entry point for TTS service using health.proto
@llm-axiom Service must implement health.proto for service discovery and monitoring
@llm-contract Provides TTS via gRPC API with health.proto compliance
@llm-token tts-service: Text-to-speech with gRPC and health.proto

Text-to-Speech Service Main Entry Point

gRPC-only service with health.proto implementation:
- gRPC API: Text-to-speech processing
- Health checks: Implements unhinged.health.v1.HealthService
- Service discovery integration via health.proto
"""

import os
import sys
import signal
from unhinged_events import create_service_logger

# Initialize event logger
events = create_service_logger("text-to-speech", "1.0.0")

def run_grpc_server():
    """Run the gRPC server with health.proto implementation"""
    try:
        from grpc_server import serve
        events.info("gRPC server started", {"port": 9092})
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
