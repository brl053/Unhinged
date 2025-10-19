#!/usr/bin/env python3
"""
Text-to-Speech Service Main Entry Point
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

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Main entry point"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=== Text-to-Speech Service Starting ===")
    logger.info(f"Model: {os.getenv('TTS_MODEL_NAME', 'tts_models/en/ljspeech/tacotron2-DDC')}")
    logger.info(f"Cache Dir: {os.getenv('TTS_CACHE_DIR', '/app/models')}")
    
    try:
        from app import app
        logger.info("Starting Flask HTTP server on port 8001...")
        app.run(host='0.0.0.0', port=8001, debug=False, threaded=True)
    except Exception as e:
        logger.error(f"Server failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
