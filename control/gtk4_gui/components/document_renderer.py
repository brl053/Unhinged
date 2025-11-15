"""
Document Renderer Component

Reusable visual component for rendering/displaying documents.
Used throughout the UI for consistent document visualization.

Supports:
- Document metadata display (name, description, type, created/updated dates)
- Hierarchical document structure
- Custom renderers per document type
- Extensible for any document type (graphs, tools, users, etc.)

@llm-type component.document-renderer
@llm-does render documents visually with metadata and hierarchy
@llm-rule renderer is document-type agnostic via custom renderers
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from typing import Any, Callable, Optional

from gi.repository import Gtk


class DocumentRenderer:
    """Reusable component for rendering documents"""

    def __init__(
        self,
        document: dict[str, Any],
        document_type: str = "document",
        custom_renderer: Optional[Callable] = None,
    ):
        """
        Initialize document renderer

        Args:
            document: Document data dict with id, name, description, etc.
            document_type: Type of document (e.g., "graph", "tool", "user")
            custom_renderer: Optional custom renderer function for document-specific display
        """
        self.document = document
        self.document_type = document_type
        self.custom_renderer = custom_renderer
        self.widget = None

    def render(self) -> Gtk.Widget:
        """Render the document and return widget"""
        if self.custom_renderer:
            return self.custom_renderer(self.document)

        return self._render_default()

    def _render_default(self) -> Gtk.Widget:
        """Render document with default layout"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)

        # Document header with metadata
        header = self._render_header()
        main_box.append(header)

        # Document content
        content = self._render_content()
        main_box.append(content)

        # Document footer with actions
        footer = self._render_footer()
        main_box.append(footer)

        self.widget = main_box
        return main_box

    def _render_header(self) -> Gtk.Widget:
        """Render document header with title and metadata"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        # Title
        title = self.document.get("name", "Untitled Document")
        title_label = Gtk.Label(label=title)
        title_label.add_css_class("title-2")
        title_label.set_halign(Gtk.Align.START)
        header_box.append(title_label)

        # Metadata row
        metadata_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        metadata_box.add_css_class("dim-label")

        # Document type
        doc_type_label = Gtk.Label(label=f"Type: {self.document_type}")
        metadata_box.append(doc_type_label)

        # Created date
        created = self.document.get("created_at", "Unknown")
        created_label = Gtk.Label(label=f"Created: {created}")
        metadata_box.append(created_label)

        # Updated date
        updated = self.document.get("updated_at", "Unknown")
        updated_label = Gtk.Label(label=f"Updated: {updated}")
        metadata_box.append(updated_label)

        header_box.append(metadata_box)

        # Description
        description = self.document.get("description", "")
        if description:
            desc_label = Gtk.Label(label=description)
            desc_label.add_css_class("dim-label")
            desc_label.set_wrap(True)
            desc_label.set_halign(Gtk.Align.START)
            header_box.append(desc_label)

        return header_box

    def _render_content(self) -> Gtk.Widget:
        """Render document content area"""
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        content_box.append(sep)

        # Document properties
        properties = self.document.get("properties", {})
        if properties:
            props_label = Gtk.Label(label="Properties")
            props_label.add_css_class("title-3")
            props_label.set_halign(Gtk.Align.START)
            content_box.append(props_label)

            for key, value in properties.items():
                prop_row = self._render_property(key, value)
                content_box.append(prop_row)
        else:
            # Placeholder
            placeholder = Gtk.Label(label="No properties defined")
            placeholder.add_css_class("dim-label")
            content_box.append(placeholder)

        return content_box

    def _render_property(self, key: str, value: Any) -> Gtk.Widget:
        """Render a single property"""
        prop_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        prop_box.set_margin_start(12)

        # Key
        key_label = Gtk.Label(label=f"{key}:")
        key_label.set_halign(Gtk.Align.START)
        key_label.set_size_request(120, -1)
        prop_box.append(key_label)

        # Value
        value_str = str(value) if value is not None else "—"
        value_label = Gtk.Label(label=value_str)
        value_label.add_css_class("dim-label")
        value_label.set_halign(Gtk.Align.START)
        value_label.set_hexpand(True)
        prop_box.append(value_label)

        return prop_box

    def _render_footer(self) -> Gtk.Widget:
        """Render document footer with metadata"""
        footer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        footer_box.append(sep)

        # Document ID
        doc_id = self.document.get("id", "Unknown")
        id_label = Gtk.Label(label=f"ID: {doc_id}")
        id_label.add_css_class("dim-label")
        id_label.set_halign(Gtk.Align.START)
        id_label.set_selectable(True)
        footer_box.append(id_label)

        return footer_box

    def get_widget(self) -> Gtk.Widget:
        """Get the rendered widget"""
        if not self.widget:
            self.render()
        return self.widget

    def update_document(self, document: dict[str, Any]):
        """Update the document and re-render"""
        self.document = document
        self.widget = None
        return self.render()
