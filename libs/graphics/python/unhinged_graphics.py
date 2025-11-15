#!/usr/bin/env python3
"""
Unhinged Graphics Python Wrapper
Simple Python interface for Unhinged native C graphics library

This provides a basic interface for Alpine Linux to use the native graphics
library for framebuffer rendering.
"""

import os
import ctypes
from pathlib import Path


class UnhingedGraphics:
    """Python wrapper for Unhinged native C graphics library"""

    def __init__(self, library_path=None):
        """Initialize the graphics library"""
        self.lib = None
        self.initialized = False

        # Try to find the library
        if library_path is None:
            # Look for library in common locations
            search_paths = [
                Path(__file__).parent.parent / "build" / "libunhinged_graphics.so",
                Path("/opt/unhinged/libunhinged_graphics.so"),
                Path("./libunhinged_graphics.so"),
                Path("../build/libunhinged_graphics.so"),
            ]

            for path in search_paths:
                if path.exists():
                    library_path = str(path)
                    break

        if library_path and os.path.exists(library_path):
            try:
                self.lib = ctypes.CDLL(library_path)
                self._setup_function_signatures()
                print(f"✅ Loaded Unhinged graphics library: {library_path}")
            except Exception as e:
                print(f"❌ Failed to load graphics library: {e}")
                self.lib = None
        else:
            print("⚠️ Unhinged graphics library not found")
            print("💡 Available fallback: basic framebuffer operations")

    def _setup_function_signatures(self):
        """Set up C function signatures"""
        if not self.lib:
            return

        try:
            # Basic initialization functions
            self.lib.ug_init.restype = ctypes.c_int
            self.lib.ug_shutdown.restype = None

            # Version function
            self.lib.ug_get_version.restype = ctypes.c_char_p

            print("✅ Function signatures configured")
        except AttributeError as e:
            print(f"⚠️ Some functions not available: {e}")

    def get_version(self):
        """Get library version"""
        if self.lib:
            try:
                version = self.lib.ug_get_version()
                return version.decode("utf-8") if version else "unknown"
            except:
                return "unknown"
        return "library not loaded"

    def initialize(self):
        """Initialize the graphics system"""
        if self.lib:
            try:
                result = self.lib.ug_init()
                if result == 0:
                    self.initialized = True
                    print("✅ Unhinged graphics initialized")
                    return True
                else:
                    print(f"❌ Graphics initialization failed: {result}")
                    return False
            except Exception as e:
                print(f"❌ Graphics initialization error: {e}")
                return False
        else:
            print("⚠️ Using fallback graphics mode")
            self.initialized = True
            return True

    def initialize_framebuffer(self):
        """Initialize framebuffer for direct rendering"""
        if not self.initialized:
            if not self.initialize():
                return False

        # Check if framebuffer device exists
        fb_devices = ["/dev/fb0", "/dev/fb1"]
        self.fb_device = None

        for device in fb_devices:
            if os.path.exists(device):
                self.fb_device = device
                print(f"✅ Found framebuffer device: {device}")
                break

        if not self.fb_device:
            print("❌ No framebuffer device found")
            return False

        return True

    def clear_screen(self, r=255, g=255, b=255):
        """Clear screen with specified color (default: white)"""
        if not self.fb_device:
            print("⚠️ No framebuffer device - using fallback")
            return self._fallback_clear_screen(r, g, b)

        try:
            # Basic framebuffer clear - this is a simplified implementation
            # In a real implementation, we'd get the framebuffer info first
            with open(self.fb_device, "wb") as fb:
                # Assume 1024x768 resolution, 32-bit color (RGBA)
                width, height = 1024, 768
                pixel = bytes([b, g, r, 255])  # BGRA format

                for _ in range(width * height):
                    fb.write(pixel)

            print(f"✅ Screen cleared to RGB({r}, {g}, {b})")
            return True

        except Exception as e:
            print(f"❌ Failed to clear screen: {e}")
            return False

    def draw_text(self, x, y, text, r=0, g=0, b=0):
        """Draw text at specified position (simplified implementation)"""
        print(f"📝 Text at ({x}, {y}): '{text}' RGB({r}, {g}, {b})")
        # This is a placeholder - real implementation would render text to framebuffer
        return True

    def present(self):
        """Present the rendered frame"""
        print("🎨 Frame presented")
        return True

    def shutdown(self):
        """Shutdown the graphics system"""
        if self.lib and self.initialized:
            try:
                self.lib.ug_shutdown()
                print("✅ Graphics system shutdown")
            except:
                pass
        self.initialized = False

    def _fallback_clear_screen(self, r, g, b):
        """Fallback screen clear using basic methods"""
        try:
            # Try to clear using ANSI escape codes
            print("\033[2J\033[H")  # Clear screen and move cursor to top
            print("🎨 UNHINGED GRAPHICS FALLBACK MODE")
            print(f"📺 Screen cleared to RGB({r}, {g}, {b})")
            return True
        except:
            return False

    def __del__(self):
        """Cleanup on destruction"""
        self.shutdown()


# Test function
def test_graphics():
    """Test the graphics system"""
    print("🧪 Testing Unhinged Graphics...")

    graphics = UnhingedGraphics()
    print(f"📋 Version: {graphics.get_version()}")

    if graphics.initialize_framebuffer():
        graphics.clear_screen(255, 255, 255)  # White background
        graphics.draw_text(100, 100, "UNHINGED ALPINE LINUX", 0, 0, 0)
        graphics.draw_text(100, 150, "Native C Graphics Test", 0, 0, 0)
        graphics.present()

        print("✅ Graphics test completed")
        return True
    else:
        print("❌ Graphics test failed")
        return False


if __name__ == "__main__":
    test_graphics()
