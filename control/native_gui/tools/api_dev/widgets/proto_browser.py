"""
📁 Proto Browser Widget - Native GTK Implementation

Displays proto files, services, and methods in a tree structure.
Pure GTK TreeView with custom models - no web bullshit.

Features:
- Hierarchical file/service/method display
- Search and filtering
- Selection handling
- Service parsing integration
"""

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GObject, Gio, GLib
from pathlib import Path
import time


class ProtoBrowser(Gtk.Box):
    """
    Proto file browser widget using native GTK TreeView.
    
    Structure:
    ┌─────────────────────────┐
    │ 🔍 Search Box           │
    ├─────────────────────────┤
    │ 📁 proto/               │
    │   ├─ 📄 llm.proto       │
    │   │   └─ 🔧 LLMService  │
    │   │       ├─ Generate   │
    │   │       └─ Stream     │
    │   └─ 📄 chat.proto      │
    │       └─ 🔧 ChatService │
    └─────────────────────────┘
    """
    
    # Custom signals
    __gsignals__ = {
        'proto-file-selected': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        'service-method-selected': (GObject.SignalFlags.RUN_FIRST, None, (str, str, str, str)),
        'network-service-selected': (GObject.SignalFlags.RUN_FIRST, None, (str, int, str)),  # host, port, service_name
    }
    
    def __init__(self, proto_scanner, network_scanner=None, reflection_client=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        self.proto_scanner = proto_scanner
        self.network_scanner = network_scanner
        self.reflection_client = reflection_client
        self.current_services = {}  # Cache parsed services
        self.network_services = {}  # Cache network discovered services

        # Apply CSS class
        self.add_css_class("proto-browser")

        # Build UI
        self._setup_mode_selector()
        self._setup_search()
        self._setup_tree_view()
        self._setup_context_menu()

        print("📁 Proto browser widget initialized")

    def _setup_mode_selector(self):
        """Create mode selector for file vs network discovery"""
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        mode_box.set_margin_start(8)
        mode_box.set_margin_end(8)
        mode_box.set_margin_top(8)

        # Mode label
        mode_label = Gtk.Label(label="Source:")
        mode_box.append(mode_label)

        # Mode dropdown
        self.mode_dropdown = Gtk.DropDown()
        modes = ["📁 Proto Files", "🌐 Network Services", "🔍 Both"]
        string_list = Gtk.StringList()
        for mode in modes:
            string_list.append(mode)
        self.mode_dropdown.set_model(string_list)
        self.mode_dropdown.set_selected(0)  # Default to proto files
        self.mode_dropdown.connect("notify::selected", self._on_mode_changed)
        mode_box.append(self.mode_dropdown)

        # Network scan button
        self.scan_network_button = Gtk.Button(label="🔍 Scan Network")
        self.scan_network_button.connect("clicked", self._on_scan_network_clicked)
        self.scan_network_button.set_sensitive(self.network_scanner is not None)
        mode_box.append(self.scan_network_button)

        # Reflection test button
        self.test_reflection_button = Gtk.Button(label="🔍 Test Reflection")
        self.test_reflection_button.connect("clicked", self._on_test_reflection_clicked)
        self.test_reflection_button.set_sensitive(self.reflection_client is not None)
        mode_box.append(self.test_reflection_button)

        self.append(mode_box)

    def _setup_search(self):
        """Create search entry for filtering"""
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        # Search icon
        search_icon = Gtk.Image.new_from_icon_name("system-search-symbolic")
        search_box.append(search_icon)
        
        # Search entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search proto files...")
        self.search_entry.connect("search-changed", self._on_search_changed)
        search_box.append(self.search_entry)
        
        self.append(search_box)
    
    def _setup_tree_view(self):
        """Create the main tree view for proto files/services"""
        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        
        # Create tree store model
        # Columns: icon, name, type, path, service_name, method_name, request_type, response_type
        self.tree_store = Gtk.TreeStore(str, str, str, str, str, str, str, str)
        
        # Create tree view
        self.tree_view = Gtk.TreeView(model=self.tree_store)
        self.tree_view.set_headers_visible(False)
        self.tree_view.set_enable_search(True)
        self.tree_view.set_search_column(1)  # Search by name
        
        # Create column with icon and text
        column = Gtk.TreeViewColumn()
        
        # Icon renderer
        icon_renderer = Gtk.CellRendererText()
        column.pack_start(icon_renderer, False)
        column.add_attribute(icon_renderer, "text", 0)
        
        # Text renderer
        text_renderer = Gtk.CellRendererText()
        column.pack_start(text_renderer, True)
        column.add_attribute(text_renderer, "text", 1)
        
        self.tree_view.append_column(column)
        
        # Connect selection signal
        selection = self.tree_view.get_selection()
        selection.connect("changed", self._on_selection_changed)
        
        # Connect double-click signal
        self.tree_view.connect("row-activated", self._on_row_activated)
        
        scrolled.set_child(self.tree_view)
        self.append(scrolled)
    
    def _setup_context_menu(self):
        """Create context menu for tree items"""
        self.context_menu = Gtk.PopoverMenu()
        
        # Create menu model
        menu_model = Gio.Menu()
        menu_model.append("Parse Services", "browser.parse-services")
        menu_model.append("Copy Path", "browser.copy-path")
        menu_model.append("Open in Editor", "browser.open-editor")
        
        self.context_menu.set_menu_model(menu_model)
        
        # Create action group
        action_group = Gio.SimpleActionGroup()
        
        parse_action = Gio.SimpleAction.new("parse-services", None)
        parse_action.connect("activate", self._on_parse_services)
        action_group.add_action(parse_action)
        
        copy_action = Gio.SimpleAction.new("copy-path", None)
        copy_action.connect("activate", self._on_copy_path)
        action_group.add_action(copy_action)
        
        open_action = Gio.SimpleAction.new("open-editor", None)
        open_action.connect("activate", self._on_open_editor)
        action_group.add_action(open_action)
        
        self.tree_view.insert_action_group("browser", action_group)
        
        # Connect right-click
        gesture = Gtk.GestureClick.new()
        gesture.set_button(3)  # Right mouse button
        gesture.connect("pressed", self._on_right_click)
        self.tree_view.add_controller(gesture)
    
    def populate_files(self, proto_files):
        """Populate tree view with proto files"""
        print(f"📁 Populating {len(proto_files)} proto files")
        
        # Clear existing data
        self.tree_store.clear()
        self.current_services.clear()
        
        # Group files by directory
        directories = {}
        for file_info in proto_files:
            file_path = Path(file_info["path"])
            dir_path = file_path.parent
            
            if dir_path not in directories:
                directories[dir_path] = []
            directories[dir_path].append(file_info)
        
        # Add directories and files to tree
        for dir_path, files in sorted(directories.items()):
            # Add directory node
            dir_iter = self.tree_store.append(None, [
                "📁", str(dir_path), "directory", str(dir_path), "", "", "", ""
            ])
            
            # Add files under directory
            for file_info in sorted(files, key=lambda f: f["name"]):
                file_iter = self.tree_store.append(dir_iter, [
                    "📄", file_info["name"], "file", file_info["path"], "", "", "", ""
                ])
        
        # Expand all directories
        self.tree_view.expand_all()
    
    def populate_services(self, services):
        """Add services and methods under the selected proto file"""
        selection = self.tree_view.get_selection()
        model, tree_iter = selection.get_selected()
        
        if not tree_iter:
            return
        
        # Get the file path
        file_path = model.get_value(tree_iter, 3)
        
        # Remove existing service children
        child_iter = model.iter_children(tree_iter)
        while child_iter:
            next_iter = model.iter_next(child_iter)
            model.remove(child_iter)
            child_iter = next_iter
        
        # Add services
        for service in services:
            service_iter = model.append(tree_iter, [
                "🔧", service["name"], "service", file_path, service["name"], "", "", ""
            ])
            
            # Add methods under service
            for method in service["methods"]:
                model.append(service_iter, [
                    "⚡", method["name"], "method", file_path,
                    service["name"], method["name"],
                    method["request_type"], method["response_type"]
                ])
        
        # Expand the file node to show services
        self.tree_view.expand_row(model.get_path(tree_iter), False)
        
        # Cache services for this file
        self.current_services[file_path] = services
        
        print(f"🔧 Added {len(services)} services to tree")

    def populate_network_services(self, network_services):
        """Add network-discovered services to the tree"""
        print(f"🌐 Populating {len(network_services)} network services")

        # Clear existing data
        self.tree_store.clear()
        self.network_services = network_services

        # Group services by source
        sources = {}
        for service_key, service_info in network_services.items():
            source = service_info.get("source", "unknown")
            if source not in sources:
                sources[source] = []
            sources[source].append(service_info)

        # Add source groups to tree
        for source, services in sources.items():
            # Add source node
            source_icon = {
                "consul": "🏛️",
                "port_scan": "🔍",
                "docker": "🐳",
                "known_endpoint": "📍"
            }.get(source, "🌐")

            source_iter = self.tree_store.append(None, [
                source_icon, f"{source.title()} ({len(services)})", "source", "", "", "", "", ""
            ])

            # Add services under source
            for service_info in services:
                service_iter = self.tree_store.append(source_iter, [
                    "🚀",
                    f"{service_info['name']} ({service_info['endpoint']})",
                    "network_service",
                    service_info['endpoint'],
                    service_info['name'],
                    str(service_info['port']),
                    service_info['host'],
                    service_info.get('health', 'unknown')
                ])

                # If we have reflection info, add methods
                if 'proto_info' in service_info and service_info['proto_info']:
                    proto_info = service_info['proto_info']
                    if 'services' in proto_info:
                        for reflected_service in proto_info['services']:
                            for method in reflected_service.get('methods', []):
                                self.tree_store.append(service_iter, [
                                    "⚡",
                                    method['name'],
                                    "network_method",
                                    service_info['endpoint'],
                                    reflected_service['name'],
                                    method['name'],
                                    method['request_type'],
                                    method['response_type']
                                ])

        # Expand all nodes
        self.tree_view.expand_all()
        print(f"🌐 Added {len(network_services)} network services to tree")

    def _on_mode_changed(self, dropdown, param):
        """Handle mode selection change"""
        selected = dropdown.get_selected()
        modes = ["📁 Proto Files", "🌐 Network Services", "🔍 Both"]

        if selected < len(modes):
            mode = modes[selected]
            print(f"🔄 Switched to mode: {mode}")

            if "Network" in mode:
                # Enable network-related buttons
                self.scan_network_button.set_sensitive(self.network_scanner is not None)
                self.test_reflection_button.set_sensitive(self.reflection_client is not None)
            else:
                # Focus on file-based discovery
                pass

    def _on_scan_network_clicked(self, button):
        """Handle network scan button click"""
        if not self.network_scanner:
            print("❌ Network scanner not available")
            return

        print("🌐 Starting network service discovery...")

        # Disable button during scan
        button.set_sensitive(False)
        button.set_label("🔄 Scanning...")

        # Scan in background to keep UI responsive
        GLib.idle_add(self._do_network_scan, button)

    def _do_network_scan(self, button):
        """Perform network scan (called from idle callback)"""
        try:
            # Discover services
            result = self.network_scanner.discover_services(force_rescan=True)

            if result.get("success"):
                network_services = result.get("services", {})

                # If we have reflection client, try to get service definitions
                if self.reflection_client:
                    self._enhance_with_reflection(network_services)

                # Populate tree with network services
                self.populate_network_services(network_services)

                # Update button with count
                count = len(network_services)
                button.set_label(f"✅ Found {count} services")
                print(f"✅ Network scan found {count} services")
            else:
                error = result.get("error", "Unknown error")
                button.set_label("❌ Scan failed")
                print(f"❌ Network scan failed: {error}")

        except Exception as e:
            button.set_label("❌ Scan failed")
            print(f"❌ Network scan error: {e}")

        finally:
            # Re-enable button
            button.set_sensitive(True)

            # Reset button text after 3 seconds
            GLib.timeout_add_seconds(3, lambda: button.set_label("🔍 Scan Network"))

        return False  # Don't repeat

    def _enhance_with_reflection(self, network_services):
        """Enhance network services with reflection data"""
        for service_key, service_info in network_services.items():
            if service_info.get('health') == 'up':
                try:
                    # Test reflection support
                    reflection_result = self.reflection_client.test_reflection_support(
                        service_info['host'], service_info['port']
                    )

                    if reflection_result.get('supported'):
                        # Get service definitions
                        definitions = self.reflection_client.discover_service_definitions(
                            service_info['host'], service_info['port']
                        )

                        if definitions.get('success'):
                            service_info['proto_info'] = {
                                'reflection_available': True,
                                'services': definitions.get('services', [])
                            }
                            print(f"✅ Enhanced {service_info['name']} with reflection data")

                except Exception as e:
                    print(f"⚠️ Reflection enhancement failed for {service_info['name']}: {e}")

    def _on_test_reflection_clicked(self, button):
        """Handle reflection test button click"""
        if not self.reflection_client:
            print("❌ Reflection client not available")
            return

        print("🔍 Testing reflection on discovered services...")

        # Test reflection on all discovered network services
        for service_key, service_info in self.network_services.items():
            if service_info.get('health') == 'up':
                result = self.reflection_client.test_reflection_support(
                    service_info['host'], service_info['port']
                )

                status = "✅" if result.get('supported') else "❌"
                print(f"{status} {service_info['name']} ({service_info['endpoint']}) - Reflection: {result.get('supported', False)}")

    def _on_search_changed(self, search_entry):
        """Handle search text changes"""
        search_text = search_entry.get_text().lower()
        
        if search_text:
            # TODO: Implement filtering
            print(f"🔍 Searching for: {search_text}")
        else:
            # Clear filter
            pass
    
    def _on_selection_changed(self, selection):
        """Handle tree selection changes"""
        model, tree_iter = selection.get_selected()
        
        if not tree_iter:
            return
        
        item_type = model.get_value(tree_iter, 2)
        item_name = model.get_value(tree_iter, 1)
        file_path = model.get_value(tree_iter, 3)
        
        if item_type == "file":
            # Proto file selected - emit signal to parse services
            print(f"📄 Selected proto file: {file_path}")
            self.emit("proto-file-selected", file_path)
        
        elif item_type == "method":
            # Method selected - emit signal with method details
            service_name = model.get_value(tree_iter, 4)
            method_name = model.get_value(tree_iter, 5)
            request_type = model.get_value(tree_iter, 6)
            response_type = model.get_value(tree_iter, 7)

            print(f"⚡ Selected method: {service_name}.{method_name}")
            self.emit("service-method-selected", service_name, method_name, request_type, response_type)

        elif item_type == "network_service":
            # Network service selected - emit signal with service details
            endpoint = model.get_value(tree_iter, 3)
            service_name = model.get_value(tree_iter, 4)
            port = int(model.get_value(tree_iter, 5))
            host = model.get_value(tree_iter, 6)

            print(f"🌐 Selected network service: {service_name} at {endpoint}")
            self.emit("network-service-selected", host, port, service_name)

        elif item_type == "network_method":
            # Network method selected - emit signal with method details
            service_name = model.get_value(tree_iter, 4)
            method_name = model.get_value(tree_iter, 5)
            request_type = model.get_value(tree_iter, 6)
            response_type = model.get_value(tree_iter, 7)
            endpoint = model.get_value(tree_iter, 3)

            print(f"⚡ Selected network method: {service_name}.{method_name} at {endpoint}")
            self.emit("service-method-selected", service_name, method_name, request_type, response_type)
    
    def _on_row_activated(self, tree_view, path, column):
        """Handle double-click on tree row"""
        model = tree_view.get_model()
        tree_iter = model.get_iter(path)
        
        item_type = model.get_value(tree_iter, 2)
        
        if item_type == "file":
            # Double-click on file - expand/collapse
            if tree_view.row_expanded(path):
                tree_view.collapse_row(path)
            else:
                tree_view.expand_row(path, False)
    
    def _on_right_click(self, gesture, n_press, x, y):
        """Handle right-click for context menu"""
        # Get clicked item
        path_info = self.tree_view.get_path_at_pos(int(x), int(y))
        if path_info:
            path, column, cell_x, cell_y = path_info
            self.tree_view.get_selection().select_path(path)
            
            # Show context menu
            self.context_menu.set_parent(self.tree_view)
            self.context_menu.popup()
    
    def _on_parse_services(self, action, param):
        """Handle parse services context menu action"""
        selection = self.tree_view.get_selection()
        model, tree_iter = selection.get_selected()
        
        if tree_iter:
            file_path = model.get_value(tree_iter, 3)
            self.emit("proto-file-selected", file_path)
    
    def _on_copy_path(self, action, param):
        """Handle copy path context menu action"""
        selection = self.tree_view.get_selection()
        model, tree_iter = selection.get_selected()
        
        if tree_iter:
            file_path = model.get_value(tree_iter, 3)
            # Copy to clipboard
            clipboard = self.get_clipboard()
            clipboard.set_text(file_path, -1)
            print(f"📋 Copied path: {file_path}")
    
    def _on_open_editor(self, action, param):
        """Handle open in editor context menu action"""
        selection = self.tree_view.get_selection()
        model, tree_iter = selection.get_selected()
        
        if tree_iter:
            file_path = model.get_value(tree_iter, 3)
            # TODO: Open in external editor
            print(f"📝 Open in editor: {file_path}")


# Register the widget type
GObject.type_register(ProtoBrowser)
