
import logging; gui_logger = logging.getLogger(__name__)

"""
@llm-type control-system
@llm-legend request_builder.py - system control component
@llm-key Core functionality for request_builder
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token request_builder: system control component
"""
"""
🔧 Request Builder Widget - Native GTK Implementation

Builds HTTP/gRPC requests with native GTK widgets.
No web forms - pure native input controls.

Features:
    pass
- Method selection (GET, POST, gRPC, etc.)
- URL/endpoint input
- Headers editor
- Body editor with syntax highlighting
- Request validation
"""

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GObject
import json


class RequestBuilder(Gtk.Box):
    """
    Request builder widget using native GTK controls.
    
    Layout:
        pass
    ┌─────────────────────────────────┐
    │ [GET ▼] [URL Entry            ] │
    ├─────────────────────────────────┤
    │ Headers:                        │
    │ ┌─────────────────────────────┐ │
    │ │ Key: Value pairs            │ │
    │ └─────────────────────────────┘ │
    ├─────────────────────────────────┤
    │ Body:                           │
    │ ┌─────────────────────────────┐ │
    │ │ JSON/Text editor            │ │
    │ └─────────────────────────────┘ │
    └─────────────────────────────────┘
    """
    
    # Custom signals
    __gsignals__ = {
        'request-ready': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
    }
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Apply CSS class
        self.add_css_class("request-builder")
        
        # Current request data
        self.current_request = {
            "type": "http",
            "method": "GET",
            "url": "",
            "headers": {},
            "body": ""
        }
        
        # Build UI
        self._setup_method_url_row()
        self._setup_headers_section()
        self._setup_body_section()
        
        gui_logger.debug(" Request builder widget initialized", {"event_type": "configuration"})
    
    def _setup_method_url_row(self):
        """Create method dropdown and URL entry row"""
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        # Method dropdown
        self.method_dropdown = Gtk.DropDown()
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "gRPC"]
        string_list = Gtk.StringList()
        for method in methods:
            string_list.append(method)
        self.method_dropdown.set_model(string_list)
        self.method_dropdown.set_selected(0)  # Default to GET
        self.method_dropdown.connect("notify::selected", self._on_method_changed)
        
        # URL entry
        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text("Enter URL or gRPC endpoint...")
        self.url_entry.set_hexpand(True)
        self.url_entry.connect("changed", self._on_url_changed)
        
        row_box.append(self.method_dropdown)
        row_box.append(self.url_entry)
        
        self.append(row_box)
    
    def _setup_headers_section(self):
        """Create headers editor section"""
        # Headers label
        headers_label = Gtk.Label(label="Headers:")
        headers_label.set_halign(Gtk.Align.START)
        self.append(headers_label)
        
        # Headers scrolled window
        headers_scroll = Gtk.ScrolledWindow()
        headers_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        headers_scroll.set_min_content_height(120)
        
        # Headers text view
        self.headers_textview = Gtk.TextView()
        self.headers_textview.set_monospace(True)
        buffer = self.headers_textview.get_buffer()
        buffer.set_text("Content-Type: application/json\nAuthorization: Bearer token")
        buffer.connect("changed", self._on_headers_changed)
        
        headers_scroll.set_child(self.headers_textview)
        self.append(headers_scroll)
    
    def _setup_body_section(self):
        """Create request body editor section"""
        # Body label
        body_label = Gtk.Label(label="Body:")
        body_label.set_halign(Gtk.Align.START)
        self.append(body_label)
        
        # Body scrolled window
        body_scroll = Gtk.ScrolledWindow()
        body_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        body_scroll.set_vexpand(True)
        
        # Body text view
        self.body_textview = Gtk.TextView()
        self.body_textview.set_monospace(True)
        buffer = self.body_textview.get_buffer()
        buffer.set_text('{\n  "message": "Hello, World!"\n}')
        buffer.connect("changed", self._on_body_changed)
        
        body_scroll.set_child(self.body_textview)
        self.append(body_scroll)
    
    def _on_method_changed(self, dropdown, param):
        """Handle method selection change"""
        selected = dropdown.get_selected()
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "gRPC"]
        
        if selected < len(methods):
            method = methods[selected]
            self.current_request["method"] = method
            
            # Update request type
            if method == "gRPC":
                self.current_request["type"] = "grpc"
                self.url_entry.set_placeholder_text("Enter gRPC endpoint (host:port)...")
            else:
                self.current_request["type"] = "http"
                self.url_entry.set_placeholder_text("Enter URL...")
            
            self._emit_request_ready()
    
    def _on_url_changed(self, entry):
        """Handle URL entry change"""
        self.current_request["url"] = entry.get_text()
        self._emit_request_ready()
    
    def _on_headers_changed(self, buffer):
        """Handle headers text change"""
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        headers_text = buffer.get_text(start, end, False)
        
        # Parse headers from text
        headers = {}
        for line in headers_text.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        
        self.current_request["headers"] = headers
        self._emit_request_ready()
    
    def _on_body_changed(self, buffer):
        """Handle body text change"""
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        body_text = buffer.get_text(start, end, False)
        
        self.current_request["body"] = body_text
        self._emit_request_ready()
    
    def populate_grpc_method(self, service_name, method_name, request_type, response_type):
        """Populate builder with gRPC method details"""
        # Set method to gRPC
        self.method_dropdown.set_selected(5)  # gRPC is index 5
        
        # Update current request
        self.current_request.update({
            "type": "grpc",
            "method": "gRPC",
            "service_name": service_name,
            "method_name": method_name,
            "request_type": request_type,
            "response_type": response_type
        })
        
        # Update headers with gRPC info
        headers_text = f"Service: {service_name}\nMethod: {method_name}\nRequest-Type: {request_type}\nResponse-Type: {response_type}"
        self.headers_textview.get_buffer().set_text(headers_text)
        
        # Generate sample request body
        sample_body = f'{{\n  "// Sample request for {request_type}": "value"\n}}'
        self.body_textview.get_buffer().set_text(sample_body)
        
        self._emit_request_ready()
    
    def get_request_data(self):
        """Get current request data"""
        return self.current_request.copy()
    
    def clear_request(self):
        """Clear the request builder"""
        self.method_dropdown.set_selected(0)  # Reset to GET
        self.url_entry.set_text("")
        self.headers_textview.get_buffer().set_text("Content-Type: application/json")
        self.body_textview.get_buffer().set_text('{\n  "message": "Hello, World!"\n}')
        
        self.current_request = {
            "type": "http",
            "method": "GET", 
            "url": "",
            "headers": {},
            "body": ""
        }
    
    def _emit_request_ready(self):
        """Emit signal that request is ready"""
        if self.current_request.get("url"):
            self.emit("request-ready", self.current_request)


# Register the widget type
GObject.type_register(RequestBuilder)
