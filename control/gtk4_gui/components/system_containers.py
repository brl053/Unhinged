"""
@llm-doc System Container Components
@llm-version 1.0.0
@llm-date 2025-11-15

SystemInfoCard and SystemStatusGrid components for displaying system information
and metrics in card and grid layouts.
"""

from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk

from .base import AdwComponentBase


class SystemInfoCard(AdwComponentBase):
    """
    Card component for displaying categorized system information.

    Features:
    - Clean card layout with header and content sections
    - Support for key-value pairs and progress indicators
    - Semantic styling with design tokens
    - Expandable sections for detailed information
    """

    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        icon_name: str | None = None,
        data: dict[str, Any] | None = None,
        expandable: bool = False,
        **kwargs,
    ):
        self.title = title
        self.subtitle = subtitle
        self.icon_name = icon_name
        self.data = data or {}
        self.expandable = expandable
        self._content_rows = []

        super().__init__("system-info-card", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the system info card widget."""
        # Create preferences group for card structure
        self.widget = Adw.PreferencesGroup()
        self.widget.set_title(self.title)
        if self.subtitle:
            self.widget.set_description(self.subtitle)

        # Add header row if icon is provided
        if self.icon_name:
            self._create_header_row()

        # Add data rows
        self._create_data_rows()

        # Apply styling
        self.add_css_class("ds-system-info-card")

        # Apply semantic styling based on data
        if self.data:
            for key, value in self.data.items():
                if key.endswith("_percent") and isinstance(value, int | float):
                    if value > 90:
                        self.add_css_class("status-error")
                    elif value > 75:
                        self.add_css_class("status-warning")
                    else:
                        self.add_css_class("status-success")

        # Add accessibility attributes
        self.widget.set_accessible_role(Gtk.AccessibleRole.GROUP)
        self.widget.update_property([Gtk.AccessibleProperty.LABEL], [f"System Information: {self.title}"])
        if self.subtitle:
            self.widget.update_property([Gtk.AccessibleProperty.DESCRIPTION], [self.subtitle])

    def _create_header_row(self):
        """Create header row with icon and title."""
        header_row = Adw.ActionRow()
        header_row.set_title(self.title)
        if self.subtitle:
            header_row.set_subtitle(self.subtitle)

        # Add icon
        icon = Gtk.Image.new_from_icon_name(self.icon_name)
        icon.set_icon_size(Gtk.IconSize.LARGE)
        header_row.add_prefix(icon)

        self.widget.add(header_row)

    def _create_data_rows(self):
        """Create rows for data display."""
        for key, value in self.data.items():
            self._add_data_row(key, value)

    def _add_data_row(self, key: str, value: Any):
        """Add a single data row."""
        row = Adw.ActionRow()
        row.set_title(self._format_key(key))

        # Format value based on type
        if isinstance(value, int | float):
            if key.endswith("_percent") or key.endswith("_usage"):
                # Show as percentage with progress bar
                self._add_progress_row(row, key, value)
            elif key.endswith("_gb") or key.endswith("_mb"):
                # Show as formatted size
                formatted_value = self._format_size(value, key)
                row.set_subtitle(formatted_value)
            else:
                row.set_subtitle(str(value))
        elif isinstance(value, list):
            # Show list as comma-separated string
            row.set_subtitle(", ".join(str(v) for v in value[:3]))  # Limit to first 3 items
            if len(value) > 3:
                row.set_subtitle(row.get_subtitle() + f" (+{len(value) - 3} more)")
        else:
            row.set_subtitle(str(value))

        self.widget.add(row)
        self._content_rows.append(row)

    def _add_progress_row(self, row: Adw.ActionRow, key: str, value: float):
        """Add progress bar to row for percentage values."""
        # Create progress bar
        progress = Gtk.ProgressBar()
        progress.set_fraction(min(value / 100.0, 1.0))
        progress.set_show_text(True)
        progress.set_text(f"{value:.1f}%")

        # Apply semantic styling based on value
        if value > 90:
            progress.add_css_class("error")
        elif value > 75:
            progress.add_css_class("warning")
        else:
            progress.add_css_class("success")

        # Set size
        progress.set_size_request(120, -1)

        row.add_suffix(progress)
        row.set_subtitle(f"{value:.1f}%")

    def _format_key(self, key: str) -> str:
        """Format key for display."""
        # Convert snake_case to Title Case
        return key.replace("_", " ").title()

    def _format_size(self, value: float, key: str) -> str:
        """Format size values for display."""
        if key.endswith("_gb"):
            if value >= 1024:
                return f"{value / 1024:.1f} TB"
            else:
                return f"{value:.1f} GB"
        elif key.endswith("_mb"):
            if value >= 1024:
                return f"{value / 1024:.1f} GB"
            else:
                return f"{value:.0f} MB"
        else:
            return str(value)

    def update_data(self, new_data: dict[str, Any]):
        """Update the card data and refresh display."""
        self.data = new_data

        # Remove existing content rows
        for row in self._content_rows:
            self.widget.remove(row)
        self._content_rows.clear()

        # Recreate data rows
        self._create_data_rows()

    def set_loading(self, loading: bool = True):
        """Set loading state for the card."""
        if loading:
            self.add_css_class("loading")
            # Could add spinner here
        else:
            self.remove_css_class("loading")


class SystemStatusGrid(AdwComponentBase):
    """
    Grid layout component for system overview display.

    Features:
    - Responsive grid layout for system metrics
    - Configurable columns and spacing
    - Support for different card types
    - Automatic layout adjustment
    """

    def __init__(
        self,
        columns: int = 2,
        spacing: int = 12,
        cards_data: list[dict[str, Any]] | None = None,
        **kwargs,
    ):
        self.columns = columns
        self.spacing = spacing
        self.cards_data = cards_data or []
        self._cards = []

        super().__init__("system-status-grid", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the system status grid."""
        # Create main container with grid layout
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=self.spacing)

        # Create grid rows
        self._create_grid_layout()

        # Apply styling
        self.add_css_class("ds-system-status-grid")

    def _create_grid_layout(self):
        """Create grid layout with cards."""
        if not self.cards_data:
            return

        current_row = None
        cards_in_row = 0

        for _i, card_data in enumerate(self.cards_data):
            # Create new row if needed
            if cards_in_row == 0:
                current_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=self.spacing)
                current_row.set_homogeneous(True)  # Equal width columns
                self.widget.append(current_row)

            # Create card based on type
            card = self._create_card(card_data)
            if card:
                current_row.append(card.get_widget())
                self._cards.append(card)
                cards_in_row += 1

            # Start new row if current row is full
            if cards_in_row >= self.columns:
                cards_in_row = 0

    def _create_card(self, card_data: dict[str, Any]):
        """Create a card based on card data."""
        card_type = card_data.get("type", "info")

        if card_type == "performance":
            # Import here to avoid circular imports
            from complex import PerformanceIndicator

            return PerformanceIndicator(
                metric_type=card_data.get("metric_type", "generic"),
                title=card_data.get("title", ""),
                current_value=card_data.get("current_value", 0.0),
                max_value=card_data.get("max_value", 100.0),
                unit=card_data.get("unit", "%"),
            )
        elif card_type == "system_info":
            return SystemInfoCard(
                title=card_data.get("title", ""),
                subtitle=card_data.get("subtitle", ""),
                icon_name=card_data.get("icon_name"),
                data=card_data.get("data", {}),
            )
        else:
            # Default to SystemInfoCard
            return SystemInfoCard(
                title=card_data.get("title", "Information"),
                subtitle=card_data.get("subtitle", ""),
                data=card_data.get("data", {}),
            )

    def update_grid(self, new_cards_data: list[dict[str, Any]]):
        """Update the grid with new card data."""
        self.cards_data = new_cards_data

        # Clear existing cards
        self._clear_grid()

        # Recreate grid
        self._create_grid_layout()

    def _clear_grid(self):
        """Clear all cards from the grid."""
        # Remove all children from widget
        child = self.widget.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.widget.remove(child)
            child = next_child

        # Clear cards list
        self._cards.clear()

    def update_card_data(self, card_index: int, new_data: dict[str, Any]):
        """Update data for a specific card."""
        if 0 <= card_index < len(self._cards):
            card = self._cards[card_index]
            if hasattr(card, "update_data"):
                card.update_data(new_data)
            elif hasattr(card, "update_value") and "current_value" in new_data:
                card.update_value(new_data["current_value"])

    def get_card_count(self) -> int:
        """Get the number of cards in the grid."""
        return len(self._cards)

    def set_columns(self, columns: int):
        """Update the number of columns and recreate layout."""
        if columns != self.columns:
            self.columns = columns
            self._clear_grid()
            self._create_grid_layout()
