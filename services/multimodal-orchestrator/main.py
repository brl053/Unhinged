#!/usr/bin/env python3
"""
Multimodal Orchestrator Service - Main Entry Point
Starts the orchestrator service that coordinates multimodal analysis workflows
"""

import os
import logging
import signal
import sys
import asyncio
from app import app, initialize_service
from orchestrator import orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("🛑 Received shutdown signal, cleaning up...")
    
    # Shutdown orchestrator
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(orchestrator.shutdown())
        loop.close()
        logger.info("✅ Orchestrator shut down successfully")
    except Exception as e:
        logger.error(f"Error shutting down orchestrator: {e}")
    
    sys.exit(0)

def main():
    """Main entry point"""
    logger.info("🔥 Starting Multimodal Orchestrator Service...")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize the service
        initialize_service()
        
        # Get configuration
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8003))
        debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        logger.info(f"🚀 Multimodal Orchestrator Service starting on {host}:{port}")
        
        # Start Flask server
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"❌ Service failed to start: {e}")
        raise

if __name__ == '__main__':
    main()
