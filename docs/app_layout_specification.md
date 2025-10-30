# Unhinged Desktop Application Layout Specification

## Overview

The Unhinged desktop application uses a **two-body layout** with a fixed sidebar navigation and dynamic main content area. This specification defines the exact structure, behavior, and styling requirements.

## Layout Architecture

### Primary Structure
```
┌─────────────────────────────────────────────────────────┐
│ Adw.ApplicationWindow (1200x800)                        │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Adw.ToastOverlay                                    │ │
│ │ ┌─────────────────────────────────────────────────┐ │ │
│ │ │ Adw.NavigationSplitView                         │ │ │
│ │ │ ┌─────────┬─────────────────────────────────────┐ │ │ │
│ │ │ │ Sidebar │ Main Content Area                   │ │ │ │
│ │ │ │ (240px) │ (Flexible)                          │ │ │ │
│ │ │ │         │                                     │ │ │ │
│ │ │ └─────────┴─────────────────────────────────────┘ │ │ │
│ │ └─────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Component Hierarchy
```
Adw.ApplicationWindow
└── Adw.ToastOverlay (notifications)
    └── Adw.NavigationSplitView (two-pane layout)
        ├── Sidebar (Adw.NavigationPage)
        │   └── Gtk.ScrolledWindow
        │       └── Gtk.ListBox (navigation items)
        │           └── Gtk.ListBoxRow[] (nav items)
        └── Content (Adw.NavigationPage)
            └── Adw.ViewStack (page container)
                ├── Main Page
                ├── Status Page
                ├── System Info Page
                ├── Processes Page
                ├── Input Page
                ├── OS Chatroom Page ← Voice recording
                ├── Bluetooth Page
                └── Output Page
```

## Sidebar Navigation Specification

### Dimensions & Styling
- **Width**: Fixed 240px
- **Background**: `var(--color-surface-default, #ffffff)`
- **Scrolling**: Vertical auto, horizontal never
- **Selection**: Single selection mode

### Navigation Items
```python
nav_items = [
    ("main", "Main", "applications-system-symbolic"),
    ("status", "Status", "dialog-information-symbolic"),
    ("system", "System Info", "computer-symbolic"),
    ("processes", "Processes", "system-run-symbolic"),
    ("input", "Input", "audio-input-microphone-symbolic"),
    ("chatroom", "OS Chatroom", "user-available-symbolic"),  # ← Voice recording
    ("bluetooth", "Bluetooth", "bluetooth-symbolic"),
    ("output", "Output", "audio-speakers-symbolic"),
]
```

### Row Structure
```
┌─────────────────────────────────┐
│ Gtk.ListBoxRow                  │
│ ┌─────────────────────────────┐ │
│ │ Gtk.Box (horizontal)        │ │
│ │ ┌───┐ ┌─────────────────────┐ │ │
│ │ │ 🔊│ │ OS Chatroom         │ │ │
│ │ └───┘ └─────────────────────┘ │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

### Active State Styling
- **Active Row**: `.sidebar-nav-active` class
- **Background**: `var(--color-action-primary, #0969da)`
- **Text Color**: White/contrasting color
- **Behavior**: Single active item, exclusive selection

## Main Content Area Specification

### Content Stack (Adw.ViewStack)
- **Expansion**: Both horizontal and vertical
- **Page Management**: Named pages with titles and icons
- **Switching**: Controlled by sidebar selection
- **Default Page**: "main"

### Page Creation Pattern
```python
def create_page_content():
    """Standard pattern for page creation"""
    try:
        # Import view class
        from .views.page_view import PageView
        
        # Create view instance
        view = PageView(self)
        
        # Return content widget
        return view.create_content()
        
    except Exception as e:
        # Log error and re-raise (NO FALLBACKS)
        print(f"❌ Error creating page: {e}")
        raise  # Let the error bubble up
```

### OS Chatroom Page (Voice Recording)
```
┌─────────────────────────────────────────────────────────┐
│ OS Chatroom Content                                     │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Chat History Area                                   │ │
│ │ (Scrollable message list)                           │ │
│ │                                                     │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Input Area                                          │ │
│ │ ┌─────────────────────────┬─────────┬─────────────┐ │ │
│ │ │ Text Editor             │ Voice   │ Send Button │ │ │
│ │ │ (Expandable)            │ Section │             │ │ │
│ │ │                         │ [🔴][🎤]│             │ │ │
│ │ └─────────────────────────┴─────────┴─────────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Error Handling Strategy

### NO FALLBACKS PRINCIPLE
- **Never create fallback content** for failed page creation
- **Let errors bubble up** to identify root causes
- **Fix the actual issues** instead of masking them
- **Provide clear error messages** for debugging

### Error Handling Pattern
```python
def _add_stack_pages(self):
    """Add all pages to the content stack - NO FALLBACKS"""
    pages = [
        ("chatroom", "OS Chatroom", self.app.create_chatroom_tab_content),
        # ... other pages
    ]
    
    for page_id, title, create_func in pages:
        try:
            content = create_func()
            page = self.app.content_stack.add_titled(content, page_id, title)
            page.set_icon_name(self._get_page_icon(page_id))
        except Exception as e:
            print(f"❌ CRITICAL: {title} page creation failed: {e}")
            # DO NOT CREATE FALLBACK - Let it fail and fix the root cause
            raise Exception(f"Page creation failed for {title}: {e}")
```

## Voice Recording Integration

### Component Requirements
- **AudioHandler**: Must be properly initialized
- **VoiceVisualizer**: Optional visual feedback component
- **Service Connectivity**: Speech-to-text service must be available
- **Error Handling**: Graceful degradation without fallbacks

### Integration Points
1. **Sidebar Navigation**: "OS Chatroom" item with microphone icon
2. **Content Area**: ChatroomView with voice recording UI
3. **Toast Notifications**: Minimal, professional feedback
4. **State Management**: Recording/processing/idle states

## CSS Classes & Styling

### Navigation Sidebar
```css
.navigation-sidebar {
    background-color: var(--color-surface-default, #ffffff);
    border-right: 1px solid var(--color-border-default, #e1e4e8);
}

.sidebar-nav-row {
    padding: 8px 12px;
    border-radius: 6px;
    margin: 2px 8px;
}

.sidebar-nav-active {
    background-color: var(--color-action-primary, #0969da);
    color: white;
}

.sidebar-nav-row:hover {
    background-color: var(--color-surface-hover, #f6f8fa);
}
```

### Voice Recording States
```css
.recording-active {
    background-color: var(--color-error, #dc3545) !important;
    color: white;
}

.processing-active {
    background-color: var(--color-warning, #fd7e14) !important;
    color: white;
}
```

## Implementation Requirements

### 1. Remove All Fallback Logic
- Delete `_create_fallback()` method
- Remove `_create_fallback_content()` from UIController
- Remove try/catch fallback patterns in page creation

### 2. Fix Root Causes
- Ensure ChatroomView imports correctly
- Fix VoiceVisualizer GTK4 compatibility
- Verify all component dependencies

### 3. Robust Error Reporting
- Clear error messages for debugging
- Proper exception propagation
- No silent failures or masking

### 4. Professional UX
- Clean, minimal interface
- Responsive layout behavior
- Consistent navigation patterns
- Professional error handling

## Testing Requirements

### Layout Verification
- [ ] Sidebar fixed at 240px width
- [ ] Content area expands to fill remaining space
- [ ] Navigation selection changes content area
- [ ] Active state styling works correctly

### Voice Recording Verification
- [ ] OS Chatroom page loads without errors
- [ ] Voice recording button appears and functions
- [ ] Timer shows MM:SS format during recording
- [ ] Transcription integrates with text editor

### Error Handling Verification
- [ ] No fallback content appears anywhere
- [ ] Clear error messages for failed components
- [ ] Application doesn't crash on component failures
- [ ] Root causes are identifiable and fixable

This specification ensures a robust, professional two-body layout with proper error handling and no fallback masking of real issues.
