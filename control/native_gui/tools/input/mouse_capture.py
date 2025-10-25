
import logging; gui_logger = logging.getLogger(__name__)

"""
Mouse Capture Module for Click Tracking and Movement Analysis
Provides pynput-based mouse capture for interaction analysis and automation.
"""

import threading
import time
import math
from typing import Optional, Dict, List, Callable, Tuple
from dataclasses import dataclass
from collections import deque
import queue

# Import pynput for mouse monitoring
try:
    from pynput import mouse
    from pynput.mouse import Button, Listener
    PYNPUT_AVAILABLE = True
except ImportError:
    gui_logger.warn(" pynput not available - install with: pip install pynput")
    PYNPUT_AVAILABLE = False


@dataclass
class MouseEvent:
    """Represents a mouse event"""
    event_type: str  # 'move', 'click', 'scroll', 'drag'
    timestamp: float
    x: int
    y: int
    button: Optional[str] = None
    pressed: Optional[bool] = None
    scroll_dx: Optional[float] = None
    scroll_dy: Optional[float] = None


@dataclass
class MouseConfig:
    """Mouse capture configuration"""
    enable_movement: bool = True
    enable_clicks: bool = True
    enable_scrolling: bool = True
    enable_dragging: bool = True
    movement_threshold: int = 5  # Minimum pixels to log movement
    max_events: int = 1000
    track_velocity: bool = True
    track_patterns: bool = True
    privacy_mode: bool = False  # Don't log exact coordinates


class MouseCapture:
    """Global mouse capture and analysis"""
    
    def __init__(self, config: Optional[MouseConfig] = None):
        self.config = config or MouseConfig()
        
        # Capture state
        self.is_capturing = False
        self.listener = None
        self.capture_thread = None
        
        # Event storage
        self.mouse_events: deque = deque(maxlen=self.config.max_events)
        self.event_queue = queue.Queue()
        self.events_lock = threading.Lock()
        
        # Current state
        self.current_position = (0, 0)
        self.last_position = (0, 0)
        self.last_move_time = 0
        self.is_dragging = False
        self.drag_start_pos = None
        self.pressed_buttons = set()
        
        # Movement analysis
        self.movement_path = deque(maxlen=100)
        self.velocity_history = deque(maxlen=50)
        self.total_distance = 0
        self.click_positions = []
        
        # Pattern detection
        self.click_patterns = []
        self.scroll_sessions = []
        self.current_scroll_session = None
        
        # Statistics
        self.total_clicks = 0
        self.total_scrolls = 0
        self.total_movements = 0
        self.session_start_time = None
        
        # Callbacks
        self.on_mouse_move: Optional[Callable[[MouseEvent], None]] = None
        self.on_mouse_click: Optional[Callable[[MouseEvent], None]] = None
        self.on_mouse_scroll: Optional[Callable[[MouseEvent], None]] = None
        self.on_drag_start: Optional[Callable[[Tuple[int, int]], None]] = None
        self.on_drag_end: Optional[Callable[[Tuple[int, int], Tuple[int, int]], None]] = None
        self.on_pattern_detected: Optional[Callable[[str, Dict], None]] = None
        
    
    def start_capture(self) -> bool:
        """Start mouse capture"""
        if not PYNPUT_AVAILABLE:
            gui_logger.error(" pynput not available")
            return False
        
        if self.is_capturing:
            gui_logger.warn(" Mouse capture already running")
            return True
        
        try:
            # Create mouse listener
            self.listener = Listener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click,
                on_scroll=self._on_mouse_scroll
            )
            
            # Start listener
            self.listener.start()
            self.is_capturing = True
            self.session_start_time = time.time()
            
            # Start processing thread
            self.capture_thread = threading.Thread(
                target=self._process_events,
                daemon=True
            )
            self.capture_thread.start()
            
            return True
            
        except Exception as e:
            gui_logger.error(f" Failed to start mouse capture: {e}")
            return False
    
    def stop_capture(self):
        """Stop mouse capture"""
        if not self.is_capturing:
            gui_logger.warn(" Mouse capture not running")
            return
        
        try:
            self.is_capturing = False
            
            # Stop listener
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            # End current scroll session
            if self.current_scroll_session:
                self._end_scroll_session()
            
            
        except Exception as e:
            gui_logger.error(f" Error stopping mouse capture: {e}")
    
    def _on_mouse_move(self, x, y):
        """Handle mouse movement"""
        try:
            if not self.config.enable_movement:
                return
            
            current_time = time.time()
            
            # Check movement threshold
            if self.last_position:
                distance = math.sqrt((x - self.last_position[0])**2 + (y - self.last_position[1])**2)
                if distance < self.config.movement_threshold:
                    return
            
            # Calculate velocity
            velocity = 0
            if self.last_move_time > 0:
                time_diff = current_time - self.last_move_time
                if time_diff > 0:
                    distance = math.sqrt((x - self.current_position[0])**2 + (y - self.current_position[1])**2)
                    velocity = distance / time_diff
            
            # Update state
            self.last_position = self.current_position
            self.current_position = (x, y)
            self.last_move_time = current_time
            
            # Store movement data
            if self.config.track_velocity:
                self.velocity_history.append(velocity)
            
            self.movement_path.append((x, y, current_time))
            self.total_distance += math.sqrt((x - self.last_position[0])**2 + (y - self.last_position[1])**2) if self.last_position else 0
            
            # Create event
            event = MouseEvent(
                event_type='move',
                timestamp=current_time,
                x=x if not self.config.privacy_mode else -1,
                y=y if not self.config.privacy_mode else -1
            )
            
            self.event_queue.put(event)
            self.total_movements += 1
            
        except Exception as e:
            gui_logger.warn(f" Mouse move handling error: {e}")
    
    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click"""
        try:
            if not self.config.enable_clicks:
                return
            
            current_time = time.time()
            button_name = button.name if hasattr(button, 'name') else str(button)
            
            # Track pressed buttons
            if pressed:
                self.pressed_buttons.add(button_name)
                
                # Check for drag start
                if button == Button.left and self.config.enable_dragging:
                    self.drag_start_pos = (x, y)
                    if self.on_drag_start:
                        self.on_drag_start((x, y))
            else:
                self.pressed_buttons.discard(button_name)
                
                # Check for drag end
                if button == Button.left and self.drag_start_pos and self.config.enable_dragging:
                    if self.on_drag_end:
                        self.on_drag_end(self.drag_start_pos, (x, y))
                    self.drag_start_pos = None
            
            # Store click position
            if pressed:
                self.click_positions.append({
                    'x': x if not self.config.privacy_mode else -1,
                    'y': y if not self.config.privacy_mode else -1,
                    'button': button_name,
                    'timestamp': current_time
                })
                
                # Detect click patterns
                if self.config.track_patterns:
                    self._detect_click_patterns()
            
            # Create event
            event = MouseEvent(
                event_type='click',
                timestamp=current_time,
                x=x if not self.config.privacy_mode else -1,
                y=y if not self.config.privacy_mode else -1,
                button=button_name,
                pressed=pressed
            )
            
            self.event_queue.put(event)
            
            if pressed:
                self.total_clicks += 1
            
        except Exception as e:
            gui_logger.warn(f" Mouse click handling error: {e}")
    
    def _on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll"""
        try:
            if not self.config.enable_scrolling:
                return
            
            current_time = time.time()
            
            # Start scroll session if needed
            if not self.current_scroll_session:
                self._start_scroll_session(x, y)
            
            # Update scroll session
            self.current_scroll_session['scrolls'] += 1
            self.current_scroll_session['total_dx'] += dx
            self.current_scroll_session['total_dy'] += dy
            self.current_scroll_session['last_time'] = current_time
            
            # Create event
            event = MouseEvent(
                event_type='scroll',
                timestamp=current_time,
                x=x if not self.config.privacy_mode else -1,
                y=y if not self.config.privacy_mode else -1,
                scroll_dx=dx,
                scroll_dy=dy
            )
            
            self.event_queue.put(event)
            self.total_scrolls += 1
            
        except Exception as e:
            gui_logger.warn(f" Mouse scroll handling error: {e}")
    
    def _process_events(self):
        """Process mouse events in separate thread"""
        while self.is_capturing:
            try:
                # Get event from queue
                event = self.event_queue.get(timeout=1.0)
                
                # Store event
                with self.events_lock:
                    self.mouse_events.append(event)
                
                # Trigger callbacks
                if event.event_type == 'move' and self.on_mouse_move:
                    self.on_mouse_move(event)
                elif event.event_type == 'click' and self.on_mouse_click:
                    self.on_mouse_click(event)
                elif event.event_type == 'scroll' and self.on_mouse_scroll:
                    self.on_mouse_scroll(event)
                
            except queue.Empty:
                # Check for scroll session timeout
                if self.current_scroll_session:
                    if time.time() - self.current_scroll_session['last_time'] > 2.0:
                        self._end_scroll_session()
                continue
            except Exception as e:
                gui_logger.warn(f" Event processing error: {e}")
    
    def _start_scroll_session(self, x: int, y: int):
        """Start new scroll session"""
        self.current_scroll_session = {
            'start_time': time.time(),
            'start_x': x,
            'start_y': y,
            'scrolls': 0,
            'total_dx': 0,
            'total_dy': 0,
            'last_time': time.time()
        }
    
    def _end_scroll_session(self):
        """End current scroll session"""
        if self.current_scroll_session:
            self.current_scroll_session['end_time'] = time.time()
            self.current_scroll_session['duration'] = (
                self.current_scroll_session['end_time'] - 
                self.current_scroll_session['start_time']
            )
            
            self.scroll_sessions.append(self.current_scroll_session)
            self.current_scroll_session = None
    
    def _detect_click_patterns(self):
        """Detect patterns in click behavior"""
        try:
            if len(self.click_positions) < 3:
                return
            
            recent_clicks = self.click_positions[-5:]  # Last 5 clicks
            
            # Check for double/triple clicks
            if len(recent_clicks) >= 2:
                last_two = recent_clicks[-2:]
                time_diff = last_two[1]['timestamp'] - last_two[0]['timestamp']
                distance = math.sqrt(
                    (last_two[1]['x'] - last_two[0]['x'])**2 + 
                    (last_two[1]['y'] - last_two[0]['y'])**2
                )
                
                if time_diff < 0.5 and distance < 10:  # Double click
                    pattern = {
                        'type': 'double_click',
                        'position': (last_two[0]['x'], last_two[0]['y']),
                        'time_diff': time_diff
                    }
                    
                    if self.on_pattern_detected:
                        self.on_pattern_detected('double_click', pattern)
            
            # Check for rapid clicking
            if len(recent_clicks) >= 5:
                time_span = recent_clicks[-1]['timestamp'] - recent_clicks[0]['timestamp']
                if time_span < 2.0:  # 5 clicks in 2 seconds
                    pattern = {
                        'type': 'rapid_clicking',
                        'clicks': len(recent_clicks),
                        'time_span': time_span,
                        'rate': len(recent_clicks) / time_span
                    }
                    
                    if self.on_pattern_detected:
                        self.on_pattern_detected('rapid_clicking', pattern)
                        
        except Exception as e:
            gui_logger.warn(f" Pattern detection error: {e}")
    
    def get_statistics(self) -> Dict:
        """Get mouse capture statistics"""
        current_time = time.time()
        session_duration = current_time - self.session_start_time if self.session_start_time else 0
        
        # Calculate average velocity
        avg_velocity = sum(self.velocity_history) / len(self.velocity_history) if self.velocity_history else 0
        
        # Calculate clicks per minute
        cpm = (self.total_clicks / session_duration) * 60 if session_duration > 0 else 0
        
        return {
            'total_clicks': self.total_clicks,
            'total_scrolls': self.total_scrolls,
            'total_movements': self.total_movements,
            'total_distance': self.total_distance,
            'session_duration': session_duration,
            'clicks_per_minute': cpm,
            'average_velocity': avg_velocity,
            'scroll_sessions': len(self.scroll_sessions),
            'click_patterns': len(self.click_patterns),
            'is_capturing': self.is_capturing,
            'current_position': self.current_position if not self.config.privacy_mode else (-1, -1)
        }
    
    def get_recent_events(self, count: int = 10) -> List[MouseEvent]:
        """Get recent mouse events"""
        with self.events_lock:
            return list(self.mouse_events)[-count:]
    
    def get_click_heatmap_data(self) -> List[Dict]:
        """Get click position data for heatmap visualization"""
        if self.config.privacy_mode:
            return []
        
        # Group clicks by position (with some tolerance)
        heatmap_data = {}
        tolerance = 20  # pixels
        
        for click in self.click_positions:
            # Find nearby position or create new one
            found_key = None
            for key in heatmap_data.keys():
                if (abs(key[0] - click['x']) < tolerance and 
                    abs(key[1] - click['y']) < tolerance):
                    found_key = key
                    break
            
            if found_key:
                heatmap_data[found_key] += 1
            else:
                heatmap_data[(click['x'], click['y'])] = 1
        
        # Convert to list format
        return [
            {'x': pos[0], 'y': pos[1], 'count': count}
            for pos, count in heatmap_data.items()
        ]
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_capture()
        
        # Clear data
        self.mouse_events.clear()
        self.movement_path.clear()
        self.velocity_history.clear()
        self.click_positions.clear()
        self.scroll_sessions.clear()
        


# Test function
def test_mouse_capture():
    """Test mouse capture functionality"""
    
    if not PYNPUT_AVAILABLE:
        gui_logger.error(" pynput not available for testing")
        return
    
    try:
        config = MouseConfig(privacy_mode=False)
        capture = MouseCapture(config)
        
        # Set up callbacks
        def on_click(event):
        
        def on_pattern(pattern_type, data):
        
        capture.on_mouse_click = on_click
        capture.on_pattern_detected = on_pattern
        
        # Start capture
        if capture.start_capture():
            
            time.sleep(10)
            
            # Get statistics
            stats = capture.get_statistics()
            
            # Get heatmap data
            heatmap = capture.get_click_heatmap_data()
            
            capture.cleanup()
            gui_logger.info(" Mouse capture test completed", {"status": "success"})
        else:
            gui_logger.error(" Failed to start mouse capture")
            
    except Exception as e:
        gui_logger.error(f" Mouse capture test failed: {e}")


if __name__ == "__main__":
    test_mouse_capture()
