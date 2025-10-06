#!/usr/bin/env python3
"""
Multimodal AI API Gateway - Main Entry Point
Unified API endpoint for the multimodal AI processing pipeline
"""

import os
import logging
from app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    logger.info("🔥 Starting Multimodal AI API Gateway...")
    
    try:
        # Get configuration
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8000))
        debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        logger.info(f"🚀 API Gateway starting on {host}:{port}")
        
        # Start Flask server
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down API Gateway...")
    except Exception as e:
        logger.error(f"❌ API Gateway failed to start: {e}")
        raise

if __name__ == '__main__':
    main()
