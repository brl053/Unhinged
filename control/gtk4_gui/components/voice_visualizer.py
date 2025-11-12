"""
Voice Visualization Component

A reusable component for displaying visual feedback during voice recording.
Provides waveform visualization, recording indicators, and state management.
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

import math
import sys
from collections.abc import Callable
from enum import Enum
from pathlib import Path

from gi.repository import GLib, Gtk

# Add utils to path for event_bus import
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from event_bus import get_event_bus, AudioEvents, Event


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
        self.use_real_audio = False  # Flag to indicate real audio data is available

        # Animation data
        self.waveform_data = [0.0] * 50  # 50 sample points
        self.bars_data = [0.0] * 8       # 8 frequency bars

        # Event bus for state updates (replaces callbacks)
        self._event_bus = get_event_bus()

        # Legacy callback for backward compatibility
        self.state_callback: Callable[[str], None] | None = None

        # Setup widget
        self.set_size_request(width, height)
        self.set_can_focus(False)

        # Animation timer
        self.animation_timer_id = None

        # Animation tuning parameters
        self.animation_speed = 0.02  # Slower animation (was 0.05)
        self.amplitude_smoothing = 0.7  # Smooth amplitude changes
        self.previous_amplitude = 0.0  # For smoothing

        # Setup drawing for GTK4
        self.set_draw_func(self._on_draw, None)

    def set_recording_state(self, recording: bool) -> None:
        """Set recording state and update visualization"""
        if self.is_recording != recording:
            self.is_recording = recording

            if recording:
                self.use_real_audio = False  # Reset real audio flag when starting
                self._start_animation()
            else:
                self.use_real_audio = False  # Reset when stopping
                self._stop_animation()

            self.queue_draw()

            # Emit event via event bus
            state = "recording" if recording else "idle"
            self._event_bus.emit_simple(AudioEvents.RECORDING_STARTED if recording else AudioEvents.RECORDING_STOPPED,
                                       {"state": state})

            # Legacy callback support
            if self.state_callback:
                self.state_callback(state)

    def set_processing_state(self, processing: bool) -> None:
        """Set processing state and update visualization"""
        if self.is_processing != processing:
            self.is_processing = processing

            if processing:
                self._start_animation()
            else:
                self._stop_animation()

            self.queue_draw()

            # Emit event via event bus
            state = "processing" if processing else "idle"
            self._event_bus.emit_simple(AudioEvents.AMPLITUDE_UPDATED, {"state": state})

            # Legacy callback support
            if self.state_callback:
                self.state_callback(state)

    def set_amplitude(self, amplitude: float) -> None:
        """Set current audio amplitude (0.0 to 1.0) from real audio data"""
        # Apply smoothing to reduce aggressive animation
        raw_amplitude = max(0.0, min(1.0, amplitude))
        self.amplitude = (self.amplitude_smoothing * self.previous_amplitude +
                         (1 - self.amplitude_smoothing) * raw_amplitude)
        self.previous_amplitude = self.amplitude
        self.use_real_audio = True  # Mark that we're receiving real audio data

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
        """Connect state change callback (DEPRECATED: use event_bus instead)"""
        self.state_callback = callback

    def subscribe_to_state_changes(self, callback: Callable[[Event], None]) -> Callable[[], None]:
        """Subscribe to state changes via event bus

        Args:
            callback: Function to call when state changes

        Returns:
            Unsubscribe function
        """
        return self._event_bus.subscribe(AudioEvents.AMPLITUDE_UPDATED, callback)

    def _start_animation(self) -> None:
        """Start animation timer"""
        if self.animation_timer_id is None:
            self.animation_timer_id = GLib.timeout_add(100, self._animate)  # 10 FPS for smoother animation

    def _stop_animation(self) -> None:
        """Stop animation timer"""
        if self.animation_timer_id is not None:
            GLib.source_remove(self.animation_timer_id)
            self.animation_timer_id = None

    def _animate(self) -> bool:
        """Animation callback"""
        self.animation_time += self.animation_speed  # Slower animation

        # Only use simulated data if we're not receiving real audio data
        if self.is_recording and not self.use_real_audio:
            # Create realistic voice-like waveform using multiple frequencies
            fundamental = 0.4 * math.sin(self.animation_time * 4)  # Base voice frequency
            harmonic1 = 0.2 * math.sin(self.animation_time * 8)    # First harmonic
            harmonic2 = 0.1 * math.sin(self.animation_time * 12)   # Second harmonic
            noise = 0.05 * math.sin(self.animation_time * 25)      # High frequency detail

            # Combine for realistic voice pattern
            voice_amplitude = fundamental + harmonic1 + harmonic2 + noise
            # Normalize to 0.0-1.0 range with some variation
            normalized_amplitude = 0.5 + 0.4 * voice_amplitude
            # Use internal amplitude setting to avoid triggering real audio flag
            self.amplitude = max(0.0, min(1.0, normalized_amplitude))
            self._update_waveform_data()
            self.queue_draw()

        elif self.is_processing:
            # Gentle pulsing for processing state
            self.amplitude = 0.3 + 0.2 * math.sin(self.animation_time * 3)
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
        """Draw realistic waveform visualization"""
        if not self.waveform_data:
            return

        cr.set_line_width(2.0)

        # Draw waveform with smooth curves and enhanced contrast
        step = width / len(self.waveform_data)
        center_y = height / 2

        # Create smooth waveform path
        cr.move_to(0, center_y)

        for i, amplitude in enumerate(self.waveform_data):
            x = i * step
            # Enhanced amplitude scaling for better visual contrast
            # Stretch the amplitude range and add more pronounced peaks/dips
            normalized_amp = (amplitude - 0.5) * 2  # Convert to -1 to 1 range
            enhanced_amp = normalized_amp * abs(normalized_amp)  # Square for more contrast
            wave_height = enhanced_amp * height * 0.4  # Reduced height for better fit
            y = center_y + wave_height

            if i == 0:
                cr.move_to(x, y)
            else:
                # Use curve_to for smoother waveform
                prev_x = (i - 1) * step
                control_x = prev_x + step / 2
                cr.curve_to(control_x, cr.get_current_point()[1],
                           control_x, y, x, y)

        cr.stroke()

        # Add subtle fill under the waveform
        cr.set_source_rgba(0.2, 0.7, 0.9, 0.2)  # Semi-transparent blue
        cr.move_to(0, center_y)
        for i, amplitude in enumerate(self.waveform_data):
            x = i * step
            wave_height = (amplitude - 0.5) * height * 0.7
            y = center_y + wave_height
            cr.line_to(x, y)
        cr.line_to(width, center_y)
        cr.close_path()
        cr.fill()

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
    def create_waveform_display(width: int = 300) -> VoiceVisualizer:
        """Create a horizontal waveform display visualizer for voice recording"""
        return VoiceVisualizer(
            mode=VisualizationMode.WAVEFORM,
            width=width,
            height=50  # Slightly taller for better visibility
        )

    @staticmethod
    def create_frequency_bars() -> VoiceVisualizer:
        """Create a frequency bars visualizer"""
        return VoiceVisualizer(
            mode=VisualizationMode.BARS,
            width=120,
            height=50
        )
