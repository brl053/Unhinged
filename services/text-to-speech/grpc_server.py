#!/usr/bin/env python3
"""
@llm-type service.api
@llm-does text-to-speech grpc server with health.proto implementation
"""

import time
from concurrent import futures

import grpc
from events import create_service_logger

# Health proto imports
from unhinged_proto_clients.health import health_pb2, health_pb2_grpc

# Initialize event logger
events = create_service_logger("text-to-speech", "1.0.0")


class TextToSpeechServicer(health_pb2_grpc.HealthServiceServicer):
    """
    Text-to-Speech gRPC service with health.proto implementation
    """

    def __init__(self):
        self.start_time = time.time()
        self.service_ready = True

    def Heartbeat(
        self, request: health_pb2.HeartbeatRequest, context
    ) -> health_pb2.HeartbeatResponse:
        """Fast heartbeat endpoint (<10ms) - health.proto implementation"""
        try:
            response = health_pb2.HeartbeatResponse()
            response.alive = True
            response.timestamp_ms = int(time.time() * 1000)
            response.service_id = "text-to-speech-service"
            response.version = "1.0.0"
            response.uptime_ms = int((time.time() - self.start_time) * 1000)
            response.status = (
                health_pb2.HEALTH_STATUS_HEALTHY
                if self.service_ready
                else health_pb2.HEALTH_STATUS_UNHEALTHY
            )
            return response
        except Exception as e:
            events.error("Heartbeat failed", exception=e)
            response = health_pb2.HeartbeatResponse()
            response.alive = False
            response.timestamp_ms = int(time.time() * 1000)
            response.service_id = "text-to-speech-service"
            response.version = "1.0.0"
            response.status = health_pb2.HEALTH_STATUS_UNHEALTHY
            return response

    def Diagnostics(
        self, request: health_pb2.DiagnosticsRequest, context
    ) -> health_pb2.DiagnosticsResponse:
        """Detailed diagnostics endpoint (<1s) - health.proto implementation"""
        try:
            # Get heartbeat first
            heartbeat = self.Heartbeat(health_pb2.HeartbeatRequest(), context)

            response = health_pb2.DiagnosticsResponse()
            response.heartbeat.CopyFrom(heartbeat)

            # Add metadata if requested
            if request.include_metrics:
                response.metadata["service_ready"] = str(self.service_ready)
                response.metadata["service_type"] = "text-to-speech"
                response.metadata["capabilities"] = "tts"

            response.last_updated.GetCurrentTime()
            return response
        except Exception as e:
            events.error("Diagnostics failed", exception=e)
            # Return minimal response on error
            response = health_pb2.DiagnosticsResponse()
            response.heartbeat.CopyFrom(
                self.Heartbeat(health_pb2.HeartbeatRequest(), context)
            )
            response.metadata["error"] = str(e)
            response.last_updated.GetCurrentTime()
            return response


def serve():
    """Start the gRPC server with health.proto implementation"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = TextToSpeechServicer()

    # Register health service
    health_pb2_grpc.add_HealthServiceServicer_to_server(servicer, server)

    listen_addr = "[::]:9092"
    server.add_insecure_port(listen_addr)

    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        pass
        server.stop(0)


if __name__ == "__main__":
    serve()
