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
import logging
import signal
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_grpc_server():
    """Run the gRPC server with health.proto implementation"""
    try:
        from grpc_server import serve
        logger.info("Starting gRPC server on port 9091...")
        serve()
    except Exception as e:
        logger.error(f"gRPC server failed: {e}")
        sys.exit(1)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Main entry point - gRPC only"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("=== Speech-to-Text gRPC Service Starting ===")
    logger.info("gRPC API: Enabled with health.proto implementation")

    try:
        run_grpc_server()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
    finally:
        logger.info("=== Speech-to-Text Service Stopped ===")

if __name__ == '__main__':
    main()
