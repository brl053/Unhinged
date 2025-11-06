#!/usr/bin/env python3
"""
@llm-doc Simple GTK4 Desktop Application Launcher
@llm-version 1.0.0
@llm-date 2025-01-26
@llm-author Unhinged Team

## Overview
Simple launcher for the GTK4 desktop application with direct control integration.
Academic exercise implementation.

@llm-principle Simple direct integration for learning and iteration
@llm-culture Independence through straightforward implementation
"""

import os
import sys
from pathlib import Path


def main():
    """Launch the GTK4 desktop application"""
    # Set up paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    # Change to project root for proper imports
    os.chdir(project_root)

    # Add current directory to Python path for control module imports
    sys.path.insert(0, str(project_root))

    try:
        # Import and run the desktop app
        from control.gtk4_gui.desktop_app import UnhingedDesktopApp

        app = UnhingedDesktopApp()
        exit_code = app.run(sys.argv)

        return exit_code

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running from the Unhinged project root")
        print("💡 Check that control modules are available")
        return 1

    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
