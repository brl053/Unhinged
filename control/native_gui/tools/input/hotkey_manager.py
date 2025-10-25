
import logging; gui_logger = logging.getLogger(__name__)

"""
Advanced Hotkey Manager for Global Shortcuts and Key Sequences
Provides sophisticated hotkey registration, conflict detection, and sequence support.
"""

import time
import threading
from typing import Dict, List, Callable, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path


class HotkeyType(Enum):
    """Types of hotkey combinations"""
    SIMPLE = "simple"           # Single key combination (Ctrl+C)
    SEQUENCE = "sequence"       # Key sequence (Ctrl+K, Ctrl+C)
    CHORD = "chord"            # Multiple keys pressed simultaneously
    CONTEXTUAL = "contextual"   # Context-dependent hotkeys


@dataclass
class HotkeyDefinition:
    """Definition of a hotkey"""
    name: str
    keys: str
    callback: Callable
    description: str = ""
    hotkey_type: HotkeyType = HotkeyType.SIMPLE
    context: Optional[str] = None
    enabled: bool = True
    global_scope: bool = True
    priority: int = 0


class HotkeyManager:
    """Advanced hotkey management system"""
    
    def __init__(self):
        # Hotkey storage
        self.hotkeys: Dict[str, HotkeyDefinition] = {}
        self.key_combinations: Dict[frozenset, HotkeyDefinition] = {}
        self.sequences: Dict[str, HotkeyDefinition] = {}
        
        # State tracking
        self.pressed_keys: Set[str] = set()
        self.current_sequence: List[str] = []
        self.sequence_start_time = 0
        self.sequence_timeout = 2.0
        
        # Context management
        self.current_context = "global"
        self.context_stack: List[str] = ["global"]
        
        # Conflict detection
        self.conflicts: Dict[str, List[str]] = {}
        
        # Statistics
        self.hotkey_usage: Dict[str, int] = {}
        self.last_triggered: Dict[str, float] = {}
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Built-in hotkeys
        self._register_builtin_hotkeys()
        
    
    def register_hotkey(self, name: str, keys: str, callback: Callable, 
                       description: str = "", hotkey_type: HotkeyType = HotkeyType.SIMPLE,
                       context: str = "global", priority: int = 0) -> bool:
                           pass
        """Register a new hotkey"""
        try:
            with self.lock:
                # Check for conflicts
                if self._has_conflict(keys, context):
                    gui_logger.warn(f" Hotkey conflict detected for '{keys}' in context '{context}'")
                    return False
                
                # Create hotkey definition
                hotkey_def = HotkeyDefinition(
                    name=name,
                    keys=keys,
                    callback=callback,
                    description=description,
                    hotkey_type=hotkey_type,
                    context=context,
                    priority=priority
                )
                
                # Store hotkey
                self.hotkeys[name] = hotkey_def
                
                # Parse and store key combination
                if hotkey_type == HotkeyType.SIMPLE:
                    key_set = self._parse_key_combination(keys)
                    if key_set:
                        self.key_combinations[key_set] = hotkey_def
                elif hotkey_type == HotkeyType.SEQUENCE:
                    self.sequences[keys] = hotkey_def
                
                # Initialize usage tracking
                self.hotkey_usage[name] = 0
                
                return True
                
        except Exception as e:
            gui_logger.error(f" Failed to register hotkey '{name}': {e}")
            return False
    
    def unregister_hotkey(self, name: str) -> bool:
        """Unregister a hotkey"""
        try:
            with self.lock:
                if name not in self.hotkeys:
                    gui_logger.warn(f" Hotkey '{name}' not found")
                    return False
                
                hotkey_def = self.hotkeys[name]
                
                # Remove from appropriate storage
                if hotkey_def.hotkey_type == HotkeyType.SIMPLE:
                    key_set = self._parse_key_combination(hotkey_def.keys)
                    if key_set and key_set in self.key_combinations:
                        del self.key_combinations[key_set]
                elif hotkey_def.hotkey_type == HotkeyType.SEQUENCE:
                    if hotkey_def.keys in self.sequences:
                        del self.sequences[hotkey_def.keys]
                
                # Remove from main storage
                del self.hotkeys[name]
                
                # Clean up tracking data
                self.hotkey_usage.pop(name, None)
                self.last_triggered.pop(name, None)
                
                return True
                
        except Exception as e:
            gui_logger.error(f" Failed to unregister hotkey '{name}': {e}")
            return False
    
    def _parse_key_combination(self, keys: str) -> Optional[frozenset]:
        """Parse key combination string into set"""
        try:
            # Normalize key names
            key_parts = [key.strip().lower() for key in keys.split('+')]
            
            # Map common key aliases
            key_mapping = {
                'ctrl': 'control',
                'cmd': 'command',
                'win': 'windows',
                'alt': 'alt',
                'shift': 'shift',
                'meta': 'command'
            }
            
            normalized_keys = []
            for key in key_parts:
                normalized_keys.append(key_mapping.get(key, key))
            
            return frozenset(normalized_keys)
            
        except Exception as e:
            gui_logger.warn(f" Failed to parse key combination '{keys}': {e}")
            return None
    
    def _has_conflict(self, keys: str, context: str) -> bool:
        """Check if hotkey conflicts with existing ones"""
        key_set = self._parse_key_combination(keys)
        if not key_set:
            return False
        
        # Check for exact matches in same context
        for existing_key_set, hotkey_def in self.key_combinations.items():
            if (key_set == existing_key_set and 
                (hotkey_def.context == context or 
                 hotkey_def.context == "global" or 
                 context == "global")):
                     pass
                return True
        
        return False
    
    def check_hotkey_trigger(self, pressed_keys: Set[str]) -> Optional[str]:
        """Check if current pressed keys match any hotkey"""
        try:
            with self.lock:
                self.pressed_keys = pressed_keys
                
                # Check simple hotkeys
                for key_set, hotkey_def in self.key_combinations.items():
                    if (hotkey_def.enabled and 
                        self._context_matches(hotkey_def.context) and
                        key_set.issubset(pressed_keys)):
                        
                        # Trigger hotkey
                        return self._trigger_hotkey(hotkey_def)
                
                return None
                
        except Exception as e:
            gui_logger.warn(f" Error checking hotkey trigger: {e}")
            return None
    
    def process_key_sequence(self, key: str) -> Optional[str]:
        """Process key for sequence hotkeys"""
        try:
            current_time = time.time()
            
            # Check sequence timeout
            if (self.current_sequence and 
                current_time - self.sequence_start_time > self.sequence_timeout):
                    pass
                self.current_sequence.clear()
            
            # Add key to sequence
            if not self.current_sequence:
                self.sequence_start_time = current_time
            
            self.current_sequence.append(key)
            
            # Check for sequence matches
            sequence_str = ', '.join(self.current_sequence)
            
            for seq_keys, hotkey_def in self.sequences.items():
                if (hotkey_def.enabled and 
                    self._context_matches(hotkey_def.context) and
                    seq_keys.startswith(sequence_str)):
                    
                    if seq_keys == sequence_str:
                        # Complete match
                        self.current_sequence.clear()
                        return self._trigger_hotkey(hotkey_def)
                    else:
                        # Partial match, continue sequence
                        return None
            
            # No matches, clear sequence
            self.current_sequence.clear()
            return None
            
        except Exception as e:
            gui_logger.warn(f" Error processing key sequence: {e}")
            return None
    
    def _context_matches(self, hotkey_context: str) -> bool:
        """Check if hotkey context matches current context"""
        return (hotkey_context == "global" or 
                hotkey_context == self.current_context or
                hotkey_context in self.context_stack)
    
    def _trigger_hotkey(self, hotkey_def: HotkeyDefinition) -> str:
        """Trigger a hotkey callback"""
        try:
            # Update statistics
            self.hotkey_usage[hotkey_def.name] += 1
            self.last_triggered[hotkey_def.name] = time.time()
            
            # Call callback
            hotkey_def.callback()
            
            return hotkey_def.name
            
        except Exception as e:
            gui_logger.error(f" Error triggering hotkey '{hotkey_def.name}': {e}")
            return hotkey_def.name
    
    def set_context(self, context: str):
        """Set current hotkey context"""
        self.current_context = context
    
    def push_context(self, context: str):
        """Push context onto stack"""
        self.context_stack.append(context)
        self.current_context = context
    
    def pop_context(self) -> Optional[str]:
        """Pop context from stack"""
        if len(self.context_stack) > 1:
            popped = self.context_stack.pop()
            self.current_context = self.context_stack[-1]
            return popped
        return None
    
    def enable_hotkey(self, name: str):
        """Enable a hotkey"""
        if name in self.hotkeys:
            self.hotkeys[name].enabled = True
    
    def disable_hotkey(self, name: str):
        """Disable a hotkey"""
        if name in self.hotkeys:
            self.hotkeys[name].enabled = False
    
    def get_hotkey_list(self, context: str = None) -> List[Dict]:
        """Get list of registered hotkeys"""
        hotkey_list = []
        
        for name, hotkey_def in self.hotkeys.items():
            if context is None or hotkey_def.context == context:
                hotkey_info = {
                    'name': name,
                    'keys': hotkey_def.keys,
                    'description': hotkey_def.description,
                    'type': hotkey_def.hotkey_type.value,
                    'context': hotkey_def.context,
                    'enabled': hotkey_def.enabled,
                    'usage_count': self.hotkey_usage.get(name, 0),
                    'last_used': self.last_triggered.get(name, 0)
                }
                hotkey_list.append(hotkey_info)
        
        return sorted(hotkey_list, key=lambda x: x['usage_count'], reverse=True)
    
    def get_statistics(self) -> Dict:
        """Get hotkey usage statistics"""
        total_usage = sum(self.hotkey_usage.values())
        
        return {
            'total_hotkeys': len(self.hotkeys),
            'enabled_hotkeys': sum(1 for h in self.hotkeys.values() if h.enabled),
            'total_triggers': total_usage,
            'current_context': self.current_context,
            'context_stack': self.context_stack.copy(),
            'most_used': max(self.hotkey_usage.items(), key=lambda x: x[1]) if self.hotkey_usage else None,
            'conflicts': len(self.conflicts)
        }
    
    def _register_builtin_hotkeys(self):
        """Register built-in system hotkeys"""
        try:
            # Help hotkey
            self.register_hotkey(
                "show_help",
                "ctrl+shift+h",
                "Show hotkey help",
                context="global"
            )
            
            # Context switching
            self.register_hotkey(
                "toggle_context",
                "ctrl+shift+c",
                lambda: self._toggle_context(),
                "Toggle hotkey context",
                context="global"
            )
            
        except Exception as e:
            gui_logger.warn(f" Failed to register built-in hotkeys: {e}")
    
    def _toggle_context(self):
        """Toggle between global and application context"""
        if self.current_context == "global":
            self.set_context("application")
        else:
            self.set_context("global")
    
    def export_hotkeys(self, filename: str):
        """Export hotkey configuration to file"""
        try:
            export_data = {
                'hotkeys': [],
                'statistics': self.get_statistics(),
                'timestamp': time.time()
            }
            
            for name, hotkey_def in self.hotkeys.items():
                hotkey_data = {
                    'name': name,
                    'keys': hotkey_def.keys,
                    'description': hotkey_def.description,
                    'type': hotkey_def.hotkey_type.value,
                    'context': hotkey_def.context,
                    'enabled': hotkey_def.enabled,
                    'priority': hotkey_def.priority
                }
                export_data['hotkeys'].append(hotkey_data)
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            
        except Exception as e:
            gui_logger.error(f" Failed to export hotkeys: {e}")
    
    def import_hotkeys(self, filename: str, callback_map: Dict[str, Callable]):
        """Import hotkey configuration from file"""
        try:
            with open(filename, 'r') as f:
                import_data = json.load(f)
            
            for hotkey_data in import_data.get('hotkeys', []):
                name = hotkey_data['name']
                
                # Skip if no callback provided
                if name not in callback_map:
                    gui_logger.warn(f" No callback for hotkey '{name}', skipping")
                    continue
                
                self.register_hotkey(
                    name=name,
                    keys=hotkey_data['keys'],
                    callback=callback_map[name],
                    description=hotkey_data.get('description', ''),
                    hotkey_type=HotkeyType(hotkey_data.get('type', 'simple')),
                    context=hotkey_data.get('context', 'global'),
                    priority=hotkey_data.get('priority', 0)
                )
            
            
        except Exception as e:
            gui_logger.error(f" Failed to import hotkeys: {e}")


# Test function
def test_hotkey_manager():
    """Test hotkey manager functionality"""
    
    try:
        manager = HotkeyManager()
        
        # Register test hotkeys
        manager.register_hotkey(
            "test_simple",
            "ctrl+t",
            "Test simple hotkey"
        )
        
        manager.register_hotkey(
            "test_sequence",
            "ctrl+k, ctrl+c",
            "Test sequence hotkey",
            hotkey_type=HotkeyType.SEQUENCE
        )
        
        # Test hotkey triggering
        pressed_keys = {"ctrl", "t"}
        triggered = manager.check_hotkey_trigger(pressed_keys)
        
        # Test sequence
        manager.process_key_sequence("ctrl+k")
        manager.process_key_sequence("ctrl+c")
        
        # Get statistics
        stats = manager.get_statistics()
        
        # Get hotkey list
        hotkeys = manager.get_hotkey_list()
        
        gui_logger.info(" Hotkey manager test completed", {"status": "success"})
        
    except Exception as e:
        gui_logger.error(f" Hotkey manager test failed: {e}")


if __name__ == "__main__":
    test_hotkey_manager()
