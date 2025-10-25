
import logging; gui_logger = logging.getLogger(__name__)

"""
@llm-type control-system
@llm-legend proto_browser.py - system control component
@llm-key Core functionality for proto_browser
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token proto_browser: system control component
"""
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

from gi.repository import Gtk, GObject, Gio
from pathlib import Path


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
    }
    
    def __init__(self, proto_scanner):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        self.proto_scanner = proto_scanner
        self.current_services = {}  # Cache parsed services
        
        # Apply CSS class
        self.add_css_class("proto-browser")
        
        # Build UI
        self._setup_search()
        self._setup_tree_view()
        self._setup_context_menu()
        
    
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
        
    
    def _on_search_changed(self, search_entry):
        """Handle search text changes"""
        search_text = search_entry.get_text().lower()
        
        if search_text:
            # TODO: Implement filtering
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
            self.emit("proto-file-selected", file_path)
        
        elif item_type == "method":
            # Method selected - emit signal with method details
            service_name = model.get_value(tree_iter, 4)
            method_name = model.get_value(tree_iter, 5)
            request_type = model.get_value(tree_iter, 6)
            response_type = model.get_value(tree_iter, 7)
            
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
    
    def _on_open_editor(self, action, param):
        """Handle open in editor context menu action"""
        selection = self.tree_view.get_selection()
        model, tree_iter = selection.get_selected()
        
        if tree_iter:
            file_path = model.get_value(tree_iter, 3)
            # TODO: Open in external editor


# Register the widget type
GObject.type_register(ProtoBrowser)
