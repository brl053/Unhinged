# Mobile UI Framework Documentation

**@llm-type documentation**  
**@llm-legend Comprehensive documentation for the Unhinged mobile-responsive UI framework**  
**@llm-key Complete guide to mobile-first responsive design implementation**  
**@llm-map Documentation for mobile UI framework in Unhinged architecture**  
**@llm-axiom Documentation must be comprehensive, accurate, and maintainable**  
**@llm-contract Provides complete reference for mobile UI framework usage and integration**  
**@llm-token mobile_ui_docs: Comprehensive mobile-responsive UI framework documentation**

## Overview

The Unhinged Mobile UI Framework provides a comprehensive mobile-first responsive design system built on GTK4/Adwaita. It enables tools to adapt seamlessly across desktop, tablet, and mobile viewports while maintaining native performance and the independence principles of the Unhinged system.

## Architecture

### Core Components

#### 1. Responsive Layout System (`responsive_layout.py`)
- **ResponsiveLayout**: Base responsive widget with breakpoint detection
- **ResponsiveGrid**: Adaptive grid layout with configurable columns
- **ResponsiveStack**: Stack layout that changes orientation based on viewport
- **ResponsiveContainer**: Container with viewport-specific layout variants

#### 2. Touch Interface (`touch_interface.py`)
- **TouchGestureRecognizer**: Advanced gesture recognition (tap, swipe, pinch, rotate)
- **TouchButton**: Touch-optimized button with haptic feedback simulation
- **SwipeableContainer**: Container with swipe navigation support
- **TouchScrollArea**: Touch-friendly scrollable areas
- **PullToRefresh**: Pull-to-refresh functionality

#### 3. Component Library (`components.py`)
- **Card**: Responsive card component with elevation
- **StatusIndicator**: Animated status display with color variants
- **ProgressCard**: Card with integrated progress tracking
- **MetricCard**: Data visualization card with trend indicators
- **ActionSheet**: Modal action sheet for mobile interfaces
- **Toast**: Enhanced notification system
- **LoadingSpinner**: Customizable loading indicators
- **EmptyState**: User-friendly empty state displays

#### 4. Input Integration (`input_integration.py`)
- **InputMonitorWidget**: Real-time input monitoring interface
- **HotkeyConfigWidget**: Hotkey configuration management
- **PrivacyControlWidget**: Privacy settings and data filtering controls

### Viewport System

The framework uses a three-tier viewport system:

```python
class ToolViewport(Enum):
    MOBILE = "mobile"      # < 768px - Touch-optimized, single column
    TABLET = "tablet"      # 768-1024px - Hybrid interface  
    DESKTOP = "desktop"    # > 1024px - Full feature set
```

### Breakpoints

- **Mobile**: ≤ 768px - Single column, touch-optimized
- **Tablet**: 768px - 1024px - Two-column grid, hybrid controls
- **Desktop**: ≥ 1024px - Multi-column, full feature set

## Tool Integration

### Enhanced BaseTool

All tools inherit from the enhanced `BaseTool` class which provides viewport-aware widget creation:

```python
class MyTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "My Tool"
        self.supports_mobile = True
        self.mobile_priority = 2
    
    def _create_viewport_widget(self, viewport: ToolViewport):
        if viewport == ToolViewport.MOBILE:
            return self._create_mobile_widget()
        elif viewport == ToolViewport.TABLET:
            return self._create_tablet_widget()
        else:
            return self._create_desktop_widget()
```

### Viewport-Specific Widgets

Tools can provide different widgets for different viewports:

- `get_mobile_widget()`: Touch-optimized, single-column layout
- `get_tablet_widget()`: Balanced two-column layout
- `get_desktop_widget()`: Full-featured multi-column layout

## Theme System

### Enhanced Theme Manager

The theme system provides mobile-responsive CSS with GTK4 integration:

```python
# Initialize theming with mobile support
theme_config = ThemeConfig(
    variant=ThemeVariant.DARK,
    mobile_optimized=True,
    touch_friendly=True
)
theme_manager = ThemeManager(theme_config)
theme_manager.setup_theming()
```

### CSS Classes

#### Responsive Utilities
- `.mobile-only`: Visible only on mobile viewports
- `.tablet-only`: Visible only on tablet viewports  
- `.desktop-only`: Visible only on desktop viewports
- `.touch-button`: Touch-optimized button styling

#### Component Classes
- `.card`: Responsive card with elevation
- `.status-indicator`: Status display with color variants
- `.metric-value`: Large metric display
- `.loading-spinner`: Animated loading indicator

## Build System Integration

### Mobile UI Builder

The framework integrates with the centralized build system through `MobileUIBuilder`:

```bash
# Build mobile UI assets
python build/modules/mobile_ui_builder.py build

# Clean generated assets
python build/modules/mobile_ui_builder.py clean
```

### Generated Assets

- **CSS Files**: `generated/static_html/mobile_ui.css`
- **Component Metadata**: `generated/mobile_ui/components/metadata.json`
- **Build Manifest**: `generated/mobile_ui/build_manifest.json`

## Input Capture Integration

### Input Capture Tool

The framework includes a comprehensive input capture tool:

```python
# Create input capture tool
input_tool = InputCaptureTool()

# Get viewport-specific widget
mobile_widget = input_tool.get_mobile_widget()
desktop_widget = input_tool.get_desktop_widget()
```

### Privacy Controls

- **Multiple Privacy Levels**: Full, Filtered, Anonymous, Statistics-only, Disabled
- **Application Filtering**: Block sensitive applications (password managers, etc.)
- **Content Filtering**: Filter passwords, emails, URLs, custom patterns
- **Data Anonymization**: Hash sensitive content while preserving analytics

## Usage Examples

### Creating a Responsive Tool

```python
from control.native_gui.core.tool_manager import BaseTool, ToolViewport
from control.native_gui.ui.components import Card, MetricCard
from control.native_gui.ui.responsive_layout import ResponsiveGrid

class MyResponsiveTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "My Responsive Tool"
        self.supports_mobile = True
        self.mobile_priority = 1
    
    def _create_viewport_widget(self, viewport: ToolViewport):
        if viewport == ToolViewport.MOBILE:
            return self._create_mobile_layout()
        elif viewport == ToolViewport.TABLET:
            return self._create_tablet_layout()
        else:
            return self._create_desktop_layout()
    
    def _create_mobile_layout(self):
        # Single column, stacked layout
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # Priority components first
        status_card = Card("Status", "Current system status")
        container.append(status_card)
        
        metrics_card = MetricCard("CPU Usage", "45%", "+2%", True)
        container.append(metrics_card)
        
        return container
    
    def _create_tablet_layout(self):
        # Two-column grid
        grid = ResponsiveGrid()
        
        status_card = Card("Status", "System overview")
        grid.add_item(status_card, mobile_span=1, tablet_span=2, desktop_span=2)
        
        cpu_card = MetricCard("CPU", "45%")
        memory_card = MetricCard("Memory", "67%")
        
        grid.add_item(cpu_card, mobile_span=1, tablet_span=1, desktop_span=1)
        grid.add_item(memory_card, mobile_span=1, tablet_span=1, desktop_span=1)
        
        return grid
    
    def _create_desktop_layout(self):
        # Full-featured layout with sidebar
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        
        # Main content area
        main_area = ResponsiveGrid()
        # ... add components
        
        # Sidebar
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        # ... add sidebar components
        
        container.append(main_area)
        container.append(sidebar)
        
        return container
```

### Using Touch Gestures

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

## Testing

### Integration Tests

Run the mobile UI integration tests:

```bash
python -m pytest control/native_gui/tests/test_mobile_ui_integration.py -v
```

### Manual Testing

1. **Viewport Testing**: Resize window to test responsive breakpoints
2. **Touch Testing**: Use touch input or simulate with mouse
3. **Theme Testing**: Switch between light/dark themes
4. **Performance Testing**: Monitor memory usage and rendering performance

## Best Practices

### Mobile-First Design

1. **Start with Mobile**: Design for mobile constraints first
2. **Progressive Enhancement**: Add features for larger viewports
3. **Touch Targets**: Minimum 44px touch targets
4. **Content Priority**: Show most important content first on mobile

### Performance

1. **Lazy Loading**: Load viewport-specific widgets on demand
2. **CSS Optimization**: Use efficient selectors and minimal reflows
3. **Memory Management**: Clean up viewport widgets when switching
4. **Animation**: Use CSS transitions for smooth interactions

### Accessibility

1. **High Contrast**: Support high contrast themes
2. **Keyboard Navigation**: Ensure all functionality is keyboard accessible
3. **Screen Readers**: Provide proper ARIA labels and descriptions
4. **Focus Management**: Maintain logical focus order

## Troubleshooting

### Common Issues

1. **Widget Not Responsive**: Check if tool implements `_create_viewport_widget()`
2. **CSS Not Applied**: Verify CSS provider is loaded and has correct priority
3. **Touch Gestures Not Working**: Ensure gesture controllers are properly set up
4. **Memory Leaks**: Check that viewport widgets are properly cleaned up

### Debug Mode

Enable debug logging for mobile UI components:

```python
import logging
logging.getLogger('mobile_ui').setLevel(logging.DEBUG)
```

## API Reference

### Core Classes

- `ResponsiveLayout`: Base responsive widget
- `ToolViewport`: Viewport enumeration
- `ThemeManager`: Enhanced theme management
- `BaseTool`: Enhanced tool base class
- `MobileUIBuilder`: Build system integration

### Component Classes

- `Card`: Responsive card component
- `StatusIndicator`: Status display
- `MetricCard`: Metric visualization
- `TouchButton`: Touch-optimized button
- `SwipeableContainer`: Swipe navigation

### Integration Classes

- `InputMonitorWidget`: Input monitoring interface
- `HotkeyConfigWidget`: Hotkey configuration
- `PrivacyControlWidget`: Privacy controls

## Contributing

When contributing to the mobile UI framework:

1. **Follow Patterns**: Use established responsive design patterns
2. **Test Viewports**: Test on all three viewport sizes
3. **Document Changes**: Update this documentation for new features
4. **Performance**: Consider performance impact of changes
5. **Accessibility**: Ensure changes maintain accessibility standards

## License

This mobile UI framework is part of the Unhinged project and follows the same licensing terms.
