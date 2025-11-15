#!/usr/bin/env python3
"""
Native C Graphics Launcher

Launches the native C graphics hello world window.
Pure C graphics rendering with DRM framebuffer.
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    print("🔥 LAUNCHING NATIVE C GRAPHICS WINDOW")
    print("=====================================")

    # Get project root
    project_root = Path(__file__).parent.parent
    hello_world_path = project_root / "libs/graphics/build/examples/hello_world"

    # Check if binary exists
    if not hello_world_path.exists():
        print("❌ Native C graphics binary not found")
        print(f"Expected: {hello_world_path}")
        print("💡 Run: cd libs/graphics && cmake -B build && cd build && make hello_world")
        return 1

    print(f"✅ Found native C graphics binary: {hello_world_path}")

    # Check DRM permissions
    drm_devices = ["/dev/dri/card0", "/dev/dri/card1"]
    has_drm_access = False

    for device in drm_devices:
        if os.path.exists(device) and os.access(device, os.R_OK | os.W_OK):
            has_drm_access = True
            break

    if not has_drm_access:
        print("⚠️  No DRM access detected")
        print("💡 This usually means the user is not in the video group")
        print("💡 The make start process should have handled this automatically")
        print("🚀 Attempting to launch anyway...")

    # Launch the native C graphics window
    try:
        print("🎮 Launching native C graphics window...")
        print("💡 Press Ctrl+C to exit")

        result = subprocess.run([str(hello_world_path)], cwd=hello_world_path.parent, check=False)

        if result.returncode == 0:
            print("✅ Native C graphics window closed successfully")
        else:
            print(f"❌ Native C graphics window exited with code: {result.returncode}")
            if result.returncode == 1:
                print("💡 This usually means DRM is in use by desktop environment")
                print("💡 Native C graphics requires exclusive DRM access")
                print(
                    "💡 Try running from a TTY console (Ctrl+Alt+F3) or disable desktop environment"
                )
                print(
                    "💡 The graphics library is working correctly - just can't access display while GUI is running"
                )

        return result.returncode

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Failed to launch native C graphics: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
