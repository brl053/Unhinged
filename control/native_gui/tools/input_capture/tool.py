"""
@llm-type tool-plugin
@llm-legend Input Capture Tool - Advanced input monitoring and analysis
@llm-key Provides comprehensive keyboard and mouse capture with privacy controls
@llm-map Integrates input capture system with the Unhinged tool architecture
@llm-axiom Input monitoring must respect user privacy and provide transparent controls
@llm-contract Implements BaseTool interface with mobile-responsive input monitoring widgets
@llm-token input_capture_tool: Advanced input monitoring tool with mobile-first responsive design
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

from ...core.tool_manager import BaseTool, ToolViewport
from ...ui.components import Card, MetricCard, StatusIndicator, ComponentVariant
from ...ui.responsive_layout import ResponsiveGrid, ResponsiveStack
from ...ui.input_integration import InputMonitorWidget, HotkeyConfigWidget, PrivacyControlWidget

# Import input capture modules
try:
    from ...tools.input.keyboard_capture import KeyboardCapture, KeyboardConfig
    from ...tools.input.mouse_capture import MouseCapture, MouseConfig
    from ...tools.input.privacy_manager import PrivacyManager, PrivacyConfig, PrivacyLevel
    from ...tools.input.hotkey_manager import HotkeyManager
    from ...tools.input.input_analyzer import InputAnalyzer, AnalysisConfig
    INPUT_CAPTURE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Input capture modules not available: {e}")
    INPUT_CAPTURE_AVAILABLE = False


class InputCaptureTool(BaseTool):
    """
    @llm-type tool-implementation
    @llm-legend Advanced input capture tool with mobile-responsive interface
    @llm-key Provides comprehensive input monitoring, analysis, and privacy controls
    @llm-map Core tool for input capture functionality in the Unhinged system
    @llm-axiom Maintains user privacy while providing valuable input insights
    @llm-contract Implements responsive design patterns for all viewport sizes
    @llm-token InputCaptureTool: Advanced input monitoring with mobile-first design
    
    Advanced input capture and analysis tool.
    Provides keyboard/mouse monitoring, hotkey management, and privacy controls.
    Adapts interface based on viewport size for optimal user experience.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Input Capture"
        self.icon = "⌨️"
        self.description = "Monitor keyboard and mouse input with privacy controls"
        self.shortcut = "Ctrl+I"
        self.supports_mobile = True
        self.mobile_priority = 3  # Medium priority on mobile
        
        # Input capture components
        self.input_monitor = None
        self.hotkey_config = None
        self.privacy_control = None
        
        # Initialize if available
        if INPUT_CAPTURE_AVAILABLE:
            self._initialize_components()
    
    def _initialize_components(self):
        """
        @llm-type method
        @llm-legend Initialize input capture components
        @llm-key Sets up monitoring, hotkey management, and privacy controls
        """
        try:
            self.input_monitor = InputMonitorWidget()
            self.hotkey_config = HotkeyConfigWidget()
            self.privacy_control = PrivacyControlWidget()
            print("⌨️ Input capture components initialized")
        except Exception as e:
            print(f"❌ Failed to initialize input capture components: {e}")
    
    def _create_viewport_widget(self, viewport: ToolViewport):
        """
        @llm-type method
        @llm-legend Create viewport-specific widget for input capture tool
        @llm-key Provides optimized layouts for mobile, tablet, and desktop viewports
        @llm-map Implements responsive design patterns for input monitoring interface
        @llm-axiom Interface must be functional and accessible across all viewport sizes
        @llm-contract Returns GTK widget optimized for the specified viewport
        @llm-token _create_viewport_widget: Responsive input capture interface creation
        
        Create input capture interface optimized for the specified viewport.
        
        Args:
            viewport: Target viewport (mobile/tablet/desktop)
            
        Returns:
            GTK widget optimized for the viewport
        """
        if not INPUT_CAPTURE_AVAILABLE:
            return self._create_unavailable_widget()
        
        if viewport == ToolViewport.MOBILE:
            return self._create_mobile_widget()
        elif viewport == ToolViewport.TABLET:
            return self._create_tablet_widget()
        else:  # DESKTOP
            return self._create_desktop_widget()
    
    def _create_mobile_widget(self):
        """
        @llm-type method
        @llm-legend Create mobile-optimized input capture interface
        @llm-key Single-column layout with essential controls prioritized
        """
        # Mobile: Single column, stacked layout
        mobile_container = ResponsiveStack()
        
        # Priority order for mobile: Monitor > Privacy > Hotkeys
        if self.input_monitor:
            mobile_container.add_item(self.input_monitor)
        
        if self.privacy_control:
            mobile_container.add_item(self.privacy_control)
        
        if self.hotkey_config:
            mobile_container.add_item(self.hotkey_config)
        
        # Wrap in scrolled window for mobile
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(mobile_container)
        
        return scrolled
    
    def _create_tablet_widget(self):
        """
        @llm-type method
        @llm-legend Create tablet-optimized input capture interface
        @llm-key Two-column grid layout with balanced component distribution
        """
        # Tablet: Two-column grid
        tablet_grid = ResponsiveGrid()
        
        if self.input_monitor:
            tablet_grid.add_item(self.input_monitor, 
                                mobile_span=1, tablet_span=2, desktop_span=2, priority=3)
        
        if self.privacy_control:
            tablet_grid.add_item(self.privacy_control,
                                mobile_span=1, tablet_span=1, desktop_span=1, priority=2)
        
        if self.hotkey_config:
            tablet_grid.add_item(self.hotkey_config,
                                mobile_span=1, tablet_span=1, desktop_span=1, priority=1)
        
        return tablet_grid
    
    def _create_desktop_widget(self):
        """
        @llm-type method
        @llm-legend Create desktop-optimized input capture interface
        @llm-key Three-column layout with full feature set and detailed controls
        """
        # Desktop: Three-column layout with sidebar
        desktop_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        desktop_container.set_margin_top(16)
        desktop_container.set_margin_bottom(16)
        desktop_container.set_margin_start(16)
        desktop_container.set_margin_end(16)
        
        # Left column: Input monitor (main focus)
        left_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        if self.input_monitor:
            left_column.append(self.input_monitor)
        
        # Right column: Controls
        right_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        right_column.set_size_request(300, -1)
        
        if self.privacy_control:
            right_column.append(self.privacy_control)
        
        if self.hotkey_config:
            right_column.append(self.hotkey_config)
        
        desktop_container.append(left_column)
        desktop_container.append(right_column)
        
        return desktop_container
    
    def _create_unavailable_widget(self):
        """
        @llm-type method
        @llm-legend Create widget when input capture is unavailable
        @llm-key Provides informative error state with installation guidance
        """
        unavailable_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        unavailable_box.set_halign(Gtk.Align.CENTER)
        unavailable_box.set_valign(Gtk.Align.CENTER)
        
        # Error icon
        error_icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic")
        error_icon.set_pixel_size(64)
        unavailable_box.append(error_icon)
        
        # Error message
        error_label = Gtk.Label(label="Input Capture Unavailable")
        error_label.add_css_class("title-2")
        unavailable_box.append(error_label)
        
        # Instructions
        instructions = Gtk.Label(
            label="Input capture modules are not available.\n"
                  "Install required dependencies:\n"
                  "pip install pynput"
        )
        instructions.set_justify(Gtk.Justification.CENTER)
        instructions.add_css_class("body")
        unavailable_box.append(instructions)
        
        return unavailable_box
    
    def on_activate(self):
        """
        @llm-type method
        @llm-legend Handle tool activation
        @llm-key Starts input monitoring services when tool becomes active
        """
        super().on_activate()
        
        if self.input_monitor and INPUT_CAPTURE_AVAILABLE:
            # Could auto-start monitoring here if desired
            print("⌨️ Input capture tool activated")
    
    def on_deactivate(self):
        """
        @llm-type method
        @llm-legend Handle tool deactivation
        @llm-key Ensures proper cleanup when tool becomes inactive
        """
        super().on_deactivate()
        
        if self.input_monitor and INPUT_CAPTURE_AVAILABLE:
            # Stop monitoring if active
            if hasattr(self.input_monitor, 'is_monitoring') and self.input_monitor.is_monitoring:
                self.input_monitor._on_stop_clicked(None)
            print("⌨️ Input capture tool deactivated")
    
    def on_destroy(self):
        """
        @llm-type method
        @llm-legend Handle tool destruction
        @llm-key Performs comprehensive cleanup of input capture resources
        """
        super().on_destroy()
        
        # Clean up components
        if self.input_monitor:
            if hasattr(self.input_monitor, 'cleanup'):
                self.input_monitor.cleanup()
        
        if self.hotkey_config:
            if hasattr(self.hotkey_config, 'cleanup'):
                self.hotkey_config.cleanup()
        
        if self.privacy_control:
            if hasattr(self.privacy_control, 'cleanup'):
                self.privacy_control.cleanup()
        
        print("⌨️ Input capture tool destroyed")
    
    def get_status_info(self) -> dict:
        """
        @llm-type method
        @llm-legend Get current status information for the tool
        @llm-key Provides status data for system monitoring and debugging
        """
        status = {
            'name': self.name,
            'active': self.active,
            'viewport': self.current_viewport.value,
            'input_capture_available': INPUT_CAPTURE_AVAILABLE,
            'monitoring_active': False
        }
        
        if self.input_monitor and hasattr(self.input_monitor, 'is_monitoring'):
            status['monitoring_active'] = self.input_monitor.is_monitoring
        
        return status


# Tool registration function
def create_tool() -> InputCaptureTool:
    """
    @llm-type factory-function
    @llm-legend Factory function for creating InputCaptureTool instances
    @llm-key Required by the tool plugin system for automatic tool discovery
    @llm-map Entry point for tool registration in the Unhinged tool manager
    @llm-axiom Must return a properly initialized tool instance
    @llm-contract Returns InputCaptureTool instance ready for use
    @llm-token create_tool: Tool factory function for plugin system integration
    
    Factory function for creating InputCaptureTool instances.
    Required by the tool plugin system.
    
    Returns:
        InputCaptureTool: Initialized input capture tool instance
    """
    return InputCaptureTool()
