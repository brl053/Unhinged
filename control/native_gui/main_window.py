"""
🎛️ Control Center Main Window - Multi-Tool Interface

Pure GTK4 implementation of the Unhinged Control Center.
Tabbed interface for multiple tools: API Dev, System Monitor, Logs, etc.

No WebKit. No JavaScript. No HTML/CSS. Pure native widgets.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from pathlib import Path

from .core.tool_manager import ToolManager, BaseTool


class ControlCenterWindow(Gtk.ApplicationWindow):
    """
    Main Control Center window with tabbed tool interface.

    Layout:
    ┌─────────────────────────────────────────────────────────┐
    │ 🎛️ Unhinged Control Center                    [_][□][×] │
    ├─────────────────────────────────────────────────────────┤
    │ [🔧 API] [🏥 Health] [📋 Logs] [🚀 Services] [📁 Files] │
    ├─────────────────────────────────────────────────────────┤
    │                                                         │
    │  Current Tool Content Area                              │
    │  ┌─────────────────────────────────────────────────┐   │
    │  │                                                 │   │
    │  │  Tool-specific interface loads here             │   │
    │  │  (API Dev Tool, System Monitor, etc.)           │   │
    │  │                                                 │   │
    │  └─────────────────────────────────────────────────┘   │
    │                                                         │
    ├─────────────────────────────────────────────────────────┤
    │ Status: Ready | Tools: 5 loaded | Independence: ✅ Max  │
    └─────────────────────────────────────────────────────────┘
    """
    
    def __init__(self, application, project_root, tool_manager):
        super().__init__(
            application=application,
            title="🎛️ Unhinged Control Center",
            default_width=1600,
            default_height=1000
        )

        self.project_root = project_root
        self.tool_manager = tool_manager

        # Current tool state
        self.current_tool = None
        self.tool_widgets = {}  # Cache tool widgets

        # Build UI
        self._setup_header_bar()
        self._setup_main_layout()
        self._setup_status_bar()
        self._load_tools()

        # Apply CSS class for theming
        self.add_css_class("control-center-window")

        print("✅ Control Center window initialized")
    
    def _setup_header_bar(self):
        """Create and configure the header bar"""
        self.header_bar = Gtk.HeaderBar()
        self.set_titlebar(self.header_bar)

        # Title with icon
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        title_label = Gtk.Label(label="🎛️ Control Center")
        title_label.add_css_class("title")
        title_box.append(title_label)

        self.header_bar.set_title_widget(title_box)

        # Left side: Tool actions (populated by active tool)
        self.tool_actions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.header_bar.pack_start(self.tool_actions_box)

        # Right side: Global actions
        settings_button = Gtk.Button()
        settings_button.set_icon_name("preferences-system-symbolic")
        settings_button.set_tooltip_text("Settings")
        settings_button.connect("clicked", self._on_settings_clicked)
        self.header_bar.pack_end(settings_button)

        about_button = Gtk.Button()
        about_button.set_icon_name("help-about-symbolic")
        about_button.set_tooltip_text("About")
        about_button.connect("clicked", self._on_about_clicked)
        self.header_bar.pack_end(about_button)
    
    def _setup_main_layout(self):
        """Create the main tabbed layout"""
        # Main vertical box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Tool tabs bar
        self.tabs_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        self.tabs_box.add_css_class("tool-tabs")
        self.tabs_box.set_margin_start(16)
        self.tabs_box.set_margin_end(16)
        self.tabs_box.set_margin_top(8)
        main_box.append(self.tabs_box)

        # Tool content area
        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.content_stack.set_transition_duration(200)
        self.content_stack.add_css_class("tool-content")
        self.content_stack.set_vexpand(True)
        main_box.append(self.content_stack)

        # Status bar will be added in _setup_status_bar

        # Set as window content
        self.set_child(main_box)
    
    def _setup_status_bar(self):
        """Create the status bar"""
        self.status_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self.status_bar.add_css_class("status-bar")
        self.status_bar.set_margin_start(16)
        self.status_bar.set_margin_end(16)
        self.status_bar.set_margin_top(8)
        self.status_bar.set_margin_bottom(8)

        # Status label
        self.status_label = Gtk.Label(label="Status: Ready")
        self.status_bar.append(self.status_label)

        # Spacer
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        self.status_bar.append(spacer)

        # Tool count
        self.tool_count_label = Gtk.Label(label="Tools: 0 loaded")
        self.status_bar.append(self.tool_count_label)

        # Independence indicator
        independence_label = Gtk.Label(label="Independence: ✅ Maximum")
        independence_label.add_css_class("status-success")
        self.status_bar.append(independence_label)

        # Add status bar to main layout
        main_box = self.get_child()
        main_box.append(self.status_bar)
    
    def _load_tools(self):
        """Load and create tabs for all registered tools"""
        tools = self.tool_manager.get_tools()

        for i, tool in enumerate(tools):
            self._create_tool_tab(tool, i)

        # Update status
        self.tool_count_label.set_text(f"Tools: {len(tools)} loaded")

        # Activate first tool if available
        if tools:
            self.switch_to_tool(0)

        print(f"✅ Loaded {len(tools)} tools")
    
    def _create_tool_tab(self, tool: BaseTool, index: int):
        """Create a tab for a tool"""
        # Create tab button
        tab_button = Gtk.Button()
        tab_button.set_label(f"{tool.get_icon()} {tool.get_name()}")
        tab_button.add_css_class("tool-tab")
        tab_button.set_tooltip_text(f"{tool.get_description()}\nShortcut: Ctrl+{index+1}")
        tab_button.connect("clicked", self._on_tool_tab_clicked, tool)

        # Add to tabs box
        self.tabs_box.append(tab_button)

        # Store reference
        tool.tab_button = tab_button

        print(f"🔧 Created tab for tool: {tool.get_name()}")
    
    def _on_tool_tab_clicked(self, button, tool: BaseTool):
        """Handle tool tab click"""
        self.switch_to_tool_by_instance(tool)

    def switch_to_tool(self, tool_index: int):
        """Switch to a tool by index"""
        tool = self.tool_manager.get_tool_by_index(tool_index)
        if tool:
            self.switch_to_tool_by_instance(tool)

    def switch_to_tool_by_instance(self, tool: BaseTool):
        """Switch to a specific tool instance"""
        if self.current_tool == tool:
            return  # Already active

        # Deactivate current tool
        if self.current_tool:
            self.current_tool.on_deactivate()
            if hasattr(self.current_tool, 'tab_button'):
                self.current_tool.tab_button.remove_css_class("active")

        # Activate new tool
        self.current_tool = tool
        tool.on_activate()

        # Update tab appearance
        if hasattr(tool, 'tab_button'):
            tool.tab_button.add_css_class("active")

        # Get or create tool widget
        if tool.get_name() not in self.tool_widgets:
            print(f"🔧 Creating widget for tool: {tool.get_name()}")
            widget = tool.create_widget()
            self.tool_widgets[tool.get_name()] = widget
            self.content_stack.add_named(widget, tool.get_name())

        # Switch to tool content
        self.content_stack.set_visible_child_name(tool.get_name())

        # Update header actions
        self._update_tool_actions(tool)

        # Update status
        self.status_label.set_text(f"Status: {tool.get_name()} active")

        print(f"🎯 Switched to tool: {tool.get_name()}")
    
    def _update_tool_actions(self, tool: BaseTool):
        """Update header actions for the current tool"""
        # Clear existing actions
        child = self.tool_actions_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.tool_actions_box.remove(child)
            child = next_child

        # Add tool-specific actions
        # This is where tools can add their own header buttons
        # For now, we'll add some common actions

        if hasattr(tool, 'get_actions'):
            actions = tool.get_actions()
            for action in actions:
                button = Gtk.Button(label=action['label'])
                if 'css_class' in action:
                    button.add_css_class(action['css_class'])
                if 'callback' in action:
                    button.connect("clicked", action['callback'])
                self.tool_actions_box.append(button)

    def _on_settings_clicked(self, button):
        """Handle settings button click"""
        print("⚙️ Opening settings...")
        # TODO: Implement settings dialog

    def _on_about_clicked(self, button):
        """Handle about button click"""
        print("ℹ️ Opening about dialog...")
        # TODO: Implement about dialog

        # For now, show a simple message
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="🎛️ Unhinged Control Center"
        )
        dialog.format_secondary_text(
            "Native GTK application for managing the Unhinged ecosystem.\n\n"
            "🔥 FUCK WEBKIT - GOING NATIVE!\n"
            "💡 CULTURE: We are independent. We render natively. We depend on nothing.\n\n"
            "Built with pure GTK4 and maximum independence."
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()
