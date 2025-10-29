#!/usr/bin/env python3
"""
@llm-doc Example Usage of Unhinged GTK4 Component Library
@llm-version 1.0.0
@llm-date 2025-10-27

Demonstrates how to integrate the component library into your existing
GTK4 application. Shows practical usage patterns and best practices.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
import sys
from pathlib import Path

# Add component library to path
sys.path.append(str(Path(__file__).parent))

# Import components
from components import (
    ActionButton, StatusLabel, ProgressIndicator,
    StatusCard, ServicePanel, LogContainer,
    LogViewer, ServiceRow, SystemStatus,
    ChatBubble, LoadingDots, CopyButton
)


class ComponentExampleApp(Adw.Application):
    """Example application demonstrating component usage."""
    
    def __init__(self):
        super().__init__(application_id='com.unhinged.components.example')
        self.window = None
    
    def do_activate(self):
        """Create and show the example window."""
        if not self.window:
            self.window = self.create_window()
        self.window.present()
    
    def create_window(self):
        """Create the main example window."""
        window = Adw.ApplicationWindow(application=self)
        window.set_title("Unhinged Component Library Examples")
        window.set_default_size(900, 700)
        
        # Load component CSS
        self._load_component_css()
        
        # Create main content
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        
        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(main_box)
        
        # Add example sections
        main_box.append(self.create_primitives_section())
        main_box.append(self.create_containers_section())
        main_box.append(self.create_complex_section())
        main_box.append(self.create_new_components_group())
        main_box.append(self.create_integration_section())
        
        window.set_content(scrolled)
        return window
    
    def _load_component_css(self):
        """Load component CSS styling."""
        try:
            css_provider = Gtk.CssProvider()
            css_path = Path(__file__).parent / "components.css"
            
            if css_path.exists():
                css_provider.load_from_path(str(css_path))
                Gtk.StyleContext.add_provider_for_display(
                    self.window.get_display() if self.window else Gtk.Widget.get_default_direction(),
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
                print("✅ Component CSS loaded")
            else:
                print("⚠️  Component CSS not found")
        except Exception as e:
            print(f"❌ Failed to load component CSS: {e}")
    
    def create_primitives_section(self):
        """Create examples of primitive components."""
        group = Adw.PreferencesGroup()
        group.set_title("Primitive Components")
        group.set_description("Basic building blocks")
        
        # Action buttons
        button_row = Adw.ActionRow()
        button_row.set_title("Action Buttons")
        button_row.set_subtitle("Different button styles and states")
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        # Primary button
        primary_btn = ActionButton(
            label="Primary",
            style="primary",
            icon_name="emblem-ok-symbolic"
        )
        primary_btn.connect('clicked', lambda b: print("Primary clicked"))
        button_box.append(primary_btn.get_widget())
        
        # Secondary button
        secondary_btn = ActionButton(
            label="Secondary", 
            style="secondary"
        )
        button_box.append(secondary_btn.get_widget())
        
        # Destructive button
        destructive_btn = ActionButton(
            label="Delete",
            style="destructive",
            icon_name="user-trash-symbolic"
        )
        button_box.append(destructive_btn.get_widget())
        
        # Loading button
        loading_btn = ActionButton(
            label="Loading",
            style="primary"
        )
        loading_btn.set_loading(True)
        button_box.append(loading_btn.get_widget())
        
        button_row.add_suffix(button_box)
        group.add(button_row)
        
        # Status labels
        status_row = Adw.ActionRow()
        status_row.set_title("Status Labels")
        status_row.set_subtitle("Different status types")
        
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        for status in ["success", "warning", "error", "info"]:
            label = StatusLabel(text=status.title(), status=status)
            status_box.append(label.get_widget())
        
        status_row.add_suffix(status_box)
        group.add(status_row)
        
        # Progress indicator
        progress_row = Adw.ActionRow()
        progress_row.set_title("Progress Indicator")
        progress_row.set_subtitle("Progress with percentage")
        
        progress = ProgressIndicator(
            progress=0.65,
            text="Processing...",
            show_percentage=True
        )
        progress_row.add_suffix(progress.get_widget())
        group.add(progress_row)
        
        return group
    
    def create_containers_section(self):
        """Create examples of container components."""
        group = Adw.PreferencesGroup()
        group.set_title("Container Components")
        group.set_description("Layout and grouping components")
        
        # Status card
        status_card = StatusCard(
            title="System Health",
            status="success",
            subtitle="All systems operational",
            description="All services are running normally with no issues detected.",
            icon_name="computer-symbolic"
        )
        
        # Add action button to card
        refresh_btn = ActionButton(
            label="Refresh",
            style="flat",
            icon_name="view-refresh-symbolic"
        )
        status_card.add_action_button(refresh_btn.get_widget())
        
        group.add(status_card.get_widget())
        
        # Service panel
        service_data = {
            "running": True,
            "port": 9092,
            "health_method": "gRPC:9092"
        }
        
        service_panel = ServicePanel(
            service_name="Text-to-Speech Service",
            service_status="running",
            port=service_data["port"],
            health_method=service_data["health_method"]
        )
        
        group.add(service_panel.get_widget())
        
        return group
    
    def create_complex_section(self):
        """Create examples of complex components."""
        group = Adw.PreferencesGroup()
        group.set_title("Complex Components")
        group.set_description("Advanced stateful components")
        
        # Log viewer
        log_viewer = LogViewer()
        
        # Add some sample logs
        log_viewer.append_log("Application started", "INFO", "10:30:15")
        log_viewer.append_log("Service connected", "INFO", "10:30:16")
        log_viewer.append_log("Configuration loaded", "DEBUG", "10:30:17")
        log_viewer.append_log("Warning: High memory usage", "WARNING", "10:30:20")
        log_viewer.append_log("Processing request", "INFO", "10:30:25")
        
        # Set a reasonable height
        log_viewer.get_widget().set_size_request(-1, 200)
        
        group.add(log_viewer.get_widget())
        
        return group
    
    def create_integration_section(self):
        """Show integration with existing app patterns."""
        group = Adw.PreferencesGroup()
        group.set_title("Integration Example")
        group.set_description("How to integrate with your existing app")
        
        # System status component
        system_status = SystemStatus()
        
        # Sample services data (like from your service_launcher.py)
        services_data = {
            "LLM Service (Ollama)": {"running": True, "port": 1500, "health_method": "HTTP:1500"},
            "Text-to-Speech Service": {"running": True, "port": 1102, "health_method": "gRPC:9092"},
            "Vision AI Service": {"running": True, "port": 1103, "health_method": "gRPC:9093"},
            "Database": {"running": True, "port": 1200, "health_method": "container"},
        }
        
        system_status.update_services(services_data)
        group.add(system_status.get_widget())
        
        return group

    def create_new_components_group(self):
        """Create examples of new components: ChatBubble, LoadingDots, CopyButton."""
        group = Adw.PreferencesGroup()
        group.set_title("New Components")
        group.set_description("Chat bubbles, loading animations, and copy-paste functionality")

        # Chat Bubble Examples
        chat_row = Adw.ActionRow()
        chat_row.set_title("Chat Bubbles")
        chat_row.set_subtitle("Message display with sender/receiver alignment")

        chat_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        chat_container.set_margin_top(12)
        chat_container.set_margin_bottom(12)

        # Left-aligned message (received)
        received_bubble = ChatBubble(
            message="Hello! This is a received message with proper alignment and styling.",
            sender="Alice",
            timestamp="2:30 PM",
            alignment="left",
            message_type="default"
        )
        chat_container.append(received_bubble.get_widget())

        # Right-aligned message (sent)
        sent_bubble = ChatBubble(
            message="This is a sent message that appears on the right side.",
            sender="You",
            timestamp="2:31 PM",
            alignment="right",
            message_type="default"
        )
        chat_container.append(sent_bubble.get_widget())

        # System message
        system_bubble = ChatBubble(
            message="Alice joined the conversation",
            timestamp="2:29 PM",
            alignment="left",
            message_type="system"
        )
        chat_container.append(system_bubble.get_widget())

        chat_row.add_suffix(chat_container)
        group.add(chat_row)

        # Loading Dots Examples
        loading_row = Adw.ActionRow()
        loading_row.set_title("Loading Animations")
        loading_row.set_subtitle("Triple dot wave animations with different styles")

        loading_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        loading_container.set_margin_top(12)
        loading_container.set_margin_bottom(12)

        # Normal loading dots
        normal_dots = LoadingDots(size="normal", speed="normal", color="primary")
        normal_dots.start_animation()
        loading_container.append(normal_dots.get_widget())

        # Small fast dots
        small_dots = LoadingDots(size="small", speed="fast", color="secondary")
        small_dots.start_animation()
        loading_container.append(small_dots.get_widget())

        # Large slow dots
        large_dots = LoadingDots(size="large", speed="slow", color="muted")
        large_dots.start_animation()
        loading_container.append(large_dots.get_widget())

        loading_row.add_suffix(loading_container)
        group.add(loading_row)

        # Copy Button Examples
        copy_row = Adw.ActionRow()
        copy_row.set_title("Copy Functionality")
        copy_row.set_subtitle("Generic copy-paste components with different content sources")

        copy_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        copy_container.set_margin_top(12)
        copy_container.set_margin_bottom(12)

        # Static content copy
        static_copy = CopyButton(
            content="This is static content to copy!",
            label="Copy Text",
            style="secondary"
        )
        copy_container.append(static_copy.get_widget())

        # Dynamic content copy
        def get_dynamic_content():
            import datetime
            return f"Generated at {datetime.datetime.now().strftime('%H:%M:%S')}"

        dynamic_copy = CopyButton(
            content_source=get_dynamic_content,
            label="Copy Time",
            style="primary"
        )
        copy_container.append(dynamic_copy.get_widget())

        # Icon-only copy button
        icon_copy = CopyButton(
            content="Secret data: 42",
            label="",
            icon_name="edit-copy-symbolic",
            style="flat"
        )
        copy_container.append(icon_copy.get_widget())

        copy_row.add_suffix(copy_container)
        group.add(copy_row)

        return group


def main():
    """Run the component example application."""
    app = ComponentExampleApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
