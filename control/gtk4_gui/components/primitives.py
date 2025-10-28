"""
@llm-doc Primitive GTK4 Components
@llm-version 1.0.0
@llm-date 2025-10-27

Basic building block components:
- ActionButton: Enhanced button with design system integration
- StatusLabel: Label with status styling (success, warning, error)
- ProgressIndicator: Progress bar with semantic styling
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, GObject, Pango
from typing import Optional, Callable, Dict, Any
from base import ComponentBase, AdwComponentBase


class ActionButton(AdwComponentBase):
    """
    Enhanced button component with design system integration.
    
    Features:
    - Semantic styling (primary, secondary, destructive)
    - Loading states with spinner
    - Icon support
    - Keyboard accessibility
    """
    
    __gsignals__ = {
        'clicked': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }
    
    def __init__(self, 
                 label: str = "",
                 style: str = "primary",
                 icon_name: Optional[str] = None,
                 **kwargs):
        self.label = label
        self.style = style
        self.icon_name = icon_name
        self._loading = False
        self._spinner = None
        self._original_child = None
        
        super().__init__("action-button", **kwargs)
    
    def _init_component(self, **kwargs):
        """Initialize the button widget."""
        self.widget = Gtk.Button()
        
        # Set up button content
        self._setup_button_content()
        
        # Apply styling
        self._apply_button_style()
        
        # Connect signals
        self.widget.connect('clicked', self._on_clicked)
        
        # Set accessibility
        if self.label:
            self.widget.set_tooltip_text(self.label)

        # Add ARIA attributes
        self.widget.set_accessible_role(Gtk.AccessibleRole.BUTTON)
        if self.label:
            self.widget.update_property([Gtk.AccessibleProperty.LABEL], [self.label])
    
    def _setup_button_content(self):
        """Setup button content with optional icon."""
        if self.icon_name:
            # Button with icon and label
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            
            icon = Gtk.Image.new_from_icon_name(self.icon_name)
            box.append(icon)
            
            if self.label:
                label = Gtk.Label(label=self.label)
                box.append(label)
            
            self.widget.set_child(box)
            self._original_child = box
        else:
            # Text-only button
            self.widget.set_label(self.label)
            self._original_child = None
    
    def _apply_button_style(self):
        """Apply semantic styling based on button style."""
        style_classes = {
            "primary": "suggested-action",
            "secondary": "",
            "destructive": "destructive-action",
            "flat": "flat",
        }
        
        css_class = style_classes.get(self.style, "")
        if css_class:
            self.widget.add_css_class(css_class)
        
        # Add design system class
        self.add_css_class(f"ds-action-{self.style}")
    
    def _on_clicked(self, button):
        """Handle button click."""
        if not self._loading:
            self.emit('clicked')
            self.trigger_action('clicked')
    
    def set_loading(self, loading: bool):
        """Set loading state with spinner."""
        if self._loading == loading:
            return
            
        self._loading = loading
        
        if loading:
            # Show spinner
            self._spinner = Gtk.Spinner()
            self._spinner.set_spinning(True)
            self.widget.set_child(self._spinner)
            self.widget.set_sensitive(False)
        else:
            # Restore original content
            if self._original_child:
                self.widget.set_child(self._original_child)
            else:
                self.widget.set_label(self.label)
            self.widget.set_sensitive(True)
            self._spinner = None
    
    def set_label(self, label: str):
        """Update button label."""
        self.label = label
        if not self._loading:
            if self._original_child is None:
                self.widget.set_label(label)
            else:
                self._setup_button_content()


class StatusLabel(ComponentBase):
    """
    Label component with semantic status styling.
    
    Supports status types: success, warning, error, info, neutral
    """
    
    def __init__(self, 
                 text: str = "",
                 status: str = "neutral",
                 **kwargs):
        self.text = text
        self.status = status
        
        super().__init__("status-label", **kwargs)
    
    def _init_component(self, **kwargs):
        """Initialize the label widget."""
        self.widget = Gtk.Label(label=self.text)
        self.widget.set_wrap(True)
        self.widget.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        
        # Apply status styling
        self._apply_status_style()
    
    def _apply_status_style(self):
        """Apply styling based on status type."""
        # Remove existing status classes
        for status_type in ["success", "warning", "error", "info", "neutral"]:
            self.widget.remove_css_class(f"status-{status_type}")
        
        # Add current status class
        self.widget.add_css_class(f"status-{self.status}")
        self.add_css_class(f"ds-status-{self.status}")
    
    def set_text(self, text: str):
        """Update label text."""
        self.text = text
        self.widget.set_label(text)
    
    def set_status(self, status: str):
        """Update status type."""
        self.status = status
        self._apply_status_style()


class ProgressIndicator(ComponentBase):
    """
    Progress indicator with semantic styling and optional text.
    
    Supports determinate and indeterminate progress.
    """
    
    def __init__(self, 
                 progress: float = 0.0,
                 text: Optional[str] = None,
                 show_percentage: bool = False,
                 **kwargs):
        self.progress = progress
        self.text = text
        self.show_percentage = show_percentage
        self._progress_bar = None
        self._label = None
        
        super().__init__("progress-indicator", **kwargs)
    
    def _init_component(self, **kwargs):
        """Initialize the progress indicator."""
        # Create container
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        # Create progress bar
        self._progress_bar = Gtk.ProgressBar()
        self._progress_bar.set_fraction(self.progress)
        self.widget.append(self._progress_bar)
        
        # Create optional label
        if self.text or self.show_percentage:
            self._label = Gtk.Label()
            self._label.add_css_class("caption")
            self.widget.append(self._label)
            self._update_label()
        
        # Apply styling
        self.add_css_class("ds-progress-indicator")
    
    def _update_label(self):
        """Update the progress label."""
        if not self._label:
            return
            
        label_text = ""
        if self.text:
            label_text = self.text
        
        if self.show_percentage:
            percentage = int(self.progress * 100)
            if label_text:
                label_text += f" ({percentage}%)"
            else:
                label_text = f"{percentage}%"
        
        self._label.set_label(label_text)
    
    def set_progress(self, progress: float):
        """Set progress value (0.0 to 1.0)."""
        self.progress = max(0.0, min(1.0, progress))
        self._progress_bar.set_fraction(self.progress)
        self._update_label()
    
    def set_text(self, text: Optional[str]):
        """Set progress text."""
        self.text = text
        self._update_label()
    
    def pulse(self):
        """Pulse the progress bar for indeterminate progress."""
        self._progress_bar.pulse()
    
    def set_indeterminate(self, indeterminate: bool):
        """Set indeterminate mode."""
        if indeterminate:
            self._progress_bar.set_fraction(0.0)
            self._progress_bar.pulse()
        else:
            self._progress_bar.set_fraction(self.progress)


class HardwareInfoRow(AdwComponentBase):
    """
    Specialized row component for displaying hardware details.

    Features:
    - Hardware-specific icons and styling
    - Status indicators for hardware health
    - Expandable details for complex hardware info
    - Semantic color coding
    """

    def __init__(self,
                 title: str = "",
                 subtitle: str = "",
                 hardware_type: str = "generic",
                 status: str = "normal",
                 details: Optional[Dict[str, Any]] = None,
                 icon_name: Optional[str] = None,
                 **kwargs):
        self.title = title
        self.subtitle = subtitle
        self.hardware_type = hardware_type
        self.status = status
        self.details = details or {}
        self.icon_name = icon_name or self._get_default_icon()

        super().__init__("hardware-info-row", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the hardware info row widget."""
        self.widget = Adw.ActionRow()
        self.widget.set_title(self.title)
        if self.subtitle:
            self.widget.set_subtitle(self.subtitle)

        # Add hardware icon
        self._setup_icon()

        # Add status indicator
        self._setup_status_indicator()

        # Add details if available
        if self.details:
            self._setup_details_button()

        # Apply styling
        self.add_css_class("ds-hardware-info-row")
        self._apply_hardware_styling()

        # Apply status-based styling
        if self.status in ["good", "normal"]:
            self.add_css_class("status-success")
        elif self.status == "warning":
            self.add_css_class("status-warning")
        elif self.status in ["error", "critical"]:
            self.add_css_class("status-error")
        else:
            self.add_css_class("status-info")

        # Add accessibility attributes
        self.widget.set_accessible_role(Gtk.AccessibleRole.LIST_ITEM)
        self.widget.update_property([Gtk.AccessibleProperty.LABEL], [f"{self.hardware_type}: {self.title}"])
        if self.subtitle:
            self.widget.update_property([Gtk.AccessibleProperty.DESCRIPTION], [self.subtitle])

    def _get_default_icon(self) -> str:
        """Get default icon based on hardware type."""
        icon_map = {
            "cpu": "cpu-symbolic",
            "memory": "memory-symbolic",
            "storage": "drive-harddisk-symbolic",
            "gpu": "video-display-symbolic",
            "network": "network-wired-symbolic",
            "motherboard": "computer-symbolic",
            "generic": "emblem-system-symbolic"
        }
        return icon_map.get(self.hardware_type, "emblem-system-symbolic")

    def _setup_icon(self):
        """Setup hardware icon."""
        icon = Gtk.Image.new_from_icon_name(self.icon_name)
        icon.set_icon_size(Gtk.IconSize.LARGE)
        icon.add_css_class(f"hardware-{self.hardware_type}")
        self.widget.add_prefix(icon)

    def _setup_status_indicator(self):
        """Setup status indicator."""
        status_icon = Gtk.Image()
        status_icon.set_icon_size(Gtk.IconSize.NORMAL)

        # Set icon and styling based on status
        if self.status == "good" or self.status == "normal":
            status_icon.set_from_icon_name("emblem-ok-symbolic")
            status_icon.add_css_class("success")
        elif self.status == "warning":
            status_icon.set_from_icon_name("dialog-warning-symbolic")
            status_icon.add_css_class("warning")
        elif self.status == "error" or self.status == "critical":
            status_icon.set_from_icon_name("dialog-error-symbolic")
            status_icon.add_css_class("error")
        else:
            status_icon.set_from_icon_name("dialog-information-symbolic")
            status_icon.add_css_class("info")

        self.widget.add_suffix(status_icon)

    def _setup_details_button(self):
        """Setup details expansion button."""
        details_button = Gtk.Button()
        details_button.set_icon_name("view-more-symbolic")
        details_button.add_css_class("flat")
        details_button.set_tooltip_text("Show details")
        self.connect_signal(details_button, "clicked", self._on_details_clicked)

        self.widget.add_suffix(details_button)

    def _apply_hardware_styling(self):
        """Apply hardware-specific styling."""
        self.add_css_class(f"hardware-{self.hardware_type}")
        self.add_css_class(f"status-{self.status}")

    def _on_details_clicked(self, button):
        """Handle details button click."""
        # Create details dialog or popover
        dialog = Adw.MessageDialog()
        dialog.set_heading(f"{self.title} Details")

        # Format details as text
        details_text = ""
        for key, value in self.details.items():
            formatted_key = key.replace('_', ' ').title()
            details_text += f"{formatted_key}: {value}\n"

        dialog.set_body(details_text)
        dialog.add_response("close", "Close")
        dialog.set_default_response("close")

        # Show dialog
        if hasattr(self.widget, 'get_root'):
            root = self.widget.get_root()
            if root:
                dialog.set_transient_for(root)

        dialog.present()

    def update_status(self, new_status: str):
        """Update hardware status."""
        self.status = new_status
        self._apply_hardware_styling()
        # Re-setup status indicator
        # Note: In a full implementation, we'd update the existing indicator

    def update_details(self, new_details: Dict[str, Any]):
        """Update hardware details."""
        self.details = new_details
