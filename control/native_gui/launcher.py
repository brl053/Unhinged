#!/usr/bin/env python3
"""
@llm-type control-system
@llm-legend launcher.py - system control component
@llm-key Core functionality for launcher
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token launcher: system control component
"""
"""
🚀 Native GTK GUI Launcher

Launch the pure native GTK API development tool.
No WebKit. No JavaScript. No HTML/CSS. Pure independence.

Usage:
    python3 control/native_gui/launcher.py
    
Requirements:
    - GTK4 (libgtk-4-dev)
    - Adwaita (libadwaita-1-dev) 
    - Python GI bindings (python3-gi)
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# This will be called from main() below


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Launch Unhinged Native GTK GUI")
    parser.add_argument("--launched-by-ai", action="store_true",
                       help="Indicate that GUI was launched by AI assistant")
    args = parser.parse_args()

    # Check GTK4 availability
    try:
        import gi
        gi.require_version('Gtk', '4.0')
        gi.require_version('Adw', '1')
        from gi.repository import Gtk, Adw
        print("✅ GTK4 and Adwaita available")
    except Exception as e:
        print(f"❌ GTK4/Adwaita not available: {e}")
        print("\n🔧 Install dependencies:")
        print("   sudo apt install libgtk-4-dev libadwaita-1-dev python3-gi")
        sys.exit(1)
    
    # Launch the application
    print("🚀 Launching mobile-first control center...")

    # Import and run the native GUI
    try:
        from control.native_gui import run_native_gui

        if args.launched_by_ai:
            print("🤖 Launched by AI Assistant")

        # Run the native application
        exit_code = run_native_gui(launched_by_ai=args.launched_by_ai)
        sys.exit(exit_code)

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔧 Required dependencies:")
        print("   sudo apt install libgtk-4-dev libadwaita-1-dev python3-gi")
        print("   pip install requests")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Failed to start native GUI: {e}")
        sys.exit(1)
