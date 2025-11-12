"""
Simple Document Detail Component

Displays details of a single document.
Minimal implementation - just document metadata.

@llm-type component.document-detail-simple
@llm-does display document details and metadata
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GObject
from typing import Optional, Dict, Any


class DocumentDetailSimple(Gtk.Box):
    """Simple document detail view"""

    # Signals
    __gsignals__ = {
        'edit-clicked': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'delete-clicked': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }
    
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12, **kwargs)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)
        
        self.current_document: Optional[Dict[str, Any]] = None
        
        self._create_ui()
    
    def _create_ui(self):
        """Create UI components"""
        # Header with title and buttons
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.set_hexpand(True)
        
        self.title_label = Gtk.Label(label="No document selected")
        self.title_label.add_css_class("title-2")
        self.title_label.set_hexpand(True)
        self.title_label.set_halign(Gtk.Align.START)
        header.append(self.title_label)
        
        # Action buttons
        edit_btn = Gtk.Button(label="Edit")
        edit_btn.connect('clicked', lambda _: self.emit('edit-clicked'))
        header.append(edit_btn)
        
        delete_btn = Gtk.Button(label="Delete")
        delete_btn.add_css_class("destructive-action")
        delete_btn.connect('clicked', lambda _: self.emit('delete-clicked'))
        header.append(delete_btn)
        
        self.append(header)
        
        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.append(sep)
        
        # Scrolled window for properties
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        
        # Properties box
        self.properties_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.properties_box.set_margin_top(12)
        self.properties_box.set_margin_bottom(12)
        self.properties_box.set_margin_start(12)
        self.properties_box.set_margin_end(12)
        
        scrolled.set_child(self.properties_box)
        self.append(scrolled)
        
        # Empty state
        self._show_empty_state()
    
    def _show_empty_state(self):
        """Show empty state message"""
        self.properties_box.set_visible(False)
        
        empty_label = Gtk.Label(label="Select a document to view details")
        empty_label.add_css_class("dim-label")
        empty_label.add_css_class("title-3")
        self.properties_box.append(empty_label)
    
    def set_document(self, document: Optional[Dict[str, Any]]):
        """Set document to display"""
        self.current_document = document
        
        if document is None:
            self.title_label.set_label("No document selected")
            self._show_empty_state()
            return
        
        self.title_label.set_label(document.get("title", "Untitled"))
        self._refresh_properties()
    
    def _refresh_properties(self):
        """Refresh properties display"""
        # Clear existing properties
        while True:
            child = self.properties_box.get_first_child()
            if child is None:
                break
            self.properties_box.remove(child)
        
        if self.current_document is None:
            self._show_empty_state()
            return
        
        self.properties_box.set_visible(True)
        
        doc = self.current_document
        
        # Document ID
        self._add_property("ID", doc.get("id", "N/A"))
        
        # Document Type
        self._add_property("Type", doc.get("type", "N/A"))
        
        # Created At
        self._add_property("Created", doc.get("created_at", "N/A"))
        
        # Modified At
        self._add_property("Modified", doc.get("modified_at", "N/A"))
        
        # Description (if available)
        if "description" in doc:
            self._add_property("Description", doc["description"])
        
        # Additional metadata
        if "metadata" in doc:
            metadata = doc["metadata"]
            if isinstance(metadata, dict):
                for key, value in metadata.items():
                    self._add_property(key.title(), str(value))
    
    def _add_property(self, label: str, value: str):
        """Add a property row"""
        row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        label_widget = Gtk.Label(label=label)
        label_widget.add_css_class("caption")
        label_widget.add_css_class("dim-label")
        label_widget.set_halign(Gtk.Align.START)
        row.append(label_widget)
        
        value_widget = Gtk.Label(label=value)
        value_widget.add_css_class("body")
        value_widget.set_halign(Gtk.Align.START)
        value_widget.set_wrap(True)
        row.append(value_widget)
        
        self.properties_box.append(row)

