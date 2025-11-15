"""
@llm-doc View Lifecycle Base Class for Unhinged Desktop Application
@llm-version 1.0.0
@llm-date 2025-01-26
@llm-author Unhinged Team

## Overview
Abstract base class for all views in the Unhinged desktop application.
Provides lifecycle management hooks (on_ready, on_cleanup) and session integration.

## Features
- Lifecycle hooks: on_ready(), on_cleanup()
- Session-based event logging
- Graceful error handling
- Spec-first, language-agnostic design

## Lifecycle
1. View is created (constructor)
2. View is displayed (on_ready called)
3. User interacts with view
4. View is closed (on_cleanup called)

@llm-principle Clear lifecycle management for deterministic behavior
@llm-culture Honest, explicit state transitions
"""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ViewBase(ABC):
    """
    @llm-doc Abstract base class for all views in Unhinged desktop application

    Provides lifecycle management and session integration for views.
    All views should inherit from this class and implement on_ready() and on_cleanup().
    """

    def __init__(self, parent_app, view_name: str):
        """
        Initialize view with parent app reference and view name.

        Args:
            parent_app: Reference to parent UnhingedDesktopApp
            view_name: Unique name for this view (e.g., "bluetooth", "output", "input")
        """
        self.app = parent_app
        self.view_name = view_name
        self.is_active = False
        self.session_logger = getattr(parent_app, "session_logger", None)

        logger.info(f"Initializing view: {view_name}")
        self._log_event("VIEW_INIT", f"View {view_name} initialized")

    @abstractmethod
    def create_content(self):
        """
        Create and return the view content widget.

        This method should be implemented by subclasses to create
        the GTK4 widget hierarchy for the view.

        Returns:
            Gtk.Widget: The root widget for this view
        """
        pass

    def on_ready(self):
        """
        Called when view is displayed and ready for interaction.

        Override this method to:
        - Start background tasks (discovery loops, monitoring)
        - Initialize real-time updates
        - Load initial data
        - Set up event listeners

        Default implementation logs the event.
        """
        self.is_active = True
        logger.info(f"View ready: {self.view_name}")
        self._log_event("VIEW_READY", f"View {self.view_name} is now active")

    def on_cleanup(self):
        """
        Called when view is closed or hidden.

        Override this method to:
        - Stop background tasks
        - Cancel timers and loops
        - Clean up resources
        - Save state if needed

        Default implementation logs the event.
        """
        self.is_active = False
        logger.info(f"View cleanup: {self.view_name}")
        self._log_event("VIEW_CLEANUP", f"View {self.view_name} cleaned up")

    def _log_event(self, event_type: str, details: str = ""):
        """
        Log an event through the session logger.

        Args:
            event_type: Type of event (e.g., "VIEW_READY", "OPERATION_STARTED")
            details: Additional details about the event
        """
        if self.session_logger:
            try:
                self.session_logger.log_gui_event(event_type, details)
            except Exception as e:
                logger.error(f"Failed to log event {event_type}: {e}")

    def show_status(self, message: str, status_type: str = "info"):
        """
        Show a status message in the application.

        Args:
            message: Status message to display
            status_type: Type of status ("info", "success", "warning", "error")
        """
        self._log_event(f"STATUS_{status_type.upper()}", message)

        # Delegate to app if it has a show_toast method
        if hasattr(self.app, "show_toast"):
            try:
                self.app.show_toast(message)
            except Exception as e:
                logger.error(f"Failed to show toast: {e}")

    def get_view_name(self) -> str:
        """Get the name of this view."""
        return self.view_name

    def is_view_active(self) -> bool:
        """Check if this view is currently active."""
        return self.is_active
