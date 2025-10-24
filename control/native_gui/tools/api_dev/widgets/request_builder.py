"""
🔧 Request Builder Widget - Native GTK Implementation

Builds HTTP/gRPC requests with native GTK widgets.
No web forms - pure native input controls.

Features:
- Method selection (GET, POST, gRPC, etc.)
- URL/endpoint input
- Headers editor
- Body editor with syntax highlighting
- Request validation
"""

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GObject, GLib
import json
from .schema_validator import SchemaValidator


class RequestBuilder(Gtk.Box):
    """
    Request builder widget using native GTK controls.
    
    Layout:
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

        # Network services data
        self.network_services = {}
        self.current_service = None
        self.current_service_methods = []

        # Schema validation
        self.schema_validator = SchemaValidator()

        # Build UI
        self._setup_method_url_row()
        self._setup_headers_section()
        self._setup_body_section()

        # Connect signals after all widgets are created to avoid AttributeError
        self.service_dropdown.connect("notify::selected", self._on_service_changed)

        print("🔧 Intelligent request builder widget initialized")
    
    def _setup_method_url_row(self):
        """Create intelligent service selection and method configuration"""
        # Service selection row
        service_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Service label
        service_label = Gtk.Label(label="Service:")
        service_label.set_size_request(80, -1)
        service_row.append(service_label)

        # Service dropdown (populated from network discovery)
        self.service_dropdown = Gtk.DropDown()
        self.service_dropdown.set_hexpand(True)
        # Note: Signal connection moved to end of __init__ to avoid AttributeError
        self._populate_service_dropdown()
        service_row.append(self.service_dropdown)

        # Refresh services button
        refresh_button = Gtk.Button()
        refresh_button.set_icon_name("view-refresh-symbolic")
        refresh_button.set_tooltip_text("Refresh network services")
        refresh_button.connect("clicked", self._on_refresh_services_clicked)
        service_row.append(refresh_button)

        self.append(service_row)

        # Method and URL row
        method_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Method label
        method_label = Gtk.Label(label="Method:")
        method_label.set_size_request(80, -1)
        method_row.append(method_label)

        # Method dropdown
        self.method_dropdown = Gtk.DropDown()
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "gRPC"]
        string_list = Gtk.StringList()
        for method in methods:
            string_list.append(method)
        self.method_dropdown.set_model(string_list)
        self.method_dropdown.set_selected(0)  # Default to GET
        self.method_dropdown.connect("notify::selected", self._on_method_changed)
        method_row.append(self.method_dropdown)

        # Service method dropdown (for gRPC services)
        self.service_method_dropdown = Gtk.DropDown()
        self.service_method_dropdown.set_visible(False)
        self.service_method_dropdown.connect("notify::selected", self._on_service_method_changed)
        method_row.append(self.service_method_dropdown)

        self.append(method_row)

        # URL row
        url_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # URL label
        url_label = Gtk.Label(label="URL:")
        url_label.set_size_request(80, -1)
        url_row.append(url_label)

        # URL entry
        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text("Select service or enter URL manually...")
        self.url_entry.set_hexpand(True)
        self.url_entry.connect("changed", self._on_url_changed)
        url_row.append(self.url_entry)

        # Health status indicator
        self.health_indicator = Gtk.Label(label="")
        self.health_indicator.set_size_request(100, -1)
        url_row.append(self.health_indicator)

        self.append(url_row)
    
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
        """Create request body editor section with validation"""
        # Body header with validation controls
        body_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        body_label = Gtk.Label(label="Body:")
        body_label.set_halign(Gtk.Align.START)
        body_label.set_hexpand(True)
        body_header.append(body_label)

        # Validate button
        self.validate_button = Gtk.Button(label="🔍 Validate")
        self.validate_button.connect("clicked", self._on_validate_clicked)
        self.validate_button.set_tooltip_text("Validate request against service schema")
        body_header.append(self.validate_button)

        # Template button
        self.template_button = Gtk.Button(label="📋 Template")
        self.template_button.connect("clicked", self._on_template_clicked)
        self.template_button.set_tooltip_text("Generate smart template for selected method")
        body_header.append(self.template_button)

        self.append(body_header)

        # Validation status bar
        self.validation_status = Gtk.Label(label="")
        self.validation_status.set_halign(Gtk.Align.START)
        self.validation_status.add_css_class("validation-status")
        self.append(self.validation_status)

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

        # Validation details (initially hidden)
        self.validation_details = Gtk.Expander(label="Validation Details")
        self.validation_details.set_visible(False)

        validation_scroll = Gtk.ScrolledWindow()
        validation_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        validation_scroll.set_size_request(-1, 100)

        self.validation_textview = Gtk.TextView()
        self.validation_textview.set_editable(False)
        self.validation_textview.set_monospace(True)
        self.validation_textview.set_wrap_mode(Gtk.WrapMode.WORD)

        validation_scroll.set_child(self.validation_textview)
        self.validation_details.set_child(validation_scroll)
        self.append(self.validation_details)
    
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
        
        print(f"🔧 Populated gRPC method: {service_name}.{method_name}")
        self._emit_request_ready()

    def populate_network_service(self, host, port, service_name):
        """Populate builder with network service details"""
        # Set method to gRPC
        self.method_dropdown.set_selected(5)  # gRPC is index 5

        # Set URL to network endpoint
        self.url_entry.set_text(f"{host}:{port}")

        # Update current request
        self.current_request.update({
            "type": "grpc",
            "method": "gRPC",
            "url": f"{host}:{port}",
            "service_name": service_name,
            "host": host,
            "port": port
        })

        # Update headers with network service info
        headers_text = f"Service: {service_name}\nEndpoint: {host}:{port}\nSource: Network Discovery"
        self.headers_textview.get_buffer().set_text(headers_text)

        # Generate sample request body
        sample_body = f'{{\n  "// Request for {service_name} at {host}:{port}": "value"\n}}'
        self.body_textview.get_buffer().set_text(sample_body)

        print(f"🌐 Populated network service: {service_name} at {host}:{port}")
        self._emit_request_ready()

    def update_network_services(self, network_services):
        """Update the available network services"""
        self.network_services = network_services
        self.schema_validator.update_service_schemas(network_services)
        self._populate_service_dropdown()
        print(f"🔄 Updated request builder with {len(network_services)} network services")

    def _populate_service_dropdown(self):
        """Populate service dropdown with discovered services"""
        # Create service list
        service_list = ["Manual Entry"]  # Default option

        for service_key, service_info in self.network_services.items():
            health_icon = "🟢" if service_info.get("health") == "up" else "🔴"
            service_display = f"{health_icon} {service_info['name']} ({service_info['endpoint']})"
            service_list.append(service_display)

        # Update dropdown model
        string_list = Gtk.StringList()
        for service in service_list:
            string_list.append(service)

        self.service_dropdown.set_model(string_list)
        self.service_dropdown.set_selected(0)  # Default to manual entry

    def _on_service_changed(self, dropdown, param):
        """Handle service selection change"""
        selected = dropdown.get_selected()

        if selected == 0:  # Manual Entry
            self.current_service = None
            self.current_service_methods = []
            self.url_entry.set_placeholder_text("Enter URL manually...")
            self.url_entry.set_text("")
            self.health_indicator.set_text("")
            self._hide_service_methods()
            return

        # Get selected service
        service_index = selected - 1  # Adjust for "Manual Entry" offset
        service_keys = list(self.network_services.keys())

        if service_index < len(service_keys):
            service_key = service_keys[service_index]
            service_info = self.network_services[service_key]
            self.current_service = service_info

            # Update URL
            self.url_entry.set_text(service_info['endpoint'])

            # Update health indicator
            health = service_info.get('health', 'unknown')
            health_text = {
                'up': '🟢 UP',
                'down': '🔴 DOWN',
                'unknown': '🟡 UNKNOWN'
            }.get(health, '🟡 UNKNOWN')
            self.health_indicator.set_text(health_text)

            # Check if service has gRPC methods
            if 'proto_info' in service_info and service_info['proto_info']:
                proto_info = service_info['proto_info']
                if proto_info.get('reflection_available') and 'services' in proto_info:
                    self._populate_service_methods(proto_info['services'])
                    self.method_dropdown.set_selected(5)  # Set to gRPC
                else:
                    self._hide_service_methods()
            else:
                self._hide_service_methods()

            print(f"🎯 Selected service: {service_info['name']} at {service_info['endpoint']}")

    def _populate_service_methods(self, services):
        """Populate service methods dropdown"""
        methods = []
        self.current_service_methods = []

        for service in services:
            for method in service.get('methods', []):
                method_display = f"{service['name']}.{method['name']}"
                methods.append(method_display)
                self.current_service_methods.append({
                    'service_name': service['name'],
                    'method_name': method['name'],
                    'request_type': method['request_type'],
                    'response_type': method['response_type'],
                    'full_signature': method.get('full_signature', '')
                })

        if methods:
            # Update service method dropdown
            string_list = Gtk.StringList()
            for method in methods:
                string_list.append(method)

            self.service_method_dropdown.set_model(string_list)
            self.service_method_dropdown.set_selected(0)
            self.service_method_dropdown.set_visible(True)

            print(f"🔧 Populated {len(methods)} service methods")
        else:
            self._hide_service_methods()

    def _hide_service_methods(self):
        """Hide service methods dropdown"""
        self.service_method_dropdown.set_visible(False)
        self.current_service_methods = []

    def _on_service_method_changed(self, dropdown, param):
        """Handle service method selection change"""
        selected = dropdown.get_selected()

        if selected < len(self.current_service_methods):
            method_info = self.current_service_methods[selected]

            # Generate intelligent request template
            self._generate_request_template(method_info)

            print(f"⚡ Selected method: {method_info['service_name']}.{method_info['method_name']}")

    def _generate_request_template(self, method_info):
        """Generate intelligent request template based on method info"""
        # Update headers with method information
        headers_text = f"""Service: {method_info['service_name']}
Method: {method_info['method_name']}
Request-Type: {method_info['request_type']}
Response-Type: {method_info['response_type']}
Content-Type: application/grpc"""

        self.headers_textview.get_buffer().set_text(headers_text)

        # Generate smart request body template
        request_template = self._create_smart_template(method_info)
        self.body_textview.get_buffer().set_text(request_template)

        # Update current request
        self.current_request.update({
            "type": "grpc",
            "method": "gRPC",
            "service_name": method_info['service_name'],
            "method_name": method_info['method_name'],
            "request_type": method_info['request_type'],
            "response_type": method_info['response_type']
        })

        self._emit_request_ready()

    def _create_smart_template(self, method_info):
        """Create intelligent request template based on method signature"""
        method_name = method_info['method_name']
        request_type = method_info['request_type']

        # Smart template generation based on common patterns
        templates = {
            'Get': {
                'id': '12345',
                'fields': ['name', 'email', 'created_at']
            },
            'List': {
                'limit': 10,
                'offset': 0,
                'filter': {},
                'sort_by': 'created_at',
                'sort_order': 'desc'
            },
            'Create': {
                'name': 'Example Name',
                'data': {},
                'metadata': {}
            },
            'Update': {
                'id': '12345',
                'data': {},
                'update_mask': ['field1', 'field2']
            },
            'Delete': {
                'id': '12345',
                'force': False
            }
        }

        # Find matching template
        template = {}
        for pattern, template_data in templates.items():
            if pattern.lower() in method_name.lower():
                template = template_data
                break

        # Default template if no pattern matches
        if not template:
            template = {
                f"// Request for {request_type}": "",
                "data": {},
                "timestamp": "2023-01-01T00:00:00Z"
            }

        # Add method-specific comment
        template[f"// Generated for {method_info['service_name']}.{method_name}"] = ""

        return json.dumps(template, indent=2)

    def _on_refresh_services_clicked(self, button):
        """Handle refresh services button click"""
        print("🔄 Refreshing network services...")
        # This would trigger a refresh in the parent tool
        # For now, just indicate the action
        button.set_sensitive(False)
        GLib.timeout_add_seconds(1, lambda: button.set_sensitive(True))

    def _on_validate_clicked(self, button):
        """Handle validate button click"""
        if not self.current_service or not self.current_service_methods:
            self.validation_status.set_text("⚠️ Select a service and method first")
            return

        # Get current method info
        selected_method = self.service_method_dropdown.get_selected()
        if selected_method >= len(self.current_service_methods):
            self.validation_status.set_text("⚠️ No method selected")
            return

        method_info = self.current_service_methods[selected_method]

        # Get request body
        buffer = self.body_textview.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        request_body = buffer.get_text(start_iter, end_iter, False)

        # Validate
        validation_result = self.schema_validator.validate_request(
            method_info['service_name'],
            method_info['method_name'],
            request_body
        )

        # Update UI with validation results
        self._display_validation_results(validation_result)

    def _on_template_clicked(self, button):
        """Handle template button click"""
        if not self.current_service or not self.current_service_methods:
            self.validation_status.set_text("⚠️ Select a service and method first")
            return

        # Get current method info
        selected_method = self.service_method_dropdown.get_selected()
        if selected_method >= len(self.current_service_methods):
            self.validation_status.set_text("⚠️ No method selected")
            return

        method_info = self.current_service_methods[selected_method]

        # Generate template
        template = self.schema_validator.get_template_for_method(
            method_info['service_name'],
            method_info['method_name']
        )

        if template:
            template_json = json.dumps(template, indent=2)
            self.body_textview.get_buffer().set_text(template_json)
            self.validation_status.set_text(f"📋 Generated template for {method_info['method_name']}")
        else:
            self.validation_status.set_text("⚠️ Could not generate template")

    def _display_validation_results(self, validation_result):
        """Display validation results in the UI"""
        if validation_result.get('valid'):
            # Valid request
            status_text = "✅ Request is valid"
            if validation_result.get('warnings'):
                status_text += f" ({len(validation_result['warnings'])} warnings)"
            self.validation_status.set_text(status_text)
            self.validation_status.remove_css_class("validation-error")
            self.validation_status.add_css_class("validation-success")
        else:
            # Invalid request
            error_count = len(validation_result.get('errors', []))
            self.validation_status.set_text(f"❌ {error_count} validation errors")
            self.validation_status.remove_css_class("validation-success")
            self.validation_status.add_css_class("validation-error")

        # Show detailed results
        details = []

        if validation_result.get('errors'):
            details.append("🚨 ERRORS:")
            for error in validation_result['errors']:
                details.append(f"  • {error}")
            details.append("")

        if validation_result.get('warnings'):
            details.append("⚠️ WARNINGS:")
            for warning in validation_result['warnings']:
                details.append(f"  • {warning}")
            details.append("")

        if validation_result.get('suggestions'):
            details.append("💡 SUGGESTIONS:")
            for suggestion in validation_result['suggestions']:
                details.append(f"  • {suggestion}")

        if details:
            details_text = "\n".join(details)
            self.validation_textview.get_buffer().set_text(details_text)
            self.validation_details.set_visible(True)
            self.validation_details.set_expanded(True)
        else:
            self.validation_details.set_visible(False)
    
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
