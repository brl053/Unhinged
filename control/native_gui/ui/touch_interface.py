"""
Touch Interface and Gesture Handling
Provides touch-optimized controls and gesture recognition for mobile interfaces.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, GLib
import math
import time
from typing import Dict, List, Optional, Callable, Tuple
from enum import Enum
from dataclasses import dataclass


class GestureType(Enum):
    """Types of touch gestures"""
    TAP = "tap"
    DOUBLE_TAP = "double_tap"
    LONG_PRESS = "long_press"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    PINCH_IN = "pinch_in"
    PINCH_OUT = "pinch_out"
    ROTATE = "rotate"
    PAN = "pan"


@dataclass
class TouchPoint:
    """Touch point data"""
    x: float
    y: float
    timestamp: float
    pressure: float = 1.0


@dataclass
class GestureEvent:
    """Gesture event data"""
    gesture_type: GestureType
    start_point: TouchPoint
    end_point: Optional[TouchPoint] = None
    velocity: float = 0.0
    distance: float = 0.0
    angle: float = 0.0
    scale: float = 1.0
    duration: float = 0.0


class TouchGestureRecognizer:
    """Recognizes touch gestures from input events"""
    
    def __init__(self):
        # Gesture thresholds
        self.tap_threshold = 10  # pixels
        self.swipe_threshold = 50  # pixels
        self.long_press_duration = 0.5  # seconds
        self.double_tap_interval = 0.3  # seconds
        self.velocity_threshold = 100  # pixels/second
        
        # State tracking
        self.touch_points: List[TouchPoint] = []
        self.gesture_start_time = 0
        self.last_tap_time = 0
        self.last_tap_position = None
        
        # Callbacks
        self.on_gesture: Optional[Callable[[GestureEvent], None]] = None
    
    def process_touch_begin(self, x: float, y: float, timestamp: float):
        """Process touch begin event"""
        touch_point = TouchPoint(x, y, timestamp)
        self.touch_points.append(touch_point)
        self.gesture_start_time = timestamp
    
    def process_touch_update(self, x: float, y: float, timestamp: float):
        """Process touch update event"""
        if not self.touch_points:
            return
        
        # Update current touch point
        current_point = TouchPoint(x, y, timestamp)
        
        # Check for pan gesture
        if len(self.touch_points) == 1:
            start_point = self.touch_points[0]
            distance = self._calculate_distance(start_point, current_point)
            
            if distance > self.tap_threshold:
                # This is a pan gesture
                velocity = self._calculate_velocity(start_point, current_point)
                
                gesture = GestureEvent(
                    gesture_type=GestureType.PAN,
                    start_point=start_point,
                    end_point=current_point,
                    velocity=velocity,
                    distance=distance,
                    duration=timestamp - self.gesture_start_time
                )
                
                if self.on_gesture:
                    self.on_gesture(gesture)
    
    def process_touch_end(self, x: float, y: float, timestamp: float):
        """Process touch end event"""
        if not self.touch_points:
            return
        
        end_point = TouchPoint(x, y, timestamp)
        start_point = self.touch_points[0]
        
        duration = timestamp - self.gesture_start_time
        distance = self._calculate_distance(start_point, end_point)
        velocity = self._calculate_velocity(start_point, end_point)
        
        # Determine gesture type
        gesture_type = self._classify_gesture(start_point, end_point, duration, distance, velocity)
        
        if gesture_type:
            gesture = GestureEvent(
                gesture_type=gesture_type,
                start_point=start_point,
                end_point=end_point,
                velocity=velocity,
                distance=distance,
                duration=duration
            )
            
            if gesture_type in [GestureType.SWIPE_LEFT, GestureType.SWIPE_RIGHT, 
                               GestureType.SWIPE_UP, GestureType.SWIPE_DOWN]:
                gesture.angle = self._calculate_angle(start_point, end_point)
            
            if self.on_gesture:
                self.on_gesture(gesture)
        
        # Clear touch points
        self.touch_points.clear()
    
    def _calculate_distance(self, point1: TouchPoint, point2: TouchPoint) -> float:
        """Calculate distance between two points"""
        return math.sqrt((point2.x - point1.x)**2 + (point2.y - point1.y)**2)
    
    def _calculate_velocity(self, point1: TouchPoint, point2: TouchPoint) -> float:
        """Calculate velocity between two points"""
        distance = self._calculate_distance(point1, point2)
        time_diff = point2.timestamp - point1.timestamp
        return distance / time_diff if time_diff > 0 else 0
    
    def _calculate_angle(self, point1: TouchPoint, point2: TouchPoint) -> float:
        """Calculate angle between two points"""
        dx = point2.x - point1.x
        dy = point2.y - point1.y
        return math.atan2(dy, dx)
    
    def _classify_gesture(self, start: TouchPoint, end: TouchPoint, 
                         duration: float, distance: float, velocity: float) -> Optional[GestureType]:
        """Classify gesture based on parameters"""
        
        # Long press
        if distance < self.tap_threshold and duration > self.long_press_duration:
            return GestureType.LONG_PRESS
        
        # Tap or double tap
        if distance < self.tap_threshold and duration < self.long_press_duration:
            current_time = end.timestamp
            
            # Check for double tap
            if (self.last_tap_time > 0 and 
                current_time - self.last_tap_time < self.double_tap_interval and
                self.last_tap_position and
                self._calculate_distance(TouchPoint(self.last_tap_position[0], self.last_tap_position[1], 0), start) < self.tap_threshold):
                
                self.last_tap_time = 0  # Reset to prevent triple tap
                return GestureType.DOUBLE_TAP
            else:
                self.last_tap_time = current_time
                self.last_tap_position = (start.x, start.y)
                return GestureType.TAP
        
        # Swipe gestures
        if distance > self.swipe_threshold and velocity > self.velocity_threshold:
            angle = self._calculate_angle(start, end)
            angle_degrees = math.degrees(angle)
            
            # Normalize angle to 0-360
            if angle_degrees < 0:
                angle_degrees += 360
            
            # Determine swipe direction
            if 315 <= angle_degrees or angle_degrees < 45:
                return GestureType.SWIPE_RIGHT
            elif 45 <= angle_degrees < 135:
                return GestureType.SWIPE_DOWN
            elif 135 <= angle_degrees < 225:
                return GestureType.SWIPE_LEFT
            elif 225 <= angle_degrees < 315:
                return GestureType.SWIPE_UP
        
        return None


class TouchButton(Gtk.Button):
    """Touch-optimized button with haptic feedback simulation"""
    
    def __init__(self, label: str = "", icon_name: str = ""):
        super().__init__()
        
        # Button properties
        self.set_size_request(44, 44)  # Minimum touch target size
        self.add_css_class("touch-button")
        
        # Content
        if icon_name and label:
            # Button with icon and text
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            icon = Gtk.Image.new_from_icon_name(icon_name)
            label_widget = Gtk.Label(label=label)
            box.append(icon)
            box.append(label_widget)
            self.set_child(box)
        elif icon_name:
            # Icon only
            self.set_icon_name(icon_name)
        else:
            # Text only
            self.set_label(label)
        
        # Touch feedback - use button-press-event and button-release-event
        self.connect("clicked", self._on_touch_clicked)
    
    def _on_touch_clicked(self, button):
        """Handle touch click with visual feedback"""
        # Add pressed class temporarily for visual feedback
        self.add_css_class("pressed")

        # Remove pressed class after a short delay
        def remove_pressed():
            self.remove_css_class("pressed")
            return False  # Don't repeat

        from gi.repository import GLib
        GLib.timeout_add(100, remove_pressed)


class SwipeableContainer(Gtk.Box):
    """Container that responds to swipe gestures"""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # Create stack for swipeable content
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(300)
        self.append(self.stack)
        
        # Gesture recognition
        self.gesture_recognizer = TouchGestureRecognizer()
        self.gesture_recognizer.on_gesture = self._on_gesture
        
        # Setup gesture controllers
        self._setup_gesture_controllers()
        
        # Pages
        self.pages: List[Gtk.Widget] = []
        self.current_page = 0
        
        # Callbacks
        self.on_page_changed: Optional[Callable[[int], None]] = None
    
    def _setup_gesture_controllers(self):
        """Setup GTK gesture controllers"""
        # Pan gesture for swiping
        self.pan_gesture = Gtk.GesturePan.new(Gtk.Orientation.HORIZONTAL)
        self.pan_gesture.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.pan_gesture.connect("pan", self._on_pan)
        self.pan_gesture.connect("end", self._on_pan_end)
        self.add_controller(self.pan_gesture)
        
        # Click gesture for taps
        self.click_gesture = Gtk.GestureClick.new()
        self.click_gesture.connect("pressed", self._on_click_pressed)
        self.click_gesture.connect("released", self._on_click_released)
        self.add_controller(self.click_gesture)
    
    def add_page(self, widget: Gtk.Widget, name: str):
        """Add page to swipeable container"""
        self.pages.append(widget)
        self.stack.add_named(widget, name)
        
        if len(self.pages) == 1:
            self.stack.set_visible_child(widget)
    
    def _on_pan(self, gesture, direction, offset):
        """Handle pan gesture"""
        # Could add visual feedback during pan
        pass
    
    def _on_pan_end(self, gesture):
        """Handle pan gesture end"""
        velocity = gesture.get_velocity()
        
        if abs(velocity[0]) > 500:  # Minimum velocity for swipe
            if velocity[0] > 0:
                self.swipe_to_previous()
            else:
                self.swipe_to_next()
    
    def _on_click_pressed(self, gesture, n_press, x, y):
        """Handle click press"""
        self.gesture_recognizer.process_touch_begin(x, y, time.time())
    
    def _on_click_released(self, gesture, n_press, x, y):
        """Handle click release"""
        self.gesture_recognizer.process_touch_end(x, y, time.time())
    
    def _on_gesture(self, gesture_event: GestureEvent):
        """Handle recognized gesture"""
        if gesture_event.gesture_type == GestureType.SWIPE_LEFT:
            self.swipe_to_next()
        elif gesture_event.gesture_type == GestureType.SWIPE_RIGHT:
            self.swipe_to_previous()
    
    def swipe_to_next(self):
        """Swipe to next page"""
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.stack.set_visible_child(self.pages[self.current_page])
            
            if self.on_page_changed:
                self.on_page_changed(self.current_page)
    
    def swipe_to_previous(self):
        """Swipe to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.stack.set_visible_child(self.pages[self.current_page])
            
            if self.on_page_changed:
                self.on_page_changed(self.current_page)


class TouchScrollArea(Gtk.ScrolledWindow):
    """Touch-optimized scrollable area"""
    
    def __init__(self):
        super().__init__()
        
        # Touch-friendly scrolling
        self.set_kinetic_scrolling(True)
        self.set_overlay_scrolling(True)
        
        # Scroll policies
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        # Minimum content size for touch
        self.set_min_content_width(300)
        self.set_min_content_height(200)


class PullToRefresh(Gtk.Widget):
    """Pull-to-refresh container"""
    
    def __init__(self):
        super().__init__()
        
        # Create main box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.main_box)
        
        # Refresh indicator
        self.refresh_indicator = Gtk.Spinner()
        self.refresh_indicator.set_visible(False)
        self.main_box.append(self.refresh_indicator)
        
        # Content area
        self.content_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.main_box.append(self.content_area)
        
        # Gesture setup
        self.pan_gesture = Gtk.GesturePan.new(Gtk.Orientation.VERTICAL)
        self.pan_gesture.connect("pan", self._on_pan)
        self.pan_gesture.connect("end", self._on_pan_end)
        self.add_controller(self.pan_gesture)
        
        # State
        self.is_refreshing = False
        self.pull_threshold = 80  # pixels
        
        # Callback
        self.on_refresh: Optional[Callable[[], None]] = None
    
    def set_content(self, widget: Gtk.Widget):
        """Set content widget"""
        # Clear existing content
        child = self.content_area.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.content_area.remove(child)
            child = next_child
        
        # Add new content
        self.content_area.append(widget)
    
    def _on_pan(self, gesture, direction, offset):
        """Handle pan gesture"""
        if direction == Gtk.PanDirection.DOWN and offset > 0:
            # Show refresh indicator based on pull distance
            if offset > self.pull_threshold / 2:
                self.refresh_indicator.set_visible(True)
    
    def _on_pan_end(self, gesture):
        """Handle pan gesture end"""
        velocity = gesture.get_velocity()
        
        if velocity[1] > 0:  # Downward velocity
            offset = gesture.get_offset()[1]
            
            if offset > self.pull_threshold and not self.is_refreshing:
                self.start_refresh()
    
    def start_refresh(self):
        """Start refresh animation"""
        if self.is_refreshing:
            return
        
        self.is_refreshing = True
        self.refresh_indicator.set_visible(True)
        self.refresh_indicator.start()
        
        if self.on_refresh:
            self.on_refresh()
    
    def stop_refresh(self):
        """Stop refresh animation"""
        self.is_refreshing = False
        self.refresh_indicator.stop()
        self.refresh_indicator.set_visible(False)


class TouchKeyboard(Gtk.Widget):
    """Virtual touch keyboard"""
    
    def __init__(self):
        super().__init__()
        
        # Create keyboard layout
        self.keyboard_grid = Gtk.Grid()
        self.keyboard_grid.set_row_homogeneous(True)
        self.keyboard_grid.set_column_homogeneous(True)
        self.keyboard_grid.set_row_spacing(4)
        self.keyboard_grid.set_column_spacing(4)
        self.set_child(self.keyboard_grid)
        
        # Keyboard state
        self.is_shift_active = False
        self.is_caps_lock = False
        
        # Callbacks
        self.on_key_pressed: Optional[Callable[[str], None]] = None
        
        # Build keyboard
        self._build_keyboard()
    
    def _build_keyboard(self):
        """Build virtual keyboard layout"""
        # QWERTY layout
        rows = [
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', 'backspace'],
            ['123', 'space', 'return']
        ]
        
        for row_idx, row in enumerate(rows):
            for col_idx, key in enumerate(row):
                button = self._create_key_button(key)
                
                # Special sizing for certain keys
                if key == 'space':
                    self.keyboard_grid.attach(button, col_idx, row_idx, 6, 1)
                elif key in ['shift', 'backspace']:
                    self.keyboard_grid.attach(button, col_idx, row_idx, 2, 1)
                else:
                    self.keyboard_grid.attach(button, col_idx, row_idx, 1, 1)
    
    def _create_key_button(self, key: str) -> TouchButton:
        """Create keyboard key button"""
        if key == 'space':
            button = TouchButton(" ")
        elif key == 'backspace':
            button = TouchButton("", "edit-clear-symbolic")
        elif key == 'return':
            button = TouchButton("", "go-next-symbolic")
        elif key == 'shift':
            button = TouchButton("", "go-up-symbolic")
        else:
            button = TouchButton(key.upper() if self.is_shift_active or self.is_caps_lock else key)
        
        button.connect("clicked", lambda b: self._on_key_clicked(key))
        return button
    
    def _on_key_clicked(self, key: str):
        """Handle key click"""
        if key == 'shift':
            self.is_shift_active = not self.is_shift_active
            self._update_key_labels()
        elif key == 'backspace':
            if self.on_key_pressed:
                self.on_key_pressed('\b')
        elif key == 'return':
            if self.on_key_pressed:
                self.on_key_pressed('\n')
        elif key == 'space':
            if self.on_key_pressed:
                self.on_key_pressed(' ')
        else:
            # Regular key
            char = key.upper() if self.is_shift_active or self.is_caps_lock else key
            if self.on_key_pressed:
                self.on_key_pressed(char)
            
            # Reset shift after key press
            if self.is_shift_active and not self.is_caps_lock:
                self.is_shift_active = False
                self._update_key_labels()
    
    def _update_key_labels(self):
        """Update key labels based on shift state"""
        # Would need to iterate through buttons and update labels
        pass


# Test function
def test_touch_interface():
    """Test touch interface components"""
    print("📱 Testing touch interface...")
    
    app = Adw.Application()
    
    def on_activate(app):
        window = Adw.ApplicationWindow(application=app)
        window.set_title("Touch Interface Test")
        window.set_default_size(400, 600)
        
        # Create swipeable container
        swipeable = SwipeableContainer()
        
        # Add test pages
        page1 = Gtk.Label(label="Page 1\nSwipe to navigate")
        page2 = Gtk.Label(label="Page 2\nSwipe left or right")
        page3 = Gtk.Label(label="Page 3\nTouch interface test")
        
        swipeable.add_page(page1, "page1")
        swipeable.add_page(page2, "page2")
        swipeable.add_page(page3, "page3")
        
        window.set_content(swipeable)
        window.present()
    
    app.connect("activate", on_activate)
    app.run()


if __name__ == "__main__":
    test_touch_interface()
