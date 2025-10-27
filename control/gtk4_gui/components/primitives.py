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
from typing import Optional, Callable
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
