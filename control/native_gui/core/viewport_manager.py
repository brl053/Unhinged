"""
@llm-type control-system
@llm-legend viewport_manager.py - system control component
@llm-key Core functionality for viewport_manager
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token viewport_manager: system control component
"""
"""
📱 Viewport Manager - Device Emulation & Responsive Design

Provides Chrome DevTools-style device emulation for GTK applications.
Configurable viewport dimensions with mobile-first responsive design.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable


class DeviceType(Enum):
    """Device type enumeration"""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    CUSTOM = "custom"


@dataclass
class ViewportConfig:
    """Viewport configuration for device emulation"""
    name: str
    width: int
    height: int
    device_type: DeviceType
    pixel_ratio: float = 1.0
    user_agent: Optional[str] = None
    description: Optional[str] = None


class ViewportManager:
    """
    Manages viewport dimensions and device emulation.
    
    Provides Chrome DevTools-style device emulation with:
    - Predefined device presets (iPhone, Pixel, iPad, etc.)
    - Custom viewport dimensions
    - Responsive breakpoint detection
    - Mobile-first design system integration
    """
    
    # Predefined device configurations
    DEVICE_PRESETS = {
        # Mobile Devices
        "iphone_15_pro": ViewportConfig(
            name="iPhone 15 Pro",
            width=393,
            height=852,
            device_type=DeviceType.MOBILE,
            pixel_ratio=3.0,
            description="iPhone 15 Pro (393×852)"
        ),
        "pixel_8": ViewportConfig(
            name="Google Pixel 8",
            width=412,
            height=915,
            device_type=DeviceType.MOBILE,
            pixel_ratio=2.625,
            description="Google Pixel 8 (412×915)"
        ),
        "galaxy_s24": ViewportConfig(
            name="Samsung Galaxy S24",
            width=384,
            height=854,
            device_type=DeviceType.MOBILE,
            pixel_ratio=3.0,
            description="Samsung Galaxy S24 (384×854)"
        ),
        
        # Tablets
        "ipad_air": ViewportConfig(
            name="iPad Air",
            width=820,
            height=1180,
            device_type=DeviceType.TABLET,
            pixel_ratio=2.0,
            description="iPad Air (820×1180)"
        ),
        "pixel_tablet": ViewportConfig(
            name="Google Pixel Tablet",
            width=1600,
            height=2560,
            device_type=DeviceType.TABLET,
            pixel_ratio=2.0,
            description="Google Pixel Tablet (1600×2560)"
        ),
        
        # Desktop
        "desktop_1080p": ViewportConfig(
            name="Desktop 1080p",
            width=1920,
            height=1080,
            device_type=DeviceType.DESKTOP,
            pixel_ratio=1.0,
            description="Desktop 1080p (1920×1080)"
        ),
        "desktop_4k": ViewportConfig(
            name="Desktop 4K",
            width=3840,
            height=2160,
            device_type=DeviceType.DESKTOP,
            pixel_ratio=2.0,
            description="Desktop 4K (3840×2160)"
        ),
    }
    
    def __init__(self, window: Optional[Gtk.Window]):
        self.window = window
        self.current_config: Optional[ViewportConfig] = None
        self.on_viewport_changed: Optional[Callable[[ViewportConfig], None]] = None
        self._pending_viewport = "pixel_8"  # Default viewport to apply when window is available

        # Apply default viewport if window is available
        if self.window is not None:
            self.set_viewport("pixel_8")

        print("📱 Viewport Manager initialized with mobile-first design")

    def set_window(self, window: Gtk.Window):
        """Set the window reference and apply any pending viewport configuration"""
        self.window = window
        if self._pending_viewport:
            self.set_viewport(self._pending_viewport)
            self._pending_viewport = None

    def set_viewport(self, preset_name: str) -> bool:
        """Set viewport to a predefined device preset"""
        if preset_name not in self.DEVICE_PRESETS:
            print(f"❌ Unknown device preset: {preset_name}")
            return False
        
        config = self.DEVICE_PRESETS[preset_name]
        return self._apply_viewport_config(config)
    
    def set_custom_viewport(self, width: int, height: int, name: str = "Custom") -> bool:
        """Set custom viewport dimensions"""
        config = ViewportConfig(
            name=name,
            width=width,
            height=height,
            device_type=DeviceType.CUSTOM,
            description=f"Custom ({width}×{height})"
        )
        return self._apply_viewport_config(config)
    
    def _apply_viewport_config(self, config: ViewportConfig) -> bool:
        """Apply viewport configuration to the window"""
        if self.window is None:
            print(f"⚠️ Window not available, deferring viewport config: {config.name}")
            self._pending_viewport = None  # Clear pending since we're storing the config
            self.current_config = config  # Store config for later application
            return False

        try:
            # Set window size
            self.window.set_default_size(config.width, config.height)

            # For existing windows, resize them
            if hasattr(self.window, 'get_allocated_width'):
                self.window.set_size_request(config.width, config.height)
            
            # Store current config
            self.current_config = config
            
            # Add CSS class for device type
            self._update_device_css_classes(config)
            
            # Notify listeners
            if self.on_viewport_changed:
                self.on_viewport_changed(config)
            
            print(f"📱 Viewport set to {config.name} ({config.width}×{config.height})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to apply viewport config: {e}")
            return False
    
    def _update_device_css_classes(self, config: ViewportConfig):
        """Update CSS classes based on device type"""
        # Remove existing device classes
        for device_type in DeviceType:
            self.window.remove_css_class(f"viewport-{device_type.value}")
        
        # Add current device class
        self.window.add_css_class(f"viewport-{config.device_type.value}")
        
        # Add responsive breakpoint classes
        if config.width <= 480:
            self.window.add_css_class("breakpoint-xs")
        elif config.width <= 768:
            self.window.add_css_class("breakpoint-sm")
        elif config.width <= 1024:
            self.window.add_css_class("breakpoint-md")
        elif config.width <= 1440:
            self.window.add_css_class("breakpoint-lg")
        else:
            self.window.add_css_class("breakpoint-xl")
    
    def get_current_config(self) -> Optional[ViewportConfig]:
        """Get current viewport configuration"""
        return self.current_config
    
    def get_available_presets(self) -> dict[str, ViewportConfig]:
        """Get all available device presets"""
        return self.DEVICE_PRESETS.copy()
    
    def is_mobile(self) -> bool:
        """Check if current viewport is mobile"""
        return (self.current_config and 
                self.current_config.device_type == DeviceType.MOBILE)
    
    def is_tablet(self) -> bool:
        """Check if current viewport is tablet"""
        return (self.current_config and 
                self.current_config.device_type == DeviceType.TABLET)
    
    def is_desktop(self) -> bool:
        """Check if current viewport is desktop"""
        return (self.current_config and 
                self.current_config.device_type == DeviceType.DESKTOP)
    
    def get_responsive_breakpoint(self) -> str:
        """Get current responsive breakpoint"""
        if not self.current_config:
            return "unknown"
        
        width = self.current_config.width
        if width <= 480:
            return "xs"
        elif width <= 768:
            return "sm"
        elif width <= 1024:
            return "md"
        elif width <= 1440:
            return "lg"
        else:
            return "xl"
    
    def create_viewport_selector_widget(self) -> Gtk.Widget:
        """Create a widget for selecting viewport presets"""
        dropdown = Gtk.DropDown()
        
        # Create string list of device names
        string_list = Gtk.StringList()
        preset_keys = list(self.DEVICE_PRESETS.keys())
        
        for key in preset_keys:
            config = self.DEVICE_PRESETS[key]
            string_list.append(f"{config.name} ({config.width}×{config.height})")
        
        dropdown.set_model(string_list)
        
        # Set current selection
        if self.current_config:
            for i, key in enumerate(preset_keys):
                if self.DEVICE_PRESETS[key].name == self.current_config.name:
                    dropdown.set_selected(i)
                    break
        
        # Connect selection handler
        def on_selection_changed(dropdown, param):
            selected = dropdown.get_selected()
            if selected < len(preset_keys):
                preset_key = preset_keys[selected]
                self.set_viewport(preset_key)
        
        dropdown.connect("notify::selected", on_selection_changed)
        
        return dropdown
