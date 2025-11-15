"""
Document Workspace Tabs Component

Generic workspace tabs interface for managing any document type (graphs, tools, users, etc.)
Provides Registry, Editor, and Metrics workspace tabs with pluggable content.

Workspace tabs are NON-CLOSEABLE tabs in a top bar. Simple, crude, with inner padding for taste.
Each tab is a unique state view with its own feature set. They represent different visual
representations of the same underlying document state.

Implementation: Adw.TabView with set_closeable(False) on each tab page.

@llm-type component.document-workspace-tabs
@llm-does generic workspace tabs for document state visualization
@llm-rule workspace tabs are reusable for any document type via callbacks
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from collections.abc import Callable
from typing import Any, List, Dict, Optional

from gi.repository import Adw, Gtk

try:
    from .document_list_simple import DocumentListSimple
    from .document_detail_simple import DocumentDetailSimple
    from .document_manager import DocumentManager
except ImportError:
    # Fallback for direct execution
    from document_list_simple import DocumentListSimple
    from document_detail_simple import DocumentDetailSimple
    from document_manager import DocumentManager


class DocumentWorkspaceTabs:
    """
    Generic workspace tabs interface for document state visualization.

    Workspace tabs are different visual representations of the same underlying
    document state. Each tab (Registry, Editor, Metrics) provides a unique view
    and feature set for interacting with documents.

    NOT traditional tabs with X buttons - these are persistent workspace views.
    """

    def __init__(self, document_type: str = "document", doc_store_client=None):
        """
        Initialize document workspace tabs

        Args:
            document_type: Type of document (e.g., "graph", "tool", "user")
            doc_store_client: Document store client for persistence
        """
        self.document_type = document_type
        self.doc_store_client = doc_store_client

        # Callbacks for workspace content
        self.on_registry_content: Callable[[], Gtk.Widget] | None = None
        self.on_editor_content: Callable[[], Gtk.Widget] | None = None
        self.on_metrics_content: Callable[[], Gtk.Widget] | None = None
        self.on_workspace_changed: Callable[[str], None] | None = None

        # UI components
        self.main_box = None
        self.tab_bar = None
        self.notebook = None

        # Tab pages
        self.registry_page = None
        self.editor_page = None
        self.metrics_page = None

        # Document management components
        self.document_list: Optional[DocumentListSimple] = None
        self.document_detail: Optional[DocumentDetailSimple] = None
        self.document_manager = DocumentManager()
        self.documents: List[Dict[str, Any]] = []
        self.selected_document: Optional[Dict[str, Any]] = None

        self._create_ui()
        self._load_documents()

    def _create_ui(self):
        """Create the workspace tabs interface"""
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Create tab view (non-closeable tabs)
        self.notebook = Adw.TabView()
        self.notebook.set_vexpand(True)
        self.notebook.set_hexpand(True)

        # Create tab bar with inner padding for taste
        self.tab_bar = Adw.TabBar()
        self.tab_bar.set_view(self.notebook)
        self.tab_bar.set_margin_top(8)
        self.tab_bar.set_margin_bottom(8)
        self.tab_bar.set_margin_start(8)
        self.tab_bar.set_margin_end(8)

        # Add to main box
        self.main_box.append(self.tab_bar)
        self.main_box.append(self.notebook)

        # Create tabs
        self._create_tabs()

        # Connect tab change signal
        self.notebook.connect("notify::selected-page", self._on_tab_changed)

    def _create_tabs(self):
        """Create the three main workspace tabs (non-closeable)"""
        # Registry Tab
        registry_content = self._create_registry_tab()
        self.registry_page = self.notebook.append(registry_content)
        self.registry_page.set_title("📚 Registry")

        # Editor Tab
        editor_content = self._create_editor_tab()
        self.editor_page = self.notebook.append(editor_content)
        self.editor_page.set_title("✏️ Editor")

        # Metrics Tab
        metrics_content = self._create_metrics_tab()
        self.metrics_page = self.notebook.append(metrics_content)
        self.metrics_page.set_title("📊 Metrics")

        # Prevent tab closing by handling the close-page signal
        self.notebook.connect("close-page", self._on_close_page_requested)

    def _create_registry_tab(self) -> Gtk.Widget:
        """Create registry tab content"""
        if self.on_registry_content:
            return self.on_registry_content()

        # Create document list component
        self.document_list = DocumentListSimple()
        self.document_list.connect("document-selected", self._on_document_selected)
        self.document_list.connect("document-opened", self._on_document_opened)

        return self.document_list

    def _create_editor_tab(self) -> Gtk.Widget:
        """Create editor tab content"""
        if self.on_editor_content:
            return self.on_editor_content()

        # Create document detail component
        self.document_detail = DocumentDetailSimple()
        self.document_detail.connect("edit-clicked", self._on_edit_clicked)
        self.document_detail.connect("delete-clicked", self._on_delete_clicked)

        return self.document_detail

    def _create_metrics_tab(self) -> Gtk.Widget:
        """Create metrics tab content"""
        if self.on_metrics_content:
            return self.on_metrics_content()

        # Default placeholder
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        label = Gtk.Label(label=f"Metrics for {self.document_type}")
        label.add_css_class("title-2")
        box.append(label)
        return box

    def _on_tab_changed(self, *args):
        """Handle workspace tab change"""
        selected_page = self.notebook.get_selected_page()
        if selected_page:
            tab_title = selected_page.get_title()
            tab_name = tab_title.split()[-1].lower() if tab_title else "unknown"

            if self.on_workspace_changed:
                self.on_workspace_changed(tab_name)

    def _on_close_page_requested(self, notebook, page):
        """Prevent tab closing - workspace tabs are non-closeable"""
        # Return True to prevent the close, False to allow it
        # We always return True to prevent closing
        return True

    def get_widget(self) -> Gtk.Widget:
        """Get the main widget"""
        return self.main_box

    def set_registry_client(self, doc_store_client):
        """Set document store client"""
        self.doc_store_client = doc_store_client

    def set_registry_content(self, callback: Callable[[], Gtk.Widget]):
        """Set registry tab content callback"""
        self.on_registry_content = callback

    def set_editor_content(self, callback: Callable[[], Gtk.Widget]):
        """Set editor tab content callback"""
        self.on_editor_content = callback

    def set_metrics_content(self, callback: Callable[[], Gtk.Widget]):
        """Set metrics tab content callback"""
        self.on_metrics_content = callback

    # Document management methods

    def _load_documents(self):
        """Load documents from manager"""
        self.documents = self.document_manager.get_all_documents()
        if self.document_list:
            self.document_list.set_documents(self.documents)

    def set_documents(self, documents: List[Dict[str, Any]]):
        """Set list of documents to display"""
        self.documents = documents
        if self.document_list:
            self.document_list.set_documents(documents)

    def _on_document_selected(self, list_widget, document_id: str):
        """Handle document selection in registry"""
        # Find document by ID
        doc = next((d for d in self.documents if d.get("id") == document_id), None)
        if doc:
            self.selected_document = doc
            if self.document_detail:
                self.document_detail.set_document(doc)

    def _on_document_opened(self, list_widget, document_id: str):
        """Handle document open (double-click)"""
        # Switch to editor tab
        if self.editor_page:
            self.notebook.set_selected_page(self.editor_page)

    def _on_edit_clicked(self, detail_widget):
        """Handle edit button click"""
        # TODO: Implement edit mode
        pass

    def _on_delete_clicked(self, detail_widget):
        """Handle delete button click"""
        # TODO: Implement delete with confirmation
        pass
