#!/usr/bin/env python3
"""
@llm-type service.launcher
@llm-does vision ai service launcher with grpc health.proto
"""

import os
import signal
import sys
from events import create_service_logger

# Initialize event logger
events = create_service_logger("vision-ai", "1.0.0")

def run_grpc_server():
    """Run the gRPC server with health.proto implementation"""
    try:
        from grpc_server import serve
        events.info("gRPC server started", {"port": 9093})
        serve()
    except Exception as e:
        events.error("gRPC server failed", exception=e)
        sys.exit(1)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    events.info("Shutdown signal received", {"signal": signum})
    sys.exit(0)

def main():
    """Main entry point - gRPC only"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)



    try:
        run_grpc_server()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        events.error("Server error", exception=e)
        sys.exit(1)

if __name__ == '__main__':
    main()
