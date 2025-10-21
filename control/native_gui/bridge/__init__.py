"""
🌉 System Bridge - Direct Python Integration

No HTTP server. No network calls. No serialization overhead.
Direct Python method calls for maximum performance and reliability.

Components:
- ProtoScanner: Proto file discovery and parsing
- GRPCClient: gRPC request handling
- HTTPClient: HTTP request handling

Architecture:
Native GTK Widget → Direct Python Call → System Operation
                 ↓
            Instant Response (no network latency)
"""

from .proto_scanner import ProtoScanner
from .grpc_client import GRPCClient
from .http_client import HTTPClient

__all__ = [
    "ProtoScanner",
    "GRPCClient", 
    "HTTPClient"
]
