"""
GUI Integration for the Event Framework

Provides specialized logging capabilities for GUI components, particularly
the native GTK4 GUI, enabling logging of user interactions, clicks, and GUI events.
"""

import os
import time
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass

from .event_logger import EventLogger, create_service_logger, LogLevel


@dataclass
class GUIEvent:
    """Represents a GUI interaction event"""
    event_type: str  # click, key_press, window_focus, etc.
    widget_id: Optional[str] = None
    widget_type: Optional[str] = None
    widget_label: Optional[str] = None
    coordinates: Optional[tuple] = None  # (x, y) for mouse events
    key_code: Optional[str] = None  # for keyboard events
    modifiers: Optional[list] = None  # Ctrl, Alt, Shift, etc.
    window_title: Optional[str] = None
    tool_name: Optional[str] = None  # Which tool/tab is active
    additional_data: Optional[Dict[str, Any]] = None


class GUIEventLogger:
    """Specialized logger for GUI events and user interactions"""
    
    def __init__(self, app_name: str = "unhinged-gui", version: str = "1.0.0"):
        self.app_name = app_name
        self.logger = create_service_logger(
            service_id=app_name,
            version=version,
            environment=os.getenv("ENVIRONMENT", "development"),
            min_log_level=LogLevel.INFO
        )
        
        # GUI-specific context
        self.session_id = f"gui_session_{int(time.time())}"
        self.current_tool = None
        self.current_window = None
        
        # Add GUI-specific context to logger
        self.logger = self.logger.with_context({
            "component_type": "native_gui",
            "gui_framework": "gtk4",
            "session_id": self.session_id
        })
    
    def log_user_interaction(self, gui_event: GUIEvent, user_id: Optional[str] = None) -> None:
        """Log a user interaction event"""
        metadata = {
            "event_type": "user_interaction",
            "gui_event_type": gui_event.event_type,
            "interaction_timestamp": time.time()
        }
        
        # Add GUI event details
        if gui_event.widget_id:
            metadata["widget_id"] = gui_event.widget_id
        if gui_event.widget_type:
            metadata["widget_type"] = gui_event.widget_type
        if gui_event.widget_label:
            metadata["widget_label"] = gui_event.widget_label
        if gui_event.coordinates:
            metadata["coordinates"] = {"x": gui_event.coordinates[0], "y": gui_event.coordinates[1]}
        if gui_event.key_code:
            metadata["key_code"] = gui_event.key_code
        if gui_event.modifiers:
            metadata["modifiers"] = gui_event.modifiers
        if gui_event.window_title:
            metadata["window_title"] = gui_event.window_title
        if gui_event.tool_name:
            metadata["tool_name"] = gui_event.tool_name
        if gui_event.additional_data:
            metadata["additional_data"] = gui_event.additional_data
        
        # Add user context if available
        if user_id:
            metadata["user_id"] = user_id
        
        # Create contextual logger if we have tool/window info
        contextual_logger = self.logger
        if gui_event.tool_name or gui_event.window_title:
            context = {}
            if gui_event.tool_name:
                context["current_tool"] = gui_event.tool_name
            if gui_event.window_title:
                context["current_window"] = gui_event.window_title
            contextual_logger = self.logger.with_context(context)
        
        # Log the interaction
        message = f"User {gui_event.event_type}"
        if gui_event.widget_label:
            message += f" on '{gui_event.widget_label}'"
        elif gui_event.widget_type:
            message += f" on {gui_event.widget_type}"
        
        contextual_logger.info(message, metadata)
    
    def log_button_click(self, button_label: str, tool_name: Optional[str] = None, 
                        coordinates: Optional[tuple] = None, user_id: Optional[str] = None) -> None:
        """Log a button click event"""
        gui_event = GUIEvent(
            event_type="button_click",
            widget_type="button",
            widget_label=button_label,
            coordinates=coordinates,
            tool_name=tool_name
        )
        self.log_user_interaction(gui_event, user_id)
    
    def log_menu_selection(self, menu_item: str, menu_path: Optional[str] = None,
                          tool_name: Optional[str] = None, user_id: Optional[str] = None) -> None:
        """Log a menu selection event"""
        gui_event = GUIEvent(
            event_type="menu_selection",
            widget_type="menu_item",
            widget_label=menu_item,
            tool_name=tool_name,
            additional_data={"menu_path": menu_path} if menu_path else None
        )
        self.log_user_interaction(gui_event, user_id)
    
    def log_text_input(self, input_length: int, widget_id: Optional[str] = None,
                      tool_name: Optional[str] = None, user_id: Optional[str] = None) -> None:
        """Log text input event (without logging actual content for privacy)"""
        gui_event = GUIEvent(
            event_type="text_input",
            widget_type="text_entry",
            widget_id=widget_id,
            tool_name=tool_name,
            additional_data={"input_length": input_length}
        )
        self.log_user_interaction(gui_event, user_id)
    
    def log_window_event(self, event_type: str, window_title: str, 
                        additional_data: Optional[Dict[str, Any]] = None,
                        user_id: Optional[str] = None) -> None:
        """Log window-level events (focus, minimize, close, etc.)"""
        gui_event = GUIEvent(
            event_type=event_type,
            widget_type="window",
            window_title=window_title,
            additional_data=additional_data
        )
        self.log_user_interaction(gui_event, user_id)
    
    def log_tool_switch(self, from_tool: Optional[str], to_tool: str, 
                       user_id: Optional[str] = None) -> None:
        """Log switching between tools/tabs"""
        gui_event = GUIEvent(
            event_type="tool_switch",
            widget_type="navigation",
            tool_name=to_tool,
            additional_data={"from_tool": from_tool, "to_tool": to_tool}
        )
        self.current_tool = to_tool
        self.log_user_interaction(gui_event, user_id)
    
    def log_keyboard_shortcut(self, shortcut: str, action: str, tool_name: Optional[str] = None,
                             user_id: Optional[str] = None) -> None:
        """Log keyboard shortcut usage"""
        gui_event = GUIEvent(
            event_type="keyboard_shortcut",
            widget_type="shortcut",
            key_code=shortcut,
            tool_name=tool_name,
            additional_data={"action": action}
        )
        self.log_user_interaction(gui_event, user_id)
    
    def log_drag_drop(self, source_type: str, target_type: str, 
                     coordinates: Optional[tuple] = None, tool_name: Optional[str] = None,
                     user_id: Optional[str] = None) -> None:
        """Log drag and drop operations"""
        gui_event = GUIEvent(
            event_type="drag_drop",
            widget_type="drag_drop",
            coordinates=coordinates,
            tool_name=tool_name,
            additional_data={"source_type": source_type, "target_type": target_type}
        )
        self.log_user_interaction(gui_event, user_id)
    
    def log_error(self, error_message: str, error_type: str = "gui_error",
                 tool_name: Optional[str] = None, exception: Optional[Exception] = None) -> None:
        """Log GUI-specific errors"""
        metadata = {
            "error_type": error_type,
            "gui_component": "native_gui"
        }
        
        if tool_name:
            metadata["tool_name"] = tool_name
        
        contextual_logger = self.logger
        if tool_name:
            contextual_logger = self.logger.with_context({"current_tool": tool_name})
        
        contextual_logger.error(error_message, exception=exception, metadata=metadata)
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "ms",
                              tool_name: Optional[str] = None) -> None:
        """Log GUI performance metrics"""
        metadata = {
            "metric_type": "gui_performance",
            "metric_name": metric_name,
            "metric_value": value,
            "metric_unit": unit
        }
        
        if tool_name:
            metadata["tool_name"] = tool_name
        
        contextual_logger = self.logger
        if tool_name:
            contextual_logger = self.logger.with_context({"current_tool": tool_name})
        
        contextual_logger.info(f"Performance metric: {metric_name} = {value}{unit}", metadata)


def create_gui_logger(app_name: str = "unhinged-gui", version: str = "1.0.0") -> GUIEventLogger:
    """Factory function to create a GUI event logger"""
    return GUIEventLogger(app_name, version)


# GTK4-specific integration helpers
def create_gtk_click_handler(gui_logger: GUIEventLogger, button_label: str, 
                           tool_name: Optional[str] = None) -> Callable:
    """Create a GTK button click handler that logs the interaction"""
    def on_button_clicked(button):
        gui_logger.log_button_click(button_label, tool_name)
    return on_button_clicked


def create_gtk_text_changed_handler(gui_logger: GUIEventLogger, widget_id: str,
                                  tool_name: Optional[str] = None) -> Callable:
    """Create a GTK text changed handler that logs input events"""
    def on_text_changed(text_buffer):
        text_length = text_buffer.get_char_count()
        gui_logger.log_text_input(text_length, widget_id, tool_name)
    return on_text_changed
