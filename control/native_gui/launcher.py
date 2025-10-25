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

# Add event framework to path
sys.path.insert(0, str(project_root / "libs/event-framework/python/src"))
from unhinged_events import create_gui_logger

# Initialize GUI event logger
gui_logger = create_gui_logger("unhinged-launcher", "1.0.0")

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
        gui_logger.info("GTK4 and Adwaita available", {
            "event_type": "dependency_check",
            "component": "launcher",
            "status": "dependencies_ok"
        })
    except Exception as e:
        gui_logger.error("GTK4/Adwaita not available", exception=e, metadata={
            "event_type": "dependency_failure",
            "component": "launcher",
            "missing_dependencies": ["libgtk-4-dev", "libadwaita-1-dev", "python3-gi"]
        })
        print("\n🔧 Install dependencies:")
        print("   sudo apt install libgtk-4-dev libadwaita-1-dev python3-gi")
        sys.exit(1)
    
    # Launch the application
    gui_logger.info("Launching mobile-first control center", {
        "event_type": "application_startup",
        "component": "launcher",
        "launched_by_ai": args.launched_by_ai
    })

    # Import and run the native GUI
    try:
        from control.native_gui import run_native_gui

        if args.launched_by_ai:
            gui_logger.info("Launched by AI Assistant", {
                "event_type": "ai_launch",
                "component": "launcher"
            })

        # Run the native application
        exit_code = run_native_gui(launched_by_ai=args.launched_by_ai)
        sys.exit(exit_code)

    except ImportError as e:
        gui_logger.error("Import error", exception=e, metadata={
            "event_type": "import_failure",
            "component": "launcher",
            "error_category": "dependency"
        })
        print("\n🔧 Required dependencies:")
        print("   sudo apt install libgtk-4-dev libadwaita-1-dev python3-gi")
        print("   pip install requests")
        sys.exit(1)

    except Exception as e:
        gui_logger.error("Failed to start native GUI", exception=e, metadata={
            "event_type": "startup_failure",
            "component": "launcher",
            "error_category": "application"
        })
        sys.exit(1)
