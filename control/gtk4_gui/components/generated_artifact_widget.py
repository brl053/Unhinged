#!/usr/bin/env python3
"""
Generated Artifact Widget

Custom widget for displaying generated artifacts (images, emails, movies, etc.)
Inherits from AbstractWindow abstraction for future extensibility.

Mini-window with top-right buttons, fits existing design hierarchy.
Designed as an iframe-like container for generated content.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import subprocess
from pathlib import Path

from gi.repository import GObject, Gtk

from .base import AdwComponentBase


class GeneratedArtifactWidget(AdwComponentBase):
    """
    Widget for displaying generated artifacts inline in chat.

    Features:
    - Mini-window appearance with header bar
    - Top-right action buttons (folder icon to open in file manager)
    - Artifact type detection (image, email, movie, etc.)
    - Extensible for future artifact types
    - Inherits from AbstractWindow abstraction
    """

    __gsignals__ = {
        "artifact-action": (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
    }

    def __init__(
        self,
        artifact_type: str = "image",
        artifact_path: str = "",
        artifact_title: str = "Generated Artifact",
        artifact_metadata: dict | None = None,
        **kwargs,
    ):
        """
        Initialize generated artifact widget.

        Args:
            artifact_type: Type of artifact ("image", "email", "movie", etc.)
            artifact_path: Full path to the artifact file
            artifact_title: Display title for the artifact
            artifact_metadata: Additional metadata dict
        """
        self.artifact_type = artifact_type
        self.artifact_path = artifact_path
        self.artifact_title = artifact_title
        self.artifact_metadata = artifact_metadata or {}

        self._header_bar = None
        self._content_area = None
        self._action_buttons = {}

        super().__init__("generated-artifact-widget", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the artifact widget component"""
        # Main container (mini-window appearance)
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.widget.set_margin_top(8)
        self.widget.set_margin_bottom(8)
        self.widget.set_margin_start(8)
        self.widget.set_margin_end(8)

        # Add CSS class for styling
        self.widget.add_css_class("generated-artifact-widget")

        # Create header bar (mini window title bar)
        self._create_header_bar()
        self.widget.append(self._header_bar)

        # Create content area based on artifact type
        self._content_area = self._create_content_area()
        self.widget.append(self._content_area)

    def _create_header_bar(self) -> Gtk.Widget:
        """Create header bar with title and action buttons"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header_box.set_margin_top(8)
        header_box.set_margin_bottom(8)
        header_box.set_margin_start(12)
        header_box.set_margin_end(12)
        header_box.add_css_class("generated-artifact-header")

        # Title label
        title_label = Gtk.Label()
        title_label.set_text(self.artifact_title)
        title_label.set_halign(Gtk.Align.START)
        title_label.set_hexpand(True)
        title_label.add_css_class("title-3")
        header_box.append(title_label)

        # Action buttons container (right-aligned)
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        buttons_box.set_halign(Gtk.Align.END)

        # Folder icon button (open in file manager)
        folder_button = Gtk.Button()
        folder_button.set_icon_name("folder-open-symbolic")
        folder_button.set_tooltip_text("Open in file manager")
        folder_button.add_css_class("flat")
        folder_button.connect("clicked", self._on_open_folder_clicked)
        self._action_buttons["open_folder"] = folder_button
        buttons_box.append(folder_button)

        header_box.append(buttons_box)
        self._header_bar = header_box

        return header_box

    def _create_content_area(self) -> Gtk.Widget:
        """Create content area based on artifact type"""
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content_box.add_css_class("generated-artifact-content")

        if self.artifact_type == "image":
            content_box.append(self._create_image_content())
        elif self.artifact_type == "email":
            content_box.append(self._create_email_content())
        elif self.artifact_type == "movie":
            content_box.append(self._create_movie_content())
        else:
            content_box.append(self._create_generic_content())

        return content_box

    def _create_image_content(self) -> Gtk.Widget:
        """Create image display content"""
        try:
            # Load and display image
            image = Gtk.Image()
            image.set_from_file(self.artifact_path)
            image.set_pixel_size(400)  # Max size
            image.add_css_class("generated-artifact-image")

            # Wrap in scrolled window for large images
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scrolled.set_child(image)
            scrolled.set_max_content_height(400)
            scrolled.set_max_content_width(400)

            return scrolled

        except Exception as e:
            return self._create_error_content(f"Failed to load image: {e}")

    def _create_email_content(self) -> Gtk.Widget:
        """Create email display content (placeholder for future)"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        label = Gtk.Label()
        label.set_text("Email artifact")
        label.set_wrap(True)
        box.append(label)

        return box

    def _create_movie_content(self) -> Gtk.Widget:
        """Create movie display content (placeholder for future)"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        label = Gtk.Label()
        label.set_text("Movie artifact")
        label.set_wrap(True)
        box.append(label)

        return box

    def _create_generic_content(self) -> Gtk.Widget:
        """Create generic artifact content"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        label = Gtk.Label()
        label.set_text(f"Generated {self.artifact_type} artifact")
        label.set_wrap(True)
        box.append(label)

        return box

    def _create_error_content(self, error_msg: str) -> Gtk.Widget:
        """Create error display content"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        label = Gtk.Label()
        label.set_text(error_msg)
        label.set_wrap(True)
        label.add_css_class("error")
        box.append(label)

        return box

    def _on_open_folder_clicked(self, button):
        """Handle open in file manager button click"""
        try:
            artifact_file = Path(self.artifact_path)
            if artifact_file.exists():
                # Open file manager at artifact location
                subprocess.Popen(["xdg-open", str(artifact_file.parent)])
                self.trigger_action("open_folder", str(artifact_file.parent))
            else:
                print(f"⚠️ Artifact file not found: {self.artifact_path}")
        except Exception as e:
            print(f"❌ Failed to open folder: {e}")
