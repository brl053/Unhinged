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
import logging
import signal

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
        logger.info("Starting gRPC server on port 9092...")
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

    logger.info("=== Text-to-Speech gRPC Service Starting ===")
    logger.info("gRPC API: Enabled with health.proto implementation")
    logger.info(f"Model: {os.getenv('TTS_MODEL_NAME', 'tts_models/en/ljspeech/tacotron2-DDC')}")
    logger.info(f"Cache Dir: {os.getenv('TTS_CACHE_DIR', '/app/models')}")

    try:
        run_grpc_server()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
    finally:
        logger.info("=== Text-to-Speech Service Stopped ===")

if __name__ == '__main__':
    main()
