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
🔧 API Development Tool

Proto file scanning, gRPC/HTTP request building, and response viewing.
Moved from the main application to be a plugin tool.

Features:
- Proto file discovery and parsing
- Service and method browsing
- Request building (HTTP/gRPC)
- Response viewing and formatting
- Direct Python integration (no HTTP bridge)
"""

from .tool import APIDevTool

__all__ = ["APIDevTool"]
