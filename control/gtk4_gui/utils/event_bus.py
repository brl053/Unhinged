"""
Unified Event Bus for Unhinged.

Provides a centralized event subscription and emission system to eliminate
custom callback patterns across the codebase. Supports multiple subscribers
per event and type-safe event handling.

Eliminates 50+ lines of duplicate callback management code.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Base event class for type-safe event handling."""

    event_type: str
    data: Any = None

    def __repr__(self) -> str:
        return f"Event({self.event_type}, {self.data})"


class EventBus:
    """
    Centralized event bus for publish-subscribe pattern.

    Eliminates custom callback management across handlers and monitors.
    Supports multiple subscribers per event type.

    Supports both patterns:
    - Global singleton: get_event_bus() for backward compatibility
    - Dependency injection: Pass EventBus instance to components
    """

    def __init__(self, max_history: int = 100):
        """Initialize event bus.

        Args:
            max_history: Maximum number of events to keep in history (default: 100)
        """
        self._subscribers: dict[str, list[Callable]] = {}
        self._event_history: list[Event] = []
        self._max_history = max_history
        self._metrics = {
            "total_events_emitted": 0,
            "total_subscriptions": 0,
            "total_unsubscriptions": 0,
        }

    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> Callable[[], None]:
        """
        Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is emitted

        Returns:
            Unsubscribe function to remove this subscription
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        self._subscribers[event_type].append(callback)
        self._metrics["total_subscriptions"] += 1

        # Return unsubscribe function
        def unsubscribe():
            if event_type in self._subscribers and callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                self._metrics["total_unsubscriptions"] += 1

        return unsubscribe

    def unsubscribe(self, event_type: str, callback: Callable[[Event], None]) -> bool:
        """
        Unsubscribe from an event type.

        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove

        Returns:
            True if callback was found and removed, False otherwise
        """
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
            return True
        return False

    def emit(self, event: Event, strict_errors: bool = False) -> None:
        """
        Emit an event to all subscribers.

        Args:
            event: Event to emit
            strict_errors: If True, raise exceptions from callbacks. If False, log and continue.
                          Useful for development (strict=True) vs production (strict=False).
        """
        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        self._metrics["total_events_emitted"] += 1

        # Call all subscribers for this event type
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    error_msg = f"Error in event callback for {event.event_type}: {e}"
                    logger.error(error_msg)
                    if strict_errors:
                        raise

    def emit_simple(self, event_type: str, data: Any = None) -> None:
        """
        Emit an event with simple parameters.

        Args:
            event_type: Type of event
            data: Event data
        """
        event = Event(event_type=event_type, data=data)
        self.emit(event)

    def get_subscribers(self, event_type: str) -> int:
        """
        Get number of subscribers for an event type.

        Args:
            event_type: Type of event

        Returns:
            Number of subscribers
        """
        return len(self._subscribers.get(event_type, []))

    def get_event_history(self, event_type: str | None = None) -> list[Event]:
        """
        Get event history.

        Args:
            event_type: Optional filter by event type

        Returns:
            List of events
        """
        if event_type:
            return [e for e in self._event_history if e.event_type == event_type]
        return self._event_history.copy()

    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()

    def clear_subscribers(self, event_type: str | None = None) -> None:
        """
        Clear subscribers.

        Args:
            event_type: Optional specific event type to clear
        """
        if event_type:
            if event_type in self._subscribers:
                self._subscribers[event_type].clear()
        else:
            self._subscribers.clear()

    def get_metrics(self) -> dict:
        """
        Get event bus metrics for monitoring and debugging.

        Returns:
            Dictionary with metrics:
            - total_events_emitted: Total events emitted
            - total_subscriptions: Total subscriptions created
            - total_unsubscriptions: Total subscriptions removed
            - active_subscriptions: Current active subscriptions
            - event_types: Number of unique event types
        """
        active_subs = sum(len(subs) for subs in self._subscribers.values())
        return {
            **self._metrics,
            "active_subscriptions": active_subs,
            "event_types": len(self._subscribers),
            "history_size": len(self._event_history),
        }


# Global event bus instance
_global_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """
    Get or create the global event bus instance.

    BACKWARD COMPATIBILITY: This function maintains the global singleton pattern
    for existing code. New code should prefer dependency injection by passing
    EventBus instances explicitly to components.

    Migration path:
    1. Create EventBus instance in app initialization
    2. Pass to components via constructor (dependency injection)
    3. Remove get_event_bus() calls once all components migrated

    Returns:
        Global EventBus instance
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def reset_event_bus() -> None:
    """Reset the global event bus (useful for testing)."""
    global _global_event_bus
    _global_event_bus = None


def create_event_bus(max_history: int = 100) -> EventBus:
    """
    Create a new EventBus instance for dependency injection.

    RECOMMENDED: Use this for new components instead of get_event_bus().
    Enables better testability and explicit dependency management.

    Args:
        max_history: Maximum events to keep in history

    Returns:
        New EventBus instance
    """
    return EventBus(max_history=max_history)


# Common event types
class AudioEvents:
    """Audio-related event types."""

    # Recording lifecycle
    RECORDING_STARTED = "audio:recording_started"
    RECORDING_STOPPED = "audio:recording_stopped"
    DEVICE_CHANGED = "audio:device_changed"
    ERROR = "audio:error"

    # Real-time audio level monitoring
    AMPLITUDE_UPDATED = "audio:amplitude_updated"  # Emitted by AudioLevelMonitor with {"amplitude": float}

    # Visualization state changes
    VISUALIZATION_STATE_CHANGED = "audio:visualization_state_changed"  # Emitted by VoiceVisualizer with {"state": str}

    # Granular transcription events (preferred over callbacks)
    TRANSCRIPTION_STARTED = "audio:transcription_started"
    TRANSCRIPTION_PROGRESS = "audio:transcription_progress"
    TRANSCRIPTION_COMPLETED = "audio:transcription_completed"
    TRANSCRIPTION_ERROR = "audio:transcription_error"

    # DEPRECATED: AMPLITUDE_UPDATED was misused for transcription data
    # Use TRANSCRIPTION_COMPLETED instead
    TRANSCRIPTION_LEGACY = "audio:amplitude_updated"  # Backward compat only


class SystemEvents:
    """System-related event types."""

    GPU_STATUS_UPDATED = "system:gpu_status_updated"
    USB_DEVICES_UPDATED = "system:usb_devices_updated"
    AUDIO_DEVICES_UPDATED = "system:audio_devices_updated"
    ERROR = "system:error"
