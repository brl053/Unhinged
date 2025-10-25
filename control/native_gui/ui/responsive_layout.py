
import logging; gui_logger = logging.getLogger(__name__)

"""
Responsive Layout System for Mobile-First UI
Provides adaptive layouts that respond to screen size changes and device orientation.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, GLib
from typing import Dict, List, Optional, Callable, Tuple
from enum import Enum
from dataclasses import dataclass


class ScreenSize(Enum):
    """Screen size categories"""
    MOBILE = "mobile"      # < 768px
    TABLET = "tablet"      # 768px - 1024px
    DESKTOP = "desktop"    # > 1024px


class Orientation(Enum):
    """Device orientation"""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


@dataclass
class LayoutBreakpoint:
    """Layout breakpoint definition"""
    name: str
    min_width: int
    max_width: Optional[int] = None
    columns: int = 1
    spacing: int = 12
    margins: Tuple[int, int, int, int] = (12, 12, 12, 12)  # top, right, bottom, left


class ResponsiveLayout(Gtk.Box):
    """Base responsive layout widget"""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # Layout state
        self.current_size = ScreenSize.DESKTOP
        self.current_orientation = Orientation.LANDSCAPE
        self.current_width = 0
        self.current_height = 0

        # Breakpoints
        self.breakpoints = {
            ScreenSize.MOBILE: LayoutBreakpoint("mobile", 0, 767, 1, 8, (8, 8, 8, 8)),
            ScreenSize.TABLET: LayoutBreakpoint("tablet", 768, 1023, 2, 12, (12, 12, 12, 12)),
            ScreenSize.DESKTOP: LayoutBreakpoint("desktop", 1024, None, 3, 16, (16, 16, 16, 16))
        }

        # Layout callbacks
        self.on_size_changed: Optional[Callable[[ScreenSize], None]] = None
        self.on_orientation_changed: Optional[Callable[[Orientation], None]] = None

        # Child widgets
        self.children: List[Gtk.Widget] = []
        self.layout_manager = None

    
    def update_size(self, width: int, height: int):
        """Update layout size manually (for testing or manual control)"""
        try:
            old_size = self.current_size
            old_orientation = self.current_orientation

            # Update dimensions
            self.current_width = width
            self.current_height = height

            # Determine screen size
            new_size = self._determine_screen_size(width)
            new_orientation = self._determine_orientation(width, height)

            # Check for changes
            size_changed = new_size != old_size
            orientation_changed = new_orientation != old_orientation

            if size_changed or orientation_changed:
                self.current_size = new_size
                self.current_orientation = new_orientation

                # Apply responsive layout
                self._apply_responsive_layout()

                # Trigger callbacks
                if size_changed and self.on_size_changed:
                    self.on_size_changed(new_size)

                if orientation_changed and self.on_orientation_changed:
                    self.on_orientation_changed(new_orientation)


        except Exception as e:
            gui_logger.warn(f" Size update error: {e}")
    
    def _determine_screen_size(self, width: int) -> ScreenSize:
        """Determine screen size category from width"""
        if width < 768:
            return ScreenSize.MOBILE
        elif width < 1024:
            return ScreenSize.TABLET
        else:
            return ScreenSize.DESKTOP
    
    def _determine_orientation(self, width: int, height: int) -> Orientation:
        """Determine orientation from dimensions"""
        return Orientation.LANDSCAPE if width > height else Orientation.PORTRAIT
    
    def _apply_responsive_layout(self):
        """Apply responsive layout based on current screen size"""
        breakpoint = self.breakpoints[self.current_size]
        
        # Apply margins
        top, right, bottom, left = breakpoint.margins
        self.set_margin_top(top)
        self.set_margin_end(right)
        self.set_margin_bottom(bottom)
        self.set_margin_start(left)
        
        # Update layout manager if available
        if self.layout_manager:
            self.layout_manager.set_spacing(breakpoint.spacing)
    
    def get_current_breakpoint(self) -> LayoutBreakpoint:
        """Get current layout breakpoint"""
        return self.breakpoints[self.current_size]
    
    def is_mobile(self) -> bool:
        """Check if current layout is mobile"""
        return self.current_size == ScreenSize.MOBILE
    
    def is_tablet(self) -> bool:
        """Check if current layout is tablet"""
        return self.current_size == ScreenSize.TABLET
    
    def is_desktop(self) -> bool:
        """Check if current layout is desktop"""
        return self.current_size == ScreenSize.DESKTOP
    
    def is_portrait(self) -> bool:
        """Check if current orientation is portrait"""
        return self.current_orientation == Orientation.PORTRAIT


class ResponsiveGrid(Gtk.Box):
    """Responsive grid layout"""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # Layout state (simplified)
        self.current_size = ScreenSize.DESKTOP
        self.current_columns = 1

        # Create grid layout
        self.grid = Gtk.Grid()
        self.grid.set_row_homogeneous(False)
        self.grid.set_column_homogeneous(True)

        # Add grid to container
        self.append(self.grid)
        self.layout_manager = self.grid

        # Grid state
        self.grid_items: List[Dict] = []

    def is_mobile(self) -> bool:
        """Check if current size is mobile"""
        return self.current_size == ScreenSize.MOBILE
    
    def add_item(self, widget: Gtk.Widget, 
                 mobile_span: int = 1, tablet_span: int = 1, desktop_span: int = 1,
                 priority: int = 0):
                     pass
        """Add item to responsive grid"""
        item = {
            'widget': widget,
            'mobile_span': mobile_span,
            'tablet_span': tablet_span,
            'desktop_span': desktop_span,
            'priority': priority
        }
        
        self.grid_items.append(item)
        self._rebuild_grid()
    
    def remove_item(self, widget: Gtk.Widget):
        """Remove item from grid"""
        self.grid_items = [item for item in self.grid_items if item['widget'] != widget]
        self.grid.remove(widget)
        self._rebuild_grid()
    
    def _apply_responsive_layout(self):
        """Apply responsive grid layout"""
        super()._apply_responsive_layout()
        
        # Update columns based on screen size
        breakpoint = self.get_current_breakpoint()
        if self.current_columns != breakpoint.columns:
            self.current_columns = breakpoint.columns
            self._rebuild_grid()
    
    def _rebuild_grid(self):
        """Rebuild grid layout"""
        try:
            # Clear grid
            child = self.grid.get_first_child()
            while child:
                next_child = child.get_next_sibling()
                self.grid.remove(child)
                child = next_child
            
            # Sort items by priority
            sorted_items = sorted(self.grid_items, key=lambda x: x['priority'], reverse=True)
            
            # Add items to grid
            row = 0
            col = 0
            
            for item in sorted_items:
                widget = item['widget']
                
                # Get span for current screen size
                if self.is_mobile():
                    span = item['mobile_span']
                elif self.is_tablet():
                    span = item['tablet_span']
                else:
                    span = item['desktop_span']
                
                # Ensure span doesn't exceed available columns
                span = min(span, self.current_columns)
                
                # Check if item fits in current row
                if col + span > self.current_columns:
                    row += 1
                    col = 0
                
                # Attach widget
                self.grid.attach(widget, col, row, span, 1)
                
                # Update column position
                col += span
                if col >= self.current_columns:
                    row += 1
                    col = 0
            
        except Exception as e:
            gui_logger.warn(f" Grid rebuild error: {e}")


class ResponsiveStack(Gtk.Box):
    """Responsive stack layout that changes orientation"""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # Layout state (simplified)
        self.current_size = ScreenSize.DESKTOP

        # Create inner box layout
        self.box = Gtk.Box()
        self.append(self.box)
        self.layout_manager = self.box

        # Stack items
        self.stack_items: List[Gtk.Widget] = []

    def is_mobile(self) -> bool:
        """Check if current size is mobile"""
        return self.current_size == ScreenSize.MOBILE
    
    def add_item(self, widget: Gtk.Widget):
        """Add item to responsive stack"""
        self.stack_items.append(widget)
        self.box.append(widget)
    
    def remove_item(self, widget: Gtk.Widget):
        """Remove item from stack"""
        if widget in self.stack_items:
            self.stack_items.remove(widget)
            self.box.remove(widget)
    
    def _apply_responsive_layout(self):
        """Apply responsive stack layout"""
        super()._apply_responsive_layout()
        
        # Change orientation based on screen size
        if self.is_mobile() or (self.is_tablet() and self.is_portrait()):
            self.box.set_orientation(Gtk.Orientation.VERTICAL)
        else:
            self.box.set_orientation(Gtk.Orientation.HORIZONTAL)
        
        # Update homogeneous property
        self.box.set_homogeneous(not self.is_mobile())


class ResponsiveContainer(Gtk.Box):
    """Container that shows/hides content based on screen size"""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # Layout state (simplified)
        self.current_size = ScreenSize.DESKTOP

        # Create stack for different layouts
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(200)
        self.append(self.stack)

        # Layout variants
        self.mobile_layout: Optional[Gtk.Widget] = None
        self.tablet_layout: Optional[Gtk.Widget] = None
        self.desktop_layout: Optional[Gtk.Widget] = None
    
    def set_mobile_layout(self, widget: Gtk.Widget):
        """Set mobile-specific layout"""
        if self.mobile_layout:
            self.stack.remove(self.mobile_layout)
        
        self.mobile_layout = widget
        self.stack.add_named(widget, "mobile")
    
    def set_tablet_layout(self, widget: Gtk.Widget):
        """Set tablet-specific layout"""
        if self.tablet_layout:
            self.stack.remove(self.tablet_layout)
        
        self.tablet_layout = widget
        self.stack.add_named(widget, "tablet")
    
    def set_desktop_layout(self, widget: Gtk.Widget):
        """Set desktop-specific layout"""
        if self.desktop_layout:
            self.stack.remove(self.desktop_layout)
        
        self.desktop_layout = widget
        self.stack.add_named(widget, "desktop")
    
    def _apply_responsive_layout(self):
        """Apply responsive container layout"""
        super()._apply_responsive_layout()
        
        # Switch to appropriate layout
        if self.is_mobile() and self.mobile_layout:
            self.stack.set_visible_child_name("mobile")
        elif self.is_tablet() and self.tablet_layout:
            self.stack.set_visible_child_name("tablet")
        elif self.is_desktop() and self.desktop_layout:
            self.stack.set_visible_child_name("desktop")
        else:
            # Fallback to available layout
            if self.desktop_layout:
                self.stack.set_visible_child_name("desktop")
            elif self.tablet_layout:
                self.stack.set_visible_child_name("tablet")
            elif self.mobile_layout:
                self.stack.set_visible_child_name("mobile")


class ResponsiveWindow(Adw.ApplicationWindow):
    """Responsive application window"""
    
    def __init__(self, application):
        super().__init__(application=application)
        
        # Window properties
        self.set_title("Responsive App")
        self.set_default_size(800, 600)
        
        # Create responsive layout
        self.responsive_layout = ResponsiveContainer()
        self.set_content(self.responsive_layout)
        
        # Connect layout callbacks
        self.responsive_layout.on_size_changed = self._on_layout_size_changed
        self.responsive_layout.on_orientation_changed = self._on_layout_orientation_changed
        
        # Window state
        self.is_maximized = False
        self.is_fullscreen = False
        
        # Connect window state events
        self.connect("notify::maximized", self._on_window_state_changed)
        self.connect("notify::fullscreened", self._on_window_state_changed)
    
    def _on_layout_size_changed(self, size: ScreenSize):
        """Handle layout size changes"""
        
        # Adjust window properties based on size
        if size == ScreenSize.MOBILE:
            self.set_resizable(True)
            # Could set minimum size for mobile
        elif size == ScreenSize.TABLET:
            self.set_resizable(True)
        else:  # DESKTOP
            self.set_resizable(True)
    
    def _on_layout_orientation_changed(self, orientation: Orientation):
        """Handle orientation changes"""
    
    def _on_window_state_changed(self, window, pspec):
        """Handle window state changes"""
        self.is_maximized = self.is_maximized()
        self.is_fullscreen = self.is_fullscreened()
        
        # Force layout recalculation
        self.responsive_layout.queue_resize()
    
    def set_mobile_layout(self, widget: Gtk.Widget):
        """Set mobile layout"""
        self.responsive_layout.set_mobile_layout(widget)
    
    def set_tablet_layout(self, widget: Gtk.Widget):
        """Set tablet layout"""
        self.responsive_layout.set_tablet_layout(widget)
    
    def set_desktop_layout(self, widget: Gtk.Widget):
        """Set desktop layout"""
        self.responsive_layout.set_desktop_layout(widget)


# Utility functions
def create_responsive_button(text: str, icon_name: Optional[str] = None) -> Gtk.Button:
    """Create responsive button that adapts to screen size"""
    button = Gtk.Button()
    
    def update_button_layout(size: ScreenSize):
        if size == ScreenSize.MOBILE:
            # Mobile: icon only or short text
            if icon_name:
                button.set_icon_name(icon_name)
                button.set_label("")
            else:
                button.set_label(text[:10] + "..." if len(text) > 10 else text)
        else:
            # Tablet/Desktop: full text and icon
            if icon_name:
                button.set_icon_name(icon_name)
            button.set_label(text)
    
    # Initial setup
    update_button_layout(ScreenSize.DESKTOP)
    
    return button


def create_responsive_spacing(mobile: int = 8, tablet: int = 12, desktop: int = 16) -> int:
    """Get responsive spacing value"""
    # This would need access to current screen size
    # For now, return desktop value
    return desktop


# Test function
def test_responsive_layout():
    """Test responsive layout system"""
    
    app = Adw.Application()
    
    def on_activate(app):
        window = ResponsiveWindow(app)
        
        # Create test layouts
        mobile_layout = Gtk.Label(label="Mobile Layout")
        tablet_layout = Gtk.Label(label="Tablet Layout")
        desktop_layout = Gtk.Label(label="Desktop Layout")
        
        window.set_mobile_layout(mobile_layout)
        window.set_tablet_layout(tablet_layout)
        window.set_desktop_layout(desktop_layout)
        
        window.present()
    
    app.connect("activate", on_activate)
    app.run()


class AdaptiveLayoutManager:
    """Manages adaptive layouts across different screen sizes and contexts"""

    def __init__(self):
        # Layout registry
        self.layouts: Dict[str, Dict[ScreenSize, Gtk.Widget]] = {}
        self.current_layout = None
        self.current_screen_size = ScreenSize.DESKTOP

        # Layout contexts
        self.contexts: Dict[str, Dict] = {}
        self.current_context = "default"

        # Layout transitions
        self.transition_duration = 300
        self.transition_type = Gtk.StackTransitionType.CROSSFADE


    def register_layout(self, name: str, layouts: Dict[ScreenSize, Gtk.Widget]):
        """Register adaptive layout variants"""
        self.layouts[name] = layouts

    def set_context(self, context: str, properties: Dict):
        """Set layout context with properties"""
        self.contexts[context] = properties
        self.current_context = context

    def get_optimal_layout(self, name: str, screen_size: ScreenSize) -> Optional[Gtk.Widget]:
        """Get optimal layout for screen size with fallback"""
        if name not in self.layouts:
            return None

        layout_variants = self.layouts[name]

        # Try exact match first
        if screen_size in layout_variants:
            return layout_variants[screen_size]

        # Fallback strategy: desktop -> tablet -> mobile
        fallback_order = [ScreenSize.DESKTOP, ScreenSize.TABLET, ScreenSize.MOBILE]

        for fallback_size in fallback_order:
            if fallback_size in layout_variants:
                return layout_variants[fallback_size]

        return None

    def create_adaptive_container(self, layout_name: str) -> 'AdaptiveContainer':
        """Create adaptive container for layout"""
        return AdaptiveContainer(self, layout_name)


class AdaptiveContainer(ResponsiveLayout):
    """Container that automatically adapts layout based on screen size"""

    def __init__(self, layout_manager: AdaptiveLayoutManager, layout_name: str):
        super().__init__()

        self.layout_manager = layout_manager
        self.layout_name = layout_name

        # Create stack for layout switching
        self.layout_stack = Gtk.Stack()
        self.layout_stack.set_transition_type(layout_manager.transition_type)
        self.layout_stack.set_transition_duration(layout_manager.transition_duration)
        self.set_child(self.layout_stack)

        # Current layout tracking
        self.current_layout_widget = None

        # Initialize with current screen size
        self._update_layout()

    def _apply_responsive_layout(self):
        """Apply responsive layout based on screen size"""
        super()._apply_responsive_layout()
        self._update_layout()

    def _update_layout(self):
        """Update layout based on current screen size"""
        optimal_layout = self.layout_manager.get_optimal_layout(
            self.layout_name,
            self.current_size
        )

        if optimal_layout and optimal_layout != self.current_layout_widget:
            # Add new layout to stack if not already present
            layout_name = f"{self.layout_name}_{self.current_size.value}"

            # Remove old layout
            if self.current_layout_widget:
                self.layout_stack.remove(self.current_layout_widget)

            # Add new layout
            self.layout_stack.add_named(optimal_layout, layout_name)
            self.layout_stack.set_visible_child(optimal_layout)

            self.current_layout_widget = optimal_layout



class NavigationManager:
    """Manages navigation patterns across different screen sizes"""

    def __init__(self):
        # Navigation patterns
        self.mobile_pattern = "bottom_tabs"  # bottom_tabs, drawer, stack
        self.tablet_pattern = "side_tabs"    # side_tabs, split_view, tabs
        self.desktop_pattern = "sidebar"     # sidebar, top_tabs, ribbon

        # Navigation state
        self.navigation_stack: List[str] = []
        self.current_page = ""

        # Callbacks
        self.on_navigation_changed: Optional[Callable[[str], None]] = None

    def get_navigation_pattern(self, screen_size: ScreenSize) -> str:
        """Get appropriate navigation pattern for screen size"""
        if screen_size == ScreenSize.MOBILE:
            return self.mobile_pattern
        elif screen_size == ScreenSize.TABLET:
            return self.tablet_pattern
        else:
            return self.desktop_pattern

    def create_navigation_container(self, screen_size: ScreenSize) -> Gtk.Widget:
        """Create navigation container for screen size"""
        pattern = self.get_navigation_pattern(screen_size)

        if pattern == "bottom_tabs":
            return self._create_bottom_tabs()
        elif pattern == "side_tabs":
            return self._create_side_tabs()
        elif pattern == "sidebar":
            return self._create_sidebar()
        elif pattern == "drawer":
            return self._create_drawer()
        elif pattern == "split_view":
            return self._create_split_view()
        else:
            return self._create_top_tabs()

    def _create_bottom_tabs(self) -> Gtk.Widget:
        """Create bottom tab navigation for mobile"""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Content area
        content_stack = Gtk.Stack()
        container.append(content_stack)

        # Bottom tab bar
        tab_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        tab_bar.set_homogeneous(True)
        tab_bar.add_css_class("bottom-tab-bar")
        container.append(tab_bar)

        return container

    def _create_side_tabs(self) -> Gtk.Widget:
        """Create side tab navigation for tablet"""
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # Side tab bar
        tab_bar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        tab_bar.set_size_request(200, -1)
        tab_bar.add_css_class("side-tab-bar")
        container.append(tab_bar)

        # Content area
        content_stack = Gtk.Stack()
        container.append(content_stack)

        return container

    def _create_sidebar(self) -> Gtk.Widget:
        """Create sidebar navigation for desktop"""
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # Sidebar
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar.set_size_request(250, -1)
        sidebar.add_css_class("sidebar")
        container.append(sidebar)

        # Main content area
        content_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        container.append(content_area)

        return container

    def _create_drawer(self) -> Gtk.Widget:
        """Create drawer navigation"""
        # Use Adwaita's navigation drawer
        split_view = Adw.NavigationSplitView()

        # Sidebar content
        sidebar_page = Adw.NavigationPage()
        sidebar_page.set_title("Navigation")
        split_view.set_sidebar(sidebar_page)

        # Main content
        content_page = Adw.NavigationPage()
        content_page.set_title("Content")
        split_view.set_content(content_page)

        return split_view

    def _create_split_view(self) -> Gtk.Widget:
        """Create split view for tablet"""
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_position(300)

        # Left panel
        left_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_panel.set_size_request(300, -1)
        paned.set_start_child(left_panel)

        # Right panel
        right_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        paned.set_end_child(right_panel)

        return paned

    def _create_top_tabs(self) -> Gtk.Widget:
        """Create top tab navigation"""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Tab bar
        tab_bar = Adw.TabBar()
        tab_view = Adw.TabView()
        tab_bar.set_view(tab_view)

        container.append(tab_bar)
        container.append(tab_view)

        return container


class LayoutPresets:
    """Predefined layout presets for common use cases"""

    @staticmethod
    def create_dashboard_layout() -> Dict[ScreenSize, Gtk.Widget]:
        """Create dashboard layout variants"""
        layouts = {}

        # Mobile: Single column, stacked cards
        mobile_layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        mobile_layout.add_css_class("mobile-dashboard")
        layouts[ScreenSize.MOBILE] = mobile_layout

        # Tablet: Two column grid
        tablet_layout = ResponsiveGrid()
        tablet_layout.add_css_class("tablet-dashboard")
        layouts[ScreenSize.TABLET] = tablet_layout

        # Desktop: Three column grid with sidebar
        desktop_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        desktop_sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        desktop_sidebar.set_size_request(250, -1)
        desktop_main = ResponsiveGrid()

        desktop_container.append(desktop_sidebar)
        desktop_container.append(desktop_main)
        desktop_container.add_css_class("desktop-dashboard")
        layouts[ScreenSize.DESKTOP] = desktop_container

        return layouts

    @staticmethod
    def create_form_layout() -> Dict[ScreenSize, Gtk.Widget]:
        """Create form layout variants"""
        layouts = {}

        # Mobile: Single column, full width
        mobile_form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        mobile_form.add_css_class("mobile-form")
        layouts[ScreenSize.MOBILE] = mobile_form

        # Tablet: Centered with max width
        tablet_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        tablet_container.set_halign(Gtk.Align.CENTER)
        tablet_form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        tablet_form.set_size_request(500, -1)
        tablet_container.append(tablet_form)
        tablet_container.add_css_class("tablet-form")
        layouts[ScreenSize.TABLET] = tablet_container

        # Desktop: Two column layout
        desktop_grid = Gtk.Grid()
        desktop_grid.set_column_spacing(24)
        desktop_grid.set_row_spacing(16)
        desktop_grid.add_css_class("desktop-form")
        layouts[ScreenSize.DESKTOP] = desktop_grid

        return layouts

    @staticmethod
    def create_list_layout() -> Dict[ScreenSize, Gtk.Widget]:
        """Create list layout variants"""
        layouts = {}

        # Mobile: Simple list
        mobile_list = Gtk.ListBox()
        mobile_list.add_css_class("mobile-list")
        layouts[ScreenSize.MOBILE] = mobile_list

        # Tablet: List with details panel
        tablet_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        tablet_list = Gtk.ListBox()
        tablet_details = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        tablet_paned.set_start_child(tablet_list)
        tablet_paned.set_end_child(tablet_details)
        tablet_paned.set_position(300)
        tablet_paned.add_css_class("tablet-list")
        layouts[ScreenSize.TABLET] = tablet_paned

        # Desktop: Multi-column list with toolbar
        desktop_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        desktop_toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        desktop_content = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)

        desktop_container.append(desktop_toolbar)
        desktop_container.append(desktop_content)
        desktop_container.add_css_class("desktop-list")
        layouts[ScreenSize.DESKTOP] = desktop_container

        return layouts


if __name__ == "__main__":
    test_responsive_layout()
