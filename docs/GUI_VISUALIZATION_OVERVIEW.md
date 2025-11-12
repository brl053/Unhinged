# GUI Visualization Components Overview

## Summary

Your GTK4 GUI has **multiple visualization components** for displaying data and managing documents.

---

## 1. Voice Visualizer 🎙️

**Location**: `control/gtk4_gui/components/voice_visualizer.py`

**Purpose**: Real-time audio visualization during voice recording

**Visualization Modes**:
- **WAVEFORM**: Smooth waveform display (like audio editors)
- **PULSE**: Pulsing circle animation
- **BARS**: Frequency bar visualization (like equalizers)
- **MINIMAL**: Simple amplitude indicator

**Features**:
- Real-time amplitude tracking from audio input
- Smooth animation with configurable speed
- Simulated voice patterns when no real audio
- Processing state visualization
- Event bus integration for state updates

**Usage**:
```python
from control.gtk4_gui.components.voice_visualizer import VoiceVisualizer, VisualizationMode

# Create visualizer
viz = VoiceVisualizer(mode=VisualizationMode.WAVEFORM, width=200, height=60)

# Set amplitude from audio data (0.0 to 1.0)
viz.set_amplitude(0.75)

# Control recording state
viz.start_recording()
viz.stop_recording()
```

---

## 2. Graph Workspace with Tabs 📊

**Location**: `control/gtk4_gui/components/graph_workspace_tabs.py`

**Purpose**: Visual graph editing and management interface

**Three Main Tabs**:

### **📚 Registry Tab**
- Browse saved graphs
- Create new graphs
- Delete graphs
- Open graphs in editor
- Full CRUD interface for documents

### **✏️ Editor Tab**
- Visual graph canvas
- Node editing
- Connection management
- Real-time graph visualization

### **📊 Metrics Tab**
- Execution performance metrics
- Statistics and monitoring
- Performance visualization

**Features**:
- Tabbed interface with visible tab bar
- Document store integration
- Async operations for responsiveness
- Callbacks for edit/delete/create operations

---

## 3. Registry UI (Document Browser) 📚

**Location**: `control/gtk4_gui/components/registry_ui.py`

**Purpose**: CRUD interface for managing graph documents

**Operations**:
- **Create**: Dialog to create new graphs with name, description, type
- **Read**: List all saved graphs with metadata
- **Update**: Edit button to open graph in editor
- **Delete**: Confirmation dialog with async deletion

**Features**:
- Scrollable list of graphs
- Status feedback
- Async operations
- Document store client integration
- Reusable pattern for any document type

---

## 4. Other Visualization Components

### **PerformanceIndicator**
- System performance monitoring
- Real-time metrics display
- Chart visualization

### **LogViewer**
- Advanced log display
- Filtering and search
- Log level filtering
- Export functionality

### **ProcessTable**
- Live process monitoring
- Process management interface
- Real-time updates

### **BluetoothTable**
- Bluetooth device visualization
- Device discovery
- Connection status

### **AudioTable**
- Audio device management
- Volume control visualization
- Device status display

---

## Architecture

```
GUI Visualization Layer
├── Voice Visualizer (Audio feedback)
├── Graph Workspace (Visual editing)
│   ├── Registry Tab (Document browser)
│   ├── Editor Tab (Canvas visualization)
│   └── Metrics Tab (Performance visualization)
├── Performance Indicator (System metrics)
├── Log Viewer (Log visualization)
├── Process Table (Process visualization)
├── Bluetooth Table (Device visualization)
└── Audio Table (Audio device visualization)
```

---

## Integration Points

### Document Store Client
- Connects to Python persistence platform
- Manages graph documents
- Async CRUD operations

### Event Bus
- Voice visualizer state updates
- Audio events
- Recording state management

### Design System
- All components use semantic tokens
- Consistent styling across UI
- Accessible color schemes

---

## Next Steps

To extend visualization capabilities:

1. **Add new visualization modes** to VoiceVisualizer
2. **Create custom chart components** for metrics
3. **Build data visualization widgets** for analytics
4. **Extend Registry UI** for other document types (tools, users, etc.)
5. **Add real-time data streaming** to visualizers

All components follow the **reusable abstraction pattern** established in the design system.

