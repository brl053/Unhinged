
import logging; gui_logger = logging.getLogger(__name__)

"""
@llm-type control-system
@llm-legend mobile_components.py - system control component
@llm-key Core functionality for mobile_components
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token mobile_components: system control component
"""
"""
📱 Mobile-First Component System

Responsive component hierarchy designed for mobile-first approach.
Replaces traditional desktop tabbed interface with mobile-optimized navigation.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, Gio
from typing import Optional, Dict, List, Callable
from enum import Enum


class NavigationStyle(Enum):
    """Navigation style based on viewport"""
    BOTTOM_TABS = "bottom_tabs"      # Mobile: Bottom navigation
    SIDE_RAIL = "side_rail"          # Tablet: Side navigation rail
    TOP_TABS = "top_tabs"            # Desktop: Traditional top tabs
    DRAWER = "drawer"                # Mobile: Collapsible drawer


class MobileNavigationBar(Gtk.Box):
    """
    Mobile-first bottom navigation bar.
    
    Replaces traditional top tabs with mobile-optimized bottom navigation.
    Supports 3-5 primary navigation items with icons and labels.
    """
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        
        self.add_css_class("mobile-nav-bar")
        self.set_homogeneous(True)
        self.set_size_request(-1, 72)  # Material Design 3 bottom nav height
        
        self.nav_items: Dict[str, Gtk.Button] = {}
        self.active_item: Optional[str] = None
        self.on_item_selected: Optional[Callable[[str], None]] = None
        
    
    def add_nav_item(self, item_id: str, icon: str, label: str, tooltip: str = ""):
        """Add a navigation item to the bottom bar"""
        button = Gtk.Button()
        button.set_has_frame(False)
        button.add_css_class("nav-item")
        
        # Create vertical layout for icon + label
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        content_box.set_halign(Gtk.Align.CENTER)
        content_box.set_valign(Gtk.Align.CENTER)
        
        # Icon
        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class("nav-icon")
        content_box.append(icon_label)
        
        # Label
        text_label = Gtk.Label(label=label)
        text_label.add_css_class("nav-label")
        content_box.append(text_label)
        
        button.set_child(content_box)
        
        if tooltip:
            button.set_tooltip_text(tooltip)
        
        # Connect click handler
        button.connect("clicked", self._on_nav_item_clicked, item_id)
        
        self.nav_items[item_id] = button
        self.append(button)
        
    
    def set_active_item(self, item_id: str):
        """Set the active navigation item"""
        # Remove active class from all items
        for button in self.nav_items.values():
            button.remove_css_class("active")
        
        # Add active class to selected item
        if item_id in self.nav_items:
            self.nav_items[item_id].add_css_class("active")
            self.active_item = item_id
    
    def _on_nav_item_clicked(self, button: Gtk.Button, item_id: str):
        """Handle navigation item click"""
        self.set_active_item(item_id)
        
        if self.on_item_selected:
            self.on_item_selected(item_id)


class ResponsiveContainer(Gtk.Box):
    """
    Responsive container that adapts layout based on viewport size.
    
    - Mobile: Single column, stacked layout
    - Tablet: Two column layout with sidebar
    - Desktop: Multi-column layout with full sidebar
    """
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        self.add_css_class("responsive-container")
        
        # Content areas
        self.header_area: Optional[Gtk.Widget] = None
        self.main_content: Optional[Gtk.Widget] = None
        self.sidebar_content: Optional[Gtk.Widget] = None
        self.footer_area: Optional[Gtk.Widget] = None
        
        # Layout state
        self.current_layout = "mobile"
        
    
    def set_header(self, widget: Gtk.Widget):
        """Set header content"""
        if self.header_area:
            self.remove(self.header_area)
        
        self.header_area = widget
        self.prepend(widget)
    
    def set_main_content(self, widget: Gtk.Widget):
        """Set main content area"""
        self.main_content = widget
        self._rebuild_layout()
    
    def set_sidebar(self, widget: Gtk.Widget):
        """Set sidebar content"""
        self.sidebar_content = widget
        self._rebuild_layout()
    
    def set_footer(self, widget: Gtk.Widget):
        """Set footer content"""
        if self.footer_area:
            self.remove(self.footer_area)
        
        self.footer_area = widget
        self.append(widget)
    
    def adapt_to_viewport(self, width: int, height: int):
        """Adapt layout based on viewport dimensions"""
        if width <= 768:
            new_layout = "mobile"
        elif width <= 1024:
            new_layout = "tablet"
        else:
            new_layout = "desktop"
        
        if new_layout != self.current_layout:
            self.current_layout = new_layout
            self._rebuild_layout()
    
    def _rebuild_layout(self):
        """Rebuild layout based on current viewport"""
        # Remove existing content layout
        children = []
        child = self.get_first_child()
        while child:
            if child != self.header_area and child != self.footer_area:
                children.append(child)
            child = child.get_next_sibling()
        
        for child in children:
            self.remove(child)
        
        # Build new layout
        if self.current_layout == "mobile":
            self._build_mobile_layout()
        elif self.current_layout == "tablet":
            self._build_tablet_layout()
        else:
            self._build_desktop_layout()
    
    def _build_mobile_layout(self):
        """Build mobile single-column layout"""
        if self.main_content:
            self.main_content.add_css_class("mobile-main")
            if self.footer_area:
                # Insert before footer
                position = 0
                child = self.get_first_child()
                while child and child != self.footer_area:
                    position += 1
                    child = child.get_next_sibling()
                self.insert_child_after(self.main_content, 
                                      self.get_nth_child(position - 1) if position > 0 else None)
            else:
                self.append(self.main_content)
    
    def _build_tablet_layout(self):
        """Build tablet two-column layout"""
        # Create horizontal container
        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        h_box.add_css_class("tablet-layout")
        
        # Add sidebar if available
        if self.sidebar_content:
            self.sidebar_content.add_css_class("tablet-sidebar")
            self.sidebar_content.set_size_request(280, -1)
            h_box.append(self.sidebar_content)
        
        # Add main content
        if self.main_content:
            self.main_content.add_css_class("tablet-main")
            self.main_content.set_hexpand(True)
            h_box.append(self.main_content)
        
        # Insert into container
        if self.footer_area:
            position = 0
            child = self.get_first_child()
            while child and child != self.footer_area:
                position += 1
                child = child.get_next_sibling()
            self.insert_child_after(h_box, 
                                  self.get_nth_child(position - 1) if position > 0 else None)
        else:
            self.append(h_box)
    
    def _build_desktop_layout(self):
        """Build desktop multi-column layout"""
        # Similar to tablet but with different proportions
        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        h_box.add_css_class("desktop-layout")
        
        if self.sidebar_content:
            self.sidebar_content.add_css_class("desktop-sidebar")
            self.sidebar_content.set_size_request(320, -1)
            h_box.append(self.sidebar_content)
        
        if self.main_content:
            self.main_content.add_css_class("desktop-main")
            self.main_content.set_hexpand(True)
            h_box.append(self.main_content)
        
        if self.footer_area:
            position = 0
            child = self.get_first_child()
            while child and child != self.footer_area:
                position += 1
                child = child.get_next_sibling()
            self.insert_child_after(h_box, 
                                  self.get_nth_child(position - 1) if position > 0 else None)
        else:
            self.append(h_box)


class MobileToolCard(Gtk.Box):
    """
    Mobile-optimized tool card component.
    
    Replaces traditional tool tabs with card-based interface.
    Optimized for touch interaction and mobile viewports.
    """
    
    def __init__(self, tool_id: str, title: str, icon: str, description: str = ""):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        self.tool_id = tool_id
        self.add_css_class("tool-card")
        self.add_css_class("mobile-tool-card")
        
        # Make it clickable
        self.set_cursor_from_name("pointer")
        
        # Card header with icon and title
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.set_margin_start(16)
        header_box.set_margin_end(16)
        header_box.set_margin_top(16)
        
        # Icon
        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class("tool-icon")
        header_box.append(icon_label)
        
        # Title and description
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        title_label = Gtk.Label(label=title)
        title_label.add_css_class("tool-title")
        title_label.set_halign(Gtk.Align.START)
        text_box.append(title_label)
        
        if description:
            desc_label = Gtk.Label(label=description)
            desc_label.add_css_class("tool-description")
            desc_label.set_halign(Gtk.Align.START)
            desc_label.set_wrap(True)
            text_box.append(desc_label)
        
        text_box.set_hexpand(True)
        header_box.append(text_box)
        
        # Arrow indicator
        arrow_label = Gtk.Label(label="›")
        arrow_label.add_css_class("tool-arrow")
        header_box.append(arrow_label)
        
        self.append(header_box)
        
        # Add click gesture
        click_gesture = Gtk.GestureClick()
        click_gesture.connect("pressed", self._on_card_clicked)
        self.add_controller(click_gesture)
        
        self.on_tool_selected: Optional[Callable[[str], None]] = None
        
    
    def _on_card_clicked(self, gesture, n_press, x, y):
        """Handle card click"""
        if self.on_tool_selected:
            self.on_tool_selected(self.tool_id)
        


class MobileFirstWindow(Adw.ApplicationWindow):
    """
    Mobile-first application window.
    
    Replaces traditional desktop window with mobile-optimized layout.
    Uses bottom navigation, responsive containers, and touch-friendly components.
    """
    
    def __init__(self, application, viewport_manager):
        super().__init__(application=application)
        
        self.viewport_manager = viewport_manager
        self.set_title("📱 Unhinged Mobile")
        
        # Start with mobile dimensions
        self.set_default_size(412, 915)  # Pixel 8 dimensions
        
        # Create mobile-first layout
        self._setup_mobile_layout()
        
        # Apply mobile-first CSS
        self.add_css_class("mobile-first-window")
        
    
    def _setup_mobile_layout(self):
        """Setup mobile-first layout structure"""
        # Main responsive container
        self.container = ResponsiveContainer()
        
        # Header (compact mobile header)
        header = self._create_mobile_header()
        self.container.set_header(header)
        
        # Main content area (will be populated by tools)
        self.content_area = Gtk.Stack()
        self.content_area.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.content_area.set_transition_duration(300)
        self.content_area.add_css_class("mobile-content")
        self.container.set_main_content(self.content_area)
        
        # Bottom navigation
        self.nav_bar = MobileNavigationBar()
        self.container.set_footer(self.nav_bar)
        
        # Set as window content
        self.set_content(self.container)
    
    def _create_mobile_header(self) -> Gtk.Widget:
        """Create compact mobile header"""
        header = Gtk.HeaderBar()
        header.add_css_class("mobile-header")
        
        # Compact title
        title_label = Gtk.Label(label="🎛️ Control")
        title_label.add_css_class("mobile-title")
        header.set_title_widget(title_label)
        
        # Viewport selector (for development)
        viewport_selector = self.viewport_manager.create_viewport_selector_widget()
        header.pack_end(viewport_selector)
        
        return header
