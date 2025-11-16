"""
@llm-doc Desktop App UI Utilities
@llm-version 1.0.0
@llm-date 2025-11-15

UI utilities for dialogs, toasts, and status updates.
"""

from gi.repository import Adw, GLib


class UIUtilities:
    """Utilities for UI operations."""

    @staticmethod
    def show_error_dialog(app, title, message):
        """Show error dialog to user."""

        def show_dialog():
            dialog = Adw.MessageDialog(transient_for=app.window)
            dialog.set_heading(title)
            dialog.set_body(message)
            dialog.add_response("ok", "OK")
            dialog.set_default_response("ok")
            dialog.present()

        GLib.idle_add(show_dialog)

    @staticmethod
    def show_toast(app, message, timeout=3):
        """Show toast notification with visual stack management."""

        def show_toast_ui():
            toast = Adw.Toast.new(message)

            if len(app.toast_stack) >= app.max_toast_stack:
                app.toast_stack.pop(0)

            app.toast_stack.append(toast)

            stack_position = len(app.toast_stack) - 1
            if stack_position == 0:
                toast.set_timeout(1)
            elif stack_position == 1:
                toast.set_timeout(2)
            else:
                toast.set_timeout(timeout)

            app.toast_overlay.add_toast(toast)

            def on_toast_dismissed():
                if toast in app.toast_stack:
                    app.toast_stack.remove(toast)

            try:
                toast.connect("dismissed", lambda t: on_toast_dismissed())
            except Exception:
                GLib.timeout_add_seconds(max(timeout, 3), lambda: on_toast_dismissed() or False)

        GLib.idle_add(show_toast_ui)

    @staticmethod
    def update_status(app, message, progress=None):
        """Update status label and progress bar."""
        GLib.idle_add(UIUtilities._update_status_ui, app, message, progress)

    @staticmethod
    def _update_status_ui(app, message, progress):
        """Update UI elements from main thread."""
        if hasattr(app, "status_view") and app.status_view:
            app.status_view._update_platform_status(message, progress)

        if app.session_logger:
            app.session_logger.log_status_change("Previous", message)

        return False

    @staticmethod
    def append_log(app, message):
        """Append message to log."""
        GLib.idle_add(UIUtilities._append_log_ui, app, message)

    @staticmethod
    def _append_log_ui(app, message):
        """Append to log from main thread."""
        if hasattr(app, "status_view") and app.status_view:
            app.status_view._append_platform_log(message)

        if app.session_logger:
            app.session_logger.log_platform_output(message)

            if "Platform started successfully" in message:
                app.session_logger.log_platform_status_update(message)

        return False

    @staticmethod
    def reset_buttons(app):
        """Reset button states."""
        if hasattr(app, "status_view") and app.status_view:
            if hasattr(app.status_view, "start_button") and app.status_view.start_button:
                app.status_view.start_button.set_sensitive(True)
            if hasattr(app.status_view, "stop_button") and app.status_view.stop_button:
                app.status_view.stop_button.set_sensitive(False)
        return False
