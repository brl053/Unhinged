"""
@llm-doc Status Stack Component for Unhinged Desktop Application
@llm-version 1.0.0
@llm-date 2025-01-26
@llm-author Unhinged Team

## Overview
High-level status stack component that displays operation status messages.
Shows 3-5 most recent messages with timestamps and status types.

## Features
- Displays operation status in real-time
- Maintains session history
- Color-coded by status type (info, success, warning, error)
- Integrates with event framework
- Positioned at highest UI level

## Status Types
- info: Informational message (blue)
- success: Operation succeeded (green)
- warning: Warning message (yellow)
- error: Error message (red)
- pending: Operation in progress (orange)

@llm-principle Real-time visibility into system operations
@llm-culture Honest status reporting
"""

import logging
from collections import deque
from datetime import datetime

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk

logger = logging.getLogger(__name__)


class StatusStack:
    """
    @llm-doc Status stack component for displaying operation status

    Maintains a stack of 3-5 status messages with timestamps.
    Integrates with event framework for all operations.
    """

    # Status type colors (CSS class names)
    STATUS_COLORS = {
        "info": "status-info",
        "success": "status-success",
        "warning": "status-warning",
        "error": "status-error",
        "pending": "status-pending",
    }

    def __init__(self, max_messages: int = 5):
        """
        Initialize status stack.

        Args:
            max_messages: Maximum number of messages to display (3-5)
        """
        self.max_messages = max(3, min(5, max_messages))
        self.messages: deque = deque(maxlen=self.max_messages)
        self.session_history: list[tuple[str, str, str]] = []  # (timestamp, type, message)

        # UI Components
        self.container = None
        self.message_box = None

        logger.info(f"Status stack initialized with max {self.max_messages} messages")

    def create_widget(self) -> Gtk.Widget:
        """
        Create the status stack widget.

        Returns:
            Gtk.Widget: The status stack container
        """
        # Create main container
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.container.set_margin_top(6)
        self.container.set_margin_bottom(6)
        self.container.set_margin_start(12)
        self.container.set_margin_end(12)
        self.container.add_css_class("status-stack")

        # Create message box (will hold individual messages)
        self.message_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.container.append(self.message_box)

        return self.container

    def push_status(self, message: str, status_type: str = "info"):
        """
        Push a new status message onto the stack.

        Args:
            message: Status message
            status_type: Type of status (info, success, warning, error, pending)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Add to messages deque (automatically removes oldest if full)
        self.messages.append((timestamp, status_type, message))

        # Add to session history
        self.session_history.append((timestamp, status_type, message))

        logger.info(f"[{status_type.upper()}] {message}")

        # Update UI
        self._update_display()

    def _update_display(self):
        """Update the display with current messages."""
        if not self.message_box:
            return

        # Clear existing messages
        while self.message_box.get_first_child():
            self.message_box.remove(self.message_box.get_first_child())

        # Add messages in reverse order (newest first)
        for timestamp, status_type, message in reversed(list(self.messages)):
            message_widget = self._create_message_widget(timestamp, status_type, message)
            self.message_box.append(message_widget)

    def _create_message_widget(self, timestamp: str, status_type: str, message: str) -> Gtk.Widget:
        """
        Create a single message widget.

        Args:
            timestamp: Message timestamp
            status_type: Type of status
            message: Message text

        Returns:
            Gtk.Widget: Message widget
        """
        message_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        message_row.add_css_class("status-message")
        message_row.add_css_class(self.STATUS_COLORS.get(status_type, "status-info"))

        # Timestamp label
        time_label = Gtk.Label(label=timestamp)
        time_label.add_css_class("ds-text-caption")
        time_label.add_css_class("monospace")
        time_label.set_size_request(60, -1)
        message_row.append(time_label)

        # Status type indicator
        type_label = Gtk.Label(label=status_type.upper())
        type_label.add_css_class("ds-text-caption")
        type_label.set_size_request(70, -1)
        message_row.append(type_label)

        # Message text
        text_label = Gtk.Label(label=message)
        text_label.add_css_class("ds-text-body")
        text_label.set_wrap(True)
        text_label.set_hexpand(True)
        text_label.set_halign(Gtk.Align.START)
        message_row.append(text_label)

        return message_row

    def get_session_history(self) -> list[tuple[str, str, str]]:
        """
        Get the complete session history.

        Returns:
            List of (timestamp, status_type, message) tuples
        """
        return self.session_history.copy()

    def clear_history(self):
        """Clear the session history."""
        self.session_history.clear()
        self.messages.clear()
        self._update_display()

    def get_status_summary(self) -> dict:
        """
        Get a summary of status messages.

        Returns:
            Dictionary with counts by status type
        """
        summary = {
            "total": len(self.session_history),
            "info": 0,
            "success": 0,
            "warning": 0,
            "error": 0,
            "pending": 0,
        }

        for _, status_type, _ in self.session_history:
            if status_type in summary:
                summary[status_type] += 1

        return summary
