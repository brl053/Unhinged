"""
Simple Document List Component

Displays list of documents with selection support.
Minimal implementation - just document name and type.

@llm-type component.document-list-simple
@llm-does display list of documents with selection
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GObject
from typing import Callable, Optional, List, Dict, Any


class DocumentListSimple(Gtk.Box):
    """Simple document list with selection support"""

    # Signals
    __gsignals__ = {
        'document-selected': (GObject.SignalFlags.RUN_FIRST, None, (str,)),  # document_id
        'document-opened': (GObject.SignalFlags.RUN_FIRST, None, (str,)),    # document_id
    }
    
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, **kwargs)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)

        self.documents: List[Dict[str, Any]] = []
        self.selected_document_id: Optional[str] = None
        self.row_to_doc_id: Dict[Gtk.ListBoxRow, str] = {}  # Map rows to document IDs

        self._create_ui()
    
    def _create_ui(self):
        """Create UI components"""
        # Header with title
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        title = Gtk.Label(label="Documents")
        title.add_css_class("title-2")
        header.append(title)
        self.append(header)
        
        # Search box (placeholder for now)
        search_box = Gtk.SearchEntry()
        search_box.set_placeholder_text("Search documents...")
        self.append(search_box)
        
        # Scrolled window for list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        
        # List box for documents
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list_box.connect('row-selected', self._on_row_selected)
        self.list_box.connect('row-activated', self._on_row_activated)
        
        scrolled.set_child(self.list_box)
        self.append(scrolled)
    
    def set_documents(self, documents: List[Dict[str, Any]]):
        """Set list of documents to display"""
        self.documents = documents
        self._refresh_list()
    
    def _refresh_list(self):
        """Refresh the document list display"""
        # Clear existing rows
        while True:
            row = self.list_box.get_first_child()
            if row is None:
                break
            self.list_box.remove(row)
        
        # Add document rows
        for doc in self.documents:
            row = self._create_document_row(doc)
            self.list_box.append(row)
    
    def _create_document_row(self, doc: Dict[str, Any]) -> Gtk.ListBoxRow:
        """Create a row for a document"""
        row = Gtk.ListBoxRow()
        # Store mapping instead of using deprecated set_data()
        self.row_to_doc_id[row] = doc.get("id")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(8)
        box.set_margin_end(8)

        # Document title
        title = Gtk.Label(label=doc.get("title", "Untitled"))
        title.set_halign(Gtk.Align.START)
        title.add_css_class("body")
        box.append(title)

        # Document type and timestamp
        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        doc_type = Gtk.Label(label=f"Type: {doc.get('type', 'unknown')}")
        doc_type.add_css_class("caption")
        doc_type.add_css_class("dim-label")
        info_box.append(doc_type)

        modified = Gtk.Label(label=f"Modified: {doc.get('modified_at', 'N/A')}")
        modified.add_css_class("caption")
        modified.add_css_class("dim-label")
        info_box.append(modified)

        box.append(info_box)
        row.set_child(box)

        return row
    
    def _on_row_selected(self, list_box, row):
        """Handle row selection"""
        if row is None:
            self.selected_document_id = None
            return

        doc_id = self.row_to_doc_id.get(row)
        if doc_id:
            self.selected_document_id = doc_id
            self.emit('document-selected', doc_id)

    def _on_row_activated(self, list_box, row):
        """Handle row double-click (open)"""
        if row is None:
            return

        doc_id = self.row_to_doc_id.get(row)
        if doc_id:
            self.emit('document-opened', doc_id)
    
    def get_selected_document_id(self) -> Optional[str]:
        """Get currently selected document ID"""
        return self.selected_document_id

