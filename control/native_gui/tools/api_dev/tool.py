"""
@llm-type control-system
@llm-legend tool.py - system control component
@llm-key Core functionality for tool
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token tool: system control component
"""
"""
🔧 API Development Tool - Main Tool Class

Implements the API development functionality as a plugin tool.
Provides proto scanning, request building, and response viewing.
"""

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GLib
from pathlib import Path

from ...core.tool_manager import BaseTool
from .widgets.proto_browser import ProtoBrowser
from .widgets.request_builder import RequestBuilder
from .widgets.response_viewer import ResponseViewer
from .bridge.proto_scanner import ProtoScanner
from .bridge.grpc_client import GRPCClient
from .bridge.http_client import HTTPClient
from .bridge.network_scanner import NetworkScanner
from .bridge.reflection_client import ReflectionClient


class APIDevTool(BaseTool):
    """
    API Development Tool plugin.
    
    Provides a three-pane interface for API development:
    - Proto Browser: File and service discovery
    - Request Builder: HTTP/gRPC request construction
    - Response Viewer: Response display and formatting
    """
    
    def __init__(self):
        super().__init__()
        self.name = "API Dev"
        self.icon = "🔧"
        self.description = "API Development Tool - Proto scanning, request building, response viewing"
        self.shortcut = "Ctrl+1"
        
        # Backend services
        self.proto_scanner = None
        self.grpc_client = None
        self.http_client = None
        self.network_scanner = None
        self.reflection_client = None
        
        # UI components
        self.proto_browser = None
        self.request_builder = None
        self.response_viewer = None
        
        # Action buttons for header
        self.scan_button = None
        self.send_button = None
    
    def create_widget(self):
        """Create the main API dev tool widget"""
        # Initialize backend services
        # We'll get project_root from the application context
        project_root = Path(__file__).parent.parent.parent.parent.parent
        self.proto_scanner = ProtoScanner(project_root)
        self.grpc_client = GRPCClient()
        self.http_client = HTTPClient()
        self.network_scanner = NetworkScanner(project_root)
        self.reflection_client = ReflectionClient()
        
        # Create main three-pane layout
        main_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        main_paned.set_shrink_start_child(False)
        main_paned.set_shrink_end_child(False)
        main_paned.add_css_class("api-dev-tool")
        
        # Left pane: Proto browser with network discovery (300px default)
        self.proto_browser = ProtoBrowser(
            self.proto_scanner,
            self.network_scanner,
            self.reflection_client
        )
        main_paned.set_start_child(self.proto_browser)
        main_paned.set_position(300)
        
        # Right side: Request builder + Response viewer
        right_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        right_paned.set_shrink_start_child(False)
        right_paned.set_shrink_end_child(False)
        
        # Center pane: Request builder
        self.request_builder = RequestBuilder()
        right_paned.set_start_child(self.request_builder)
        
        # Right pane: Response viewer
        self.response_viewer = ResponseViewer()
        right_paned.set_end_child(self.response_viewer)
        
        # Set equal split for request/response
        right_paned.set_position(400)
        
        main_paned.set_end_child(right_paned)
        
        # Connect signals
        self._connect_signals()
        
        print("✅ API Dev Tool widget created")
        return main_paned
    
    def _connect_signals(self):
        """Connect widget signals for inter-component communication"""
        # Proto browser signals
        self.proto_browser.connect("proto-file-selected", self._on_proto_file_selected)
        self.proto_browser.connect("service-method-selected", self._on_service_method_selected)
        self.proto_browser.connect("network-service-selected", self._on_network_service_selected)
        
        # Request builder signals
        self.request_builder.connect("request-ready", self._on_request_ready)
    
    def get_actions(self):
        """Get tool-specific header actions"""
        return [
            {
                'label': '🔍 Scan Proto',
                'callback': self._on_scan_proto_clicked,
                'css_class': 'primary-button'
            },
            {
                'label': '🌐 Discover Services',
                'callback': self._on_discover_services_clicked,
                'css_class': 'secondary-button'
            },
            {
                'label': '🚀 Send Request',
                'callback': self._on_send_request_clicked,
                'css_class': 'danger-button'
            }
        ]
    
    def on_activate(self):
        """Called when tool becomes active"""
        super().on_activate()
        print("🔧 API Dev Tool activated")
    
    def on_deactivate(self):
        """Called when tool becomes inactive"""
        super().on_deactivate()
        print("🔧 API Dev Tool deactivated")
    
    def _on_scan_proto_clicked(self, button):
        """Handle scan proto files button click"""
        print("🔍 Scanning proto files...")
        
        # Disable button during scan
        button.set_sensitive(False)
        button.set_label("🔄 Scanning...")
        
        # Scan in background to keep UI responsive
        GLib.idle_add(self._do_proto_scan, button)
    
    def _do_proto_scan(self, button):
        """Perform proto file scan (called from idle callback)"""
        try:
            # Direct method call - no HTTP bridge needed!
            result = self.proto_scanner.scan_proto_files()
            
            if result.get("success"):
                proto_files = result.get("proto_files", [])
                self.proto_browser.populate_files(proto_files)
                
                # Update button with count
                count = len(proto_files)
                button.set_label(f"✅ Found {count} files")
                print(f"✅ Found {count} proto files")
            else:
                error = result.get("error", "Unknown error")
                button.set_label("❌ Scan failed")
                print(f"❌ Proto scan failed: {error}")
                
        except Exception as e:
            button.set_label("❌ Scan failed")
            print(f"❌ Proto scan error: {e}")
        
        finally:
            # Re-enable button
            button.set_sensitive(True)
            
            # Reset button text after 3 seconds
            GLib.timeout_add_seconds(3, lambda: button.set_label("🔍 Scan Proto"))
        
        return False  # Don't repeat

    def _on_discover_services_clicked(self, button):
        """Handle discover services button click"""
        print("🌐 Discovering network services...")

        # Disable button during discovery
        button.set_sensitive(False)
        button.set_label("🔄 Discovering...")

        # Discover in background to keep UI responsive
        GLib.idle_add(self._do_service_discovery, button)

    def _do_service_discovery(self, button):
        """Perform service discovery (called from idle callback)"""
        try:
            # Discover network services
            result = self.network_scanner.discover_services(force_rescan=True)

            if result.get("success"):
                network_services = result.get("services", {})

                # Enhance with reflection if available
                if self.reflection_client:
                    for service_key, service_info in network_services.items():
                        if service_info.get('health') == 'up':
                            try:
                                reflection_result = self.reflection_client.discover_service_definitions(
                                    service_info['host'], service_info['port']
                                )

                                if reflection_result.get('success'):
                                    service_info['proto_info'] = {
                                        'reflection_available': True,
                                        'services': reflection_result.get('services', [])
                                    }
                                    print(f"✅ Enhanced {service_info['name']} with reflection")

                            except Exception as e:
                                print(f"⚠️ Reflection failed for {service_info['name']}: {e}")

                # Populate proto browser with network services
                self.proto_browser.populate_network_services(network_services)

                # Update request builder with network services
                self.request_builder.update_network_services(network_services)

                # Update button with count
                count = len(network_services)
                button.set_label(f"✅ Found {count} services")
                print(f"✅ Service discovery found {count} services")
            else:
                error = result.get("error", "Unknown error")
                button.set_label("❌ Discovery failed")
                print(f"❌ Service discovery failed: {error}")

        except Exception as e:
            button.set_label("❌ Discovery failed")
            print(f"❌ Service discovery error: {e}")

        finally:
            # Re-enable button
            button.set_sensitive(True)

            # Reset button text after 3 seconds
            GLib.timeout_add_seconds(3, lambda: button.set_label("🌐 Discover Services"))

        return False  # Don't repeat

    def _on_network_service_selected(self, browser, host, port, service_name):
        """Handle network service selection"""
        print(f"🌐 Selected network service: {service_name} at {host}:{port}")

        # Update request builder with network endpoint
        self.request_builder.populate_network_service(host, port, service_name)

        # Try to get service definition via reflection
        if self.reflection_client:
            try:
                result = self.reflection_client.discover_service_definitions(host, port)
                if result.get('success'):
                    services = result.get('services', [])
                    if services:
                        # Find the selected service and populate its methods
                        for service in services:
                            if service['name'] == service_name:
                                print(f"🔍 Found service definition for {service_name}")
                                # You could populate methods here
                                break

            except Exception as e:
                print(f"⚠️ Failed to get service definition: {e}")
    
    def _on_proto_file_selected(self, browser, file_path):
        """Handle proto file selection"""
        print(f"📁 Selected proto file: {file_path}")
        
        # Parse services from the selected file
        try:
            result = self.proto_scanner.parse_proto_services(file_path)
            if result.get("success"):
                services = result.get("services", [])
                browser.populate_services(services)
                print(f"🔧 Found {len(services)} services")
            else:
                print(f"❌ Failed to parse proto: {result.get('error')}")
        except Exception as e:
            print(f"❌ Proto parsing error: {e}")
    
    def _on_service_method_selected(self, browser, service_name, method_name, request_type, response_type):
        """Handle service method selection"""
        print(f"⚡ Selected method: {service_name}.{method_name}")
        
        # Populate request builder with method details
        self.request_builder.populate_grpc_method(
            service_name, method_name, request_type, response_type
        )
    
    def _on_request_ready(self, builder, request_data):
        """Handle request ready signal from builder"""
        print("🎯 Request ready for sending")
        # Enable send button if we have one
        if self.send_button:
            self.send_button.set_sensitive(True)
    
    def _on_send_request_clicked(self, button):
        """Handle send request button click"""
        print("🚀 Sending request...")
        
        # Get request data from builder
        request_data = self.request_builder.get_request_data()
        
        if not request_data:
            print("❌ No request data available")
            return
        
        # Disable button during request
        button.set_sensitive(False)
        button.set_label("🔄 Sending...")
        
        # Send in background
        GLib.idle_add(self._do_send_request, button, request_data)
    
    def _do_send_request(self, button, request_data):
        """Perform the actual request (called from idle callback)"""
        try:
            # Determine request type and send accordingly
            if request_data.get("type") == "grpc":
                response = self.grpc_client.send_request(request_data)
            else:
                response = self.http_client.send_request(request_data)
            
            # Display response
            self.response_viewer.display_response(response)
            
            # Update button
            status = response.get("status", 0)
            if 200 <= status < 300:
                button.set_label("✅ Success")
            else:
                button.set_label("❌ Error")
                
        except Exception as e:
            print(f"❌ Request error: {e}")
            button.set_label("❌ Failed")
            
            # Show error in response viewer
            error_response = {
                "status": 0,
                "error": str(e),
                "duration": 0
            }
            self.response_viewer.display_response(error_response)
        
        finally:
            # Re-enable button
            button.set_sensitive(True)
            
            # Reset button text after 3 seconds
            GLib.timeout_add_seconds(3, lambda: button.set_label("🚀 Send Request"))
        
        return False  # Don't repeat
