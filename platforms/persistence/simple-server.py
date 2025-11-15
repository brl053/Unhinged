#!/usr/bin/env python3

"""
Simple Persistence Platform Mock Service

Provides basic health endpoints for the persistence platform
until the full Java/Kotlin implementation is ready.
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse


class PersistenceHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for persistence platform mock"""

    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path

        if path == "/api/v1/health":
            self.send_health_response()
        elif path == "/api/v1/status":
            self.send_status_response()
        else:
            self.send_not_found()

    def send_health_response(self):
        """Send health check response"""
        response = {
            "status": "healthy",
            "service": "persistence-platform-mock",
            "version": "1.0.0",
            "timestamp": "2025-10-26T14:30:00Z",
        }
        self.send_json_response(200, response)

    def send_status_response(self):
        """Send status response"""
        response = {
            "service": "persistence-platform-mock",
            "status": "running",
            "databases": {
                "redis": "mock",
                "cockroachdb": "mock",
                "mongodb": "mock",
                "weaviate": "mock",
                "elasticsearch": "mock",
            },
            "message": "Mock service - full implementation pending",
        }
        self.send_json_response(200, response)

    def send_not_found(self):
        """Send 404 response"""
        response = {"error": "Not found", "path": self.path}
        self.send_json_response(404, response)

    def send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        """Override to use proper logging"""
        logging.info(f"{self.address_string()} - {format % args}")


def main():
    """Start the mock persistence platform server"""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    port = 8090  # Internal port (mapped to 1300 externally)
    server = HTTPServer(("0.0.0.0", port), PersistenceHandler)

    logging.info(f"🚀 Persistence Platform Mock starting on port {port}")
    logging.info("📋 Available endpoints:")
    logging.info("   • GET /api/v1/health - Health check")
    logging.info("   • GET /api/v1/status - Service status")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("🛑 Shutting down server")
        server.shutdown()


if __name__ == "__main__":
    main()
