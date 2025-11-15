"""
@llm-doc Primitive GTK4 Components
@llm-version 1.0.0
@llm-date 2025-10-28

Basic building block components with design system integration:
- ActionButton: Enhanced button with semantic styling
- StatusLabel: Label with status styling (success, warning, error)
- ProgressIndicator: Progress bar with semantic styling
- HardwareInfoRow: Hardware information display row
- ProcessRow: Process information display with controls
- BluetoothRow: Bluetooth device display with connection controls
- AudioDeviceRow: Audio device display with volume controls
"""

import logging

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")


from gi.repository import GObject, Gtk, Pango

from ..base import AdwComponentBase

logger = logging.getLogger(__name__)


class ChatBubble(AdwComponentBase):
    """
    Chat bubble component for message display with sender/receiver alignment.

    Features:
    - Sender/receiver alignment (left/right)
    - Message content with timestamp
    - Design system integration with card patterns
    - Accessibility support
    - Semantic styling based on message type
    """

    __gsignals__ = {
        "message-clicked": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(
        self,
        message: str = "",
        sender: str = "",
        timestamp: str = "",
        alignment: str = "left",  # "left" or "right"
        message_type: str = "default",  # "default", "system", "error"
        **kwargs,
    ):
        self.message = message
        self.sender = sender
        self.timestamp = timestamp
        self.alignment = alignment
        self.message_type = message_type
        self._message_label = None
        self._sender_label = None
        self._timestamp_label = None

        super().__init__("chat-bubble", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the chat bubble component."""
        # Create main container with proper alignment
        self.widget = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        # Create bubble container (card-like)
        bubble_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        bubble_container.set_margin_top(4)
        bubble_container.set_margin_bottom(4)
        bubble_container.set_margin_start(8)
        bubble_container.set_margin_end(8)

        # Add sender label if provided
        if self.sender:
            self._sender_label = Gtk.Label()
            self._sender_label.set_text(self.sender)
            self._sender_label.set_halign(
                Gtk.Align.START if self.alignment == "left" else Gtk.Align.END
            )
            self._sender_label.add_css_class("ds-chat-sender")
            bubble_container.append(self._sender_label)

        # Create message content container
        message_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        # Message label
        self._message_label = Gtk.Label()
        self._message_label.set_text(self.message)
        self._message_label.set_wrap(True)
        self._message_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self._message_label.set_max_width_chars(50)
        self._message_label.set_halign(
            Gtk.Align.START if self.alignment == "left" else Gtk.Align.END
        )
        self._message_label.set_selectable(True)
        message_container.append(self._message_label)

        # Timestamp label if provided
        if self.timestamp:
            self._timestamp_label = Gtk.Label()
            self._timestamp_label.set_text(self.timestamp)
            self._timestamp_label.set_halign(
                Gtk.Align.START if self.alignment == "left" else Gtk.Align.END
            )
            self._timestamp_label.add_css_class("ds-chat-timestamp")
            message_container.append(self._timestamp_label)

        bubble_container.append(message_container)

        # Apply bubble styling
        self._apply_bubble_styling(bubble_container)

        # Add alignment spacing
        if self.alignment == "right":
            spacer = Gtk.Box()
            spacer.set_hexpand(True)
            self.widget.append(spacer)
            self.widget.append(bubble_container)
        else:
            self.widget.append(bubble_container)
            spacer = Gtk.Box()
            spacer.set_hexpand(True)
            self.widget.append(spacer)

        # Make clickable
        click_controller = Gtk.GestureClick()
        click_controller.connect("pressed", self._on_bubble_clicked)
        bubble_container.add_controller(click_controller)

        # Accessibility
        bubble_container.set_accessible_role(Gtk.AccessibleRole.ARTICLE)
        if self.message:
            bubble_container.update_property(
                [Gtk.AccessibleProperty.LABEL],
                [f"Message from {self.sender}: {self.message}"],
            )

    def _apply_bubble_styling(self, container):
        """Apply chat bubble styling using design system tokens."""
        # Base bubble styling
        container.add_css_class("ds-chat-bubble")
        container.add_css_class(f"ds-chat-{self.alignment}")
        container.add_css_class(f"ds-chat-{self.message_type}")

        # Apply card-like appearance
        container.add_css_class("ds-card")

    def _on_bubble_clicked(self, gesture, n_press, x, y):
        """Handle bubble click."""
        self.emit("message-clicked", self.message)
        self.trigger_action("message-clicked", self.message)

    def set_message(self, message: str):
        """Update message content."""
        self.message = message
        if self._message_label:
            self._message_label.set_text(message)

    def set_timestamp(self, timestamp: str):
        """Update timestamp."""
        self.timestamp = timestamp
        if self._timestamp_label:
            self._timestamp_label.set_text(timestamp)
        elif timestamp:
            # Create timestamp label if it doesn't exist
            self._timestamp_label = Gtk.Label()
            self._timestamp_label.set_text(timestamp)
            self._timestamp_label.set_halign(
                Gtk.Align.START if self.alignment == "left" else Gtk.Align.END
            )
            self._timestamp_label.add_css_class("ds-chat-timestamp")
            # Add to parent container (need to find message container)
            parent = self._message_label.get_parent()
            if parent:
                parent.append(self._timestamp_label)
