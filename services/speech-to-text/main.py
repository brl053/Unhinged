#!/usr/bin/env python3
"""
Whisper TTS Service Main Entry Point
Supports both Flask HTTP API (legacy) and gRPC API (new)
"""

import os
import sys
import threading
import logging
import signal
import time
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_flask_server():
    """Run the Flask HTTP server for backward compatibility"""
    try:
        from app import app
        logger.info("Starting Flask HTTP server on port 8000...")
        app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)
    except Exception as e:
        logger.error(f"Flask server failed: {e}")

def run_grpc_server():
    """Run the gRPC server for new proto-compliant API"""
    try:
        from grpc_server import serve
        logger.info("Starting gRPC server on port 9091...")
        serve()
    except Exception as e:
        logger.error(f"gRPC server failed: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Main entry point - runs both servers"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Determine which servers to run based on environment
    run_flask = os.getenv('ENABLE_FLASK', 'true').lower() == 'true'
    run_grpc = os.getenv('ENABLE_GRPC', 'true').lower() == 'true'
    
    if not run_flask and not run_grpc:
        logger.error("At least one server (Flask or gRPC) must be enabled")
        sys.exit(1)
    
    logger.info("=== Whisper TTS Service Starting ===")
    logger.info(f"Flask HTTP API: {'Enabled' if run_flask else 'Disabled'}")
    logger.info(f"gRPC API: {'Enabled' if run_grpc else 'Disabled'}")
    
    # Use ThreadPoolExecutor to run servers concurrently
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        
        if run_flask:
            futures.append(executor.submit(run_flask_server))
        
        if run_grpc:
            futures.append(executor.submit(run_grpc_server))
        
        try:
            # Wait for any server to complete (which shouldn't happen in normal operation)
            for future in futures:
                future.result()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            logger.info("=== Whisper TTS Service Stopped ===")

if __name__ == '__main__':
    main()
