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
🧩 Native GTK Widgets - Custom UI Components

Pure GTK4 widget implementations for the API dev tool.
No web technologies - native desktop widgets only.

Components:
    pass
- ProtoBrowser: Proto file and service browser
- RequestBuilder: HTTP/gRPC request construction
- ResponseViewer: Response display and formatting
- JSONEditor: JSON editing with syntax highlighting
- SyntaxHighlight: Code highlighting utilities
"""

# Widget exports
from .proto_browser import ProtoBrowser
from .request_builder import RequestBuilder  
from .response_viewer import ResponseViewer

__all__ = [
    "ProtoBrowser",
    "RequestBuilder", 
    "ResponseViewer"
]
