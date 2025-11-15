"""
UI Controller - Handles all UI creation and layout management

Extracted from desktop_app.py to achieve 75% reduction target.
Manages window creation, tab navigation, and content layout.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk


class UIController:
    """Controller for UI creation and layout management"""

    def __init__(self, app):
        """Initialize UI controller with app reference"""
        self.app = app
        self.project_root = app.project_root

    def create_main_window(self):
        """Create the main application window using AbstractWindow component"""
        # Import AbstractWindow component (lazy import to avoid circular dependencies)
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent))
        from components import AbstractWindow

        # Create AbstractWindow with proper configuration
        abstract_window = AbstractWindow(
            title="Unhinged Platform",
            width=1200,
            height=800,
            min_width=800,
            min_height=600,
            resizable=True,
            decorated=True,  # Use platform decorations
            modal=False,
            always_on_top=False,
            application=self.app,
        )

        # Create toast overlay for notifications
        self.app.toast_overlay = Adw.ToastOverlay()

        # Create tab navigation
        self.create_tab_navigation()

        # Set toast overlay as window content
        abstract_window.set_content(self.app.toast_overlay)

        # Store reference to AbstractWindow component
        self.app.abstract_window = abstract_window

        # Return the underlying GTK widget for compatibility
        return abstract_window.widget

    def create_tab_navigation(self):
        """Create sidebar navigation with NavigationSplitView"""
        # Create navigation split view
        self.app.navigation_split_view = Adw.NavigationSplitView()

        # Create content area with stack for different pages
        self.app.content_stack = Adw.ViewStack()
        self.app.content_stack.set_vexpand(True)
        self.app.content_stack.set_hexpand(True)

        # Add pages to stack
        self._add_stack_pages()

        # Create sidebar navigation
        sidebar_content = self.create_sidebar_navigation()

        # Wrap sidebar in NavigationPage (required by NavigationSplitView)
        sidebar_page = Adw.NavigationPage.new(sidebar_content, "Navigation")
        sidebar_page.set_title("Navigation")

        # Wrap content stack in NavigationPage
        content_page = Adw.NavigationPage.new(self.app.content_stack, "Content")
        content_page.set_title("Content")

        # Set up navigation split view with wrapped pages
        self.app.navigation_split_view.set_sidebar(sidebar_page)
        self.app.navigation_split_view.set_content(content_page)

        # Set default page to Status (main tab removed)
        self.app.content_stack.set_visible_child_name("status")

        # Set up toast overlay
        self.app.toast_overlay.set_child(self.app.navigation_split_view)

    def _add_stack_pages(self):
        """Add all pages to the content stack (main tab removed)"""
        pages = [
            ("status", "Status", self.app.create_status_tab_content),
            ("system", "System Info", self.app.create_system_info_tab_content),
            ("processes", "Processes", self.app.create_processes_tab_content),
            ("input", "Input", self.app.create_input_tab_content),
            ("chatroom", "OS Chatroom", self.app.create_chatroom_tab_content),
            ("gpu_drivers", "GPU", self.app.create_gpu_drivers_tab_content),
            ("bluetooth", "Bluetooth", self.app.create_bluetooth_tab_content),
            ("output", "Output", self.app.create_output_tab_content),
            ("usb", "USB", self.app.create_usb_tab_content),
            ("documents", "Documents", self.app.create_documents_tab_content),
            ("graphs", "Graphs", self.app.create_graph_tab_content),
        ]

        created = 0
        failed = []
        for page_id, title, create_func in pages:
            try:
                content = create_func()
                page = self.app.content_stack.add_titled(content, page_id, title)
                page.set_icon_name(self._get_page_icon(page_id))
                created += 1
            except Exception as e:
                failed.append(f"{title}: {e}")
                # NO FALLBACKS - Let it fail and fix the root cause
                import traceback

                traceback.print_exc()
                raise Exception(f"Page creation failed for {title}: {e}")

        # Aggregate output
        print(f"✅ UI pages initialized ({created}/{len(pages)} pages)")

    def _get_page_icon(self, page_id):
        """Get icon name for page (main tab removed)"""
        icons = {
            "status": "dialog-information-symbolic",
            "system": "computer-symbolic",
            "processes": "system-run-symbolic",
            "input": "audio-input-microphone-symbolic",
            "chatroom": "user-available-symbolic",
            "gpu_drivers": "video-card-symbolic",
            "bluetooth": "bluetooth-symbolic",
            "output": "audio-speakers-symbolic",
            "usb": "drive-removable-media-symbolic",
            "graphs": "network-workgroup-symbolic",
        }
        return icons.get(page_id, "dialog-information-symbolic")

    def create_sidebar_navigation(self):
        """Create sidebar navigation with design system styling"""
        # Create sidebar list box
        sidebar_list = Gtk.ListBox()
        sidebar_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        sidebar_list.add_css_class("navigation-sidebar")

        # Navigation items (main tab removed)
        nav_items = [
            ("status", "Status", "dialog-information-symbolic"),
            ("system", "System Info", "computer-symbolic"),
            ("processes", "Processes", "system-run-symbolic"),
            ("input", "Input", "audio-input-microphone-symbolic"),
            ("chatroom", "OS Chatroom", "user-available-symbolic"),
            ("gpu_drivers", "GPU", "video-card-symbolic"),
            ("bluetooth", "Bluetooth", "bluetooth-symbolic"),
            ("output", "Output", "audio-speakers-symbolic"),
            ("usb", "USB", "drive-removable-media-symbolic"),
            ("documents", "Documents", "folder-documents-symbolic"),
            ("graphs", "Graphs", "network-workgroup-symbolic"),
        ]

        for item_id, title, icon_name in nav_items:
            row = self._create_sidebar_row(item_id, title, icon_name)
            sidebar_list.append(row)

        # Connect selection handler
        sidebar_list.connect("row-selected", self._on_sidebar_selection_changed)

        # Set default selection
        first_row = sidebar_list.get_row_at_index(0)
        if first_row:
            sidebar_list.select_row(first_row)
            first_row.add_css_class("sidebar-nav-active")

        # Create scrolled window
        sidebar_scrolled = Gtk.ScrolledWindow()
        sidebar_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sidebar_scrolled.set_child(sidebar_list)

        # Apply design system width
        sidebar_scrolled.set_size_request(240, -1)

        return sidebar_scrolled

    def _create_sidebar_row(self, item_id, title, icon_name):
        """Create a sidebar navigation row"""
        row = Gtk.ListBoxRow()
        row.item_id = item_id
        row.add_css_class("sidebar-nav-row")

        # Create row content
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(12)
        box.set_margin_end(12)

        # Icon
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_icon_size(Gtk.IconSize.NORMAL)
        box.append(icon)

        # Label
        label = Gtk.Label(label=title)
        label.set_halign(Gtk.Align.START)
        box.append(label)

        row.set_child(box)
        return row

    def _on_sidebar_selection_changed(self, list_box, row):
        """Handle sidebar navigation selection with lifecycle management"""
        if row and hasattr(row, "item_id"):
            # Cleanup previous view if it has lifecycle hooks
            if hasattr(self.app, "current_view") and self.app.current_view:
                if hasattr(self.app.current_view, "on_cleanup"):
                    try:
                        self.app.current_view.on_cleanup()
                    except Exception as e:
                        print(f"⚠️ Error during view cleanup: {e}")

            # Switch to selected page
            self.app.content_stack.set_visible_child_name(row.item_id)

            # Call on_ready for new view if it has lifecycle hooks
            view_name = row.item_id
            if view_name == "bluetooth" and hasattr(self.app, "bluetooth_view"):
                self.app.current_view = self.app.bluetooth_view
                if hasattr(self.app.bluetooth_view, "on_ready"):
                    try:
                        self.app.bluetooth_view.on_ready()
                    except Exception as e:
                        print(f"⚠️ Error during view ready: {e}")
            elif view_name == "processes" and hasattr(self.app, "processes_view"):
                self.app.current_view = self.app.processes_view
                if hasattr(self.app.processes_view, "on_ready"):
                    try:
                        self.app.processes_view.on_ready()
                    except Exception as e:
                        print(f"⚠️ Error during view ready: {e}")
            elif view_name == "chatroom" and hasattr(self.app, "chatroom_view"):
                self.app.current_view = self.app.chatroom_view
                if hasattr(self.app.chatroom_view, "on_ready"):
                    try:
                        self.app.chatroom_view.on_ready()
                    except Exception as e:
                        print(f"⚠️ Error during view ready: {e}")
            elif view_name == "usb" and hasattr(self.app, "usb_view"):
                self.app.current_view = self.app.usb_view
                if hasattr(self.app.usb_view, "on_ready"):
                    try:
                        self.app.usb_view.on_ready()
                    except Exception as e:
                        print(f"⚠️ Error during view ready: {e}")
            elif view_name == "gpu_drivers" and hasattr(self.app, "gpu_view"):
                self.app.current_view = self.app.gpu_view
                if hasattr(self.app.gpu_view, "on_ready"):
                    try:
                        self.app.gpu_view.on_ready()
                    except Exception as e:
                        print(f"⚠️ Error during view ready: {e}")
            else:
                self.app.current_view = None

            # Update active styling
            self._update_sidebar_active_state(row)

    def _update_sidebar_active_state(self, active_row):
        """Update sidebar active state styling"""
        # Remove active class from all rows
        parent = active_row.get_parent()
        if parent:
            row_index = 0
            while True:
                row = parent.get_row_at_index(row_index)
                if not row:
                    break
                row.remove_css_class("sidebar-nav-active")
                row_index += 1

        # Add active class to selected row
        active_row.add_css_class("sidebar-nav-active")
