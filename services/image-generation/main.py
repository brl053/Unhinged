#!/usr/bin/env python3
"""
@llm-type service.launcher
@llm-does image generation service launcher with grpc health.proto implementation
"""

import os
import signal
import sys
from pathlib import Path

# Add build directory to path for image generation module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "build"))

from events import create_service_logger

# Initialize event logger
events = create_service_logger("image-generation", "1.0.0")


def run_grpc_server():
    """Run the gRPC server with health.proto implementation"""
    try:
        from grpc_server import serve

        events.info("gRPC server started", {"port": 9094})
        serve()
    except Exception as e:
        events.error("gRPC server failed", exception=e)
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

    events.info("Starting image generation service", {"version": "1.0.0", "pid": os.getpid()})

    # Check environment
    cuda_available = False
    try:
        import torch

        cuda_available = torch.cuda.is_available()
        if cuda_available:
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            events.info(
                "GPU detected",
                {"gpu_name": gpu_name, "gpu_memory_gb": f"{gpu_memory:.1f}"},
            )
        else:
            events.warning("No GPU detected, using CPU mode")
    except ImportError:
        events.warning("PyTorch not available")

    # Start gRPC server
    run_grpc_server()


if __name__ == "__main__":
    main()
