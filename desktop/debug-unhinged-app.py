#!/usr/bin/env python3
"""
Debug version of Unhinged desktop application with extensive error catching
"""

import sys
import os
import traceback
from pathlib import Path

print("🔍 DEBUG: Starting Unhinged desktop application debug...")
print(f"🔍 DEBUG: Python version: {sys.version}")
print(f"🔍 DEBUG: Working directory: {os.getcwd()}")
print(f"🔍 DEBUG: Script location: {__file__}")

# Check project root
project_root = Path(__file__).parent.parent
print(f"🔍 DEBUG: Project root: {project_root}")
print(f"🔍 DEBUG: Project root exists: {project_root.exists()}")

# Check Makefile
makefile = project_root / "Makefile"
print(f"🔍 DEBUG: Makefile exists: {makefile.exists()}")

try:
    print("🔍 DEBUG: Importing gi...")
    import gi
    print("✅ DEBUG: gi imported successfully")
    
    print("🔍 DEBUG: Setting GTK4 version...")
    gi.require_version('Gtk', '4.0')
    print("✅ DEBUG: GTK4 version set")
    
    print("🔍 DEBUG: Setting Adwaita version...")
    gi.require_version('Adw', '1')
    print("✅ DEBUG: Adwaita version set")
    
    print("🔍 DEBUG: Importing GTK4 modules...")
    from gi.repository import Gtk, Adw, GLib, Gio, Pango
    print("✅ DEBUG: All GTK4 modules imported")
    
except Exception as e:
    print(f"❌ DEBUG: Import error: {e}")
    print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
    sys.exit(1)

try:
    print("🔍 DEBUG: Importing other modules...")
    import subprocess
    import threading
    import time
    import json
    print("✅ DEBUG: Standard modules imported")
    
except Exception as e:
    print(f"❌ DEBUG: Standard module import error: {e}")
    sys.exit(1)

class DebugUnhingedApp(Adw.Application):
    def __init__(self):
        print("🔍 DEBUG: Creating application object...")
        try:
            super().__init__(application_id='com.unhinged.platform.debug')
            print("✅ DEBUG: Application object created successfully")
            self.project_root = project_root
            self.window = None
        except Exception as e:
            print(f"❌ DEBUG: Application creation error: {e}")
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            raise
    
    def do_activate(self):
        print("🔍 DEBUG: Application activation called...")
        try:
            if not self.window:
                print("🔍 DEBUG: Creating main window...")
                self.window = self.create_debug_window()
                print("✅ DEBUG: Main window created")
            
            print("🔍 DEBUG: Presenting window...")
            self.window.present()
            print("✅ DEBUG: Window presented successfully")
            
        except Exception as e:
            print(f"❌ DEBUG: Activation error: {e}")
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            # Don't re-raise, try to show error dialog
            self.show_error_dialog(str(e))
    
    def create_debug_window(self):
        print("🔍 DEBUG: Creating window components...")
        try:
            # Create main window
            window = Adw.ApplicationWindow(application=self)
            window.set_title("Unhinged Debug")
            window.set_default_size(600, 400)
            print("✅ DEBUG: Base window created")
            
            # Create header bar
            header_bar = Adw.HeaderBar()
            window.set_titlebar(header_bar)
            print("✅ DEBUG: Header bar created")
            
            # Create simple content
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            main_box.set_margin_top(24)
            main_box.set_margin_bottom(24)
            main_box.set_margin_start(24)
            main_box.set_margin_end(24)
            
            # Add debug info
            debug_label = Gtk.Label()
            debug_label.set_markup(f"""<b>Unhinged Desktop Application Debug</b>

✅ GTK4/Libadwaita: Working
✅ Application: Created successfully
✅ Window: Displaying properly
📁 Project root: {self.project_root}
📄 Makefile exists: {(self.project_root / 'Makefile').exists()}

If you see this window, the basic GTK4 functionality is working.
The issue may be in the complex UI components or backend integration.""")
            
            debug_label.set_wrap(True)
            main_box.append(debug_label)
            
            # Add test button
            test_button = Gtk.Button.new_with_label("Test Button")
            test_button.connect("clicked", self.on_test_clicked)
            main_box.append(test_button)
            
            window.set_content(main_box)
            print("✅ DEBUG: Window content set")
            
            return window
            
        except Exception as e:
            print(f"❌ DEBUG: Window creation error: {e}")
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            raise
    
    def on_test_clicked(self, button):
        print("🔍 DEBUG: Test button clicked")
        button.set_label("Button Clicked!")
    
    def show_error_dialog(self, error_message):
        try:
            print(f"🔍 DEBUG: Showing error dialog: {error_message}")
            # Create a simple error window since dialog might fail
            error_window = Gtk.Window()
            error_window.set_title("Debug Error")
            error_window.set_default_size(400, 200)
            
            error_label = Gtk.Label()
            error_label.set_text(f"Error: {error_message}")
            error_label.set_wrap(True)
            
            error_window.set_child(error_label)
            error_window.present()
            
        except Exception as e:
            print(f"❌ DEBUG: Error dialog creation failed: {e}")

def main():
    print("🔍 DEBUG: Main function called")
    try:
        print("🔍 DEBUG: Creating debug application...")
        app = DebugUnhingedApp()
        print("✅ DEBUG: Debug application created")
        
        print("🔍 DEBUG: Running application...")
        result = app.run(sys.argv)
        print(f"✅ DEBUG: Application finished with result: {result}")
        return result
        
    except Exception as e:
        print(f"❌ DEBUG: Main function error: {e}")
        print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    print("🔍 DEBUG: Script started")
    try:
        sys.exit(main())
    except Exception as e:
        print(f"❌ DEBUG: Script execution error: {e}")
        print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
        sys.exit(1)
