#!/usr/bin/env python3
"""
@llm-type service.launcher
@llm-does DAG execution service launcher for AI workflow orchestration
"""

import os
import signal
import sys
from pathlib import Path

# Add session library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "libs" / "python"))

from events import create_service_logger

# Initialize event logger
events = create_service_logger("dag-service", "1.0.0")


def run_grpc_server():
    """Run the DAG gRPC server"""
    try:
        from grpc_server import serve

        events.info("DAG gRPC server started", {"port": 9096})
        serve()
    except Exception as e:
        events.error("DAG gRPC server failed", exception=e)
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

    events.info(
        "Starting DAG execution service",
        {
            "version": "1.0.0",
            "pid": os.getpid(),
            "purpose": "AI workflow orchestration",
        },
    )

    # Check environment
    redis_host = os.getenv("REDIS_HOST", "localhost")

    events.info(
        "Environment configuration",
        {"redis_host": redis_host, "port": 9096, "service_type": "dag_execution"},
    )

    # Start gRPC server
    run_grpc_server()


if __name__ == "__main__":
    main()
