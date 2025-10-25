
import logging; gui_logger = logging.getLogger(__name__)

"""
Keyboard Capture Module for Global Key Monitoring and Hotkeys
Provides pynput-based keyboard capture for input analysis and automation.
"""

import threading
import time
import json
from typing import Optional, Dict, List, Callable, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque
import queue

# Import pynput for keyboard monitoring
try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode
    PYNPUT_AVAILABLE = True
except ImportError:
    gui_logger.warn(" pynput not available - install with: pip install pynput")
    PYNPUT_AVAILABLE = False


@dataclass
class KeyEvent:
    """Represents a keyboard event"""
    key: str
    event_type: str  # 'press' or 'release'
    timestamp: float
    modifiers: List[str]
    is_special: bool
    char: Optional[str] = None


@dataclass
class KeyboardConfig:
    """Keyboard capture configuration"""
    enable_logging: bool = True
    log_special_keys: bool = True
    log_modifiers: bool = True
    max_log_entries: int = 1000
    enable_hotkeys: bool = True
    enable_typing_analysis: bool = True
    privacy_mode: bool = False  # Don't log actual characters
    save_to_file: bool = False
    log_file: str = "keyboard_log.json"


class KeyboardCapture:
    """Global keyboard capture and analysis"""
    
    def __init__(self, config: Optional[KeyboardConfig] = None):
        self.config = config or KeyboardConfig()
        
        # Capture state
        self.is_capturing = False
        self.listener = None
        self.capture_thread = None
        
        # Event storage
        self.key_events: deque = deque(maxlen=self.config.max_log_entries)
        self.event_queue = queue.Queue()
        self.events_lock = threading.Lock()
        
        # Current state tracking
        self.pressed_keys: Set[str] = set()
        self.current_modifiers: Set[str] = set()
        self.last_key_time = 0
        
        # Enhanced hotkey system
        self.hotkeys: Dict[str, Callable] = {}
        self.hotkey_combinations: Dict[frozenset, Callable] = {}
        self.hotkey_metadata: Dict[str, Dict] = {}
        self.sequence_hotkeys: Dict[str, Dict] = {}  # For key sequences like "ctrl+k, ctrl+c"
        self.current_sequence = []
        self.sequence_timeout = 2.0  # Seconds to wait for sequence completion
        
        # Typing analysis
        self.typing_sessions = []
        self.current_session = None
        self.words_typed = []
        self.current_word = ""
        
        # Statistics
        self.total_keystrokes = 0
        self.keys_per_minute = 0
        self.session_start_time = None
        
        # Callbacks
        self.on_key_press: Optional[Callable[[KeyEvent], None]] = None
        self.on_key_release: Optional[Callable[[KeyEvent], None]] = None
        self.on_hotkey_triggered: Optional[Callable[[str], None]] = None
        self.on_word_completed: Optional[Callable[[str], None]] = None
        self.on_typing_session_start: Optional[Callable[[], None]] = None
        self.on_typing_session_end: Optional[Callable[[Dict], None]] = None
        
    
    def start_capture(self) -> bool:
        """Start keyboard capture"""
        if not PYNPUT_AVAILABLE:
            gui_logger.error(" pynput not available")
            return False
        
        if self.is_capturing:
            gui_logger.warn(" Keyboard capture already running")
            return True
        
        try:
            # Create keyboard listener
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
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
            
            
            # Trigger session start callback
            if self.on_typing_session_start:
                self.on_typing_session_start()
            
            return True
            
        except Exception as e:
            gui_logger.error(f" Failed to start keyboard capture: {e}")
            return False
    
    def stop_capture(self):
        """Stop keyboard capture"""
        if not self.is_capturing:
            gui_logger.warn(" Keyboard capture not running")
            return
        
        try:
            self.is_capturing = False
            
            # Stop listener
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            # End current typing session
            if self.current_session:
                self._end_typing_session()
            
            # Save log if enabled
            if self.config.save_to_file:
                self._save_log()
            
            
        except Exception as e:
            gui_logger.error(f" Error stopping keyboard capture: {e}")
    
    def _on_key_press(self, key):
        """Handle key press event"""
        try:
            current_time = time.time()
            key_str = self._key_to_string(key)
            
            # Track pressed keys
            self.pressed_keys.add(key_str)
            
            # Update modifiers
            if self._is_modifier_key(key):
                self.current_modifiers.add(key_str)
            
            # Create key event
            event = KeyEvent(
                key=key_str,
                event_type='press',
                timestamp=current_time,
                modifiers=list(self.current_modifiers),
                is_special=self._is_special_key(key),
                char=self._get_char(key)
            )
            
            # Add to queue for processing
            self.event_queue.put(event)
            
            # Check for hotkeys
            self._check_hotkeys()
            
            # Update statistics
            self.total_keystrokes += 1
            self.last_key_time = current_time
            
        except Exception as e:
            gui_logger.warn(f" Key press handling error: {e}")
    
    def _on_key_release(self, key):
        """Handle key release event"""
        try:
            current_time = time.time()
            key_str = self._key_to_string(key)
            
            # Remove from pressed keys
            self.pressed_keys.discard(key_str)
            
            # Update modifiers
            if self._is_modifier_key(key):
                self.current_modifiers.discard(key_str)
            
            # Create key event
            event = KeyEvent(
                key=key_str,
                event_type='release',
                timestamp=current_time,
                modifiers=list(self.current_modifiers),
                is_special=self._is_special_key(key),
                char=self._get_char(key)
            )
            
            # Add to queue for processing
            self.event_queue.put(event)
            
        except Exception as e:
            gui_logger.warn(f" Key release handling error: {e}")
    
    def _process_events(self):
        """Process keyboard events in separate thread"""
        while self.is_capturing:
            try:
                # Get event from queue
                event = self.event_queue.get(timeout=1.0)
                
                # Store event
                if self.config.enable_logging:
                    with self.events_lock:
                        self.key_events.append(event)
                
                # Process typing analysis
                if self.config.enable_typing_analysis and event.event_type == 'press':
                    self._analyze_typing(event)
                
                # Trigger callbacks
                if event.event_type == 'press' and self.on_key_press:
                    self.on_key_press(event)
                elif event.event_type == 'release' and self.on_key_release:
                    self.on_key_release(event)
                
            except queue.Empty:
                continue
            except Exception as e:
                gui_logger.warn(f" Event processing error: {e}")
    
    def _key_to_string(self, key) -> str:
        """Convert key to string representation"""
        try:
            if hasattr(key, 'char') and key.char:
                return key.char
            elif hasattr(key, 'name'):
                return key.name
            else:
                return str(key)
        except:
            return 'unknown'
    
    def _is_modifier_key(self, key) -> bool:
        """Check if key is a modifier"""
        modifiers = {Key.ctrl, Key.ctrl_l, Key.ctrl_r, Key.alt, Key.alt_l, Key.alt_r, 
                    Key.shift, Key.shift_l, Key.shift_r, Key.cmd, Key.cmd_l, Key.cmd_r}
        return key in modifiers
    
    def _is_special_key(self, key) -> bool:
        """Check if key is a special key"""
        return not (hasattr(key, 'char') and key.char and key.char.isprintable())
    
    def _get_char(self, key) -> Optional[str]:
        """Get character representation of key"""
        try:
            if hasattr(key, 'char') and key.char:
                return key.char if not self.config.privacy_mode else '*'
            return None
        except:
            return None
    
    def _check_hotkeys(self):
        """Check if current key combination matches any hotkeys"""
        try:
            current_combo = frozenset(self.pressed_keys)
            
            # Check registered hotkey combinations
            for combo, callback in self.hotkey_combinations.items():
                if combo.issubset(current_combo):
                    try:
                        callback()
                        if self.on_hotkey_triggered:
                            self.on_hotkey_triggered('+'.join(sorted(combo)))
                    except Exception as e:
                        gui_logger.warn(f" Hotkey callback error: {e}")
                        
        except Exception as e:
            gui_logger.warn(f" Hotkey check error: {e}")
    
    def _analyze_typing(self, event: KeyEvent):
        """Analyze typing patterns"""
        try:
            if not event.char:
                # Handle special keys
                if event.key in ['space', 'enter', 'tab']:
                    if self.current_word:
                        self._complete_word()
                elif event.key == 'backspace':
                    if self.current_word:
                        self.current_word = self.current_word[:-1]
                return
            
            # Add character to current word
            if event.char.isalnum() or event.char in "'-":
                self.current_word += event.char
                
                # Start new typing session if needed
                if not self.current_session:
                    self._start_typing_session()
            else:
                # Complete current word on punctuation
                if self.current_word:
                    self._complete_word()
                    
        except Exception as e:
            gui_logger.warn(f" Typing analysis error: {e}")
    
    def _start_typing_session(self):
        """Start new typing session"""
        self.current_session = {
            'start_time': time.time(),
            'keystrokes': 0,
            'words': 0,
            'characters': 0
        }
    
    def _complete_word(self):
        """Complete current word"""
        if self.current_word and len(self.current_word) > 1:
            self.words_typed.append({
                'word': self.current_word if not self.config.privacy_mode else '*' * len(self.current_word),
                'timestamp': time.time(),
                'length': len(self.current_word)
            })
            
            # Update session stats
            if self.current_session:
                self.current_session['words'] += 1
                self.current_session['characters'] += len(self.current_word)
            
            # Trigger callback
            if self.on_word_completed:
                word = self.current_word if not self.config.privacy_mode else '*' * len(self.current_word)
                self.on_word_completed(word)
        
        self.current_word = ""
    
    def _end_typing_session(self):
        """End current typing session"""
        if self.current_session:
            self.current_session['end_time'] = time.time()
            self.current_session['duration'] = self.current_session['end_time'] - self.current_session['start_time']
            
            # Calculate WPM
            if self.current_session['duration'] > 0:
                minutes = self.current_session['duration'] / 60
                self.current_session['wpm'] = self.current_session['words'] / minutes if minutes > 0 else 0
            
            self.typing_sessions.append(self.current_session)
            
            # Trigger callback
            if self.on_typing_session_end:
                self.on_typing_session_end(self.current_session.copy())
            
            self.current_session = None
    
    def register_hotkey(self, key_combination: str, callback: Callable):
        """Register hotkey combination"""
        try:
            keys = set(key_combination.lower().split('+'))
            self.hotkey_combinations[frozenset(keys)] = callback
        except Exception as e:
            gui_logger.error(f" Failed to register hotkey: {e}")
    
    def unregister_hotkey(self, key_combination: str):
        """Unregister hotkey combination"""
        try:
            keys = frozenset(key_combination.lower().split('+'))
            if keys in self.hotkey_combinations:
                del self.hotkey_combinations[keys]
        except Exception as e:
            gui_logger.error(f" Failed to unregister hotkey: {e}")
    
    def get_statistics(self) -> Dict:
        """Get keyboard capture statistics"""
        current_time = time.time()
        session_duration = current_time - self.session_start_time if self.session_start_time else 0
        
        # Calculate KPM (keys per minute)
        if session_duration > 0:
            self.keys_per_minute = (self.total_keystrokes / session_duration) * 60
        
        return {
            'total_keystrokes': self.total_keystrokes,
            'keys_per_minute': self.keys_per_minute,
            'session_duration': session_duration,
            'words_typed': len(self.words_typed),
            'typing_sessions': len(self.typing_sessions),
            'hotkeys_registered': len(self.hotkey_combinations),
            'events_logged': len(self.key_events),
            'is_capturing': self.is_capturing,
            'privacy_mode': self.config.privacy_mode
        }
    
    def get_recent_events(self, count: int = 10) -> List[KeyEvent]:
        """Get recent keyboard events"""
        with self.events_lock:
            return list(self.key_events)[-count:]
    
    def _save_log(self):
        """Save keyboard log to file"""
        try:
            if not self.config.save_to_file:
                return
            
            log_data = {
                'events': [asdict(event) for event in self.key_events],
                'statistics': self.get_statistics(),
                'typing_sessions': self.typing_sessions,
                'words_typed': self.words_typed[-100:],  # Last 100 words
                'timestamp': time.time()
            }
            
            with open(self.config.log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            
        except Exception as e:
            gui_logger.error(f" Failed to save keyboard log: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_capture()
        
        # Clear data
        self.key_events.clear()
        self.words_typed.clear()
        self.typing_sessions.clear()
        


# Test function
def test_keyboard_capture():
    """Test keyboard capture functionality"""
    
    if not PYNPUT_AVAILABLE:
        gui_logger.error(" pynput not available for testing")
        return
    
    try:
        config = KeyboardConfig(privacy_mode=True, save_to_file=False)
        capture = KeyboardCapture(config)
        
        # Set up callbacks
        def on_key_press(event):
        
        def on_hotkey(combo):
        
        capture.on_key_press = on_key_press
        capture.on_hotkey_triggered = on_hotkey
        
        # Register test hotkey
        
        # Start capture
        if capture.start_capture():
            
            time.sleep(10)
            
            # Get statistics
            stats = capture.get_statistics()
            
            capture.cleanup()
            gui_logger.info(" Keyboard capture test completed", {"status": "success"})
        else:
            gui_logger.error(" Failed to start keyboard capture")
            
    except Exception as e:
        gui_logger.error(f" Keyboard capture test failed: {e}")


if __name__ == "__main__":
    test_keyboard_capture()
