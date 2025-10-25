
import logging; gui_logger = logging.getLogger(__name__)

"""
@llm-type control-system
@llm-legend response_viewer.py - system control component
@llm-key Core functionality for response_viewer
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token response_viewer: system control component
"""
"""
📊 Response Viewer Widget - Native GTK Implementation

Displays HTTP/gRPC responses with native GTK widgets.
No web rendering - pure native text display with formatting.

Features:
- Status display with color coding
- Headers viewer
- Body viewer with JSON formatting
- Timing information
- Error handling
"""

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Pango
import json
from typing import Dict, Any


class ResponseViewer(Gtk.Box):
    """
    Response viewer widget using native GTK controls.
    
    Layout:
    ┌─────────────────────────────────┐
    │ Status: 200 OK (150ms)          │
    ├─────────────────────────────────┤
    │ Headers:                        │
    │ ┌─────────────────────────────┐ │
    │ │ content-type: application/  │ │
    │ │ content-length: 1234        │ │
    │ └─────────────────────────────┘ │
    ├─────────────────────────────────┤
    │ Body:                           │
    │ ┌─────────────────────────────┐ │
    │ │ {                           │ │
    │ │   "message": "response"     │ │
    │ │ }                           │ │
    │ └─────────────────────────────┘ │
    └─────────────────────────────────┘
    """
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Apply CSS class
        self.add_css_class("response-viewer")
        
        # Build UI
        self._setup_status_section()
        self._setup_headers_section()
        self._setup_body_section()
        
        # Show placeholder
        self._show_placeholder()
        
    
    def _setup_status_section(self):
        """Create status display section"""
        status_frame = Gtk.Frame()
        status_frame.set_label("Status")
        
        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.set_markup("<span font_family='monospace'>Ready to send request...</span>")
        
        status_frame.set_child(self.status_label)
        self.append(status_frame)
    
    def _setup_headers_section(self):
        """Create headers display section"""
        headers_frame = Gtk.Frame()
        headers_frame.set_label("Headers")
        
        # Headers scrolled window
        headers_scroll = Gtk.ScrolledWindow()
        headers_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        headers_scroll.set_min_content_height(100)
        
        # Headers text view (read-only)
        self.headers_textview = Gtk.TextView()
        self.headers_textview.set_editable(False)
        self.headers_textview.set_monospace(True)
        self.headers_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        
        headers_scroll.set_child(self.headers_textview)
        headers_frame.set_child(headers_scroll)
        self.append(headers_frame)
    
    def _setup_body_section(self):
        """Create body display section"""
        body_frame = Gtk.Frame()
        body_frame.set_label("Body")
        
        # Body scrolled window
        body_scroll = Gtk.ScrolledWindow()
        body_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        body_scroll.set_vexpand(True)
        
        # Body text view (read-only)
        self.body_textview = Gtk.TextView()
        self.body_textview.set_editable(False)
        self.body_textview.set_monospace(True)
        self.body_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        
        body_scroll.set_child(self.body_textview)
        body_frame.set_child(body_scroll)
        self.append(body_frame)
    
    def display_response(self, response_data: Dict[str, Any]):
        """Display response data in the viewer"""
        try:
            # Display status
            self._display_status(response_data)
            
            # Display headers
            self._display_headers(response_data.get("headers", {}))
            
            # Display body
            self._display_body(response_data.get("body", ""))
            
            
        except Exception as e:
            gui_logger.error(f" Error displaying response: {e}")
            self._show_error(f"Failed to display response: {str(e)}")
    
    def _display_status(self, response_data: Dict[str, Any]):
        """Display status information"""
        status = response_data.get("status", 0)
        duration = response_data.get("duration", 0)
        success = response_data.get("success", False)
        error = response_data.get("error", "")
        
        if error:
            # Error response
            status_text = f"❌ Error: {error}"
            css_class = "status-error"
        elif success and 200 <= status < 300:
            # Success response
            status_text = f"✅ {status} OK ({duration}ms)"
            css_class = "status-success"
        elif status >= 400:
            # HTTP error
            status_text = f"❌ {status} Error ({duration}ms)"
            css_class = "status-error"
        else:
            # Other status
            status_text = f"ℹ️ {status} ({duration}ms)"
            css_class = "status-info"
        
        # Update label with markup
        markup = f"<span font_family='monospace' class='{css_class}'>{status_text}</span>"
        self.status_label.set_markup(markup)
    
    def _display_headers(self, headers: Dict[str, Any]):
        """Display response headers"""
        if not headers:
            self.headers_textview.get_buffer().set_text("No headers")
            return
        
        # Format headers as key: value pairs
        headers_text = ""
        for key, value in headers.items():
            headers_text += f"{key}: {value}\n"
        
        self.headers_textview.get_buffer().set_text(headers_text.strip())
    
    def _display_body(self, body: Any):
        """Display response body with formatting"""
        if not body:
            self.body_textview.get_buffer().set_text("No body")
            return
        
        # Format body based on type
        if isinstance(body, dict) or isinstance(body, list):
            # JSON response - format with indentation
            try:
                formatted_body = json.dumps(body, indent=2, ensure_ascii=False)
            except:
                formatted_body = str(body)
        elif isinstance(body, str):
            # String response - try to parse as JSON for formatting
            try:
                parsed = json.loads(body)
                formatted_body = json.dumps(parsed, indent=2, ensure_ascii=False)
            except:
                formatted_body = body
        else:
            formatted_body = str(body)
        
        # Set text in buffer
        buffer = self.body_textview.get_buffer()
        buffer.set_text(formatted_body)
        
        # Apply basic syntax highlighting for JSON
        self._apply_json_highlighting(buffer, formatted_body)
    
    def _apply_json_highlighting(self, buffer, text):
        """Apply basic JSON syntax highlighting"""
        try:
            # Create text tags for different JSON elements
            tag_table = buffer.get_tag_table()
            
            # Create tags if they don't exist
            if not tag_table.lookup("json-string"):
                string_tag = buffer.create_tag("json-string")
                string_tag.set_property("foreground", "#a5d6ff")
                
                number_tag = buffer.create_tag("json-number")
                number_tag.set_property("foreground", "#79c0ff")
                
                keyword_tag = buffer.create_tag("json-keyword")
                keyword_tag.set_property("foreground", "#ff7b72")
                keyword_tag.set_property("weight", Pango.Weight.BOLD)
            
            # Simple highlighting - this is a basic implementation
            # In a full implementation, you'd use proper JSON parsing
            lines = text.split('\n')
            for i, line in enumerate(lines):
                line_start = buffer.get_iter_at_line(i)
                line_end = buffer.get_iter_at_line(i)
                line_end.forward_to_line_end()
                
                # Highlight strings (basic pattern matching)
                if '"' in line:
                    # This is a simplified approach
                    # A proper implementation would use regex or JSON parsing
                    pass
        
        except Exception as e:
            gui_logger.error(f" Syntax highlighting error: {e}")
    
    def _show_placeholder(self):
        """Show placeholder content"""
        self.status_label.set_markup("<span font_family='monospace'>Ready to send request...</span>")
        self.headers_textview.get_buffer().set_text("Headers will appear here after sending a request")
        self.body_textview.get_buffer().set_text("Response body will appear here after sending a request")
    
    def _show_error(self, error_message: str):
        """Show error message"""
        self.status_label.set_markup(f"<span font_family='monospace' color='red'>❌ {error_message}</span>")
        self.headers_textview.get_buffer().set_text("No headers (error)")
        self.body_textview.get_buffer().set_text(f"Error: {error_message}")
    
    def clear_response(self):
        """Clear the response viewer"""
        self._show_placeholder()
