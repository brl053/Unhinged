"""
Generic Document Registry Component

Reusable CRUD interface for managing any document type.
Supports create, read, update, delete operations on documents.

@llm-type component.document-registry
@llm-does generic CRUD UI for any document type
@llm-rule registry is document-type agnostic via callbacks
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from collections.abc import Callable
from typing import Any

from gi.repository import Adw, Gtk


class DocumentRegistry:
    """Generic registry UI for managing documents"""

    def __init__(self, document_type: str = "document", doc_store_client=None):
        """
        Initialize document registry

        Args:
            document_type: Type of document (e.g., "graph", "tool", "user")
            doc_store_client: Document store client for persistence
        """
        self.document_type = document_type
        self.doc_store_client = doc_store_client
        self.documents: list[dict[str, Any]] = []

        # Callbacks
        self.on_create: Callable[[str, str, str], None] | None = None
        self.on_edit: Callable[[str], None] | None = None
        self.on_delete: Callable[[str], None] | None = None

        # UI components
        self.documents_list_box = None
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
        title = Gtk.Label(label=f"{self.document_type.title()} Registry")
        title.add_css_class("title-1")
        title.set_halign(Gtk.Align.START)
        header_box.append(title)

        desc = Gtk.Label(label=f"Create, manage, and edit {self.document_type}s")
        desc.add_css_class("dim-label")
        desc.set_halign(Gtk.Align.START)
        desc.set_wrap(True)
        header_box.append(desc)
        main_box.append(header_box)

        # Create button
        create_btn = Gtk.Button(label=f"+ Create New {self.document_type.title()}")
        create_btn.add_css_class("suggested-action")
        create_btn.connect("clicked", self._on_create_clicked)
        main_box.append(create_btn)

        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.append(sep)

        # Documents list
        list_label = Gtk.Label(label=f"Saved {self.document_type.title()}s")
        list_label.add_css_class("title-3")
        list_label.set_halign(Gtk.Align.START)
        main_box.append(list_label)

        # Scrolled window for documents list
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Documents list box
        self.documents_list_box = Gtk.ListBox()
        self.documents_list_box.add_css_class("boxed-list")
        scroll.set_child(self.documents_list_box)
        main_box.append(scroll)

        # Status label
        self.status_label = Gtk.Label(label="No documents yet")
        self.status_label.add_css_class("dim-label")
        main_box.append(self.status_label)

        return main_box

    def _on_create_clicked(self, button):
        """Handle create button click"""
        dialog = Adw.MessageDialog.new()
        dialog.set_heading(f"Create New {self.document_type.title()}")
        dialog.set_body(f"Enter details for the new {self.document_type}")

        # Add response buttons
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("create", "Create")
        dialog.set_response_appearance("create", Adw.ResponseAppearance.SUGGESTED)

        dialog.connect("response", self._on_create_response)
        dialog.present()

    def _on_create_response(self, dialog, response):
        """Handle create dialog response"""
        if response == "create" and self.on_create:
            # Simple implementation - can be extended with form fields
            self.on_create(
                name=f"New {self.document_type}",
                description="",
                doc_type=self.document_type,
            )

    def _on_delete_clicked(self, button, doc_id):
        """Handle delete button click"""
        dialog = Adw.MessageDialog.new()
        dialog.set_heading("Delete Document?")
        dialog.set_body(f"Are you sure you want to delete this {self.document_type}?")

        dialog.add_response("cancel", "Cancel")
        dialog.add_response("delete", "Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)

        dialog.connect("response", lambda d, r: self._on_delete_response(d, r, doc_id))
        dialog.present()

    def _on_delete_response(self, dialog, response, doc_id):
        """Handle delete confirmation"""
        if response == "delete" and self.on_delete:
            self.on_delete(doc_id)

    def add_document(self, doc_id: str, name: str, description: str = ""):
        """Add document to list"""
        row = Gtk.ListBoxRow()

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(12)
        box.set_margin_end(12)

        # Document info
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        name_label = Gtk.Label(label=name)
        name_label.set_halign(Gtk.Align.START)
        info_box.append(name_label)

        if description:
            desc_label = Gtk.Label(label=description)
            desc_label.add_css_class("dim-label")
            desc_label.set_halign(Gtk.Align.START)
            info_box.append(desc_label)

        box.append(info_box)
        box.set_hexpand(True)

        # Action buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        edit_btn = Gtk.Button(label="Edit")
        edit_btn.connect("clicked", lambda b: self.on_edit(doc_id) if self.on_edit else None)
        button_box.append(edit_btn)

        delete_btn = Gtk.Button(label="Delete")
        delete_btn.add_css_class("destructive-action")
        delete_btn.connect("clicked", self._on_delete_clicked, doc_id)
        button_box.append(delete_btn)

        box.append(button_box)
        row.set_child(box)
        self.documents_list_box.append(row)

    def clear_documents(self):
        """Clear all documents from list"""
        while True:
            row = self.documents_list_box.get_row_at_index(0)
            if not row:
                break
            self.documents_list_box.remove(row)
