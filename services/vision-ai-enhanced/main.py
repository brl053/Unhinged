#!/usr/bin/env python3
"""
Enhanced Vision AI Service - Main Entry Point
Starts the enhanced vision service with multiple model support
"""

import os
import logging
import threading
import time
from app import app, initialize_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    logger.info("🔥 Starting Enhanced Vision AI Service...")
    
    try:
        # Initialize the service
        initialize_service()
        
        # Get configuration
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8001))
        debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        logger.info(f"🚀 Enhanced Vision AI Service starting on {host}:{port}")
        
        # Start Flask server
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down Enhanced Vision AI Service...")
    except Exception as e:
        logger.error(f"❌ Service failed to start: {e}")
        raise

if __name__ == '__main__':
    main()
