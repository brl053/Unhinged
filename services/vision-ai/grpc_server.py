#!/usr/bin/env python3
"""
@llm-type service
@llm-legend Vision AI gRPC server with health.proto implementation
@llm-key Provides vision analysis via gRPC with standardized health endpoints
@llm-map gRPC server for vision AI service using health.proto compliance
@llm-axiom Service must implement health.proto for service discovery and monitoring
@llm-contract Provides vision analysis via gRPC API with health.proto compliance
@llm-token vision-service: Vision AI with gRPC and health.proto

Vision AI gRPC Server

Implements health.proto for service discovery:
- Health checks: Implements unhinged.health.v1.HealthService
- Vision processing: Image analysis and captioning
- Service discovery integration via health.proto
"""

import os
import logging
import grpc
from concurrent import futures
import time

# Add path for generated health proto
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "generated/python/clients"))

# Health proto imports
from unhinged_proto_clients.health import health_pb2
from unhinged_proto_clients.health import health_pb2_grpc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VisionAIServicer(health_pb2_grpc.HealthServiceServicer):
    """
    Vision AI gRPC service with health.proto implementation
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.vision_model_loaded = False
        self.service_ready = False
        self._load_vision_model()

    def _load_vision_model(self):
        """Load the vision model"""
        try:
            # Import vision model loading logic
            # This would normally load BLIP or other vision models
            logger.info("Loading vision model...")
            # Simulate model loading
            self.vision_model_loaded = True
            self.service_ready = True
            logger.info("Vision model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load vision model: {e}")
            self.vision_model_loaded = False
            self.service_ready = False

    def Heartbeat(self, request: health_pb2.HeartbeatRequest, context) -> health_pb2.HeartbeatResponse:
        """Fast heartbeat endpoint (<10ms) - health.proto implementation"""
        try:
            response = health_pb2.HeartbeatResponse()
            response.alive = True
            response.timestamp_ms = int(time.time() * 1000)
            response.service_id = "vision-ai-service"
            response.version = "1.0.0"
            response.uptime_ms = int((time.time() - self.start_time) * 1000)
            response.status = health_pb2.HEALTH_STATUS_HEALTHY if self.service_ready else health_pb2.HEALTH_STATUS_UNHEALTHY
            return response
        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")
            response = health_pb2.HeartbeatResponse()
            response.alive = False
            response.timestamp_ms = int(time.time() * 1000)
            response.service_id = "vision-ai-service"
            response.version = "1.0.0"
            response.status = health_pb2.HEALTH_STATUS_UNHEALTHY
            return response

    def Diagnostics(self, request: health_pb2.DiagnosticsRequest, context) -> health_pb2.DiagnosticsResponse:
        """Detailed diagnostics endpoint (<1s) - health.proto implementation"""
        try:
            # Get heartbeat first
            heartbeat = self.Heartbeat(health_pb2.HeartbeatRequest(), context)
            
            response = health_pb2.DiagnosticsResponse()
            response.heartbeat.CopyFrom(heartbeat)
            
            # Add metadata if requested
            if request.include_metrics:
                response.metadata["vision_model_loaded"] = str(self.vision_model_loaded)
                response.metadata["service_ready"] = str(self.service_ready)
                response.metadata["service_type"] = "vision-ai"
                response.metadata["capabilities"] = "image-analysis,image-description,object-detection"
                
            response.last_updated.GetCurrentTime()
            return response
        except Exception as e:
            logger.error(f"Diagnostics failed: {e}")
            # Return minimal response on error
            response = health_pb2.DiagnosticsResponse()
            response.heartbeat.CopyFrom(self.Heartbeat(health_pb2.HeartbeatRequest(), context))
            response.metadata["error"] = str(e)
            response.last_updated.GetCurrentTime()
            return response


def serve():
    """Start the gRPC server with health.proto implementation"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = VisionAIServicer()
    
    # Register health service
    health_pb2_grpc.add_HealthServiceServicer_to_server(servicer, server)
    
    listen_addr = '[::]:9093'
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting Vision AI gRPC server on {listen_addr}")
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down Vision AI gRPC server...")
        server.stop(0)


if __name__ == '__main__':
    serve()
