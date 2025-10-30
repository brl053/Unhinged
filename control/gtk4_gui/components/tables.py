#!/usr/bin/env python3
"""
@llm-doc Generic Table Components for GTK4 UI
@llm-version 1.0.0
@llm-date 2025-10-28

Reusable table foundation components following design system patterns
for structured data display with sorting, filtering, and accessibility.
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from collections.abc import Callable
from enum import Enum
from typing import Any

from gi.repository import Gtk, Pango


class SortDirection(Enum):
    """Sort direction enumeration"""
    ASCENDING = "asc"
    DESCENDING = "desc"


class TableColumn:
    """Table column definition"""
    def __init__(self, name: str, title: str, sortable: bool = True, width: int = -1):
        self.name = name
        self.title = title
        self.sortable = sortable
        self.width = width


class GenericTable(Gtk.Box):
    """
    Reusable table foundation for structured data display.
    
    Features:
    - Column headers with sort indicators
    - Row selection and highlighting
    - Keyboard navigation (arrow keys, enter)
    - Accessibility labels and descriptions
    - Design system integration
    """

    def __init__(self, columns: list[TableColumn], row_factory: Callable):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Configuration
        self.columns = columns
        self.row_factory = row_factory
        self.sort_column = None
        self.sort_direction = SortDirection.ASCENDING
        self.data = []
        self.filtered_data = []
        self.filter_func = None

        # UI Components
        self.header_box = None
        self.list_box = None
        self.selection_model = None

        # Callbacks
        self.sort_changed_callback = None
        self.selection_changed_callback = None

        # Setup UI
        self._setup_ui()
        self._setup_accessibility()
        self._setup_keyboard_navigation()

        # Apply design system styling
        self.add_css_class("ds-generic-table")

    def _setup_ui(self):
        """Setup the table UI structure"""
        # Create header
        self.header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.header_box.add_css_class("ds-table-header")
        self.header_box.set_homogeneous(True)

        # Create column headers
        for column in self.columns:
            header_button = self._create_column_header(column)
            self.header_box.append(header_button)

        self.append(self.header_box)

        # Create scrolled window for content
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        scrolled.set_min_content_height(250)  # Ensure minimum height for table content

        # Create list box for rows
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list_box.add_css_class("ds-table-body")

        # Connect selection signal
        self.list_box.connect("row-selected", self._on_row_selected)

        scrolled.set_child(self.list_box)
        self.append(scrolled)

    def _create_column_header(self, column: TableColumn) -> Gtk.Button:
        """Create a column header button with sort indicator"""
        button = Gtk.Button()
        button.set_hexpand(True)
        button.add_css_class("ds-table-header-button")

        # Create header content box
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.set_halign(Gtk.Align.START)

        # Column title
        title_label = Gtk.Label(label=column.title)
        title_label.set_ellipsize(Pango.EllipsizeMode.END)
        title_label.add_css_class("ds-table-header-title")
        header_box.append(title_label)

        # Sort indicator (initially hidden)
        sort_icon = Gtk.Image()
        sort_icon.set_visible(False)
        sort_icon.add_css_class("ds-table-sort-indicator")
        header_box.append(sort_icon)

        button.set_child(header_box)

        # Store references for sorting
        button.column = column
        button.sort_icon = sort_icon
        button.title_label = title_label

        # Connect sort signal if sortable
        if column.sortable:
            button.connect("clicked", self._on_column_header_clicked)
            button.set_tooltip_text(f"Sort by {column.title}")
        else:
            button.set_sensitive(False)

        return button

    def _setup_accessibility(self):
        """Setup accessibility features"""
        # Set accessible role
        self.set_accessible_role(Gtk.AccessibleRole.TABLE)

        # Add table description using tooltip
        self.set_tooltip_text(f"Data table with {len(self.columns)} columns")

    def _setup_keyboard_navigation(self):
        """Setup keyboard navigation"""
        # Create key controller
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        self.list_box.add_controller(key_controller)

        # Set focusable
        self.list_box.set_can_focus(True)

    def _on_column_header_clicked(self, button):
        """Handle column header click for sorting"""
        column = button.column

        # Toggle sort direction if same column, otherwise set ascending
        if self.sort_column == column.name:
            self.sort_direction = (
                SortDirection.DESCENDING
                if self.sort_direction == SortDirection.ASCENDING
                else SortDirection.ASCENDING
            )
        else:
            self.sort_column = column.name
            self.sort_direction = SortDirection.ASCENDING

        # Update sort indicators
        self._update_sort_indicators()

        # Apply sort
        self._apply_sort()

        # Notify callback
        if self.sort_changed_callback:
            self.sort_changed_callback(self.sort_column, self.sort_direction)

    def _update_sort_indicators(self):
        """Update visual sort indicators in headers"""
        # Clear all indicators first
        for child in self.header_box:
            if hasattr(child, 'sort_icon'):
                child.sort_icon.set_visible(False)

        # Set indicator for current sort column
        if self.sort_column:
            for child in self.header_box:
                if hasattr(child, 'column') and child.column.name == self.sort_column:
                    icon_name = (
                        "view-sort-ascending-symbolic"
                        if self.sort_direction == SortDirection.ASCENDING
                        else "view-sort-descending-symbolic"
                    )
                    child.sort_icon.set_from_icon_name(icon_name)
                    child.sort_icon.set_visible(True)
                    break

    def _on_row_selected(self, list_box, row):
        """Handle row selection"""
        if self.selection_changed_callback and row:
            # Get the data associated with this row
            row_data = getattr(row, 'data', None)
            self.selection_changed_callback(row_data)

    def _on_key_pressed(self, controller, keyval, keycode, state):
        """Handle keyboard navigation"""
        if keyval == 65293:  # Enter key
            selected_row = self.list_box.get_selected_row()
            if selected_row and self.selection_changed_callback:
                row_data = getattr(selected_row, 'data', None)
                self.selection_changed_callback(row_data)
            return True
        return False

    def set_data(self, data: list[Any]):
        """Set table data and refresh display"""
        self.data = data
        self.filtered_data = data.copy()
        self._apply_filter()
        self._apply_sort()
        self._refresh_rows()

    def add_data(self, item: Any):
        """Add single item to table"""
        self.data.append(item)
        if not self.filter_func or self.filter_func(item):
            self.filtered_data.append(item)
            self._apply_sort()
            self._refresh_rows()

    def remove_data(self, item: Any):
        """Remove item from table"""
        if item in self.data:
            self.data.remove(item)
        if item in self.filtered_data:
            self.filtered_data.remove(item)
            self._refresh_rows()

    def set_filter(self, filter_func: Callable[[Any], bool] | None):
        """Set filter function and refresh display"""
        self.filter_func = filter_func
        self._apply_filter()
        self._apply_sort()
        self._refresh_rows()

    def _apply_filter(self):
        """Apply current filter to data"""
        if self.filter_func:
            self.filtered_data = [item for item in self.data if self.filter_func(item)]
        else:
            self.filtered_data = self.data.copy()

    def _apply_sort(self):
        """Apply current sort to filtered data"""
        if self.sort_column and self.filtered_data:
            reverse = self.sort_direction == SortDirection.DESCENDING
            try:
                self.filtered_data.sort(
                    key=lambda item: getattr(item, self.sort_column, 0),
                    reverse=reverse
                )
            except (AttributeError, TypeError):
                # Fallback for items without the sort attribute
                pass

    def _refresh_rows(self):
        """Refresh table rows with current data"""
        # Clear existing rows
        while True:
            row = self.list_box.get_first_child()
            if row is None:
                break
            self.list_box.remove(row)

        # Add new rows
        for item in self.filtered_data:
            row_widget = self.row_factory(item)

            # Create list box row
            list_row = Gtk.ListBoxRow()
            list_row.set_child(row_widget)
            list_row.data = item  # Store data reference
            list_row.add_css_class("ds-table-row")

            self.list_box.append(list_row)

        # Update accessibility
        self.set_tooltip_text(f"Data table with {len(self.filtered_data)} rows, {len(self.columns)} columns")

    def get_selected_data(self) -> Any | None:
        """Get data for currently selected row"""
        selected_row = self.list_box.get_selected_row()
        return getattr(selected_row, 'data', None) if selected_row else None

    def set_sort_changed_callback(self, callback: Callable[[str, SortDirection], None]):
        """Set callback for sort changes"""
        self.sort_changed_callback = callback

    def set_selection_changed_callback(self, callback: Callable[[Any], None]):
        """Set callback for selection changes"""
        self.selection_changed_callback = callback

    def clear(self):
        """Clear all data and rows"""
        self.data.clear()
        self.filtered_data.clear()
        self._refresh_rows()
