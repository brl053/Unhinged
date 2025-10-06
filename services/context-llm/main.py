#!/usr/bin/env python3
"""
Context-Aware LLM Service - Main Entry Point
Starts the context-aware LLM service with documentation and codebase indexing
"""

import os
import logging
import signal
import sys
from app import app, initialize_service
from indexers.documentation_indexer import documentation_indexer
from indexers.codebase_indexer import codebase_indexer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("🛑 Received shutdown signal, cleaning up...")
    
    # Shutdown indexers
    try:
        documentation_indexer.shutdown()
        codebase_indexer.shutdown()
        logger.info("✅ Indexers shut down successfully")
    except Exception as e:
        logger.error(f"Error shutting down indexers: {e}")
    
    sys.exit(0)

def main():
    """Main entry point"""
    logger.info("🔥 Starting Context-Aware LLM Service...")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize the service
        initialize_service()
        
        # Get configuration
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8002))
        debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        logger.info(f"🚀 Context-Aware LLM Service starting on {host}:{port}")
        
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
