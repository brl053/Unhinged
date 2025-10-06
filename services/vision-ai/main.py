#!/usr/bin/env python3
"""
@llm-type service
@llm-legend Provides AI-powered image analysis using BLIP vision model for user-uploaded content
@llm-key Loads BLIP model on startup, serves Flask HTTP API on port 8001, implements health checks
@llm-map Entry point for vision processing pipeline, integrates with backend via HTTP API
@llm-axiom Vision model must be loaded and ready before accepting any processing requests
@llm-contract Returns structured analysis JSON or appropriate HTTP error codes for failures
@llm-token BLIP: Bootstrapping Language-Image Pre-training model for image captioning

Vision AI Service - Main Entry Point
Starts both Flask HTTP server and gRPC server based on environment variables
"""

import os
import logging
import threading
import time
from app import app, load_vision_model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_flask_server():
    """
    @llm-type function
    @llm-legend Starts Flask HTTP server to handle image analysis requests from backend
    @llm-key Binds to all interfaces on port 8001, disables debug mode for production
    @llm-map Called by main thread, serves HTTP endpoints defined in app.py
    @llm-contract Blocks until server shutdown, logs startup status
    """
    logger.info("Starting Flask HTTP server on port 8001...")
    app.run(host='0.0.0.0', port=8001, debug=False, use_reloader=False)

def start_grpc_server():
    """Start the gRPC server (placeholder for future implementation)"""
    logger.info("gRPC server not yet implemented for vision service")
    # TODO: Implement gRPC server similar to whisper-tts
    pass

def main():
    """Main entry point"""
    logger.info("🔥 Starting Vision AI Service...")
    
    # Load the vision model first
    try:
        load_vision_model()
        logger.info("✅ Vision model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load vision model: {e}")
        return
    
    # Check which servers to start
    enable_flask = os.getenv('ENABLE_FLASK', 'true').lower() == 'true'
    enable_grpc = os.getenv('ENABLE_GRPC', 'false').lower() == 'true'
    
    threads = []
    
    if enable_flask:
        flask_thread = threading.Thread(target=start_flask_server, daemon=True)
        flask_thread.start()
        threads.append(flask_thread)
        logger.info("✅ Flask HTTP server started")
    
    if enable_grpc:
        grpc_thread = threading.Thread(target=start_grpc_server, daemon=True)
        grpc_thread.start()
        threads.append(grpc_thread)
        logger.info("✅ gRPC server started")
    
    if not threads:
        logger.error("❌ No servers enabled. Set ENABLE_FLASK=true or ENABLE_GRPC=true")
        return
    
    logger.info("🚀 Vision AI Service is ready!")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down Vision AI Service...")

if __name__ == '__main__':
    main()
