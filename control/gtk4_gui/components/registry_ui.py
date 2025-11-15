"""
Registry UI Component for managing graph documents

Provides UI for:
- Creating new graphs
- Listing saved graphs
- Deleting graphs
- Opening graphs in editor
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import asyncio
from collections.abc import Callable
from typing import Any

from gi.repository import Adw, GLib, Gtk


class RegistryUI:
    """UI for managing graph documents in the registry"""

    def __init__(self, doc_store_client=None):
        """Initialize registry UI"""
        self.doc_store_client = doc_store_client
        self.graphs: list[dict[str, Any]] = []

        # Callbacks
        self.on_create_graph: Callable[[str, str, str], None] | None = None
        self.on_edit_graph: Callable[[str], None] | None = None
        self.on_delete_graph: Callable[[str], None] | None = None

        # UI components
        self.graphs_list_box = None
        self.status_label = None

    def create_widget(self) -> Gtk.Widget:
        """Create the registry UI widget"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)

        # Header
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        title = Gtk.Label(label="Graph Registry")
        title.add_css_class("title-1")
        title.set_halign(Gtk.Align.START)
        header_box.append(title)

        desc = Gtk.Label(label="Create, manage, and edit graphs")
        desc.add_css_class("dim-label")
        desc.set_halign(Gtk.Align.START)
        desc.set_wrap(True)
        header_box.append(desc)
        main_box.append(header_box)

        # Create button
        create_btn = Gtk.Button(label="+ Create New Graph")
        create_btn.add_css_class("suggested-action")
        create_btn.connect("clicked", self._on_create_clicked)
        main_box.append(create_btn)

        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.append(sep)

        # Graphs list
        list_label = Gtk.Label(label="Saved Graphs")
        list_label.add_css_class("title-3")
        list_label.set_halign(Gtk.Align.START)
        main_box.append(list_label)

        # Scrolled window for graphs list
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.graphs_list_box = Gtk.ListBox()
        self.graphs_list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.graphs_list_box.add_css_class("boxed-list")
        scroll.set_child(self.graphs_list_box)
        main_box.append(scroll)

        # Status label
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.add_css_class("dim-label")
        self.status_label.set_halign(Gtk.Align.START)
        main_box.append(self.status_label)

        # Load graphs on idle (after event loop is running)
        GLib.idle_add(self._load_graphs_idle)

        return main_box

    def _on_create_clicked(self, button):
        """Handle create graph button click"""
        dialog = self._create_graph_dialog()
        dialog.present()

    def _create_graph_dialog(self) -> Adw.Dialog:
        """Create a dialog for creating new graphs"""
        dialog = Adw.Dialog()

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content_box.set_margin_top(12)
        content_box.set_margin_bottom(12)
        content_box.set_margin_start(12)
        content_box.set_margin_end(12)

        # Title
        title = Gtk.Label(label="Create New Graph")
        title.add_css_class("title-2")
        content_box.append(title)

        # Name field
        name_label = Gtk.Label(label="Graph Name")
        name_label.set_halign(Gtk.Align.START)
        content_box.append(name_label)

        name_entry = Gtk.Entry()
        name_entry.set_placeholder_text("e.g., My Workflow")
        content_box.append(name_entry)

        # Description field
        desc_label = Gtk.Label(label="Description (optional)")
        desc_label.set_halign(Gtk.Align.START)
        content_box.append(desc_label)

        desc_entry = Gtk.Entry()
        desc_entry.set_placeholder_text("e.g., A workflow for processing audio")
        content_box.append(desc_entry)

        # Graph type selector
        type_label = Gtk.Label(label="Graph Type")
        type_label.set_halign(Gtk.Align.START)
        content_box.append(type_label)

        type_combo = Gtk.ComboBoxText()
        type_combo.append("dag", "DAG (Directed Acyclic Graph)")
        type_combo.append("cyclic", "Cyclic")
        type_combo.append("cyclic_breakers", "Cyclic with Breakers")
        type_combo.append("tree", "Tree")
        type_combo.append("unrestricted", "Unrestricted")
        type_combo.set_active_id("dag")
        content_box.append(type_combo)

        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(12)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda b: dialog.close())
        button_box.append(cancel_btn)

        create_btn = Gtk.Button(label="Create")
        create_btn.add_css_class("suggested-action")
        create_btn.connect(
            "clicked",
            lambda b: self._handle_create_graph(
                name_entry.get_text(),
                desc_entry.get_text(),
                type_combo.get_active_id(),
                dialog,
            ),
        )
        button_box.append(create_btn)

        content_box.append(button_box)

        dialog.set_child(content_box)
        dialog.set_title("Create New Graph")
        return dialog

    def _handle_create_graph(
        self, name: str, description: str, graph_type: str, dialog
    ):
        """Handle graph creation"""
        if not name.strip():
            self._update_status("❌ Graph name is required")
            return

        dialog.close()
        self._update_status(f"Creating graph: {name}...")

        if self.on_create_graph:
            self.on_create_graph(name, description, graph_type)

        # Reload graphs
        try:
            asyncio.ensure_future(self._load_graphs())
        except RuntimeError:
            # No event loop yet, schedule for later
            GLib.idle_add(self._load_graphs_idle)

    def _load_graphs_idle(self):
        """Idle callback to load graphs when event loop is ready"""
        try:
            # Use ensure_future instead of create_task for better compatibility
            asyncio.ensure_future(self._load_graphs())
        except RuntimeError:
            # No event loop yet, try again later
            GLib.idle_add(self._load_graphs_idle)
        return False  # Don't repeat

    async def _load_graphs(self):
        """Load graphs from document store"""
        if not self.doc_store_client:
            self._update_status("⚠️ Document store not available")
            return

        try:
            self._update_status("Loading graphs...")
            self.graphs = await self.doc_store_client.list_graphs()
            self._render_graphs_list()
            self._update_status(f"✅ Loaded {len(self.graphs)} graphs")
        except Exception as e:
            self._update_status(f"❌ Error loading graphs: {e}")
            print(f"Error: {e}")

    async def _delete_graph_async(self, graph_id: str):
        """Delete graph from document store"""
        if not self.doc_store_client:
            self._update_status("⚠️ Document store not available")
            return

        try:
            self._update_status("Deleting graph...")
            await self.doc_store_client.delete_graph(graph_id)
            self._update_status("✅ Graph deleted")
            await self._load_graphs()
        except Exception as e:
            self._update_status(f"❌ Error deleting graph: {e}")
            print(f"Error: {e}")

    def _render_graphs_list(self):
        """Render the list of graphs"""
        # Clear existing items
        while True:
            child = self.graphs_list_box.get_first_child()
            if child is None:
                break
            self.graphs_list_box.remove(child)

        if not self.graphs:
            empty_label = Gtk.Label(label="No graphs yet. Create one to get started!")
            empty_label.add_css_class("dim-label")
            empty_label.set_margin_top(24)
            empty_label.set_margin_bottom(24)
            self.graphs_list_box.append(empty_label)
            return

        # Add graph items
        for graph in self.graphs:
            row = self._create_graph_row(graph)
            self.graphs_list_box.append(row)

    def _create_graph_row(self, graph: dict[str, Any]) -> Gtk.Widget:
        """Create a row for a graph in the list"""
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row_box.set_margin_top(8)
        row_box.set_margin_bottom(8)
        row_box.set_margin_start(8)
        row_box.set_margin_end(8)

        # Graph info
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info_box.set_hexpand(True)

        name_label = Gtk.Label(label=graph.get("name", "Unnamed"))
        name_label.add_css_class("title-4")
        name_label.set_halign(Gtk.Align.START)
        info_box.append(name_label)

        version_label = Gtk.Label(label=f"v{graph.get('version', 1)}")
        version_label.add_css_class("dim-label")
        version_label.set_halign(Gtk.Align.START)
        info_box.append(version_label)

        row_box.append(info_box)

        # Action buttons
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)

        edit_btn = Gtk.Button(label="Edit")
        edit_btn.connect("clicked", lambda b: self._on_edit_clicked(graph["id"]))
        action_box.append(edit_btn)

        delete_btn = Gtk.Button(label="Delete")
        delete_btn.add_css_class("destructive-action")
        delete_btn.connect(
            "clicked",
            lambda b: self._on_delete_clicked(
                graph["id"], graph.get("name", "Unnamed")
            ),
        )
        action_box.append(delete_btn)

        row_box.append(action_box)

        return row_box

    def _on_edit_clicked(self, graph_id: str):
        """Handle edit button click"""
        self._update_status(f"Opening graph {graph_id}...")
        if self.on_edit_graph:
            self.on_edit_graph(graph_id)

    def _on_delete_clicked(self, graph_id: str, graph_name: str):
        """Handle delete button click"""
        dialog = Adw.AlertDialog()
        dialog.set_heading(f"Delete '{graph_name}'?")
        dialog.set_body("This action cannot be undone.")
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("delete", "Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect(
            "response",
            lambda d, response: self._handle_delete_response(response, graph_id),
        )
        dialog.present()

    def _handle_delete_response(self, response: str, graph_id: str):
        """Handle delete confirmation"""
        if response == "delete":
            if self.on_delete_graph:
                self.on_delete_graph(graph_id)
            asyncio.create_task(self._delete_graph_async(graph_id))

    def _update_status(self, message: str):
        """Update status label"""
        if self.status_label:
            self.status_label.set_label(message)
