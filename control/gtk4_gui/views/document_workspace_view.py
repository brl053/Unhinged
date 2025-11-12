"""
Document Workspace View

Generic document management interface supporting any document type.
Provides tabbed workspace with Registry, Editor, and Metrics tabs.

@llm-type view.document-workspace
@llm-does generic document management interface
@llm-rule supports any document type via configuration
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw, Gtk

from .base import ViewBase


class DocumentWorkspaceView(ViewBase):
    """Generic document workspace view"""

    def __init__(self, app, document_type: str = "document"):
        """
        Initialize document workspace view

        Args:
            app: Application instance
            document_type: Type of document to manage
        """
        super().__init__(app, f"documents_{document_type}")
        self.document_type = document_type
        self.doc_store_client = None
        self.tabs = None

    def create_content(self):
        """Create the document workspace content"""
        try:
            from ..components import DocumentWorkspaceTabs
            from ..components.document_registry import DocumentRegistry
            from ..components.document_store_client import DocumentStoreClient
            
            # Create main container
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            main_box.set_hexpand(True)
            main_box.set_vexpand(True)

            # Create toolbar
            toolbar = self._create_toolbar()
            main_box.append(toolbar)

            # Create document store client
            self.doc_store_client = DocumentStoreClient()

            # Create workspace tabs
            self.tabs = DocumentWorkspaceTabs(
                document_type=self.document_type,
                doc_store_client=self.doc_store_client
            )
            self.tabs.on_workspace_changed = self._on_workspace_changed

            # Create registry for this document type
            registry = DocumentRegistry(
                document_type=self.document_type,
                doc_store_client=self.doc_store_client
            )
            registry.on_create = self._on_create_document
            registry.on_edit = self._on_edit_document
            registry.on_delete = self._on_delete_document

            # Set registry as content callback
            self.tabs.set_registry_content(lambda: registry.create_widget())

            # Set editor and metrics placeholders
            self.tabs.set_editor_content(self._create_editor_placeholder)
            self.tabs.set_metrics_content(self._create_metrics_placeholder)

            # Add tabs to main box
            main_box.append(self.tabs.get_widget())

            self.content = main_box
            return main_box

        except Exception as e:
            print(f"❌ Error creating document workspace: {e}")
            import traceback
            traceback.print_exc()
            return self._create_error_view(str(e))

    def _create_toolbar(self) -> Gtk.Widget:
        """Create toolbar (not HeaderBar to avoid window nesting)"""
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        toolbar.set_margin_top(12)
        toolbar.set_margin_bottom(12)
        toolbar.set_margin_start(12)
        toolbar.set_margin_end(12)

        # Title
        title = Gtk.Label(label=f"{self.document_type.title()} Workspace")
        title.add_css_class("title-2")
        toolbar.append(title)

        return toolbar

    def _create_editor_placeholder(self) -> Gtk.Widget:
        """Create editor tab placeholder"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)
        
        label = Gtk.Label(label=f"Editor for {self.document_type}")
        label.add_css_class("title-2")
        box.append(label)
        
        desc = Gtk.Label(label="Select a document from the registry to edit")
        desc.add_css_class("dim-label")
        desc.set_wrap(True)
        box.append(desc)
        
        return box

    def _create_metrics_placeholder(self) -> Gtk.Widget:
        """Create metrics tab placeholder"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)
        
        label = Gtk.Label(label=f"Metrics for {self.document_type}")
        label.add_css_class("title-2")
        box.append(label)
        
        desc = Gtk.Label(label="Performance and usage statistics")
        desc.add_css_class("dim-label")
        desc.set_wrap(True)
        box.append(desc)
        
        return box

    def _on_workspace_changed(self, workspace_name: str):
        """Handle workspace change"""
        print(f"📑 Switched to {workspace_name} workspace for {self.document_type}")

    def _on_create_document(self, name: str, description: str, doc_type: str):
        """Handle document creation"""
        print(f"➕ Creating {doc_type}: {name}")
        # Implementation depends on document type

    def _on_edit_document(self, doc_id: str):
        """Handle document edit"""
        print(f"✏️ Editing document: {doc_id}")
        # Implementation depends on document type

    def _on_delete_document(self, doc_id: str):
        """Handle document deletion"""
        print(f"🗑️ Deleting document: {doc_id}")
        # Implementation depends on document type

    def _create_error_view(self, error_message: str) -> Gtk.Widget:
        """Create error view"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)
        
        label = Gtk.Label(label="Error")
        label.add_css_class("title-2")
        box.append(label)
        
        error_label = Gtk.Label(label=error_message)
        error_label.add_css_class("dim-label")
        error_label.set_wrap(True)
        box.append(error_label)
        
        return box

