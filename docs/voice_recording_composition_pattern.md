# Voice Recording Composition Pattern

## Overview

The Unhinged voice recording system implements a composition pattern that allows for flexible, non-destructive voice input with unlimited recording duration and seamless text editing integration.

## Core Principles

### 1. **Non-Destructive Composition**
- Multiple recordings can be made without erasing previous content
- Each recording appends to existing text with proper spacing
- Users maintain full control over the final composed message

### 2. **Unlimited Duration Recording**
- No artificial time limits on recording length
- Native OS audio capabilities (arecord) for optimal performance
- Clean signal handling for user-controlled stop

### 3. **Seamless Text Integration**
- Voice transcripts integrate naturally with typed text
- Users can edit transcribed content before sending
- Mixed input modes (voice + typing) supported

## Architecture Components

### AudioHandler (`control/gtk4_gui/handlers/audio_handler.py`)
```python
class AudioHandler:
    """Handles audio recording and transcription operations"""
    
    # State management
    - RecordingState.IDLE
    - RecordingState.RECORDING  
    - RecordingState.PROCESSING
    - RecordingState.ERROR
    
    # Core methods
    - start_recording()  # Uncapped duration
    - stop_recording()   # User-controlled
    - Callback system for UI updates
```

### Voice Visualizer (`control/gtk4_gui/components/voice_visualizer.py`)
```python
class VoiceVisualizer:
    """Reusable voice visualization component"""
    
    # Visualization modes
    - VisualizationMode.WAVEFORM
    - VisualizationMode.PULSE
    - VisualizationMode.BARS
    - VisualizationMode.MINIMAL
    
    # State synchronization
    - set_recording_state()
    - set_processing_state()
    - Real-time visual feedback
```

### ChatroomView Integration (`control/gtk4_gui/views/chatroom_view.py`)
```python
class ChatroomView:
    """OS Chatroom implementation with voice composition"""
    
    # Composition behavior
    - add_voice_transcript()  # Appends to existing content
    - Non-destructive editing
    - Visual state management
```

## User Experience Flow

### Recording Initiation
1. User clicks microphone button
2. Visual feedback begins (button state + visualizer)
3. Timer starts showing MM:SS elapsed time
4. No duration limits - record as long as needed

### Recording Active State
```
[Text Editor with existing content]
[🔴 Visualizer] [⏹️ Stop Button] [Send]
Tooltip: "Recording 01:23 (click to stop)"
```

### Recording Completion
1. User clicks stop button
2. Visual feedback shows processing state
3. Transcript is generated via speech-to-text service
4. Content is appended to text editor with spacing

### Content Composition
```
Before: "Hello, I wanted to discuss"
After:  "Hello, I wanted to discuss the project timeline and deliverables."
```

## Implementation Pattern

### 1. **State Management**
```python
# Recording state
self._is_recording = False
self._recording_start_time = None
self._recording_timer_id = None

# Visual components
self._voice_visualizer = VoiceVisualizerFactory.create_recording_indicator()
self._chatroom_voice_button = ActionButton(...)
```

### 2. **Toggle Recording Logic**
```python
def _on_chatroom_voice_toggle(self, button):
    if not self._is_recording:
        self._start_toggle_recording()
    else:
        self._stop_toggle_recording()
```

### 3. **Content Composition**
```python
def add_voice_transcript(self, transcript):
    current_text = self._chat_input.get_content()
    if current_text.strip():
        # Append with spacing
        new_text = f"{current_text} {transcript}"
    else:
        # Set as new content
        new_text = transcript
    
    self._chat_input.set_content(new_text)
```

### 4. **Visual Feedback Integration**
```python
# Start recording
self._voice_visualizer.set_recording_state(True)
self._start_recording_timer()

# Processing
self._voice_visualizer.set_processing_state(True)

# Complete
self._voice_visualizer.set_processing_state(False)
```

## Key Benefits

### For Users
- **Natural workflow**: Record, edit, send
- **No time pressure**: Unlimited recording duration
- **Flexible composition**: Mix voice and text input
- **Visual feedback**: Clear state indication
- **Error recovery**: Can re-record if needed

### For Developers
- **Reusable components**: VoiceVisualizer, AudioHandler
- **Clean separation**: UI, audio handling, transcription
- **Extensible**: Easy to add new visualization modes
- **Testable**: Clear interfaces and state management

## Future Considerations

### Potential Enhancements
- **Multiple recording segments**: Record → Edit → Record more
- **Voice note previews**: Play back before transcription
- **Transcript editing**: Inline correction of transcribed text
- **Voice commands**: "Delete last sentence", "New paragraph"

### UI Polish (Deferred)
- **Rounded corners**: Text editor visual improvements
- **Subtle animations**: Smooth state transitions
- **Drop shadows**: Enhanced visual depth
- **Micro-interactions**: Button hover states

## Consistency Guidelines

### For Future Implementations
1. **Always use AudioHandler**: Don't create separate audio logic
2. **Include VoiceVisualizer**: Provide visual feedback
3. **Support composition**: Append, don't replace content
4. **Unlimited duration**: No artificial time limits
5. **Clean state management**: Clear recording/processing/idle states
6. **Minimal toast notifications**: Let visual components show state

### Component Reuse
```python
# Standard pattern for voice-enabled components
from ..components.voice_visualizer import VoiceVisualizerFactory
from ..handlers.audio_handler import AudioHandler

# Create visualizer
visualizer = VoiceVisualizerFactory.create_recording_indicator()

# Connect to AudioHandler
audio_handler.set_callbacks(
    state_callback=self._on_recording_state_change,
    result_callback=self._on_transcript_received
)
```

This composition pattern ensures consistent, professional voice recording behavior across all components while maintaining flexibility for different use cases and UI contexts.
