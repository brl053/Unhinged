#!/usr/bin/env python3
"""
@llm-type service.launcher
@llm-does chat service launcher with embedded session management
"""

import os
import sys
import signal
import time
from pathlib import Path

# Add session library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "libs" / "python"))

from events import create_service_logger

# Initialize event logger
events = create_service_logger("chat-with-sessions", "1.0.0")

def run_grpc_server():
    """Run the gRPC server with embedded session management"""
    try:
        from grpc_server import serve
        events.info("Chat gRPC server with sessions started", {"port": 9095})
        serve()
    except Exception as e:
        events.error("Chat gRPC server failed", exception=e)
        sys.exit(1)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    events.info("Shutdown signal received", {"signal": signum})
    sys.exit(0)

def main():
    """Main service entry point"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    events.info("Starting chat service with embedded sessions", {
        "version": "1.0.0",
        "pid": os.getpid(),
        "write_through_architecture": True
    })
    
    # Check environment
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    crdb_host = os.getenv('CRDB_HOST', 'localhost')
    
    events.info("Session store configuration", {
        "redis_host": redis_host,
        "crdb_host": crdb_host,
        "architecture": "write_through"
    })
    
    # Start gRPC server
    run_grpc_server()

if __name__ == '__main__':
    main()
