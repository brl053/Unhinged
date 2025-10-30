"""
Action Controller - Handles all user interactions and events

Extracted from desktop_app.py to achieve 75% reduction target.
Manages button clicks, menu actions, and user interactions.
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

import subprocess
import threading

from gi.repository import Adw, Gio, GLib, Gtk


class ActionController:
    """Controller for user actions and event handling"""

    def __init__(self, app):
        """Initialize action controller with app reference"""
        self.app = app
        self.project_root = app.project_root

    def setup_actions(self):
        """Setup application actions for menu"""
        # About action
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about_action)
        self.app.add_action(about_action)

        # Preferences action
        preferences_action = Gio.SimpleAction.new("preferences", None)
        preferences_action.connect("activate", self.on_preferences_action)
        self.app.add_action(preferences_action)

        # Quit action
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit_action)
        self.app.add_action(quit_action)

        # Keyboard shortcuts
        self.app.set_accels_for_action("app.quit", ["<Ctrl>Q"])

        # Create application menu
        menu = Gio.Menu()
        menu.append("About Unhinged", "app.about")
        menu.append("Preferences", "app.preferences")
        menu.append("Quit", "app.quit")
        self.app.set_menubar(menu)

    def on_about_action(self, action, param):
        """Show about dialog"""
        about = Adw.AboutWindow(transient_for=self.app.window)
        about.set_application_name("Unhinged")
        about.set_application_icon("applications-graphics")
        about.set_developer_name("Unhinged Team")
        about.set_version("1.0.0")
        about.set_website("https://github.com/unhinged/platform")
        about.set_issue_url("https://github.com/unhinged/platform/issues")
        about.set_copyright("© 2025 Unhinged Team")
        about.set_license_type(Gtk.License.MIT_X11)
        about.set_comments("Native Graphics Platform with VM Communication\n\nIndependent graphics rendering with reliable communication pipeline.")
        about.present()

    def on_preferences_action(self, action, param):
        """Show preferences dialog"""
        # Create preferences window
        prefs = Adw.PreferencesWindow(transient_for=self.app.window)
        prefs.set_title("Preferences")

        # General page
        general_page = Adw.PreferencesPage()
        general_page.set_title("General")
        general_page.set_icon_name("preferences-system-symbolic")

        # Launch settings group
        launch_group = Adw.PreferencesGroup()
        launch_group.set_title("Launch Settings")
        launch_group.set_description("Configure how Unhinged starts")

        # Auto-start row
        autostart_row = Adw.SwitchRow()
        autostart_row.set_title("Auto-start on login")
        autostart_row.set_subtitle("Automatically start Unhinged when you log in")
        launch_group.add(autostart_row)

        general_page.add(launch_group)
        prefs.add(general_page)
        prefs.present()

    def on_quit_action(self, action, param):
        """Quit application"""
        if self.app.running:
            self.on_stop_clicked(None)

        # Close session logging
        if hasattr(self.app, 'session_logger') and self.app.session_logger:
            self.app.session_logger.log_session_event("APP_QUIT", "Application quit requested")
            self.app.session_logger.close_session()

        self.app.quit()

    def on_start_clicked(self, button):
        """Handle start button click using PlatformHandler"""
        if self.app.running:
            return

        self.app.running = True
        self.app.start_button.set_sensitive(False)
        self.app.stop_button.set_sensitive(True)

        # Get selected mode
        mode_names = ["Enhanced", "Simple", "QoL", "Custom ISO"]
        selected_mode = self.app.mode_dropdown.get_selected()
        mode_name = mode_names[selected_mode] if selected_mode < len(mode_names) else "Enhanced"

        # Log GUI events
        if hasattr(self.app, 'session_logger') and self.app.session_logger:
            self.app.session_logger.log_gui_event("START_BUTTON_CLICKED", "User clicked start button")
            self.app.session_logger.log_mode_selection(mode_name)

        # Show toast notification
        self.app.show_toast(f"Starting Unhinged in {mode_name} mode...")

        # Start platform using handler
        if hasattr(self.app, 'platform_handler') and self.app.platform_handler:
            thread = threading.Thread(target=self.app.platform_handler.start_platform, daemon=True)
            thread.start()
        else:
            self.app.show_error_dialog("Platform Error", "Platform handler not available")

    def on_stop_clicked(self, button):
        """Handle stop button click using PlatformHandler"""
        if not self.app.running:
            return

        self.app.running = False
        self.app.start_button.set_sensitive(True)
        self.app.stop_button.set_sensitive(False)

        # Log GUI event
        if hasattr(self.app, 'session_logger') and self.app.session_logger:
            self.app.session_logger.log_gui_event("STOP_BUTTON_CLICKED", "User clicked stop button")

        # Stop platform using handler
        if hasattr(self.app, 'platform_handler') and self.app.platform_handler:
            self.app.platform_handler.stop_platform()
        else:
            self.app.append_log("⚠️ Platform handler not available")
            self.app.update_status("Stopped", 0)

    def on_record_voice_clicked(self, button):
        """Handle voice recording button click"""
        try:
            # Log the event
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("VOICE_RECORD_CLICKED", "User clicked voice record button")

            # Disable button during recording
            button.set_sensitive(False)
            button.set_label("Recording...")

            # Show toast
            self.app.show_toast("Recording voice for 10 seconds...")

            # Start recording in background thread
            def record_and_restore():
                try:
                    # Use the existing record_and_transcribe_voice method
                    if hasattr(self.app, 'record_and_transcribe_voice'):
                        self.app.record_and_transcribe_voice()
                    else:
                        # Fallback: show message
                        GLib.idle_add(self.app.show_toast, "Voice recording not available")

                except Exception as e:
                    print(f"❌ Voice recording error: {e}")
                    GLib.idle_add(self.app.show_toast, f"Voice recording failed: {e}")
                finally:
                    # Restore button state
                    GLib.idle_add(self._restore_voice_button, button)

            thread = threading.Thread(target=record_and_restore, daemon=True)
            thread.start()

        except Exception as e:
            print(f"❌ Voice button click error: {e}")
            self.app.show_toast(f"Voice recording failed: {e}")
            self._restore_voice_button(button)

    def _restore_voice_button(self, button):
        """Restore voice button to normal state"""
        try:
            button.set_sensitive(True)
            button.set_label("Record Voice")
        except Exception as e:
            print(f"❌ Error restoring voice button: {e}")

    def on_set_default_input_device(self, button, device):
        """Set the selected device as the Ubuntu host OS default input device"""
        try:

            # Use pactl to set default source
            alsa_device = device.get('alsa_device', '')
            if alsa_device:
                # Convert ALSA device to PulseAudio source name
                # This is a simplified approach - in practice, you'd need to map ALSA to PA
                result = subprocess.run(['pactl', 'set-default-source', alsa_device],
                                      capture_output=True, text=True)

                if result.returncode == 0:
                    self.app.show_toast(f"Set {device['name']} as default input")
                    if hasattr(self.app, 'session_logger') and self.app.session_logger:
                        self.app.session_logger.log_gui_event("DEFAULT_INPUT_SET",
                                                            f"Set default input to {device['name']}")
                else:
                    self.app.show_toast(f"Failed to set default input: {result.stderr}")

        except FileNotFoundError:
            self.app.show_toast("PulseAudio tools not available")
        except Exception as e:
            self.app.show_toast(f"Error setting default input: {e}")
            print(f"❌ Set default input error: {e}")

    def on_set_default_output_device(self, button, device):
        """Set the selected device as the Ubuntu host OS default output device"""
        try:
            # Use pactl to set default sink
            alsa_device = device.get('alsa_device', '')
            if alsa_device:
                result = subprocess.run(['pactl', 'set-default-sink', alsa_device],
                                      capture_output=True, text=True)

                if result.returncode == 0:
                    self.app.show_toast(f"Set {device['name']} as default output")
                    if hasattr(self.app, 'session_logger') and self.app.session_logger:
                        self.app.session_logger.log_gui_event("DEFAULT_OUTPUT_SET",
                                                            f"Set default output to {device['name']}")
                else:
                    self.app.show_toast(f"Failed to set default output: {result.stderr}")

        except FileNotFoundError:
            self.app.show_toast("PulseAudio tools not available")
        except Exception as e:
            self.app.show_toast(f"Error setting default output: {e}")
            print(f"❌ Set default output error: {e}")
