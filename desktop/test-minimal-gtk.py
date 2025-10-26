#!/usr/bin/env python3
"""
Minimal GTK4 test to isolate desktop application issues
"""

import sys
import gi

print("Testing minimal GTK4 application...")

try:
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Gtk, Adw
    print("✅ GTK4/Libadwaita imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class MinimalApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.test.minimal')
        print("✅ Application object created")
        
    def do_activate(self):
        print("✅ Application activated")
        window = Adw.ApplicationWindow(application=self)
        window.set_title("Minimal Test")
        window.set_default_size(400, 300)
        
        label = Gtk.Label(label="If you see this, GTK4 is working!")
        window.set_content(label)
        
        print("✅ Window created, presenting...")
        window.present()
        print("✅ Window presented")

def main():
    print("Creating minimal application...")
    app = MinimalApp()
    print("Running application...")
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
