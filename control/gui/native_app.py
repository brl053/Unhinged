#!/usr/bin/env python3
"""
@llm-type native-gui
@llm-legend Native GUI application using raw X11 and Python ctypes
@llm-key Native window application with direct X11 rendering for hello world and red square
@llm-map Native GUI application providing direct system window access without browser dependencies
@llm-axiom Native GUI must be lightweight, fast, and provide direct system integration
@llm-contract Provides native window with custom rendering using X11 and graphics primitives
@llm-token native-gui: Raw X11 native application for direct system window rendering

Unhinged Native GUI Application - Game Developer Approach
Raw X11 window with custom rendering - Hello World + Red Square
No frameworks, no dependencies, just pure native windowing
"""

import ctypes
import ctypes.util
import sys
import time
from ctypes import Structure, c_int, c_uint, c_ulong, c_char_p, c_void_p, POINTER

class UnhingedNativeGUI:
    """
    @llm-type x11-native-app
    @llm-legend Native X11 application providing direct window rendering
    @llm-key Raw X11 window with custom graphics rendering for native GUI
    @llm-map Native application using X11 primitives for direct system integration
    @llm-axiom Native GUI must be minimal, fast, and provide direct hardware access
    @llm-contract Provides native window with X11 rendering for custom graphics
    @llm-token x11-native-app: Raw X11 application for native window rendering
    
    Game developer approach: Direct X11 access, no middleware
    """
    
    def __init__(self, width=800, height=600, title="Unhinged Native GUI"):
        self.width = width
        self.height = height
        self.title = title.encode('utf-8')
        
        # Load X11 library
        self.xlib = ctypes.CDLL(ctypes.util.find_library('X11'))
        
        # X11 function signatures
        self._setup_x11_functions()
        
        # Initialize X11 connection
        self.display = None
        self.window = None
        self.screen = None
        self.gc = None
        self.running = False
        
        print(f"🎮 Initializing Unhinged Native GUI...")
        print(f"📐 Window size: {width}x{height}")
        print(f"🏷️  Title: {title}")
    
    def _setup_x11_functions(self):
        """Setup X11 function signatures for ctypes"""
        
        # XOpenDisplay
        self.xlib.XOpenDisplay.argtypes = [c_char_p]
        self.xlib.XOpenDisplay.restype = c_void_p
        
        # XDefaultScreen
        self.xlib.XDefaultScreen.argtypes = [c_void_p]
        self.xlib.XDefaultScreen.restype = c_int
        
        # XRootWindow
        self.xlib.XRootWindow.argtypes = [c_void_p, c_int]
        self.xlib.XRootWindow.restype = c_ulong
        
        # XCreateSimpleWindow
        self.xlib.XCreateSimpleWindow.argtypes = [
            c_void_p, c_ulong, c_int, c_int, c_uint, c_uint, 
            c_uint, c_ulong, c_ulong
        ]
        self.xlib.XCreateSimpleWindow.restype = c_ulong
        
        # XMapWindow
        self.xlib.XMapWindow.argtypes = [c_void_p, c_ulong]
        self.xlib.XMapWindow.restype = c_int
        
        # XSelectInput
        self.xlib.XSelectInput.argtypes = [c_void_p, c_ulong, c_ulong]
        self.xlib.XSelectInput.restype = c_int
        
        # XStoreName
        self.xlib.XStoreName.argtypes = [c_void_p, c_ulong, c_char_p]
        self.xlib.XStoreName.restype = c_int
        
        # XDefaultGC
        self.xlib.XDefaultGC.argtypes = [c_void_p, c_int]
        self.xlib.XDefaultGC.restype = c_void_p
        
        # XSetForeground
        self.xlib.XSetForeground.argtypes = [c_void_p, c_void_p, c_ulong]
        self.xlib.XSetForeground.restype = c_int
        
        # XFillRectangle
        self.xlib.XFillRectangle.argtypes = [
            c_void_p, c_ulong, c_void_p, c_int, c_int, c_uint, c_uint
        ]
        self.xlib.XFillRectangle.restype = c_int
        
        # XDrawString
        self.xlib.XDrawString.argtypes = [
            c_void_p, c_ulong, c_void_p, c_int, c_int, c_char_p, c_int
        ]
        self.xlib.XDrawString.restype = c_int
        
        # XFlush
        self.xlib.XFlush.argtypes = [c_void_p]
        self.xlib.XFlush.restype = c_int
        
        # XNextEvent
        self.xlib.XNextEvent.argtypes = [c_void_p, c_void_p]
        self.xlib.XNextEvent.restype = c_int
        
        # XPending
        self.xlib.XPending.argtypes = [c_void_p]
        self.xlib.XPending.restype = c_int
        
        # XCloseDisplay
        self.xlib.XCloseDisplay.argtypes = [c_void_p]
        self.xlib.XCloseDisplay.restype = c_int
    
    def create_window(self):
        """Create native X11 window"""
        try:
            # Open display
            self.display = self.xlib.XOpenDisplay(None)
            if not self.display:
                raise Exception("Cannot open X11 display")
            
            # Get default screen
            self.screen = self.xlib.XDefaultScreen(self.display)
            
            # Get root window
            root = self.xlib.XRootWindow(self.display, self.screen)
            
            # Create window
            self.window = self.xlib.XCreateSimpleWindow(
                self.display, root,
                100, 100,  # x, y position
                self.width, self.height,  # width, height
                1,  # border width
                0x000000,  # border color (black)
                0xFFFFFF   # background color (white)
            )
            
            # Set window title
            self.xlib.XStoreName(self.display, self.window, self.title)
            
            # Select input events
            ExposureMask = 1 << 15
            KeyPressMask = 1 << 0
            ButtonPressMask = 1 << 2
            self.xlib.XSelectInput(self.display, self.window, 
                                 ExposureMask | KeyPressMask | ButtonPressMask)
            
            # Map window (make it visible)
            self.xlib.XMapWindow(self.display, self.window)
            
            # Get graphics context
            self.gc = self.xlib.XDefaultGC(self.display, self.screen)
            
            # Flush to ensure window appears
            self.xlib.XFlush(self.display)
            
            print("✅ Native window created successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create window: {e}")
            return False
    
    def draw_content(self):
        """Draw hello world text and red square"""
        if not self.display or not self.window or not self.gc:
            return
        
        # Clear window (fill with white)
        self.xlib.XSetForeground(self.display, self.gc, 0xFFFFFF)
        self.xlib.XFillRectangle(self.display, self.window, self.gc, 
                               0, 0, self.width, self.height)
        
        # Draw "Hello World" text in black
        self.xlib.XSetForeground(self.display, self.gc, 0x000000)
        hello_text = b"Hello World from Unhinged Native GUI!"
        self.xlib.XDrawString(self.display, self.window, self.gc, 
                            50, 50, hello_text, len(hello_text))
        
        # Draw red square
        self.xlib.XSetForeground(self.display, self.gc, 0xFF0000)  # Red color
        square_size = 100
        square_x = (self.width - square_size) // 2
        square_y = (self.height - square_size) // 2
        
        self.xlib.XFillRectangle(self.display, self.window, self.gc,
                               square_x, square_y, square_size, square_size)
        
        # Add some info text
        self.xlib.XSetForeground(self.display, self.gc, 0x000000)
        info_text = b"Press any key or click to exit"
        self.xlib.XDrawString(self.display, self.window, self.gc,
                            50, self.height - 30, info_text, len(info_text))
        
        # Flush drawing commands
        self.xlib.XFlush(self.display)
    
    def handle_events(self):
        """Handle X11 events"""
        if not self.display:
            return True
        
        # Check for pending events
        while self.xlib.XPending(self.display):
            # Create event structure (simplified)
            event = (ctypes.c_char * 192)()  # XEvent is about 192 bytes
            
            # Get next event
            self.xlib.XNextEvent(self.display, event)
            
            # Get event type (first 4 bytes)
            event_type = ctypes.c_int.from_buffer(event).value
            
            # Handle different event types
            if event_type == 12:  # Expose event
                self.draw_content()
            elif event_type == 2 or event_type == 4:  # KeyPress or ButtonPress
                print("🎮 User input detected - exiting...")
                return False
        
        return True
    
    def run(self):
        """Main application loop"""
        if not self.create_window():
            return False
        
        print("🚀 Starting native GUI application...")
        print("💡 Press any key or click to exit")
        
        self.running = True
        
        # Initial draw
        self.draw_content()
        
        # Main event loop
        try:
            while self.running:
                if not self.handle_events():
                    break
                
                # Small delay to prevent CPU spinning
                time.sleep(0.016)  # ~60 FPS
                
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        
        self.cleanup()
        return True
    
    def cleanup(self):
        """Clean up X11 resources"""
        if self.display:
            print("🧹 Cleaning up X11 resources...")
            self.xlib.XCloseDisplay(self.display)
            self.display = None
        
        print("✅ Native GUI application closed")


def main():
    """Entry point for native GUI application"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Unhinged Native GUI - Game Dev Approach",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default window
  python3 native_app.py
  
  # Custom size
  python3 native_app.py --width 1024 --height 768
  
  # Custom title
  python3 native_app.py --title "My Game Window"
        """
    )
    
    parser.add_argument("--width", type=int, default=800, help="Window width")
    parser.add_argument("--height", type=int, default=600, help="Window height")
    parser.add_argument("--title", default="Unhinged Native GUI", help="Window title")
    
    args = parser.parse_args()
    
    print("🎮 Unhinged Native GUI Application")
    print("=" * 40)
    
    # Create and run native GUI
    app = UnhingedNativeGUI(args.width, args.height, args.title)
    
    success = app.run()
    
    if success:
        print("✅ Application completed successfully!")
    else:
        print("❌ Application failed to run")
        sys.exit(1)


if __name__ == "__main__":
    main()
