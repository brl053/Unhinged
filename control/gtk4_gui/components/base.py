"""
@llm-doc Base Component Classes for GTK4 Component Library
@llm-version 1.0.0
@llm-date 2025-10-27

Base classes providing common functionality for all components:
- Design system integration
- Theme management
- Event handling patterns
- Accessibility support
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, GObject
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import json

# Optional yaml import for design tokens
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ComponentError(Exception):
    """Base exception for component-related errors."""
    pass


class ComponentBase(GObject.Object):
    """
    Base class for all Unhinged GTK4 components.
    
    Provides:
    - Design system token integration
    - Theme management
    - Common event handling patterns
    - Accessibility helpers
    - State management
    """
    
    # GObject signals
    __gsignals__ = {
        'state-changed': (GObject.SignalFlags.RUN_FIRST, None, (str, object)),
        'action-triggered': (GObject.SignalFlags.RUN_FIRST, None, (str, object)),
    }
    
    def __init__(self, component_id: str, **kwargs):
        super().__init__()
        
        self.component_id = component_id
        self.widget = None  # Main GTK widget - set by subclasses
        self._state = {}
        self._design_tokens = {}
        self._css_classes = set()
        
        # Load design tokens
        self._load_design_tokens()
        
        # Initialize component
        self._init_component(**kwargs)
        self._setup_accessibility()
        self._apply_design_system()
    
    def _init_component(self, **kwargs):
        """Override in subclasses to initialize the component."""
        pass
    
    def _load_design_tokens(self):
        """Load design system tokens for component styling."""
        try:
            # Path to design system tokens
            project_root = Path(__file__).parent.parent.parent.parent
            tokens_path = project_root / "libs" / "design_system" / "tokens" / "semantic.yaml"
            
            if tokens_path.exists() and YAML_AVAILABLE:
                with open(tokens_path) as f:
                    self._design_tokens = yaml.safe_load(f)
            else:
                # Fallback to basic tokens
                self._design_tokens = self._get_fallback_tokens()
                
        except Exception as e:
            print(f"⚠️  Could not load design tokens: {e}")
            self._design_tokens = self._get_fallback_tokens()
    
    def _get_fallback_tokens(self) -> Dict[str, Any]:
        """Fallback design tokens when file loading fails."""
        return {
            "color": {
                "action": {"primary": "#0066CC", "secondary": "#6C757D"},
                "status": {"success": "#28A745", "warning": "#FFC107", "error": "#DC3545"},
                "surface": {"primary": "#FFFFFF", "secondary": "#F8F9FA"}
            },
            "spacing": {
                "sp_1": "4px", "sp_2": "8px", "sp_3": "12px", "sp_4": "16px"
            },
            "radius": {
                "sm": "4px", "md": "8px", "lg": "12px"
            }
        }
    
    def _setup_accessibility(self):
        """Setup accessibility features for the component."""
        if self.widget:
            # Set accessible name if not already set
            if not self.widget.get_accessible_role():
                self.widget.set_accessible_role(Gtk.AccessibleRole.WIDGET)
    
    def _apply_design_system(self):
        """Apply design system styling to the component."""
        if self.widget:
            # Add component base class
            self.widget.add_css_class(f"unhinged-{self.component_id}")
            
            # Add semantic classes
            for css_class in self._css_classes:
                self.widget.add_css_class(css_class)
    
    def add_css_class(self, css_class: str):
        """Add a CSS class to the component."""
        self._css_classes.add(css_class)
        if self.widget:
            self.widget.add_css_class(css_class)
    
    def remove_css_class(self, css_class: str):
        """Remove a CSS class from the component."""
        self._css_classes.discard(css_class)
        if self.widget:
            self.widget.remove_css_class(css_class)
    
    def set_state(self, key: str, value: Any):
        """Set component state and emit signal."""
        old_value = self._state.get(key)
        self._state[key] = value
        
        if old_value != value:
            self.emit('state-changed', key, value)
            self._on_state_changed(key, value, old_value)
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get component state value."""
        return self._state.get(key, default)
    
    def _on_state_changed(self, key: str, new_value: Any, old_value: Any):
        """Override in subclasses to handle state changes."""
        pass
    
    def trigger_action(self, action: str, data: Any = None):
        """Trigger a component action and emit signal."""
        self.emit('action-triggered', action, data)
        self._on_action_triggered(action, data)
    
    def _on_action_triggered(self, action: str, data: Any):
        """Override in subclasses to handle actions."""
        pass
    
    def get_widget(self) -> Gtk.Widget:
        """Get the main GTK widget for this component."""
        return self.widget

    def cleanup(self):
        """Clean up component resources and disconnect signals."""
        if hasattr(self, '_signal_handlers'):
            for handler_id, widget in self._signal_handlers:
                if widget and handler_id:
                    try:
                        widget.disconnect(handler_id)
                    except:
                        pass  # Widget may already be destroyed
            self._signal_handlers.clear()

        # Clear widget reference
        if hasattr(self, 'widget'):
            self.widget = None

    def connect_signal(self, widget, signal, callback, *args):
        """Connect a signal and track it for cleanup."""
        if not hasattr(self, '_signal_handlers'):
            self._signal_handlers = []

        handler_id = widget.connect(signal, callback, *args)
        self._signal_handlers.append((handler_id, widget))
        return handler_id
    
    def set_sensitive(self, sensitive: bool):
        """Set component sensitivity (enabled/disabled)."""
        if self.widget:
            self.widget.set_sensitive(sensitive)
    
    def set_visible(self, visible: bool):
        """Set component visibility."""
        if self.widget:
            self.widget.set_visible(visible)
    
    def get_design_token(self, path: str, default: str = "") -> str:
        """
        Get a design token value by path.
        
        Args:
            path: Dot-separated path like "color.action.primary"
            default: Default value if token not found
            
        Returns:
            Token value or default
        """
        try:
            value = self._design_tokens
            for key in path.split('.'):
                value = value[key]
            return str(value)
        except (KeyError, TypeError):
            return default


class AdwComponentBase(ComponentBase):
    """
    Base class for components that use Libadwaita widgets.
    
    Provides additional Adw-specific functionality and styling.
    """
    
    def __init__(self, component_id: str, **kwargs):
        super().__init__(component_id, **kwargs)
    
    def _apply_design_system(self):
        """Apply design system with Adw-specific enhancements."""
        super()._apply_design_system()
        
        # Add Adw-specific classes
        if self.widget:
            self.widget.add_css_class("adw-component")
