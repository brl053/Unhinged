"""
@llm-type control-system
@llm-legend __init__.py - system control component
@llm-key Core functionality for __init__
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token __init__: system control component
"""
"""
🌉 System Bridge - Direct Python Integration

No HTTP server. No network calls. No serialization overhead.
Direct Python method calls for maximum performance and reliability.

Components:
    pass
- ProtoScanner: Proto file discovery and parsing
- GRPCClient: gRPC request handling
- HTTPClient: HTTP request handling

Architecture:
    pass
Native GTK Widget → Direct Python Call → System Operation
                 ↓
            Instant Response (no network latency)
"""

from ....bridge.proto_scanner import ProtoScanner
from .grpc_client import GRPCClient
from .http_client import HTTPClient

__all__ = [
    "ProtoScanner",
    "GRPCClient", 
    "HTTPClient"
]
