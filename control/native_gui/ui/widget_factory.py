"""
@llm-type widget-factory
@llm-legend Widget Factory - Standardized widget creation utilities
@llm-key Provides unified widget creation patterns to eliminate duplicate code
@llm-map Central widget factory component in Unhinged native GUI architecture
@llm-axiom Widget creation must be consistent and follow GTK4 best practices
@llm-contract Provides standardized widget creation interface for all UI components
@llm-token widget_factory: Unified widget creation system for consistent UI patterns
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from typing import Optional, List, Callable, Dict, Any
from enum import Enum


class ContainerType(Enum):
    """
    @llm-type enum
    @llm-legend Container types for different layout patterns
    @llm-key Defines standard container types for consistent layouts
    """
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    GRID = "grid"
    SCROLLED = "scrolled"
    CARD = "card"


class ButtonStyle(Enum):
    """
    @llm-type enum
    @llm-legend Button style variants for consistent styling
    @llm-key Defines standard button styles for UI consistency
    """
    DEFAULT = "default"
    SUGGESTED = "suggested-action"
    DESTRUCTIVE = "destructive-action"
    FLAT = "flat"
    PILL = "pill"
    TOUCH = "touch-button"


class WidgetFactory:
    """
    @llm-type factory-class
    @llm-legend Factory for creating standardized GTK4 widgets
    @llm-key Eliminates duplicate widget creation patterns across tools
    @llm-map Central widget factory for Unhinged native GUI with consistent styling
    @llm-axiom Widget creation must be consistent and follow established patterns
    @llm-contract Provides standardized widget creation interface for all UI needs
    @llm-token WidgetFactory: Unified widget creation system for consistent UI patterns
    
    Factory class for creating standardized GTK4 widgets.
    Eliminates duplicate widget creation patterns across tools.
    """
    
    # Standard spacing and sizing constants
    SPACING_SMALL = 4
    SPACING_MEDIUM = 8
    SPACING_LARGE = 12
    SPACING_XLARGE = 16
    
    MARGIN_SMALL = 8
    MARGIN_MEDIUM = 12
    MARGIN_LARGE = 16
    MARGIN_XLARGE = 24
    
    TOUCH_TARGET_SIZE = 44
    
    @staticmethod
    def create_main_container(spacing: int = SPACING_MEDIUM, 
                            margin: int = MARGIN_LARGE,
                            orientation: Gtk.Orientation = Gtk.Orientation.VERTICAL) -> Gtk.Box:
        """
        @llm-type factory-method
        @llm-legend Create standardized main container with consistent spacing and margins
        @llm-key Creates main container widget with standard layout properties
        """
        container = Gtk.Box(orientation=orientation, spacing=spacing)
        container.set_margin_start(margin)
        container.set_margin_end(margin)
        container.set_margin_top(margin)
        container.set_margin_bottom(margin)
        return container
    
    @staticmethod
    def create_header_box(title: str, 
                         subtitle: Optional[str] = None,
                         spacing: int = SPACING_MEDIUM) -> Gtk.Box:
        """
        @llm-type factory-method
        @llm-legend Create standardized header box with title and optional subtitle
        @llm-key Creates header widget with consistent typography and spacing
        """
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=spacing // 2)
        
        # Title
        title_label = Gtk.Label(label=title)
        title_label.set_halign(Gtk.Align.START)
        title_label.add_css_class("heading")
        title_label.add_css_class("title-1")
        header_box.append(title_label)
        
        # Subtitle
        if subtitle:
            subtitle_label = Gtk.Label(label=subtitle)
            subtitle_label.set_halign(Gtk.Align.START)
            subtitle_label.add_css_class("dim-label")
            subtitle_label.add_css_class("caption")
            header_box.append(subtitle_label)
        
        return header_box
    
    @staticmethod
    def create_scrolled_window(hexpand: bool = True, 
                             vexpand: bool = True,
                             hpolicy: Gtk.PolicyType = Gtk.PolicyType.AUTOMATIC,
                             vpolicy: Gtk.PolicyType = Gtk.PolicyType.AUTOMATIC) -> Gtk.ScrolledWindow:
        """
        @llm-type factory-method
        @llm-legend Create standardized scrolled window with consistent policies
        @llm-key Creates scrolled window widget with standard scrolling behavior
        """
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(hpolicy, vpolicy)
        scrolled.set_hexpand(hexpand)
        scrolled.set_vexpand(vexpand)
        return scrolled
    
    @staticmethod
    def create_button(label: str, 
                     icon_name: Optional[str] = None,
                     style: ButtonStyle = ButtonStyle.DEFAULT,
                     callback: Optional[Callable] = None,
                     tooltip: Optional[str] = None) -> Gtk.Button:
        """
        @llm-type factory-method
        @llm-legend Create standardized button with consistent styling and behavior
        @llm-key Creates button widget with standard appearance and touch optimization
        """
        if icon_name and label:
            # Button with icon and label
            button = Gtk.Button()
            content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=WidgetFactory.SPACING_SMALL)
            
            icon = Gtk.Image.new_from_icon_name(icon_name)
            content_box.append(icon)
            
            label_widget = Gtk.Label(label=label)
            content_box.append(label_widget)
            
            button.set_child(content_box)
        elif icon_name:
            # Icon-only button
            button = Gtk.Button.new_from_icon_name(icon_name)
        else:
            # Text-only button
            button = Gtk.Button.new_with_label(label)
        
        # Apply style
        if style != ButtonStyle.DEFAULT:
            button.add_css_class(style.value)
        
        # Touch optimization for mobile
        if style == ButtonStyle.TOUCH:
            button.set_size_request(WidgetFactory.TOUCH_TARGET_SIZE, WidgetFactory.TOUCH_TARGET_SIZE)
        
        # Connect callback
        if callback:
            button.connect("clicked", lambda b: callback())
        
        # Set tooltip
        if tooltip:
            button.set_tooltip_text(tooltip)
        
        return button
    
    @staticmethod
    def create_card_container(title: Optional[str] = None,
                            subtitle: Optional[str] = None,
                            spacing: int = SPACING_MEDIUM) -> Gtk.Box:
        """
        @llm-type factory-method
        @llm-legend Create standardized card container with optional header
        @llm-key Creates card widget with consistent styling and layout
        """
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=spacing)
        card.add_css_class("card")
        
        # Add header if title provided
        if title:
            header = WidgetFactory.create_header_box(title, subtitle, spacing)
            card.append(header)
        
        return card
    
    @staticmethod
    def create_list_box(selection_mode: Gtk.SelectionMode = Gtk.SelectionMode.SINGLE,
                       show_separators: bool = True) -> Gtk.ListBox:
        """
        @llm-type factory-method
        @llm-legend Create standardized list box with consistent behavior
        @llm-key Creates list box widget with standard selection and appearance
        """
        list_box = Gtk.ListBox()
        list_box.set_selection_mode(selection_mode)
        list_box.set_show_separators(show_separators)
        list_box.add_css_class("boxed-list")
        return list_box
    
    @staticmethod
    def create_entry(placeholder: Optional[str] = None,
                    callback: Optional[Callable[[str], None]] = None) -> Gtk.Entry:
        """
        @llm-type factory-method
        @llm-legend Create standardized entry widget with consistent behavior
        @llm-key Creates entry widget with standard appearance and callbacks
        """
        entry = Gtk.Entry()
        
        if placeholder:
            entry.set_placeholder_text(placeholder)
        
        if callback:
            entry.connect("changed", lambda e: callback(e.get_text()))
        
        return entry
    
    @staticmethod
    def create_search_entry(placeholder: str = "Search...",
                          callback: Optional[Callable[[str], None]] = None) -> Gtk.SearchEntry:
        """
        @llm-type factory-method
        @llm-legend Create standardized search entry with consistent behavior
        @llm-key Creates search entry widget with standard search functionality
        """
        search_entry = Gtk.SearchEntry()
        search_entry.set_placeholder_text(placeholder)
        
        if callback:
            search_entry.connect("search-changed", lambda e: callback(e.get_text()))
        
        return search_entry
    
    @staticmethod
    def create_switch(label: str,
                     active: bool = False,
                     callback: Optional[Callable[[bool], None]] = None) -> Gtk.Box:
        """
        @llm-type factory-method
        @llm-legend Create standardized switch with label
        @llm-key Creates switch widget with consistent layout and behavior
        """
        switch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=WidgetFactory.SPACING_MEDIUM)
        
        label_widget = Gtk.Label(label=label)
        label_widget.set_hexpand(True)
        label_widget.set_halign(Gtk.Align.START)
        switch_box.append(label_widget)
        
        switch = Gtk.Switch()
        switch.set_active(active)
        switch.set_halign(Gtk.Align.END)
        
        if callback:
            switch.connect("state-set", lambda s, state: callback(state))
        
        switch_box.append(switch)
        
        return switch_box
    
    @staticmethod
    def create_progress_bar(fraction: float = 0.0,
                          show_text: bool = False,
                          text: Optional[str] = None) -> Gtk.ProgressBar:
        """
        @llm-type factory-method
        @llm-legend Create standardized progress bar with consistent appearance
        @llm-key Creates progress bar widget with standard styling and behavior
        """
        progress = Gtk.ProgressBar()
        progress.set_fraction(fraction)
        progress.set_show_text(show_text)
        
        if text:
            progress.set_text(text)
        
        return progress
    
    @staticmethod
    def create_separator(orientation: Gtk.Orientation = Gtk.Orientation.HORIZONTAL) -> Gtk.Separator:
        """
        @llm-type factory-method
        @llm-legend Create standardized separator with consistent styling
        @llm-key Creates separator widget with standard appearance
        """
        separator = Gtk.Separator(orientation=orientation)
        return separator
    
    @staticmethod
    def create_toolbar(items: List[Dict[str, Any]]) -> Gtk.Box:
        """
        @llm-type factory-method
        @llm-legend Create standardized toolbar with consistent button layout
        @llm-key Creates toolbar widget with standard button arrangement
        """
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=WidgetFactory.SPACING_SMALL)
        toolbar.add_css_class("toolbar")
        
        for item in items:
            if item.get("type") == "button":
                button = WidgetFactory.create_button(
                    label=item.get("label", ""),
                    icon_name=item.get("icon"),
                    style=ButtonStyle(item.get("style", "default")),
                    callback=item.get("callback"),
                    tooltip=item.get("tooltip")
                )
                toolbar.append(button)
            elif item.get("type") == "separator":
                separator = WidgetFactory.create_separator(Gtk.Orientation.VERTICAL)
                toolbar.append(separator)
        
        return toolbar
    
    @staticmethod
    def create_status_row(label: str, 
                         value: str,
                         status_class: Optional[str] = None) -> Gtk.Box:
        """
        @llm-type factory-method
        @llm-legend Create standardized status row with label and value
        @llm-key Creates status row widget with consistent layout and styling
        """
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=WidgetFactory.SPACING_MEDIUM)
        
        label_widget = Gtk.Label(label=label)
        label_widget.set_hexpand(True)
        label_widget.set_halign(Gtk.Align.START)
        row.append(label_widget)
        
        value_widget = Gtk.Label(label=value)
        value_widget.set_halign(Gtk.Align.END)
        
        if status_class:
            value_widget.add_css_class(status_class)
        
        row.append(value_widget)
        
        return row
