"""
@llm-doc Window Container Components
@llm-version 1.0.0
@llm-date 2025-11-15

AbstractWindow component providing window management functionality with dragging,
resizing, state management, focus handling, and design system integration.
"""

import contextlib

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")

from gi.repository import Adw, Gdk, GLib, GObject, Gtk

from .base import AdwComponentBase


class AbstractWindow(AdwComponentBase):
    """
    Abstract window component providing window management functionality.

    Features:
    - Window dragging and moving
    - Window resizing with constraints
    - Window state management (normal, maximized, minimized, fullscreen)
    - Focus management
    - Design system integration
    - Accessibility support

    Based on window.yaml component specification.
    """

    # GObject signals for window events
    __gsignals__ = {
        "window-resize": (GObject.SignalFlags.RUN_FIRST, None, (int, int, str)),
        "window-state-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (str, str, GObject.TYPE_INT64),
        ),
        "window-close-requested": (GObject.SignalFlags.RUN_FIRST, None, (bool, str)),
        "window-focus-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (bool, GObject.TYPE_INT64),
        ),
        "window-move": (GObject.SignalFlags.RUN_FIRST, None, (int, int, str)),
    }

    def __init__(
        self,
        title: str,
        width: int = 800,
        height: int = 600,
        min_width: int = 320,
        min_height: int = 240,
        resizable: bool = True,
        decorated: bool = True,
        modal: bool = False,
        always_on_top: bool = False,
        application: Adw.Application | None = None,
        **kwargs,
    ):
        """
        Initialize the abstract window component.

        Args:
            title: Window title displayed in title bar
            width: Default window width in pixels
            height: Default window height in pixels
            min_width: Minimum allowed window width
            min_height: Minimum allowed window height
            resizable: Whether window can be resized by user
            decorated: Whether to show platform window decorations
            modal: Whether window blocks interaction with other windows
            always_on_top: Whether window stays above other windows
            application: GTK application instance
        """
        # Store window properties
        self.title = title
        self.width = width
        self.height = height
        self.min_width = min_width
        self.min_height = min_height
        self.resizable = resizable
        self.decorated = decorated
        self.modal = modal
        self.always_on_top = always_on_top
        self.application = application

        # Window state tracking
        self._current_state = "default"
        self._previous_state = "default"
        self._is_focused = False

        # Gesture controllers for dragging
        self._drag_gesture = None

        super().__init__("abstract-window", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the window component."""
        # Create the main window widget
        if self.application:
            self.widget = Adw.ApplicationWindow(application=self.application)
        else:
            self.widget = Adw.ApplicationWindow()

        # Configure basic window properties
        self.widget.set_title(self.title)
        self.widget.set_default_size(self.width, self.height)
        self.widget.set_size_request(self.min_width, self.min_height)
        self.widget.set_resizable(self.resizable)
        self.widget.set_decorated(self.decorated)
        self.widget.set_modal(self.modal)

        # Set always on top if requested
        if self.always_on_top:
            # Note: This requires additional platform-specific handling
            pass

        # Create main container box for header bar + content
        self._main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Create and add header bar (required for Adw.ApplicationWindow to be draggable)
        self._header_bar = Adw.HeaderBar()
        self._header_bar.set_title_widget(Gtk.Label(label=self.title))
        self._main_box.append(self._header_bar)

        # Create content container (will be set via set_content())
        self._content_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._content_container.set_vexpand(True)
        self._content_container.set_hexpand(True)
        self._main_box.append(self._content_container)

        # Set main box as window content
        self.widget.set_content(self._main_box)

        # Set up window event handlers
        self._setup_window_handlers()

        # Set up drag gesture for window movement
        self._setup_drag_gesture()

        # Set up resize handlers
        self._setup_resize_handlers()

        # Apply initial state
        self.set_state("current_state", self._current_state)

    def _setup_window_handlers(self):
        """Set up basic window event handlers."""
        # Connect window state change signals
        self.connect_signal(self.widget, "notify::is-active", self._on_focus_changed)
        self.connect_signal(self.widget, "close-request", self._on_close_requested)

        # Connect to window state notifications
        if hasattr(self.widget, "connect"):
            # Monitor window state changes (maximized, minimized, etc.)
            self.connect_signal(self.widget, "notify::maximized", self._on_window_state_changed)
            self.connect_signal(self.widget, "notify::fullscreened", self._on_window_state_changed)

    def _setup_drag_gesture(self):
        """Set up drag gesture for window movement."""
        # Create drag gesture controller
        self._drag_gesture = Gtk.GestureDrag()
        self._drag_gesture.set_button(Gdk.BUTTON_PRIMARY)

        # Connect drag signals
        self.connect_signal(self._drag_gesture, "drag-begin", self._on_drag_begin)
        self.connect_signal(self._drag_gesture, "drag-update", self._on_drag_update)
        self.connect_signal(self._drag_gesture, "drag-end", self._on_drag_end)

        # Add gesture to window
        self.widget.add_controller(self._drag_gesture)

    def _setup_resize_handlers(self):
        """Set up resize event handlers."""
        # Connect to size change notifications
        self.connect_signal(self.widget, "notify::default-width", self._on_window_resized)
        self.connect_signal(self.widget, "notify::default-height", self._on_window_resized)

    def _apply_design_system(self):
        """Apply design system styling and window-specific CSS classes."""
        super()._apply_design_system()
        # Add window-specific semantic classes
        self.add_css_class("ds-window")
        self.add_css_class("ds-container")

    def _on_drag_begin(self, gesture, x, y):
        """Handle drag begin event for window movement."""
        # Only allow dragging from title bar area or if window is decorated
        if self.decorated:
            # Begin window move operation
            surface = self.widget.get_surface()
            if surface:
                device = gesture.get_device()
                if device:
                    with contextlib.suppress(AttributeError):
                        # Wayland surfaces don't support begin_move_drag
                        surface.begin_move_drag(
                            device,
                            Gdk.BUTTON_PRIMARY,
                            x,
                            y,
                            gesture.get_current_event_time(),
                        )

    def _on_drag_update(self, gesture, offset_x, offset_y):
        """Handle drag update event for window movement."""
        # Window movement is handled by the window manager
        # This is mainly for tracking purposes
        pass

    def _on_drag_end(self, gesture, offset_x, offset_y):
        """Handle drag end event for window movement."""
        # Get final window position
        if self.widget.get_surface():
            # Emit move signal with final position
            self.emit("window-move", int(offset_x), int(offset_y), "drag")

    def _on_window_resized(self, window, param):
        """Handle window resize events."""
        # Get current window size
        width = self.widget.get_width()
        height = self.widget.get_height()

        # Update internal size tracking
        self.width = width
        self.height = height

        # Emit resize signal
        self.emit("window-resize", width, height, "user")

    def _on_window_state_changed(self, window, param):
        """Handle window state changes (maximize, minimize, fullscreen)."""
        # Determine new state
        new_state = "normal"
        if hasattr(window, "is_maximized") and window.is_maximized():
            new_state = "maximized"
        elif hasattr(window, "is_fullscreen") and window.is_fullscreen():
            new_state = "fullscreen"

        # Update state if changed
        if new_state != self._current_state:
            old_state = self._current_state
            self._previous_state = old_state
            self._current_state = new_state

            # Update component state
            self.set_state("current_state", new_state)

            # Emit state change signal
            self.emit("window-state-changed", old_state, new_state, GLib.get_monotonic_time())

    def _on_focus_changed(self, window, param):
        """Handle window focus changes."""
        is_active = window.is_active() if hasattr(window, "is_active") else False

        if is_active != self._is_focused:
            self._is_focused = is_active

            # Update component state
            focus_state = "focused" if is_active else "unfocused"
            self.set_state("focus_state", focus_state)

            # Emit focus change signal
            self.emit("window-focus-changed", is_active, GLib.get_monotonic_time())

    def _on_close_requested(self, window):
        """Handle window close request."""
        # Emit close requested signal
        self.emit("window-close-requested", True, "user")

        # Return False to allow default close behavior
        # Subclasses can override this to prevent closing
        return False

    # Public API methods
    def set_window_state(self, state: str):
        """Set window state programmatically."""
        if state == "maximized":
            self.widget.maximize()
        elif state == "minimized":
            self.widget.minimize()
        elif state == "fullscreen":
            self.widget.fullscreen()
        elif state == "normal":
            if hasattr(self.widget, "unmaximize"):
                self.widget.unmaximize()
            if hasattr(self.widget, "unfullscreen"):
                self.widget.unfullscreen()

    def get_window_state(self) -> str:
        """Get current window state."""
        return self._current_state

    def set_window_title(self, title: str):
        """Set window title."""
        self.title = title
        self.widget.set_title(title)
        # Also update header bar title
        self._header_bar.set_title_widget(Gtk.Label(label=title))

    def get_window_title(self) -> str:
        """Get window title."""
        return self.title

    def set_window_size(self, width: int, height: int):
        """Set window size."""
        self.width = width
        self.height = height
        self.widget.set_default_size(width, height)

    def get_window_size(self) -> tuple[int, int]:
        """Get current window size."""
        return (self.width, self.height)

    def present_window(self):
        """Present the window to the user."""
        self.widget.present()

    def close_window(self):
        """Close the window."""
        self.widget.close()

    def set_content(self, content: Gtk.Widget):
        """
        Set the main content widget for the window.

        This replaces any existing content in the content area below the header bar.

        Args:
            content: The widget to set as window content
        """
        # Remove existing content if any
        child = self._content_container.get_first_child()
        if child:
            self._content_container.remove(child)

        # Add new content
        self._content_container.append(content)

    def get_content(self) -> Gtk.Widget | None:
        """
        Get the current content widget.

        Returns:
            The current content widget or None
        """
        return self._content_container.get_first_child()

    def get_header_bar(self) -> Adw.HeaderBar:
        """
        Get the window's header bar for customization.

        Returns:
            The header bar widget
        """
        return self._header_bar
