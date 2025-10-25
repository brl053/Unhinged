
# Initialize GUI event logger
gui_logger = create_gui_logger("unhinged-components", "1.0.0")

"""
Reusable UI Component Library
Provides consistent, reusable components following the design system patterns.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, GLib, Gio
from typing import Dict, List, Optional, Callable, Any, Union
from enum import Enum
from dataclasses import dataclass
import time
from unhinged_events import create_gui_logger


class ComponentSize(Enum):
    """Component size variants"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class ComponentVariant(Enum):
    """Component style variants"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"


@dataclass
class ComponentTheme:
    """Component theming configuration"""
    primary_color: str = "#007AFF"
    secondary_color: str = "#5856D6"
    success_color: str = "#34C759"
    warning_color: str = "#FF9500"
    error_color: str = "#FF3B30"
    info_color: str = "#5AC8FA"
    
    background_color: str = "#FFFFFF"
    surface_color: str = "#F2F2F7"
    text_color: str = "#000000"
    secondary_text_color: str = "#8E8E93"
    
    border_radius: int = 8
    spacing: int = 12
    padding: int = 16


class Card(Adw.Bin):
    """Card component with elevation and rounded corners"""
    
    def __init__(self, title: str = "", subtitle: str = "", 
                 variant: ComponentVariant = ComponentVariant.PRIMARY):
        super().__init__()
        
        # Card properties
        self.title = title
        self.subtitle = subtitle
        self.variant = variant
        
        # Create card structure
        self._create_card()
        
        # Apply styling
        self.add_css_class("card")
        self.add_css_class(f"card-{variant.value}")
    
    def _create_card(self):
        """Create card structure"""
        # Main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.main_box.set_margin_top(16)
        self.main_box.set_margin_bottom(16)
        self.main_box.set_margin_start(16)
        self.main_box.set_margin_end(16)
        
        # Header
        if self.title or self.subtitle:
            self.header = self._create_header()
            self.main_box.append(self.header)
        
        # Content area
        self.content_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.main_box.append(self.content_area)
        
        # Actions area
        self.actions_area = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.actions_area.set_halign(Gtk.Align.END)
        self.actions_area.set_visible(False)
        self.main_box.append(self.actions_area)
        
        self.set_child(self.main_box)
    
    def _create_header(self) -> Gtk.Widget:
        """Create card header"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        if self.title:
            title_label = Gtk.Label(label=self.title)
            title_label.set_halign(Gtk.Align.START)
            title_label.add_css_class("card-title")
            header_box.append(title_label)
        
        if self.subtitle:
            subtitle_label = Gtk.Label(label=self.subtitle)
            subtitle_label.set_halign(Gtk.Align.START)
            subtitle_label.add_css_class("card-subtitle")
            header_box.append(subtitle_label)
        
        return header_box
    
    def set_content(self, widget: Gtk.Widget):
        """Set card content"""
        # Clear existing content
        child = self.content_area.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.content_area.remove(child)
            child = next_child
        
        # Add new content
        self.content_area.append(widget)
    
    def add_action(self, button: Gtk.Button):
        """Add action button to card"""
        self.actions_area.append(button)
        self.actions_area.set_visible(True)


class StatusIndicator(Gtk.Box):
    """Status indicator with color and animation"""

    def __init__(self, status: str = "idle",
                 variant: ComponentVariant = ComponentVariant.INFO,
                 animated: bool = False):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.status = status
        self.variant = variant
        self.animated = animated

        # Set alignment
        self.set_halign(Gtk.Align.START)

        # Status dot
        self.dot = Gtk.DrawingArea()
        self.dot.set_size_request(12, 12)
        self.dot.set_draw_func(self._draw_dot)
        self.append(self.dot)

        # Status label
        self.label = Gtk.Label(label=status)
        self.label.add_css_class("status-label")
        self.append(self.label)
        
        # Apply styling
        self.add_css_class("status-indicator")
        self.add_css_class(f"status-{variant.value}")
        
        # Animation
        if animated:
            self._start_animation()
    
    def _draw_dot(self, area, cr, width, height, user_data):
        """Draw status dot"""
        # Get color based on variant
        colors = {
            ComponentVariant.PRIMARY: (0.0, 0.48, 1.0),    # Blue
            ComponentVariant.SUCCESS: (0.2, 0.78, 0.35),   # Green
            ComponentVariant.WARNING: (1.0, 0.58, 0.0),    # Orange
            ComponentVariant.ERROR: (1.0, 0.23, 0.19),     # Red
            ComponentVariant.INFO: (0.35, 0.78, 0.98),     # Light blue
            ComponentVariant.SECONDARY: (0.35, 0.34, 0.84) # Purple
        }
        
        color = colors.get(self.variant, (0.5, 0.5, 0.5))
        
        # Draw circle
        cr.set_source_rgb(*color)
        cr.arc(width / 2, height / 2, min(width, height) / 2 - 1, 0, 2 * 3.14159)
        cr.fill()
    
    def _start_animation(self):
        """Start pulsing animation"""
        def pulse():
            self.dot.queue_draw()
            return True  # Continue animation
        
        GLib.timeout_add(500, pulse)
    
    def set_status(self, status: str, variant: ComponentVariant = None):
        """Update status"""
        self.status = status
        self.label.set_text(status)
        
        if variant:
            # Remove old variant class
            self.remove_css_class(f"status-{self.variant.value}")
            self.variant = variant
            self.add_css_class(f"status-{variant.value}")
            
            self.dot.queue_draw()


class ProgressCard(Card):
    """Card with progress indicator"""
    
    def __init__(self, title: str, total_steps: int = 100):
        super().__init__(title=title)
        
        self.total_steps = total_steps
        self.current_step = 0
        
        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_fraction(0.0)
        
        # Progress info
        self.progress_info = Gtk.Label(label="0 / 0")
        self.progress_info.add_css_class("caption")
        self.progress_info.set_halign(Gtk.Align.END)
        
        # Add to content
        progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        progress_box.append(self.progress_bar)
        progress_box.append(self.progress_info)
        
        self.set_content(progress_box)
    
    def set_progress(self, current: int, total: int = None):
        """Update progress"""
        if total:
            self.total_steps = total
        
        self.current_step = current
        fraction = current / self.total_steps if self.total_steps > 0 else 0
        
        self.progress_bar.set_fraction(fraction)
        self.progress_bar.set_text(f"{fraction * 100:.1f}%")
        self.progress_info.set_text(f"{current} / {self.total_steps}")
    
    def pulse(self):
        """Pulse progress bar for indeterminate progress"""
        self.progress_bar.pulse()


class MetricCard(Card):
    """Card displaying a metric with value and trend"""
    
    def __init__(self, title: str, value: str = "0", 
                 trend: Optional[str] = None, 
                 trend_positive: bool = True):
        super().__init__(title=title)
        
        self.value = value
        self.trend = trend
        self.trend_positive = trend_positive
        
        # Create metric display
        self._create_metric_display()
    
    def _create_metric_display(self):
        """Create metric display"""
        metric_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # Value
        value_label = Gtk.Label(label=self.value)
        value_label.add_css_class("metric-value")
        value_label.set_halign(Gtk.Align.START)
        metric_box.append(value_label)
        
        # Trend
        if self.trend:
            trend_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            
            # Trend icon
            trend_icon = Gtk.Image()
            if self.trend_positive:
                trend_icon.set_from_icon_name("go-up-symbolic")
                trend_box.add_css_class("trend-positive")
            else:
                trend_icon.set_from_icon_name("go-down-symbolic")
                trend_box.add_css_class("trend-negative")
            
            trend_box.append(trend_icon)
            
            # Trend text
            trend_label = Gtk.Label(label=self.trend)
            trend_label.add_css_class("trend-text")
            trend_box.append(trend_label)
            
            metric_box.append(trend_box)
        
        self.set_content(metric_box)
    
    def update_metric(self, value: str, trend: Optional[str] = None, 
                     trend_positive: bool = True):
        """Update metric values"""
        self.value = value
        self.trend = trend
        self.trend_positive = trend_positive
        
        # Recreate display
        self._create_metric_display()


class ActionSheet(Adw.Window):
    """Modal action sheet for mobile interfaces"""
    
    def __init__(self, parent: Gtk.Window, title: str = ""):
        super().__init__()
        
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(400, -1)
        
        # Create content
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.main_box)
        
        # Header
        if title:
            header = Adw.HeaderBar()
            header.set_title_widget(Gtk.Label(label=title))
            
            # Close button
            close_button = Gtk.Button.new_from_icon_name("window-close-symbolic")
            close_button.connect("clicked", lambda b: self.close())
            header.pack_end(close_button)
            
            self.main_box.append(header)
        
        # Actions list
        self.actions_list = Gtk.ListBox()
        self.actions_list.add_css_class("boxed-list")
        self.main_box.append(self.actions_list)
        
        # Actions
        self.actions: List[Dict] = []
    
    def add_action(self, label: str, callback: Callable, 
                   icon_name: Optional[str] = None,
                   destructive: bool = False):
        """Add action to sheet"""
        action_row = Adw.ActionRow()
        action_row.set_title(label)
        
        if icon_name:
            action_row.add_prefix(Gtk.Image.new_from_icon_name(icon_name))
        
        if destructive:
            action_row.add_css_class("destructive-action")
        
        # Connect callback
        def on_activated(row):
            callback()
            self.close()
        
        action_row.set_activatable(True)
        action_row.connect("activated", on_activated)
        
        self.actions_list.append(action_row)
        
        self.actions.append({
            'label': label,
            'callback': callback,
            'icon_name': icon_name,
            'destructive': destructive
        })


def create_toast(message: str,
                variant: ComponentVariant = ComponentVariant.INFO,
                duration: int = 3000,
                action_label: Optional[str] = None,
                action_callback: Optional[Callable] = None) -> Adw.Toast:
    """
    Create enhanced toast notification

    Args:
        message: Toast message text
        variant: Toast variant for styling
        duration: Display duration in milliseconds
        action_label: Optional action button label
        action_callback: Optional action button callback

    Returns:
        Configured Adw.Toast instance
    """
    toast = Adw.Toast.new(message)
    toast.set_timeout(duration)

    # Add action if provided
    if action_label and action_callback:
        toast.set_button_label(action_label)
        toast.connect("button-clicked", lambda t: action_callback())

    # Apply variant styling
    if variant == ComponentVariant.SUCCESS:
        toast.add_css_class("toast-success")
    elif variant == ComponentVariant.WARNING:
        toast.add_css_class("toast-warning")
    elif variant == ComponentVariant.ERROR:
        toast.add_css_class("toast-error")

    return toast


class LoadingSpinner(Gtk.Box):
    """Loading spinner with customizable size and message"""

    def __init__(self, message: str = "Loading...",
                 size: ComponentSize = ComponentSize.MEDIUM):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        self.message = message
        self.size = size

        # Set alignment
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)

        # Spinner
        self.spinner = Gtk.Spinner()
        self.spinner.set_spinning(True)

        # Size variants
        if size == ComponentSize.SMALL:
            self.spinner.set_size_request(16, 16)
        elif size == ComponentSize.LARGE:
            self.spinner.set_size_request(48, 48)
        else:  # MEDIUM
            self.spinner.set_size_request(32, 32)

        self.append(self.spinner)

        # Message
        if message:
            message_label = Gtk.Label(label=message)
            message_label.add_css_class("loading-message")
            self.append(message_label)
        
        # Apply styling
        self.add_css_class("loading-spinner")
        self.add_css_class(f"loading-{size.value}")
    
    def set_message(self, message: str):
        """Update loading message"""
        self.message = message
        # Would need to update the label widget
    
    def start(self):
        """Start spinner animation"""
        self.spinner.start()
    
    def stop(self):
        """Stop spinner animation"""
        self.spinner.stop()


class EmptyState(Gtk.Box):
    """Empty state component with icon and message"""

    def __init__(self, title: str, subtitle: str = "",
                 icon_name: str = "folder-symbolic",
                 action_label: Optional[str] = None,
                 action_callback: Optional[Callable] = None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)

        # Set alignment
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)

        # Icon
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(64)
        icon.add_css_class("empty-state-icon")
        self.append(icon)

        # Title
        title_label = Gtk.Label(label=title)
        title_label.add_css_class("empty-state-title")
        self.append(title_label)

        # Subtitle
        if subtitle:
            subtitle_label = Gtk.Label(label=subtitle)
            subtitle_label.add_css_class("empty-state-subtitle")
            subtitle_label.set_wrap(True)
            subtitle_label.set_justify(Gtk.Justification.CENTER)
            self.append(subtitle_label)

        # Action button
        if action_label and action_callback:
            action_button = Gtk.Button(label=action_label)
            action_button.add_css_class("suggested-action")
            action_button.connect("clicked", lambda b: action_callback())
            self.append(action_button)
        
        # Apply styling
        self.add_css_class("empty-state")


# Component factory functions
def create_primary_button(label: str, callback: Callable) -> Gtk.Button:
    """Create primary action button"""
    button = Gtk.Button(label=label)
    button.add_css_class("suggested-action")
    button.connect("clicked", lambda b: callback())
    return button


def create_secondary_button(label: str, callback: Callable) -> Gtk.Button:
    """Create secondary action button"""
    button = Gtk.Button(label=label)
    button.connect("clicked", lambda b: callback())
    return button


def create_destructive_button(label: str, callback: Callable) -> Gtk.Button:
    """Create destructive action button"""
    button = Gtk.Button(label=label)
    button.add_css_class("destructive-action")
    button.connect("clicked", lambda b: callback())
    return button


def show_toast(parent: Adw.ToastOverlay, message: str,
               variant: ComponentVariant = ComponentVariant.INFO) -> Adw.Toast:
    """Show toast notification"""
    toast = create_toast(message, variant)
    parent.add_toast(toast)
    return toast


# Test function
def test_components():
    """Test UI components"""
    gui_logger.info(" Testing UI components...", {"event_type": "theming"})
    
    app = Adw.Application()
    
    def on_activate(app):
        window = Adw.ApplicationWindow(application=app)
        window.set_title("Component Library Test")
        window.set_default_size(600, 800)
        
        # Create toast overlay
        toast_overlay = Adw.ToastOverlay()
        window.set_content(toast_overlay)
        
        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        toast_overlay.set_child(scrolled)
        
        # Create main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(16)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)
        scrolled.set_child(main_box)
        
        # Test cards
        card1 = Card("Test Card", "This is a test card")
        card1.set_content(Gtk.Label(label="Card content goes here"))
        main_box.append(card1)
        
        # Test metric card
        metric_card = MetricCard("Active Users", "1,234", "+12%", True)
        main_box.append(metric_card)
        
        # Test progress card
        progress_card = ProgressCard("Upload Progress", 100)
        progress_card.set_progress(75)
        main_box.append(progress_card)
        
        # Test status indicator
        status = StatusIndicator("Connected", ComponentVariant.SUCCESS, True)
        main_box.append(status)
        
        # Test buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        primary_btn = create_primary_button("Primary", 
                                          lambda: show_toast(toast_overlay, "Primary clicked!"))
        secondary_btn = create_secondary_button("Secondary", 
                                              lambda: show_toast(toast_overlay, "Secondary clicked!"))
        destructive_btn = create_destructive_button("Delete", 
                                                   lambda: show_toast(toast_overlay, "Delete clicked!", ComponentVariant.ERROR))
        
        button_box.append(primary_btn)
        button_box.append(secondary_btn)
        button_box.append(destructive_btn)
        main_box.append(button_box)
        
        # Test empty state
        empty_state = EmptyState("No Data", "Try adding some content", 
                                "folder-symbolic", "Add Content", 
                                lambda: show_toast(toast_overlay, "Add content clicked!"))
        main_box.append(empty_state)
        
        window.present()
    
    app.connect("activate", on_activate)
    app.run()


if __name__ == "__main__":
    test_components()
