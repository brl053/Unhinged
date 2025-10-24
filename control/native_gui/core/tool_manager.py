"""
@llm-type control-system
@llm-legend tool_manager.py - system control component
@llm-key Core functionality for tool_manager
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token tool_manager: system control component
"""
"""
🔧 Tool Manager - Plugin System

Manages tool registration, lifecycle, and communication.
Provides a plugin architecture for adding new tools to the application.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import importlib
import inspect


class BaseTool:
    """
    Base class for all tools in the Unhinged Control Center.
    
    Each tool must inherit from this class and implement the required methods.
    """
    
    def __init__(self):
        self.name = "Base Tool"
        self.icon = "🔧"
        self.description = "Base tool description"
        self.shortcut = None  # e.g., "Ctrl+1"
        self.widget = None
        self.active = False
    
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
    
    def create_widget(self):
        """
        Create and return the main widget for this tool.
        
        This method must be implemented by each tool.
        Should return a Gtk.Widget that represents the tool's interface.
        """
        raise NotImplementedError("Tools must implement create_widget()")
    
    def on_activate(self):
        """
        Called when the tool becomes active (selected).
        
        Override this method to perform any setup when the tool is shown.
        """
        self.active = True
        print(f"🔧 Activated tool: {self.name}")
    
    def on_deactivate(self):
        """
        Called when the tool becomes inactive (another tool selected).
        
        Override this method to perform any cleanup when the tool is hidden.
        """
        self.active = False
        print(f"🔧 Deactivated tool: {self.name}")
    
    def on_destroy(self):
        """
        Called when the tool is being destroyed.
        
        Override this method to perform any final cleanup.
        """
        print(f"🔧 Destroying tool: {self.name}")
    
    def is_active(self) -> bool:
        """Check if the tool is currently active"""
        return self.active
    
    def get_widget(self):
        """Get the tool's widget (creates if not exists)"""
        if self.widget is None:
            self.widget = self.create_widget()
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
        
        print("🔧 Tool manager initialized")
    
    def register_tool(self, tool: BaseTool):
        """Register a new tool"""
        if not isinstance(tool, BaseTool):
            raise ValueError(f"Tool must inherit from BaseTool: {type(tool)}")
        
        # Check for duplicate names
        for existing_tool in self.tools:
            if existing_tool.get_name() == tool.get_name():
                print(f"⚠️ Tool with name '{tool.get_name()}' already registered")
                return False
        
        self.tools.append(tool)
        print(f"✅ Registered tool: {tool.get_name()} {tool.get_icon()}")
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
                print(f"🗑️ Unregistered tool: {tool_name}")
                return True
        
        print(f"❌ Tool not found: {tool_name}")
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
            print(f"❌ Tool not registered: {tool.get_name()}")
            return False
        
        # Deactivate current tool
        if self.active_tool:
            self.active_tool.on_deactivate()
        
        # Activate new tool
        self.active_tool = tool
        tool.on_activate()
        
        print(f"🎯 Activated tool: {tool.get_name()}")
        return True
    
    def activate_tool_by_name(self, tool_name: str) -> bool:
        """Activate a tool by name"""
        tool = self.get_tool(tool_name)
        if tool:
            return self.activate_tool(tool)
        
        print(f"❌ Tool not found: {tool_name}")
        return False
    
    def activate_tool_by_index(self, index: int) -> bool:
        """Activate a tool by index"""
        tool = self.get_tool_by_index(index)
        if tool:
            return self.activate_tool(tool)
        
        print(f"❌ Tool index out of range: {index}")
        return False
    
    def deactivate_tool(self):
        """Deactivate the current tool"""
        if self.active_tool:
            self.active_tool.on_deactivate()
            self.active_tool = None
            print("🔧 Deactivated current tool")
    
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
            print(f"⚠️ Tools directory not found: {tools_directory}")
            return
        
        print(f"🔍 Auto-discovering tools in: {tools_directory}")
        
        for tool_dir in tools_directory.iterdir():
            if tool_dir.is_dir() and (tool_dir / "tool.py").exists():
                try:
                    self._load_tool_from_directory(tool_dir)
                except Exception as e:
                    print(f"❌ Failed to load tool from {tool_dir}: {e}")
    
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
                print(f"⚠️ No BaseTool subclass found in {tool_module_path}")
                
        except ImportError as e:
            print(f"❌ Failed to import {tool_module_path}: {e}")
    
    def destroy_all_tools(self):
        """Destroy all registered tools"""
        for tool in self.tools:
            tool.on_destroy()
        
        self.tools.clear()
        self.active_tool = None
        print("🗑️ Destroyed all tools")
