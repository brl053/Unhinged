"""
Graph Workspace Tabs Component

Provides a tabbed interface for the graph workspace with three main sections:
- Registry: Node and graph registry/library
- Editor: Visual graph editing canvas
- Metrics: Execution metrics and monitoring
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
from typing import Callable, Optional, Dict, Any

# Import registry UI
try:
    from .registry_ui import RegistryUI
    REGISTRY_UI_AVAILABLE = True
except ImportError:
    REGISTRY_UI_AVAILABLE = False


class GraphWorkspaceTabs:
    """Tabbed interface for graph workspace with registry, editor, and metrics tabs"""

    def __init__(self):
        """Initialize the tabbed workspace"""
        # Main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.main_box.set_hexpand(True)
        self.main_box.set_vexpand(True)

        # Tab view
        self.notebook = Adw.TabView()
        self.notebook.set_hexpand(True)
        self.notebook.set_vexpand(True)

        # Tab bar to display tabs
        self.tab_bar = Adw.TabBar()
        self.tab_bar.set_view(self.notebook)
        self.main_box.append(self.tab_bar)
        self.main_box.append(self.notebook)

        # Tab pages
        self.registry_page = None
        self.editor_page = None
        self.metrics_page = None

        # Tab content widgets
        self.registry_content = None
        self.editor_content = None
        self.metrics_content = None

        # Callbacks
        self.on_tab_changed: Optional[Callable[[str], None]] = None

        self._create_tabs()

    def _create_tabs(self):
        """Create the three main tabs"""
        # Registry Tab
        self.registry_content = self._create_registry_tab()
        self.registry_page = self.notebook.append(self.registry_content)
        self.registry_page.set_title("📚 Registry")

        # Editor Tab
        self.editor_content = self._create_editor_tab()
        self.editor_page = self.notebook.append(self.editor_content)
        self.editor_page.set_title("✏️ Editor")

        # Metrics Tab
        self.metrics_content = self._create_metrics_tab()
        self.metrics_page = self.notebook.append(self.metrics_content)
        self.metrics_page.set_title("📊 Metrics")

        # Connect tab change signal
        self.notebook.connect('notify::selected-page', self._on_tab_changed)

    def _create_registry_tab(self) -> Gtk.Widget:
        """Create the registry tab content"""
        if REGISTRY_UI_AVAILABLE:
            # Use the new RegistryUI component
            self.registry_ui = RegistryUI()
            return self.registry_ui.create_widget()
        else:
            # Fallback placeholder
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            box.set_margin_top(12)
            box.set_margin_bottom(12)
            box.set_margin_start(12)
            box.set_margin_end(12)

            title = Gtk.Label(label="Node Registry")
            title.add_css_class("title-2")
            box.append(title)

            desc = Gtk.Label(label="Browse and manage available node types and saved graphs")
            desc.add_css_class("dim-label")
            desc.set_wrap(True)
            box.append(desc)

            placeholder = Gtk.Label(label="Registry UI not available")
            placeholder.add_css_class("dim-label")
            placeholder.set_vexpand(True)
            placeholder.set_valign(Gtk.Align.CENTER)
            box.append(placeholder)

            return box

    def _create_editor_tab(self) -> Gtk.Widget:
        """Create the editor tab content (placeholder for canvas)"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_hexpand(True)
        box.set_vexpand(True)

        # Placeholder - will be replaced with actual canvas
        placeholder = Gtk.Label(label="Graph Editor Canvas")
        placeholder.add_css_class("title-2")
        placeholder.set_vexpand(True)
        placeholder.set_valign(Gtk.Align.CENTER)
        box.append(placeholder)

        return box

    def _create_metrics_tab(self) -> Gtk.Widget:
        """Create the metrics tab content"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        # Title
        title = Gtk.Label(label="Execution Metrics")
        title.add_css_class("title-2")
        box.append(title)

        # Description
        desc = Gtk.Label(label="Monitor graph execution performance and statistics")
        desc.add_css_class("dim-label")
        desc.set_wrap(True)
        box.append(desc)

        # Metrics grid
        metrics_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        metrics_box.set_vexpand(True)

        # Sample metrics
        metrics = [
            ("Total Executions", "0"),
            ("Successful", "0"),
            ("Failed", "0"),
            ("Average Duration", "0ms"),
        ]

        for label, value in metrics:
            metric_row = self._create_metric_row(label, value)
            metrics_box.append(metric_row)

        box.append(metrics_box)

        return box

    def _create_metric_row(self, label: str, value: str) -> Gtk.Widget:
        """Create a single metric row"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.add_css_class("card")

        label_widget = Gtk.Label(label=label)
        label_widget.set_hexpand(True)
        label_widget.set_halign(Gtk.Align.START)
        row.append(label_widget)

        value_widget = Gtk.Label(label=value)
        value_widget.add_css_class("monospace")
        value_widget.add_css_class("dim-label")
        row.append(value_widget)

        return row

    def _on_tab_changed(self, notebook, param):
        """Handle tab change event"""
        selected_page = self.notebook.get_selected_page()
        if selected_page:
            tab_title = selected_page.get_title()
            if self.on_tab_changed:
                self.on_tab_changed(tab_title.lower())

    def get_widget(self) -> Gtk.Widget:
        """Get the main widget (TabBar + TabView)"""
        return self.main_box

    def set_editor_content(self, widget: Gtk.Widget):
        """Set the editor tab content with actual canvas"""
        # Get the container (Box) that was created for this tab
        container = self.editor_page.get_child()
        if container and isinstance(container, Gtk.Box):
            # Clear all children from the container
            while True:
                child = container.get_first_child()
                if child is None:
                    break
                container.remove(child)

            # Add the new widget
            container.append(widget)
            self.editor_content = widget

    def set_registry_content(self, widget: Gtk.Widget):
        """Set the registry tab content"""
        # Get the container (Box) that was created for this tab
        container = self.registry_page.get_child()
        if container and isinstance(container, Gtk.Box):
            # Clear all children from the container
            while True:
                child = container.get_first_child()
                if child is None:
                    break
                container.remove(child)

            # Add the new widget
            container.append(widget)
            self.registry_content = widget

    def set_metrics_content(self, widget: Gtk.Widget):
        """Set the metrics tab content"""
        # Get the container (Box) that was created for this tab
        container = self.metrics_page.get_child()
        if container and isinstance(container, Gtk.Box):
            # Clear all children from the container
            while True:
                child = container.get_first_child()
                if child is None:
                    break
                container.remove(child)

            # Add the new widget
            container.append(widget)
            self.metrics_content = widget

    def get_current_tab(self) -> str:
        """Get the currently selected tab name"""
        selected_page = self.notebook.get_selected_page()
        if selected_page:
            return selected_page.get_title().lower()
        return "editor"

    def set_current_tab(self, tab_name: str):
        """Set the current tab by name"""
        tab_name_lower = tab_name.lower()
        for i in range(self.notebook.get_n_pages()):
            page = self.notebook.get_nth_page(i)
            if page.get_title().lower() == tab_name_lower:
                self.notebook.set_selected_page(page)
                break

    def update_metrics(self, metrics: Dict[str, Any]):
        """Update metrics display"""
        # This will be implemented to update the metrics tab
        pass

    def set_registry_client(self, doc_store_client):
        """Set the document store client for registry operations"""
        if REGISTRY_UI_AVAILABLE and hasattr(self, 'registry_ui'):
            self.registry_ui.doc_store_client = doc_store_client

