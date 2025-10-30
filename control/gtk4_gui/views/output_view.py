"""
OutputView - Audio Output Management tab extracted from desktop_app.py

This module contains all the audio output management functionality that was previously
embedded in the monolithic desktop_app.py file.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw


class OutputView:
    """Handles the Audio Output Management tab functionality"""
    
    def __init__(self, parent_app):
        """Initialize with reference to parent app"""
        self.app = parent_app
        
        # Audio table reference
        self.audio_table = None
        
    def create_content(self):
        """Create the Output tab content with audio device management and connection switching."""
        try:
            # Import AudioTable component
            from components.complex import AudioTable

            # Create main content box
            output_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            output_box.set_margin_top(24)
            output_box.set_margin_bottom(24)
            output_box.set_margin_start(24)
            output_box.set_margin_end(24)

            # Create header section
            header_group = Adw.PreferencesGroup()
            header_group.set_title("Audio Output Management")
            header_group.set_description("Manage audio devices, volume control, and connection switching")

            # Add audio info row
            info_row = Adw.ActionRow()
            info_row.set_title("Audio System")
            info_row.set_subtitle("Control audio output devices and volume settings")

            # Add audio icon
            audio_icon = Gtk.Image.new_from_icon_name("audio-speakers-symbolic")
            audio_icon.set_icon_size(Gtk.IconSize.LARGE)
            info_row.add_prefix(audio_icon)

            header_group.add(info_row)
            output_box.append(header_group)

            # Create AudioTable
            self.audio_table = AudioTable()

            # Create audio table group
            table_group = Adw.PreferencesGroup()
            table_group.set_title("Audio Devices")

            # Add AudioTable widget directly to the group (no ActionRow wrapper)
            audio_table_widget = self.audio_table.get_widget()
            audio_table_widget.set_vexpand(True)
            audio_table_widget.set_hexpand(True)

            # Create a clamp for better layout
            clamp = Adw.Clamp()
            clamp.set_maximum_size(1200)
            clamp.set_tightening_threshold(600)
            clamp.set_child(audio_table_widget)
            clamp.set_vexpand(True)

            table_group.add(clamp)
            output_box.append(table_group)

            # Log Output tab creation
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("OUTPUT_TAB_CREATED", "Output tab with AudioTable created")

            return output_box

        except Exception as e:
            # Create error fallback
            error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            error_box.set_margin_top(24)
            error_box.set_margin_bottom(24)
            error_box.set_margin_start(24)
            error_box.set_margin_end(24)

            # Error group
            error_group = Adw.PreferencesGroup()
            error_group.set_title("Output Tab Error")
            error_group.set_description("Failed to load audio management interface")

            # Error row
            error_row = Adw.ActionRow()
            error_row.set_title("Audio Management Unavailable")
            error_row.set_subtitle(f"Error: {str(e)}")

            error_icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic")
            error_icon.set_icon_size(Gtk.IconSize.LARGE)
            error_row.add_prefix(error_icon)

            error_group.add(error_row)
            error_box.append(error_group)

            # Log error
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("OUTPUT_TAB_ERROR", f"Failed to create Output tab: {e}")

            return error_box

    def get_audio_table(self):
        """Get reference to the audio table for external access"""
        return self.audio_table

    def refresh_audio_devices(self):
        """Refresh the audio device list"""
        try:
            if self.audio_table and hasattr(self.audio_table, 'refresh'):
                self.audio_table.refresh()
                
            # Log refresh
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("AUDIO_DEVICES_REFRESH", "Audio device list refreshed")
                
        except Exception as e:
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("AUDIO_DEVICES_REFRESH_ERROR", str(e))

    def set_default_device(self, device_name):
        """Set the default audio output device"""
        try:
            if self.audio_table and hasattr(self.audio_table, 'set_default_device'):
                self.audio_table.set_default_device(device_name)
                
            # Log device change
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("AUDIO_DEFAULT_DEVICE_CHANGED", f"Default device set to: {device_name}")
                
        except Exception as e:
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("AUDIO_DEFAULT_DEVICE_ERROR", str(e))

    def cleanup(self):
        """Clean up audio output components"""
        try:
            if self.audio_table and hasattr(self.audio_table, 'cleanup'):
                self.audio_table.cleanup()
                
            # Log cleanup
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("AUDIO_OUTPUT_CLEANUP", "Audio output components cleaned up")
                
        except Exception as e:
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("AUDIO_OUTPUT_CLEANUP_ERROR", str(e))
