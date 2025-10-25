
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "libs" / "event-framework" / "python" / "src"))

try:
    from unhinged_events import create_gui_logger
    # Initialize GUI event logger
    gui_logger = create_gui_logger("unhinged-tool-manager", "1.0.0")
except ImportError:
    # Fallback to basic logging if event framework not available
    import logging
    gui_logger = logging.getLogger("unhinged-tool-manager")

"""
@llm-type control-system
@llm-legend tool_manager.py - Enhanced tool management with mobile-responsive capabilities
@llm-key Core functionality for tool lifecycle, registration, and mobile UI integration
@llm-map Central component in Unhinged tool architecture, bridges desktop and mobile interfaces
@llm-axiom Tools must support both desktop and mobile viewports while maintaining native GTK performance
@llm-contract Provides standardized BaseTool interface with mobile-responsive widget creation
@llm-token tool_manager: Enhanced tool management system with mobile-first responsive design
"""
"""
🔧 Tool Manager - Plugin System

Manages tool registration, lifecycle, and communication.
Provides a plugin architecture for adding new tools to the application.
"""

from typing import Dict, List, Optional, Any, Callable, Type
from pathlib import Path
import importlib
import inspect
from enum import Enum
from unhinged_events import create_gui_logger

# Import mobile UI framework
try:
    from ..ui.responsive_layout import ResponsiveLayout, ScreenSize, Orientation
    from ..ui.components import ComponentVariant
    MOBILE_UI_AVAILABLE = True
except ImportError:
    gui_logger.warn(" Mobile UI framework not available")
    MOBILE_UI_AVAILABLE = False

# Import tool configuration system
try:
    from .tool_config import ToolConfig, ToolMetadata, ToolConfigValidator
    TOOL_CONFIG_AVAILABLE = True
except ImportError:
    gui_logger.warn(" Tool configuration system not available")
    TOOL_CONFIG_AVAILABLE = False


class ToolViewport(Enum):
    """
    @llm-type enum
    @llm-legend Tool viewport types for responsive design
    @llm-key Defines how tools adapt to different screen sizes
    """
    MOBILE = "mobile"      # < 768px - Touch-optimized, single column
    TABLET = "tablet"      # 768-1024px - Hybrid interface
    DESKTOP = "desktop"    # > 1024px - Full feature set


class BaseTool:
    """
    @llm-type base-class
    @llm-legend Enhanced base class for all tools with mobile-responsive capabilities
    @llm-key Provides standardized interface for tool creation with viewport adaptation
    @llm-map Foundation of the tool plugin system, supports both desktop and mobile interfaces
    @llm-axiom Tools must gracefully adapt to different screen sizes while maintaining functionality
    @llm-contract All tools inherit from this class and implement viewport-specific widget creation
    @llm-token BaseTool: Enhanced tool base class with mobile-first responsive design

    Base class for all tools in the Unhinged Control Center.
    Enhanced with mobile-responsive capabilities and viewport adaptation.

    Each tool must inherit from this class and implement the required methods.
    Tools can provide different widgets for different viewports (mobile/tablet/desktop).
    """

    def __init__(self, config: Optional['ToolConfig'] = None):
        # Use ToolConfig if available and provided
        if TOOL_CONFIG_AVAILABLE and config:
            self._apply_config(config)
            self.config = config
            self.metadata = ToolMetadata()
        else:
            # Fallback to manual initialization
            self.name = "Base Tool"
            self.icon = "🔧"
            self.description = "Base tool description"
            self.shortcut = None
            self.supports_mobile = True
            self.mobile_priority = 0
            self.config = None
            self.metadata = None

        # Common properties
        self.widget = None
        self.active = False
        self.current_viewport = ToolViewport.DESKTOP
        self.viewport_widgets: Dict[ToolViewport, Any] = {}

        # Responsive callbacks
        self.on_viewport_changed: Optional[Callable[[ToolViewport], None]] = None

    def _apply_config(self, config: 'ToolConfig'):
        """Apply tool configuration to instance properties"""
        self.name = config.name
        self.icon = config.icon
        self.description = config.description
        self.shortcut = config.shortcut
        self.supports_mobile = config.supports_mobile
        self.mobile_priority = config.mobile_priority.value if hasattr(config.mobile_priority, 'value') else config.mobile_priority

        # Apply callbacks if provided
        if config.on_activate:
            self.on_activate = config.on_activate
        if config.on_deactivate:
            self.on_deactivate = config.on_deactivate
        if config.on_mobile_mode_changed:
            self.on_mobile_mode_changed = config.on_mobile_mode_changed
    
    def get_name(self) -> str:
        """Get the tool name"""
        return self.name
    
    def get_icon(self) -> str:
        """Get the tool icon (emoji or icon name)"""
        return self.icon
    
    def get_description(self) -> str:
        """Get the tool description"""
        return self.description
    
    def get_shortcut(self) -> Optional[str]:
        """Get the keyboard shortcut for this tool"""
        return self.shortcut
    
    def create_widget(self, viewport: ToolViewport = ToolViewport.DESKTOP):
        """
        @llm-type method
        @llm-legend Create viewport-specific widget for the tool
        @llm-key Enhanced widget creation with responsive design support
        @llm-map Core method for tool widget instantiation with viewport awareness
        @llm-axiom Widgets must adapt to viewport constraints while maintaining functionality
        @llm-contract Returns GTK widget optimized for the specified viewport
        @llm-token create_widget: Enhanced widget creation with mobile-responsive design

        Create and return the tool's widget for the specified viewport.
        Tools can override this to provide viewport-specific implementations.

        Args:
            viewport: Target viewport (mobile/tablet/desktop)

        Returns:
            GTK widget optimized for the viewport
        """
        # Check if we have a cached widget for this viewport
        if viewport in self.viewport_widgets:
            return self.viewport_widgets[viewport]

        # Create viewport-specific widget
        widget = self._create_viewport_widget(viewport)

        # Cache the widget
        if widget:
            self.viewport_widgets[viewport] = widget
            self.current_viewport = viewport

        return widget

    def _create_viewport_widget(self, viewport: ToolViewport):
        """
        @llm-type method
        @llm-legend Internal method for viewport-specific widget creation
        @llm-key Override this method to provide custom viewport implementations

        Create widget for specific viewport. Override in subclasses.
        Default implementation provides basic responsive behavior.
        """
        # Default implementation - tools should override this
        raise NotImplementedError(f"Tool {self.name} must implement _create_viewport_widget()")
    
    def on_activate(self):
        """
        Called when the tool becomes active (selected).
        
        Override this method to perform any setup when the tool is shown.
        """
        self.active = True
    
    def on_deactivate(self):
        """
        Called when the tool becomes inactive (another tool selected).
        
        Override this method to perform any cleanup when the tool is hidden.
        """
        self.active = False
    
    def on_destroy(self):
        """
        Called when the tool is being destroyed.

        Override this method to perform any final cleanup.
        Enhanced to clean up viewport-specific widgets.
        """
        # Clear cached widgets
        self.viewport_widgets.clear()
    
    def is_active(self) -> bool:
        """Check if the tool is currently active"""
        return self.active
    
    def get_mobile_widget(self):
        """Get mobile-optimized widget"""
        return self.create_widget(ToolViewport.MOBILE)

    def get_tablet_widget(self):
        """Get tablet-optimized widget"""
        return self.create_widget(ToolViewport.TABLET)

    def get_desktop_widget(self):
        """Get desktop widget"""
        return self.create_widget(ToolViewport.DESKTOP)

    def set_viewport(self, viewport: ToolViewport):
        """
        @llm-type method
        @llm-legend Update tool's current viewport and trigger adaptation
        @llm-key Handles viewport transitions and widget updates
        """
        if self.current_viewport != viewport:
            old_viewport = self.current_viewport
            self.current_viewport = viewport

            # Trigger viewport change callback
            if self.on_viewport_changed:
                self.on_viewport_changed(viewport)


    def supports_viewport(self, viewport: ToolViewport) -> bool:
        """Check if tool supports the specified viewport"""
        if viewport == ToolViewport.MOBILE:
            return self.supports_mobile
        return True  # All tools support tablet and desktop by default

    def get_widget(self, viewport: ToolViewport = None):
        """
        @llm-type method
        @llm-legend Get tool's widget with optional viewport specification
        @llm-key Enhanced widget retrieval with viewport awareness

        Get the tool's widget (creates if not exists).
        Enhanced to support viewport-specific widgets.
        """
        if viewport is None:
            viewport = self.current_viewport

        if self.widget is None or viewport != self.current_viewport:
            self.widget = self.create_widget(viewport)
        return self.widget


class ToolManager:
    """
    Manages tool registration and lifecycle.
    
    Provides a plugin system for dynamically loading and managing tools.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tools: List[BaseTool] = []
        self.active_tool: Optional[BaseTool] = None
        
        gui_logger.debug(" Tool manager initialized", {"event_type": "configuration"})
    
    def register_tool(self, tool: BaseTool):
        """Register a new tool"""
        if not isinstance(tool, BaseTool):
            raise ValueError(f"Tool must inherit from BaseTool: {type(tool)}")
        
        # Check for duplicate names
        for existing_tool in self.tools:
            if existing_tool.get_name() == tool.get_name():
                gui_logger.warn(f" Tool with name '{tool.get_name()}' already registered")
                return False
        
        self.tools.append(tool)
        return True
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool by name"""
        for i, tool in enumerate(self.tools):
            if tool.get_name() == tool_name:
                # Deactivate if currently active
                if self.active_tool == tool:
                    self.deactivate_tool()
                
                # Destroy the tool
                tool.on_destroy()
                
                # Remove from list
                self.tools.pop(i)
                return True
        
        gui_logger.error(f" Tool not found: {tool_name}")
        return False
    
    def get_tools(self) -> List[BaseTool]:
        """Get list of all registered tools"""
        return self.tools.copy()
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        for tool in self.tools:
            if tool.get_name() == tool_name:
                return tool
        return None
    
    def get_tool_by_index(self, index: int) -> Optional[BaseTool]:
        """Get a tool by index"""
        if 0 <= index < len(self.tools):
            return self.tools[index]
        return None
    
    def activate_tool(self, tool: BaseTool) -> bool:
        """Activate a specific tool"""
        if tool not in self.tools:
            gui_logger.error(f" Tool not registered: {tool.get_name()}")
            return False
        
        # Deactivate current tool
        if self.active_tool:
            self.active_tool.on_deactivate()
        
        # Activate new tool
        self.active_tool = tool
        tool.on_activate()
        
        return True
    
    def activate_tool_by_name(self, tool_name: str) -> bool:
        """Activate a tool by name"""
        tool = self.get_tool(tool_name)
        if tool:
            return self.activate_tool(tool)
        
        gui_logger.error(f" Tool not found: {tool_name}")
        return False
    
    def activate_tool_by_index(self, index: int) -> bool:
        """Activate a tool by index"""
        tool = self.get_tool_by_index(index)
        if tool:
            return self.activate_tool(tool)
        
        gui_logger.error(f" Tool index out of range: {index}")
        return False
    
    def deactivate_tool(self):
        """Deactivate the current tool"""
        if self.active_tool:
            self.active_tool.on_deactivate()
            self.active_tool = None
            gui_logger.debug(" Deactivated current tool", {"event_type": "configuration"})
    
    def get_active_tool(self) -> Optional[BaseTool]:
        """Get the currently active tool"""
        return self.active_tool
    
    def get_tool_count(self) -> int:
        """Get the number of registered tools"""
        return len(self.tools)
    
    def auto_discover_tools(self, tools_directory: Path):
        """
        Automatically discover and load tools from a directory.
        
        Looks for tool.py files in subdirectories and attempts to load them.
        """
        if not tools_directory.exists():
            gui_logger.warn(f" Tools directory not found: {tools_directory}")
            return
        
        
        for tool_dir in tools_directory.iterdir():
            if tool_dir.is_dir() and (tool_dir / "tool.py").exists():
                try:
                    self._load_tool_from_directory(tool_dir)
                except Exception as e:
                    gui_logger.error(f" Failed to load tool from {tool_dir}: {e}")
    
    def _load_tool_from_directory(self, tool_dir: Path):
        """Load a tool from a directory containing tool.py"""
        tool_module_path = f"control.native_gui.tools.{tool_dir.name}.tool"
        
        try:
            module = importlib.import_module(tool_module_path)
            
            # Find classes that inherit from BaseTool
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseTool) and obj != BaseTool:
                    tool_instance = obj()
                    self.register_tool(tool_instance)
                    break
            else:
                gui_logger.warn(f" No BaseTool subclass found in {tool_module_path}")
                
        except ImportError as e:
            gui_logger.error(f" Failed to import {tool_module_path}: {e}")
    
    def destroy_all_tools(self):
        """Destroy all registered tools"""
        for tool in self.tools:
            tool.on_destroy()
        
        self.tools.clear()
        self.active_tool = None
