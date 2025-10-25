
import logging; gui_logger = logging.getLogger(__name__)

"""
Input Integration Layer
Connects UI components with the input capture system for seamless interaction.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import threading
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass

# Import input capture modules
try:
    from ..tools.input.keyboard_capture import KeyboardCapture, KeyboardConfig
    from ..tools.input.mouse_capture import MouseCapture, MouseConfig
    from ..tools.input.privacy_manager import PrivacyManager, PrivacyConfig, PrivacyLevel
    from ..tools.input.hotkey_manager import HotkeyManager, HotkeyType
    from ..tools.input.input_analyzer import InputAnalyzer, AnalysisConfig, PatternType
    INPUT_MODULES_AVAILABLE = True
except ImportError as e:
    gui_logger.warn(f" Input modules not available: {e}")
    INPUT_MODULES_AVAILABLE = False

# Import UI components
from .components import Card, MetricCard, StatusIndicator, ComponentVariant, create_toast, show_toast
from .responsive_layout import ResponsiveLayout, ScreenSize


@dataclass
class InputStats:
    """Input statistics for UI display"""
    keystrokes_per_minute: float = 0.0
    mouse_clicks_per_minute: float = 0.0
    total_keystrokes: int = 0
    total_clicks: int = 0
    active_hotkeys: int = 0
    patterns_detected: int = 0
    privacy_level: str = "filtered"
    session_duration: float = 0.0


class InputMonitorWidget(Card):
    """Widget displaying real-time input monitoring"""
    
    def __init__(self):
        super().__init__(title="Input Monitor", subtitle="Real-time activity tracking")
        
        # Input capture components
        self.keyboard_capture = None
        self.mouse_capture = None
        self.privacy_manager = None
        self.hotkey_manager = None
        self.input_analyzer = None
        
        # UI state
        self.is_monitoring = False
        self.stats = InputStats()
        
        # Create monitoring interface
        self._create_monitoring_interface()
        
        # Initialize input capture if available
        if INPUT_MODULES_AVAILABLE:
            self._initialize_input_capture()
        
        # Update timer
        self.update_timer = None
    
    def _create_monitoring_interface(self):
        """Create monitoring interface"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Status indicator
        self.status_indicator = StatusIndicator("Stopped", ComponentVariant.SECONDARY)
        main_box.append(self.status_indicator)
        
        # Statistics grid
        stats_grid = Gtk.Grid()
        stats_grid.set_column_spacing(16)
        stats_grid.set_row_spacing(8)
        
        # Keyboard stats
        self.keyboard_metric = MetricCard("Keystrokes/min", "0")
        stats_grid.attach(self.keyboard_metric, 0, 0, 1, 1)
        
        # Mouse stats
        self.mouse_metric = MetricCard("Clicks/min", "0")
        stats_grid.attach(self.mouse_metric, 1, 0, 1, 1)
        
        # Patterns detected
        self.patterns_metric = MetricCard("Patterns", "0")
        stats_grid.attach(self.patterns_metric, 0, 1, 1, 1)
        
        # Session duration
        self.session_metric = MetricCard("Session", "0:00")
        stats_grid.attach(self.session_metric, 1, 1, 1, 1)
        
        main_box.append(stats_grid)
        
        # Control buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.CENTER)
        
        self.start_button = Gtk.Button(label="Start Monitoring")
        self.start_button.add_css_class("suggested-action")
        self.start_button.connect("clicked", self._on_start_clicked)
        button_box.append(self.start_button)
        
        self.stop_button = Gtk.Button(label="Stop")
        self.stop_button.set_sensitive(False)
        self.stop_button.connect("clicked", self._on_stop_clicked)
        button_box.append(self.stop_button)
        
        self.settings_button = Gtk.Button.new_from_icon_name("preferences-system-symbolic")
        self.settings_button.connect("clicked", self._on_settings_clicked)
        button_box.append(self.settings_button)
        
        main_box.append(button_box)
        
        self.set_content(main_box)
    
    def _initialize_input_capture(self):
        """Initialize input capture components"""
        try:
            # Privacy manager
            privacy_config = PrivacyConfig(level=PrivacyLevel.FILTERED)
            self.privacy_manager = PrivacyManager(privacy_config)
            
            # Keyboard capture
            keyboard_config = KeyboardConfig(privacy_mode=True)
            self.keyboard_capture = KeyboardCapture(keyboard_config)
            
            # Mouse capture
            mouse_config = MouseConfig(privacy_mode=True)
            self.mouse_capture = MouseCapture(mouse_config)
            
            # Hotkey manager
            self.hotkey_manager = HotkeyManager()
            
            # Input analyzer
            analysis_config = AnalysisConfig()
            self.input_analyzer = InputAnalyzer(analysis_config)
            
            # Connect callbacks
            self._setup_callbacks()
            
            
        except Exception as e:
            gui_logger.error(f" Failed to initialize input capture: {e}")
    
    def _setup_callbacks(self):
        """Setup input capture callbacks"""
        if not INPUT_MODULES_AVAILABLE:
            return
        
        # Keyboard callbacks
        if self.keyboard_capture:
            self.keyboard_capture.on_key_press = self._on_key_press
            self.keyboard_capture.on_hotkey_triggered = self._on_hotkey_triggered
        
        # Mouse callbacks
        if self.mouse_capture:
            self.mouse_capture.on_mouse_click = self._on_mouse_click
            self.mouse_capture.on_pattern_detected = self._on_mouse_pattern
        
        # Analyzer callbacks
        if self.input_analyzer:
            # Would set up pattern detection callbacks
            pass
    
    def _on_key_press(self, event):
        """Handle keyboard event"""
        if self.privacy_manager:
            filtered_event = self.privacy_manager.filter_keyboard_event(event.__dict__)
            if filtered_event and self.input_analyzer:
                self.input_analyzer.add_keyboard_event(filtered_event)
    
    def _on_mouse_click(self, event):
        """Handle mouse event"""
        if self.privacy_manager:
            filtered_event = self.privacy_manager.filter_mouse_event(event.__dict__)
            if filtered_event and self.input_analyzer:
                self.input_analyzer.add_mouse_event(filtered_event)
    
    def _on_hotkey_triggered(self, hotkey_name):
        """Handle hotkey trigger"""
    
    def _on_mouse_pattern(self, pattern_type, data):
        """Handle mouse pattern detection"""
    
    def _on_start_clicked(self, button):
        """Start input monitoring"""
        if not INPUT_MODULES_AVAILABLE:
            gui_logger.error(" Input capture not available")
            return
        
        try:
            # Start capture components
            if self.keyboard_capture:
                self.keyboard_capture.start_capture()
            
            if self.mouse_capture:
                self.mouse_capture.start_capture()
            
            # Update UI state
            self.is_monitoring = True
            self.start_button.set_sensitive(False)
            self.stop_button.set_sensitive(True)
            self.status_indicator.set_status("Monitoring", ComponentVariant.SUCCESS)
            
            # Start update timer
            self.update_timer = GLib.timeout_add(1000, self._update_stats)
            
            
        except Exception as e:
            gui_logger.error(f" Failed to start monitoring: {e}")
    
    def _on_stop_clicked(self, button):
        """Stop input monitoring"""
        try:
            # Stop capture components
            if self.keyboard_capture:
                self.keyboard_capture.stop_capture()
            
            if self.mouse_capture:
                self.mouse_capture.stop_capture()
            
            # Update UI state
            self.is_monitoring = False
            self.start_button.set_sensitive(True)
            self.stop_button.set_sensitive(False)
            self.status_indicator.set_status("Stopped", ComponentVariant.SECONDARY)
            
            # Stop update timer
            if self.update_timer:
                GLib.source_remove(self.update_timer)
                self.update_timer = None
            
            
        except Exception as e:
            gui_logger.error(f" Failed to stop monitoring: {e}")
    
    def _on_settings_clicked(self, button):
        """Show settings dialog"""
        # Would open settings dialog
    
    def _update_stats(self) -> bool:
        """Update statistics display"""
        try:
            if not self.is_monitoring:
                return False
            
            # Get statistics from capture components
            if self.keyboard_capture:
                kb_stats = self.keyboard_capture.get_statistics()
                self.stats.keystrokes_per_minute = kb_stats.get('keys_per_minute', 0)
                self.stats.total_keystrokes = kb_stats.get('total_keystrokes', 0)
                self.stats.session_duration = kb_stats.get('session_duration', 0)
            
            if self.mouse_capture:
                mouse_stats = self.mouse_capture.get_statistics()
                self.stats.mouse_clicks_per_minute = mouse_stats.get('clicks_per_minute', 0)
                self.stats.total_clicks = mouse_stats.get('total_clicks', 0)
            
            if self.hotkey_manager:
                hk_stats = self.hotkey_manager.get_statistics()
                self.stats.active_hotkeys = hk_stats.get('total_hotkeys', 0)
            
            # Update UI
            self.keyboard_metric.update_metric(f"{self.stats.keystrokes_per_minute:.1f}")
            self.mouse_metric.update_metric(f"{self.stats.mouse_clicks_per_minute:.1f}")
            self.patterns_metric.update_metric(str(self.stats.patterns_detected))
            
            # Format session duration
            duration_mins = int(self.stats.session_duration // 60)
            duration_secs = int(self.stats.session_duration % 60)
            self.session_metric.update_metric(f"{duration_mins}:{duration_secs:02d}")
            
            return True  # Continue timer
            
        except Exception as e:
            gui_logger.warn(f" Stats update error: {e}")
            return True


class HotkeyConfigWidget(Card):
    """Widget for configuring hotkeys"""
    
    def __init__(self):
        super().__init__(title="Hotkeys", subtitle="Configure keyboard shortcuts")
        
        self.hotkey_manager = None
        
        # Create hotkey interface
        self._create_hotkey_interface()
        
        # Initialize hotkey manager
        if INPUT_MODULES_AVAILABLE:
            self.hotkey_manager = HotkeyManager()
            self._load_hotkeys()
    
    def _create_hotkey_interface(self):
        """Create hotkey configuration interface"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Hotkey list
        self.hotkey_list = Gtk.ListBox()
        self.hotkey_list.add_css_class("boxed-list")
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_max_content_height(200)
        scrolled.set_child(self.hotkey_list)
        
        main_box.append(scrolled)
        
        # Add hotkey button
        add_button = Gtk.Button(label="Add Hotkey")
        add_button.add_css_class("suggested-action")
        add_button.connect("clicked", self._on_add_hotkey)
        main_box.append(add_button)
        
        self.set_content(main_box)
    
    def _load_hotkeys(self):
        """Load configured hotkeys"""
        if not self.hotkey_manager:
            return
        
        hotkeys = self.hotkey_manager.get_hotkey_list()
        
        for hotkey in hotkeys:
            self._add_hotkey_row(hotkey)
    
    def _add_hotkey_row(self, hotkey_info: Dict):
        """Add hotkey row to list"""
        row = Adw.ActionRow()
        row.set_title(hotkey_info['name'])
        row.set_subtitle(f"{hotkey_info['keys']} - {hotkey_info['description']}")
        
        # Enable/disable switch
        switch = Gtk.Switch()
        switch.set_active(hotkey_info['enabled'])
        switch.connect("notify::active", lambda s, p: self._toggle_hotkey(hotkey_info['name'], s.get_active()))
        row.add_suffix(switch)
        
        # Delete button
        delete_button = Gtk.Button.new_from_icon_name("user-trash-symbolic")
        delete_button.add_css_class("destructive-action")
        delete_button.connect("clicked", lambda b: self._delete_hotkey(hotkey_info['name'], row))
        row.add_suffix(delete_button)
        
        self.hotkey_list.append(row)
    
    def _on_add_hotkey(self, button):
        """Add new hotkey"""
        # Would open hotkey creation dialog
    
    def _toggle_hotkey(self, name: str, enabled: bool):
        """Toggle hotkey enabled state"""
        if self.hotkey_manager:
            if enabled:
                self.hotkey_manager.enable_hotkey(name)
            else:
                self.hotkey_manager.disable_hotkey(name)
    
    def _delete_hotkey(self, name: str, row: Adw.ActionRow):
        """Delete hotkey"""
        if self.hotkey_manager:
            self.hotkey_manager.unregister_hotkey(name)
            self.hotkey_list.remove(row)


class PrivacyControlWidget(Card):
    """Widget for privacy controls"""
    
    def __init__(self):
        super().__init__(title="Privacy", subtitle="Control data collection and filtering")
        
        self.privacy_manager = None
        
        # Create privacy interface
        self._create_privacy_interface()
        
        # Initialize privacy manager
        if INPUT_MODULES_AVAILABLE:
            from ..tools.input.privacy_manager import PrivacyConfig, PrivacyLevel
            config = PrivacyConfig()
            self.privacy_manager = PrivacyManager(config)
    
    def _create_privacy_interface(self):
        """Create privacy control interface"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Privacy level selection
        level_group = Adw.PreferencesGroup()
        level_group.set_title("Privacy Level")
        
        self.level_row = Adw.ComboRow()
        self.level_row.set_title("Data Collection Level")
        
        level_model = Gtk.StringList()
        levels = ["Full Logging", "Filtered", "Anonymous", "Statistics Only", "Disabled"]
        for level in levels:
            level_model.append(level)
        
        self.level_row.set_model(level_model)
        self.level_row.set_selected(1)  # Default to Filtered
        self.level_row.connect("notify::selected", self._on_privacy_level_changed)
        
        level_group.add(self.level_row)
        main_box.append(level_group)
        
        # Filter options
        filter_group = Adw.PreferencesGroup()
        filter_group.set_title("Content Filters")
        
        # Password filtering
        password_row = Adw.ActionRow()
        password_row.set_title("Filter Passwords")
        password_row.set_subtitle("Hide password fields and sensitive input")
        
        self.password_switch = Gtk.Switch()
        self.password_switch.set_active(True)
        password_row.add_suffix(self.password_switch)
        filter_group.add(password_row)
        
        # Email filtering
        email_row = Adw.ActionRow()
        email_row.set_title("Filter Email Addresses")
        
        self.email_switch = Gtk.Switch()
        email_row.add_suffix(self.email_switch)
        filter_group.add(email_row)
        
        main_box.append(filter_group)
        
        # Blocked applications
        app_group = Adw.PreferencesGroup()
        app_group.set_title("Blocked Applications")
        
        self.app_list = Gtk.ListBox()
        self.app_list.add_css_class("boxed-list")
        app_group.add(self.app_list)
        
        main_box.append(app_group)
        
        self.set_content(main_box)
    
    def _on_privacy_level_changed(self, combo_row, pspec):
        """Handle privacy level change"""
        selected = combo_row.get_selected()
        levels = [PrivacyLevel.FULL_LOGGING, PrivacyLevel.FILTERED, 
                 PrivacyLevel.ANONYMOUS, PrivacyLevel.STATISTICS_ONLY, 
                 PrivacyLevel.DISABLED]
        
        if selected < len(levels) and self.privacy_manager:
            self.privacy_manager.config.level = levels[selected]


class InputIntegrationManager:
    """Manages integration between UI and input capture"""
    
    def __init__(self):
        self.input_monitor = None
        self.hotkey_config = None
        self.privacy_control = None
        
        # Integration state
        self.is_integrated = False
        
    
    def create_input_dashboard(self) -> Gtk.Widget:
        """Create integrated input dashboard"""
        dashboard = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        
        # Input monitor
        self.input_monitor = InputMonitorWidget()
        dashboard.append(self.input_monitor)
        
        # Hotkey configuration
        self.hotkey_config = HotkeyConfigWidget()
        dashboard.append(self.hotkey_config)
        
        # Privacy controls
        self.privacy_control = PrivacyControlWidget()
        dashboard.append(self.privacy_control)
        
        self.is_integrated = True
        return dashboard
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            'integrated': self.is_integrated,
            'input_modules_available': INPUT_MODULES_AVAILABLE,
            'monitoring_active': self.input_monitor.is_monitoring if self.input_monitor else False,
            'components': {
                'input_monitor': self.input_monitor is not None,
                'hotkey_config': self.hotkey_config is not None,
                'privacy_control': self.privacy_control is not None
            }
        }


# Test function
def test_input_integration():
    """Test input integration"""
    
    app = Adw.Application()
    
    def on_activate(app):
        window = Adw.ApplicationWindow(application=app)
        window.set_title("Input Integration Test")
        window.set_default_size(600, 800)
        
        # Create integration manager
        integration_manager = InputIntegrationManager()
        
        # Create dashboard
        dashboard = integration_manager.create_input_dashboard()
        
        # Wrap in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(dashboard)
        
        window.set_content(scrolled)
        window.present()
    
    app.connect("activate", on_activate)
    app.run()


if __name__ == "__main__":
    test_input_integration()
