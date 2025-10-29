"""
@llm-doc Container GTK4 Components
@llm-version 1.0.0
@llm-date 2025-10-27

Container components for organizing and grouping content:
- StatusCard: Card displaying status information with icon and actions
- ServicePanel: Panel for displaying service information and controls
- LogContainer: Scrollable container for log content
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, GObject, Pango
from typing import Optional, List
from .base import ComponentBase, AdwComponentBase
from typing import Dict, Any, Optional, List


class StatusCard(AdwComponentBase):
    """
    Card component for displaying status information.
    
    Features:
    - Status icon and title
    - Optional subtitle and description
    - Action buttons
    - Status-based styling
    """
    
    def __init__(self,
                 title: str,
                 status: str = "neutral",
                 subtitle: Optional[str] = None,
                 description: Optional[str] = None,
                 icon_name: Optional[str] = None,
                 **kwargs):
        self.title = title
        self.status = status
        self.subtitle = subtitle
        self.description = description
        self.icon_name = icon_name
        self._action_buttons = []
        
        super().__init__("status-card", **kwargs)
    
    def _init_component(self, **kwargs):
        """Initialize the status card."""
        # Create main card
        self.widget = Adw.PreferencesGroup()
        
        # Create status row
        self._status_row = Adw.ActionRow()
        self._status_row.set_title(self.title)
        
        if self.subtitle:
            self._status_row.set_subtitle(self.subtitle)
        
        # Add icon if provided
        if self.icon_name:
            icon = Gtk.Image.new_from_icon_name(self.icon_name)
            self._status_row.add_prefix(icon)
        
        self.widget.add(self._status_row)
        
        # Add description if provided
        if self.description:
            desc_row = Adw.ActionRow()
            desc_label = Gtk.Label(label=self.description)
            desc_label.set_wrap(True)
            desc_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            desc_label.add_css_class("caption")
            desc_row.set_child(desc_label)
            self.widget.add(desc_row)
        
        # Apply status styling
        self._apply_status_styling()
    
    def _apply_status_styling(self):
        """Apply styling based on status."""
        # Status-based CSS classes
        status_classes = {
            "success": "success",
            "warning": "warning", 
            "error": "error",
            "info": "accent",
            "neutral": ""
        }
        
        css_class = status_classes.get(self.status, "")
        if css_class:
            self.widget.add_css_class(css_class)
        
        self.add_css_class(f"ds-status-{self.status}")
    
    def add_action_button(self, button: Gtk.Widget):
        """Add an action button to the card."""
        self._action_buttons.append(button)
        self._status_row.add_suffix(button)
    
    def set_title(self, title: str):
        """Update card title."""
        self.title = title
        self._status_row.set_title(title)
    
    def set_subtitle(self, subtitle: Optional[str]):
        """Update card subtitle."""
        self.subtitle = subtitle
        self._status_row.set_subtitle(subtitle or "")
    
    def set_status(self, status: str):
        """Update card status."""
        # Remove old status class
        old_class = f"ds-status-{self.status}"
        self.remove_css_class(old_class)
        
        self.status = status
        self._apply_status_styling()


class ServicePanel(AdwComponentBase):
    """
    Panel for displaying service information and controls.
    
    Features:
    - Service name and status
    - Health indicator
    - Control buttons
    - Expandable details
    """
    
    def __init__(self,
                 service_name: str,
                 service_status: str = "unknown",
                 port: Optional[int] = None,
                 health_method: Optional[str] = None,
                 **kwargs):
        self.service_name = service_name
        self.service_status = service_status
        self.port = port
        self.health_method = health_method
        self._expandable_row = None
        self._details_group = None
        
        super().__init__("service-panel", **kwargs)
    
    def _init_component(self, **kwargs):
        """Initialize the service panel."""
        # Create expandable row
        self._expandable_row = Adw.ExpanderRow()
        self._expandable_row.set_title(self.service_name)
        
        # Set status subtitle
        self._update_status_display()
        
        # Add status icon
        self._status_icon = Gtk.Image()
        self._update_status_icon()
        self._expandable_row.add_prefix(self._status_icon)
        
        # Create details group for expanded content
        self._details_group = Adw.PreferencesGroup()
        
        # Add port information
        if self.port:
            port_row = Adw.ActionRow()
            port_row.set_title("Port")
            port_row.set_subtitle(str(self.port))
            self._details_group.add(port_row)
        
        # Add health method information
        if self.health_method:
            health_row = Adw.ActionRow()
            health_row.set_title("Health Check")
            health_row.set_subtitle(self.health_method)
            self._details_group.add(health_row)
        
        # Create main container
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.widget.append(self._expandable_row)
        self.widget.append(self._details_group)
        
        # Apply styling
        self.add_css_class("ds-service-panel")
    
    def _update_status_display(self):
        """Update the status display."""
        status_text = self.service_status.replace("-", " ").title()
        self._expandable_row.set_subtitle(status_text)
    
    def _update_status_icon(self):
        """Update the status icon."""
        if self.service_status == "running":
            icon_name = "emblem-ok-symbolic"
            css_class = "success"
        elif self.service_status == "stopped":
            icon_name = "process-stop-symbolic"
            css_class = "error"
        elif self.service_status == "starting":
            icon_name = "content-loading-symbolic"
            css_class = "warning"
        else:
            icon_name = "dialog-question-symbolic"
            css_class = "neutral"
        
        self._status_icon.set_from_icon_name(icon_name)
        
        # Remove old status classes
        for status in ["success", "error", "warning", "neutral"]:
            self._status_icon.remove_css_class(status)
        
        self._status_icon.add_css_class(css_class)
    
    def set_service_status(self, status: str):
        """Update service status."""
        self.service_status = status
        self._update_status_display()
        self._update_status_icon()
    
    def add_action_button(self, button: Gtk.Widget):
        """Add an action button to the service panel."""
        self._expandable_row.add_suffix(button)


class LogContainer(ComponentBase):
    """
    Scrollable container for log content with filtering and search.
    
    Features:
    - Auto-scrolling to bottom
    - Text filtering
    - Copy functionality
    - Monospace font
    """
    
    def __init__(self,
                 auto_scroll: bool = True,
                 max_lines: int = 1000,
                 **kwargs):
        self.auto_scroll = auto_scroll
        self.max_lines = max_lines
        self._text_buffer = None
        self._text_view = None
        self._scrolled_window = None
        
        super().__init__("log-container", **kwargs)
    
    def _init_component(self, **kwargs):
        """Initialize the log container."""
        # Create scrolled window
        self._scrolled_window = Gtk.ScrolledWindow()
        self._scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC
        )
        self._scrolled_window.set_min_content_height(200)
        
        # Create text view
        self._text_view = Gtk.TextView()
        self._text_view.set_editable(False)
        self._text_view.set_cursor_visible(False)
        self._text_view.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self._text_view.add_css_class("monospace")
        
        # Get text buffer
        self._text_buffer = self._text_view.get_buffer()
        
        # Add text view to scrolled window
        self._scrolled_window.set_child(self._text_view)
        
        # Set as main widget
        self.widget = self._scrolled_window
        
        # Apply styling
        self.add_css_class("ds-log-container")


class SystemInfoCard(AdwComponentBase):
    """
    Card component for displaying categorized system information.

    Features:
    - Clean card layout with header and content sections
    - Support for key-value pairs and progress indicators
    - Semantic styling with design tokens
    - Expandable sections for detailed information
    """

    def __init__(self,
                 title: str = "",
                 subtitle: str = "",
                 icon_name: Optional[str] = None,
                 data: Optional[Dict[str, Any]] = None,
                 expandable: bool = False,
                 **kwargs):
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
                if key.endswith('_percent') and isinstance(value, (int, float)):
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
        if isinstance(value, (int, float)):
            if key.endswith('_percent') or key.endswith('_usage'):
                # Show as percentage with progress bar
                self._add_progress_row(row, key, value)
            elif key.endswith('_gb') or key.endswith('_mb'):
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
        return key.replace('_', ' ').title()

    def _format_size(self, value: float, key: str) -> str:
        """Format size values for display."""
        if key.endswith('_gb'):
            if value >= 1024:
                return f"{value / 1024:.1f} TB"
            else:
                return f"{value:.1f} GB"
        elif key.endswith('_mb'):
            if value >= 1024:
                return f"{value / 1024:.1f} GB"
            else:
                return f"{value:.0f} MB"
        else:
            return str(value)

    def update_data(self, new_data: Dict[str, Any]):
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

    def __init__(self,
                 columns: int = 2,
                 spacing: int = 12,
                 cards_data: Optional[List[Dict[str, Any]]] = None,
                 **kwargs):
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

        for i, card_data in enumerate(self.cards_data):
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

    def _create_card(self, card_data: Dict[str, Any]):
        """Create a card based on card data."""
        card_type = card_data.get('type', 'info')

        if card_type == 'performance':
            # Import here to avoid circular imports
            from complex import PerformanceIndicator
            return PerformanceIndicator(
                metric_type=card_data.get('metric_type', 'generic'),
                title=card_data.get('title', ''),
                current_value=card_data.get('current_value', 0.0),
                max_value=card_data.get('max_value', 100.0),
                unit=card_data.get('unit', '%')
            )
        elif card_type == 'system_info':
            return SystemInfoCard(
                title=card_data.get('title', ''),
                subtitle=card_data.get('subtitle', ''),
                icon_name=card_data.get('icon_name'),
                data=card_data.get('data', {})
            )
        else:
            # Default to SystemInfoCard
            return SystemInfoCard(
                title=card_data.get('title', 'Information'),
                subtitle=card_data.get('subtitle', ''),
                data=card_data.get('data', {})
            )

    def update_grid(self, new_cards_data: List[Dict[str, Any]]):
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

    def update_card_data(self, card_index: int, new_data: Dict[str, Any]):
        """Update data for a specific card."""
        if 0 <= card_index < len(self._cards):
            card = self._cards[card_index]
            if hasattr(card, 'update_data'):
                card.update_data(new_data)
            elif hasattr(card, 'update_value') and 'current_value' in new_data:
                card.update_value(new_data['current_value'])

    def get_card_count(self) -> int:
        """Get the number of cards in the grid."""
        return len(self._cards)

    def set_columns(self, columns: int):
        """Update the number of columns and recreate layout."""
        if columns != self.columns:
            self.columns = columns
            self._clear_grid()
            self._create_grid_layout()
    
    def append_text(self, text: str, tag: Optional[str] = None):
        """Append text to the log."""
        # Get end iterator
        end_iter = self._text_buffer.get_end_iter()
        
        # Insert text (simplified - no tags for now)
        self._text_buffer.insert(end_iter, text + "\n")
        
        # Limit buffer size
        self._limit_buffer_size()
        
        # Auto-scroll if enabled
        if self.auto_scroll:
            self._scroll_to_bottom()
    
    def _limit_buffer_size(self):
        """Limit buffer to max_lines."""
        line_count = self._text_buffer.get_line_count()
        if line_count > self.max_lines:
            # Remove lines from the beginning
            lines_to_remove = line_count - self.max_lines
            start_iter = self._text_buffer.get_start_iter()
            end_iter = self._text_buffer.get_iter_at_line(lines_to_remove)
            self._text_buffer.delete(start_iter, end_iter)
    
    def _scroll_to_bottom(self):
        """Scroll to the bottom of the log."""
        mark = self._text_buffer.get_insert()
        end_iter = self._text_buffer.get_end_iter()
        self._text_buffer.place_cursor(end_iter)
        self._text_view.scroll_mark_onscreen(mark)
    
    def clear(self):
        """Clear all log content."""
        self._text_buffer.set_text("")
    
    def get_text(self) -> str:
        """Get all log text."""
        start_iter = self._text_buffer.get_start_iter()
        end_iter = self._text_buffer.get_end_iter()
        return self._text_buffer.get_text(start_iter, end_iter, False)
