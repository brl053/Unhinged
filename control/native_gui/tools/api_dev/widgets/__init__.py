"""
🧩 Native GTK Widgets - Custom UI Components

Pure GTK4 widget implementations for the API dev tool.
No web technologies - native desktop widgets only.

Components:
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
