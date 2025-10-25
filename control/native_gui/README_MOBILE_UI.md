# Mobile UI Framework Integration

**@llm-type integration-guide**  
**@llm-legend Complete integration guide for mobile-responsive UI framework**  
**@llm-key Step-by-step guide for integrating mobile UI framework with Unhinged tools**  
**@llm-map Integration documentation for mobile UI framework in Unhinged architecture**  
**@llm-axiom Integration must maintain system independence and architectural compliance**  
**@llm-contract Provides complete integration workflow for mobile-responsive UI framework**  
**@llm-token mobile_ui_integration: Complete integration guide for mobile-first responsive design**

## Overview

This document provides a complete integration guide for the Unhinged Mobile UI Framework, which enables tools to provide responsive, mobile-first interfaces while maintaining native GTK4 performance and system independence.

## Quick Start

### 1. Build Mobile UI Assets

```bash
# Navigate to project root
cd /path/to/Unhinged

# Build mobile UI framework
python build/modules/mobile_ui_builder.py build

# Verify build
ls generated/mobile_ui/
ls generated/static_html/mobile_ui.css
```

### 2. Create a Mobile-Responsive Tool

```python
from control.native_gui.core.tool_manager import BaseTool, ToolViewport
from control.native_gui.ui.components import Card, MetricCard
from control.native_gui.ui.responsive_layout import ResponsiveGrid

class MyMobileTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "My Mobile Tool"
        self.icon = "📱"
        self.description = "Mobile-responsive tool example"
        self.supports_mobile = True
        self.mobile_priority = 1
    
    def _create_viewport_widget(self, viewport: ToolViewport):
        if viewport == ToolViewport.MOBILE:
            return self._create_mobile_widget()
        elif viewport == ToolViewport.TABLET:
            return self._create_tablet_widget()
        else:
            return self._create_desktop_widget()
    
    def _create_mobile_widget(self):
        # Single column, touch-optimized
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        status_card = Card("Status", "Current status")
        container.append(status_card)
        
        return container
    
    def _create_tablet_widget(self):
        # Two-column grid
        grid = ResponsiveGrid()
        
        status_card = Card("Status", "System overview")
        grid.add_item(status_card, tablet_span=2)
        
        return grid
    
    def _create_desktop_widget(self):
        # Full-featured layout
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        
        # Main content
        main_area = ResponsiveGrid()
        status_card = Card("Status", "Detailed status")
        main_area.add_item(status_card, desktop_span=2)
        
        # Sidebar
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        control_card = Card("Controls", "Tool controls")
        sidebar.append(control_card)
        
        container.append(main_area)
        container.append(sidebar)
        
        return container

# Tool factory function (required)
def create_tool() -> MyMobileTool:
    return MyMobileTool()
```

### 3. Register Tool

Place your tool in the appropriate directory:
```
control/native_gui/tools/my_mobile_tool/
├── __init__.py
└── tool.py
```

### 4. Test Integration

```bash
# Run mobile UI tests
python -m pytest control/native_gui/tests/test_mobile_ui_integration.py -v

# Run your tool
python control/native_gui/main.py
```

## Architecture Integration

### Enhanced Tool System

The mobile UI framework extends the existing tool architecture:

```
BaseTool (Enhanced)
├── viewport_widgets: Dict[ToolViewport, Widget]
├── current_viewport: ToolViewport
├── supports_mobile: bool
├── mobile_priority: int
└── Methods:
    ├── create_widget(viewport) -> Widget
    ├── get_mobile_widget() -> Widget
    ├── get_tablet_widget() -> Widget
    ├── get_desktop_widget() -> Widget
    └── set_viewport(viewport)
```

### Theme System Integration

The enhanced theme manager provides mobile-responsive CSS:

```python
# Initialize enhanced theming
from control.native_gui.core.theme_manager import ThemeManager, ThemeConfig, ThemeVariant

config = ThemeConfig(
    variant=ThemeVariant.DARK,
    mobile_optimized=True,
    touch_friendly=True
)

theme_manager = ThemeManager(config)
theme_manager.setup_theming()
```

### Build System Integration

Mobile UI assets are generated through the centralized build system:

```
build/modules/mobile_ui_builder.py
├── Discovers UI components
├── Generates responsive CSS
├── Creates component metadata
├── Validates layouts
└── Outputs to generated/
```

## Component Library

### Core Components

#### Cards
```python
from control.native_gui.ui.components import Card, ComponentVariant

# Basic card
card = Card("Title", "Subtitle", ComponentVariant.PRIMARY)

# Add content
content_widget = Gtk.Label(label="Card content")
card.set_content(content_widget)

# Add actions
action_button = Gtk.Button(label="Action")
card.add_action(action_button)
```

#### Status Indicators
```python
from control.native_gui.ui.components import StatusIndicator, ComponentVariant

# Animated status indicator
status = StatusIndicator("Connected", ComponentVariant.SUCCESS, animated=True)

# Update status
status.set_status("Disconnected", ComponentVariant.ERROR)
```

#### Metric Cards
```python
from control.native_gui.ui.components import MetricCard

# Metric with trend
metric = MetricCard("CPU Usage", "75%", "+5%", trend_positive=True)

# Update metric
metric.update_metric("80%", "+10%", True)
```

### Responsive Layouts

#### Responsive Grid
```python
from control.native_gui.ui.responsive_layout import ResponsiveGrid

grid = ResponsiveGrid()

# Add items with responsive spans
widget1 = Card("Card 1")
grid.add_item(widget1, mobile_span=1, tablet_span=1, desktop_span=2)

widget2 = Card("Card 2")
grid.add_item(widget2, mobile_span=1, tablet_span=1, desktop_span=1)
```

#### Responsive Container
```python
from control.native_gui.ui.responsive_layout import ResponsiveContainer

container = ResponsiveContainer()

# Set viewport-specific layouts
mobile_layout = create_mobile_layout()
tablet_layout = create_tablet_layout()
desktop_layout = create_desktop_layout()

container.set_mobile_layout(mobile_layout)
container.set_tablet_layout(tablet_layout)
container.set_desktop_layout(desktop_layout)
```

### Touch Interface

#### Touch Gestures
```python
from control.native_gui.ui.touch_interface import SwipeableContainer

# Create swipeable container
swipeable = SwipeableContainer()

# Add pages
page1 = Gtk.Label(label="Page 1")
page2 = Gtk.Label(label="Page 2")

swipeable.add_page(page1, "page1")
swipeable.add_page(page2, "page2")

# Handle page changes
def on_page_changed(page_index):
    print(f"Switched to page {page_index}")

swipeable.on_page_changed = on_page_changed
```

#### Touch Buttons
```python
from control.native_gui.ui.touch_interface import TouchButton

# Touch-optimized button
button = TouchButton("Touch Me", "touch-icon")

# Connect callback
button.connect("clicked", lambda b: print("Touch button clicked"))
```

## Input Capture Integration

The framework includes a comprehensive input capture tool:

### Features
- **Real-time Monitoring**: Keyboard and mouse input tracking
- **Privacy Controls**: Multiple privacy levels and content filtering
- **Hotkey Management**: Advanced hotkey configuration and sequences
- **Pattern Detection**: Input pattern analysis and insights
- **Mobile Interface**: Touch-optimized monitoring interface

### Usage
```python
from control.native_gui.tools.input_capture.tool import InputCaptureTool

# Create input capture tool
input_tool = InputCaptureTool()

# Get mobile-optimized widget
mobile_widget = input_tool.get_mobile_widget()

# Get desktop widget
desktop_widget = input_tool.get_desktop_widget()
```

## CSS and Theming

### Generated CSS

The build system generates mobile-responsive CSS:

```css
/* Mobile-first responsive design */
@media (max-width: 768px) {
    .mobile-only { display: block; }
    .desktop-only { display: none; }
    
    .touch-button {
        min-height: 44px;
        min-width: 44px;
        padding: 12px;
    }
}

@media (min-width: 1024px) {
    .mobile-only { display: none; }
    .desktop-only { display: block; }
}
```

### Custom Styling

Add tool-specific CSS:

```python
# In your tool
def _create_viewport_widget(self, viewport):
    widget = self._create_base_widget()
    
    # Add viewport-specific CSS classes
    if viewport == ToolViewport.MOBILE:
        widget.add_css_class("mobile-optimized")
    elif viewport == ToolViewport.TABLET:
        widget.add_css_class("tablet-optimized")
    else:
        widget.add_css_class("desktop-optimized")
    
    return widget
```

## Testing

### Run Integration Tests

```bash
# Run all mobile UI tests
python -m pytest control/native_gui/tests/test_mobile_ui_integration.py -v

# Run specific test class
python -m pytest control/native_gui/tests/test_mobile_ui_integration.py::TestResponsiveLayout -v

# Run with coverage
python -m pytest control/native_gui/tests/test_mobile_ui_integration.py --cov=control.native_gui.ui
```

### Manual Testing

1. **Viewport Testing**: Resize window to test breakpoints
2. **Touch Testing**: Use touch input or simulate with mouse
3. **Theme Testing**: Switch between light/dark themes
4. **Performance Testing**: Monitor memory and CPU usage

## Troubleshooting

### Common Issues

#### Tool Not Responsive
```python
# Ensure tool implements viewport-specific widgets
def _create_viewport_widget(self, viewport: ToolViewport):
    # Must implement this method
    if viewport == ToolViewport.MOBILE:
        return self._create_mobile_widget()
    # ... other viewports
```

#### CSS Not Applied
```bash
# Rebuild mobile UI assets
python build/modules/mobile_ui_builder.py clean
python build/modules/mobile_ui_builder.py build

# Check generated CSS
cat generated/static_html/mobile_ui.css
```

#### Touch Gestures Not Working
```python
# Ensure gesture controllers are set up
def _setup_gesture_controllers(self):
    self.pan_gesture = Gtk.GesturePan.new(Gtk.Orientation.HORIZONTAL)
    self.pan_gesture.connect("pan", self._on_pan)
    self.add_controller(self.pan_gesture)
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('mobile_ui').setLevel(logging.DEBUG)
```

## Performance Optimization

### Best Practices

1. **Lazy Loading**: Create viewport widgets on demand
2. **Memory Management**: Clean up unused viewport widgets
3. **CSS Efficiency**: Use efficient selectors and minimal reflows
4. **Touch Optimization**: Implement proper touch feedback

### Memory Management

```python
def cleanup(self):
    """Clean up viewport widgets"""
    super().cleanup()
    
    # Clear cached viewport widgets
    self.viewport_widgets.clear()
    
    # Clean up component resources
    if hasattr(self, 'input_monitor'):
        self.input_monitor.cleanup()
```

## Migration Guide

### Existing Tools

To migrate existing tools to the mobile UI framework:

1. **Update Tool Class**: Inherit from enhanced `BaseTool`
2. **Implement Viewport Widgets**: Add `_create_viewport_widget()` method
3. **Add Mobile Support**: Set `supports_mobile = True`
4. **Test Responsiveness**: Verify behavior across viewports
5. **Update CSS**: Add mobile-responsive styling

### Example Migration

```python
# Before (old tool)
class OldTool(BaseTool):
    def create_widget(self):
        return Gtk.Label(label="Old Tool")

# After (mobile-responsive tool)
class NewTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.supports_mobile = True
        self.mobile_priority = 2
    
    def _create_viewport_widget(self, viewport: ToolViewport):
        if viewport == ToolViewport.MOBILE:
            return self._create_mobile_widget()
        else:
            return self._create_desktop_widget()
    
    def _create_mobile_widget(self):
        # Mobile-optimized implementation
        return Card("Mobile Tool", "Touch-optimized interface")
    
    def _create_desktop_widget(self):
        # Desktop implementation (can reuse old logic)
        return Gtk.Label(label="Desktop Tool")
```

## Contributing

When contributing to the mobile UI framework:

1. **Follow Patterns**: Use established responsive design patterns
2. **Test All Viewports**: Ensure functionality across mobile/tablet/desktop
3. **Document Changes**: Update documentation for new features
4. **Performance**: Consider performance impact of changes
5. **Accessibility**: Maintain accessibility standards

## Support

For issues or questions:

1. **Check Documentation**: Review this guide and API documentation
2. **Run Tests**: Execute integration tests to verify setup
3. **Debug Mode**: Enable debug logging for detailed information
4. **Performance Profiling**: Use GTK inspector for UI debugging

## License

This mobile UI framework integration is part of the Unhinged project and follows the same licensing terms.
