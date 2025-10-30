"""
Voice Visualization Component

A reusable component for displaying visual feedback during voice recording.
Provides waveform visualization, recording indicators, and state management.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, GLib, Gdk, GObject
import math
import time
from typing import Optional, Callable
from enum import Enum


class VisualizationMode(Enum):
    """Visualization modes for the voice component"""
    WAVEFORM = "waveform"
    PULSE = "pulse"
    BARS = "bars"
    MINIMAL = "minimal"


class VoiceVisualizer(Gtk.DrawingArea):
    """Voice visualization component with multiple display modes"""
    
    def __init__(self, 
                 mode: VisualizationMode = VisualizationMode.PULSE,
                 width: int = 200,
                 height: int = 60):
        """Initialize voice visualizer
        
        Args:
            mode: Visualization mode
            width: Component width in pixels
            height: Component height in pixels
        """
        super().__init__()
        
        # Configuration
        self.mode = mode
        self.width = width
        self.height = height
        
        # State
        self.is_recording = False
        self.is_processing = False
        self.amplitude = 0.0
        self.animation_time = 0.0
        
        # Animation data
        self.waveform_data = [0.0] * 50  # 50 sample points
        self.bars_data = [0.0] * 8       # 8 frequency bars
        
        # Callbacks
        self.state_callback: Optional[Callable[[str], None]] = None
        
        # Setup widget
        self.set_size_request(width, height)
        self.set_can_focus(False)

        # Animation timer
        self.animation_timer_id = None

        # Setup drawing for GTK4
        self.set_draw_func(self._on_draw, None)
        
    def set_recording_state(self, recording: bool) -> None:
        """Set recording state and update visualization"""
        if self.is_recording != recording:
            self.is_recording = recording
            
            if recording:
                self._start_animation()
            else:
                self._stop_animation()
                
            self.queue_draw()
            
            if self.state_callback:
                self.state_callback("recording" if recording else "idle")
    
    def set_processing_state(self, processing: bool) -> None:
        """Set processing state and update visualization"""
        if self.is_processing != processing:
            self.is_processing = processing
            
            if processing:
                self._start_animation()
            else:
                self._stop_animation()
                
            self.queue_draw()
            
            if self.state_callback:
                self.state_callback("processing" if processing else "idle")
    
    def set_amplitude(self, amplitude: float) -> None:
        """Set current audio amplitude (0.0 to 1.0)"""
        self.amplitude = max(0.0, min(1.0, amplitude))
        
        # Update visualization data based on mode
        if self.mode == VisualizationMode.WAVEFORM:
            self._update_waveform_data()
        elif self.mode == VisualizationMode.BARS:
            self._update_bars_data()
            
        self.queue_draw()
    
    def set_mode(self, mode: VisualizationMode) -> None:
        """Change visualization mode"""
        self.mode = mode
        self.queue_draw()
    
    def connect_state_callback(self, callback: Callable[[str], None]) -> None:
        """Connect state change callback"""
        self.state_callback = callback
    
    def _start_animation(self) -> None:
        """Start animation timer"""
        if self.animation_timer_id is None:
            self.animation_timer_id = GLib.timeout_add(50, self._animate)  # 20 FPS
    
    def _stop_animation(self) -> None:
        """Stop animation timer"""
        if self.animation_timer_id is not None:
            GLib.source_remove(self.animation_timer_id)
            self.animation_timer_id = None
    
    def _animate(self) -> bool:
        """Animation callback"""
        self.animation_time += 0.05  # 50ms increment
        
        # Generate simulated audio data if recording
        if self.is_recording:
            # Simulate varying amplitude
            base_amplitude = 0.3 + 0.4 * math.sin(self.animation_time * 2)
            noise = 0.1 * math.sin(self.animation_time * 15)
            self.set_amplitude(base_amplitude + noise)
        elif self.is_processing:
            # Gentle pulsing for processing
            self.amplitude = 0.2 + 0.1 * math.sin(self.animation_time * 3)
            self.queue_draw()
        
        return True  # Continue animation
    
    def _update_waveform_data(self) -> None:
        """Update waveform visualization data"""
        # Shift existing data left
        self.waveform_data = self.waveform_data[1:] + [self.amplitude]
    
    def _update_bars_data(self) -> None:
        """Update frequency bars visualization data"""
        # Simulate frequency distribution
        for i in range(len(self.bars_data)):
            frequency_factor = 1.0 - (i / len(self.bars_data))
            self.bars_data[i] = self.amplitude * frequency_factor * (0.8 + 0.4 * math.sin(self.animation_time * (i + 1)))
    
    def _on_draw(self, area, cr, width, height, user_data) -> None:
        """Draw the visualization"""
        # Clear background
        cr.set_source_rgba(0, 0, 0, 0.1)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        
        # Set drawing color based on state
        if self.is_recording:
            cr.set_source_rgba(0.2, 0.7, 0.9, 0.8)  # Blue for recording
        elif self.is_processing:
            cr.set_source_rgba(0.9, 0.6, 0.2, 0.8)  # Orange for processing
        else:
            cr.set_source_rgba(0.5, 0.5, 0.5, 0.5)  # Gray for idle
        
        # Draw based on mode
        if self.mode == VisualizationMode.WAVEFORM:
            self._draw_waveform(cr, width, height)
        elif self.mode == VisualizationMode.PULSE:
            self._draw_pulse(cr, width, height)
        elif self.mode == VisualizationMode.BARS:
            self._draw_bars(cr, width, height)
        elif self.mode == VisualizationMode.MINIMAL:
            self._draw_minimal(cr, width, height)
    
    def _draw_waveform(self, cr, width: int, height: int) -> None:
        """Draw waveform visualization"""
        if not self.waveform_data:
            return
            
        cr.set_line_width(2)
        
        # Draw waveform
        step = width / len(self.waveform_data)
        center_y = height / 2
        
        cr.move_to(0, center_y)
        
        for i, amplitude in enumerate(self.waveform_data):
            x = i * step
            y = center_y + (amplitude - 0.5) * height * 0.8
            cr.line_to(x, y)
        
        cr.stroke()
    
    def _draw_pulse(self, cr, width: int, height: int) -> None:
        """Draw pulse visualization"""
        center_x = width / 2
        center_y = height / 2
        
        # Draw multiple concentric circles
        for i in range(3):
            radius = (self.amplitude * 0.8 + 0.2) * min(width, height) / 2
            radius *= (1.0 - i * 0.3)
            
            alpha = 0.8 - i * 0.2
            cr.set_source_rgba(0.2, 0.7, 0.9, alpha)
            
            cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
            cr.fill()
    
    def _draw_bars(self, cr, width: int, height: int) -> None:
        """Draw frequency bars visualization"""
        if not self.bars_data:
            return
            
        bar_width = width / len(self.bars_data)
        
        for i, amplitude in enumerate(self.bars_data):
            x = i * bar_width
            bar_height = amplitude * height * 0.9
            y = height - bar_height
            
            cr.rectangle(x + 2, y, bar_width - 4, bar_height)
            cr.fill()
    
    def _draw_minimal(self, cr, width: int, height: int) -> None:
        """Draw minimal dot indicator"""
        center_x = width / 2
        center_y = height / 2
        
        # Simple dot that changes size with amplitude
        radius = 4 + self.amplitude * 8
        
        cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
        cr.fill()


class VoiceVisualizerFactory:
    """Factory for creating voice visualizer components"""
    
    @staticmethod
    def create_recording_indicator(compact: bool = False) -> VoiceVisualizer:
        """Create a recording indicator visualizer"""
        if compact:
            return VoiceVisualizer(
                mode=VisualizationMode.MINIMAL,
                width=24,
                height=24
            )
        else:
            return VoiceVisualizer(
                mode=VisualizationMode.PULSE,
                width=60,
                height=60
            )
    
    @staticmethod
    def create_waveform_display(width: int = 200) -> VoiceVisualizer:
        """Create a waveform display visualizer"""
        return VoiceVisualizer(
            mode=VisualizationMode.WAVEFORM,
            width=width,
            height=40
        )
    
    @staticmethod
    def create_frequency_bars() -> VoiceVisualizer:
        """Create a frequency bars visualizer"""
        return VoiceVisualizer(
            mode=VisualizationMode.BARS,
            width=120,
            height=50
        )
