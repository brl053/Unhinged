#!/usr/bin/env python3
"""
@llm-type service-launcher
@llm-legend Vision AI service launcher with gRPC health.proto implementation
@llm-key Launches gRPC API for vision analysis with standardized health endpoints
@llm-map Main entry point for vision AI service using health.proto
@llm-axiom Service must implement health.proto for service discovery and monitoring
@llm-contract Provides vision analysis via gRPC API with health.proto compliance
@llm-token vision-service: Vision AI with gRPC and health.proto

Vision AI Service Main Entry Point

gRPC-only service with health.proto implementation:
- gRPC API: Image analysis and captioning
- Health checks: Implements unhinged.health.v1.HealthService
- Service discovery integration via health.proto
- BLIP model management and processing
"""

import os
import logging
import signal
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_grpc_server():
    """Run the gRPC server with health.proto implementation"""
    try:
        from grpc_server import serve
        logger.info("Starting gRPC server on port 9093...")
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

    logger.info("🔥 Starting Vision AI gRPC Service...")
    logger.info("gRPC API: Enabled with health.proto implementation")

    try:
        run_grpc_server()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
    finally:
        logger.info("🛑 Vision AI Service Stopped")

if __name__ == '__main__':
    main()
