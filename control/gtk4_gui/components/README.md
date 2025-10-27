# Unhinged GTK4 Component Library

A focused, practical component library for GTK4 applications that integrates seamlessly with the Unhinged design system.

## 🎯 **Design Principles**

- **Design System Integration**: Uses semantic tokens from `libs/design_system/`
- **Libadwaita First**: Builds on Adw widgets for native GNOME experience  
- **Focused Components**: Only components actually needed by the application
- **Type Safety**: Proper GTK4 typing and signal handling
- **Accessibility**: ARIA labels, keyboard navigation, screen reader support

## 📦 **Components Overview**

### **Primitives** (Basic building blocks)
- **`ActionButton`** - Enhanced button with design system integration
- **`StatusLabel`** - Label with semantic status styling  
- **`ProgressIndicator`** - Progress bar with text and percentage

### **Containers** (Layout and grouping)
- **`StatusCard`** - Card displaying status information with actions
- **`ServicePanel`** - Panel for service information and controls
- **`LogContainer`** - Scrollable container for log content

### **Complex** (Stateful components)
- **`LogViewer`** - Advanced log viewer with filtering and search
- **`ServiceRow`** - Complete service status row with controls
- **`SystemStatus`** - Overall system status display

## 🚀 **Quick Start**

### 1. Import Components

```python
from control.gtk4_gui.components import (
    ActionButton, StatusLabel, ProgressIndicator,
    StatusCard, ServicePanel, LogViewer,
    SystemStatus
)
```

### 2. Load Component CSS

```python
def load_component_css(self):
    """Load component CSS in your application."""
    css_provider = Gtk.CssProvider()
    css_path = Path(__file__).parent / "components" / "components.css"
    css_provider.load_from_path(str(css_path))
    
    Gtk.StyleContext.add_provider_for_display(
        self.window.get_display(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
```

### 3. Use Components

```python
# Create an action button
start_button = ActionButton(
    label="Start Service",
    style="primary",
    icon_name="media-playback-start-symbolic"
)
start_button.connect('clicked', self.on_start_clicked)

# Create a status card
status_card = StatusCard(
    title="Service Health",
    status="success",
    subtitle="All systems operational",
    icon_name="emblem-ok-symbolic"
)

# Add to your layout
container.append(start_button.get_widget())
container.append(status_card.get_widget())
```

## 🔧 **Integration with Existing App**

### Replace Existing Widgets

**Before** (in your `desktop_app.py`):
```python
# Old button creation
self.start_button = Gtk.Button.new_with_label("Start Platform")
self.start_button.add_css_class("suggested-action")
```

**After** (with components):
```python
# New component usage
self.start_button = ActionButton(
    label="Start Platform",
    style="primary",
    icon_name="media-playback-start-symbolic"
)
```

### Service Status Integration

```python
# Update your get_service_status method
def update_service_display(self, services_data):
    """Update UI with service status using components."""
    
    # Create system status overview
    system_status = SystemStatus()
    system_status.update_services(services_data)
    
    # Create individual service rows
    for name, data in services_data.items():
        service_row = ServiceRow(name, data)
        service_row.connect('action-requested', self.on_service_action)
        self.services_container.append(service_row.get_widget())
```

### Log Display Enhancement

```python
# Replace basic text view with LogViewer
self.log_viewer = LogViewer()
self.log_viewer.connect('export-requested', self.on_export_logs)

# Add logs with proper formatting
self.log_viewer.append_log(
    message="Service started successfully",
    level="INFO",
    timestamp="10:30:15"
)
```

## 🎨 **Design System Integration**

Components automatically use your design system tokens:

```css
/* Components use semantic tokens */
.ds-action-primary {
  background-color: var(--color-action-primary);
  color: var(--color-action-primary-text);
}

.ds-status-success {
  background-color: var(--color-status-success-bg);
  color: var(--color-status-success);
}
```

## 📱 **Accessibility Features**

All components include:
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader Support**: Proper ARIA labels and roles
- **High Contrast**: Enhanced visibility in high contrast mode
- **Reduced Motion**: Respects motion preferences

## 🧪 **Testing Components**

Run the example application:

```bash
cd control/gtk4_gui/components
python3 example_usage.py
```

This shows all components in action with practical examples.

## 🔄 **Component Lifecycle**

### State Management
```python
# Components emit signals for state changes
component.connect('state-changed', self.on_component_state_changed)
component.connect('action-triggered', self.on_component_action)

# Update component state
component.set_state('loading', True)
status = component.get_state('status', 'unknown')
```

### Event Handling
```python
# Components provide semantic events
button.connect('clicked', self.on_button_clicked)
service_row.connect('action-requested', self.on_service_action)
log_viewer.connect('filter-changed', self.on_log_filter_changed)
```

## 🎯 **Best Practices**

1. **Use Semantic Styling**: Always use design system classes (`ds-*`)
2. **Handle Signals**: Connect to component signals for proper event handling
3. **Load CSS**: Always load component CSS for proper styling
4. **Accessibility**: Set proper labels and roles for screen readers
5. **State Management**: Use component state methods for consistency

## 🔧 **Extending Components**

Create custom components by extending base classes:

```python
from .base import AdwComponentBase

class CustomComponent(AdwComponentBase):
    def __init__(self, **kwargs):
        super().__init__("custom-component", **kwargs)
    
    def _init_component(self, **kwargs):
        self.widget = Gtk.Box()
        # Custom implementation
```

## 📚 **API Reference**

See individual component files for detailed API documentation:
- `primitives.py` - Basic components
- `containers.py` - Layout components  
- `complex.py` - Advanced components
- `base.py` - Base classes and utilities
