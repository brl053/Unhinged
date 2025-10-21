"""
🎛️ Main Window - Native GTK API Development Tool

Pure GTK4 implementation of the API dev tool interface.
Three-pane layout: Proto Browser | Request Builder | Response Viewer

No WebKit. No JavaScript. No HTML/CSS. Pure native widgets.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from pathlib import Path

from .widgets.proto_browser import ProtoBrowser
from .widgets.request_builder import RequestBuilder
from .widgets.response_viewer import ResponseViewer
from .bridge.proto_scanner import ProtoScanner
from .bridge.grpc_client import GRPCClient
from .bridge.http_client import HTTPClient


class MainWindow(Gtk.ApplicationWindow):
    """
    Main application window with three-pane layout.
    
    Layout:
    ┌─────────────────────────────────────────────────────────┐
    │ Header Bar (title, menu, actions)                      │
    ├─────────────┬─────────────────┬─────────────────────────┤
    │ Proto       │ Request         │ Response                │
    │ Browser     │ Builder         │ Viewer                  │
    │             │                 │                         │
    │ - Files     │ - Method/URL    │ - Status                │
    │ - Services  │ - Headers       │ - Headers               │
    │ - Methods   │ - Body          │ - Body                  │
    │             │ - Send Button   │ - Timing                │
    └─────────────┴─────────────────┴─────────────────────────┘
    """
    
    def __init__(self, application, project_root):
        super().__init__(
            application=application,
            title="🔧 Unhinged API Dev Tool",
            default_width=1400,
            default_height=900
        )
        
        self.project_root = project_root
        
        # Initialize backend services (direct Python objects - no HTTP bridge!)
        self.proto_scanner = ProtoScanner(project_root)
        self.grpc_client = GRPCClient()
        self.http_client = HTTPClient()
        
        # Build UI
        self._setup_header_bar()
        self._setup_main_layout()
        self._connect_signals()
        
        # Apply CSS class for theming
        self.add_css_class("api-dev-window")
        
        print("✅ Native GTK main window initialized")
    
    def _setup_header_bar(self):
        """Create and configure the header bar"""
        self.header_bar = Gtk.HeaderBar()
        self.set_titlebar(self.header_bar)
        
        # Title with icon
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        title_label = Gtk.Label(label="🔧 API Dev Tool")
        title_label.add_css_class("title")
        title_box.append(title_label)
        
        self.header_bar.set_title_widget(title_box)
        
        # Left side buttons
        scan_button = Gtk.Button(label="🔍 Scan Proto")
        scan_button.connect("clicked", self._on_scan_proto_clicked)
        scan_button.add_css_class("suggested-action")
        self.header_bar.pack_start(scan_button)
        
        # Right side buttons
        send_button = Gtk.Button(label="🚀 Send Request")
        send_button.connect("clicked", self._on_send_request_clicked)
        send_button.add_css_class("destructive-action")
        self.header_bar.pack_end(send_button)
        
        # Store references for later use
        self.scan_button = scan_button
        self.send_button = send_button
    
    def _setup_main_layout(self):
        """Create the three-pane main layout"""
        # Main horizontal paned container
        main_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        main_paned.set_shrink_start_child(False)
        main_paned.set_shrink_end_child(False)
        
        # Left pane: Proto browser (300px default)
        self.proto_browser = ProtoBrowser(self.proto_scanner)
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
        
        # Set as window content
        self.set_child(main_paned)
    
    def _connect_signals(self):
        """Connect widget signals for inter-component communication"""
        # Proto browser signals
        self.proto_browser.connect("proto-file-selected", self._on_proto_file_selected)
        self.proto_browser.connect("service-method-selected", self._on_service_method_selected)
        
        # Request builder signals
        self.request_builder.connect("request-ready", self._on_request_ready)
    
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
    
    def new_request(self):
        """Create a new request (called from keyboard shortcut)"""
        self.request_builder.clear_request()
        print("📝 New request created")
    
    def send_request(self):
        """Send current request (called from keyboard shortcut)"""
        if self.send_button.get_sensitive():
            self._on_send_request_clicked(self.send_button)
