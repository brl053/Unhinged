"""
@llm-doc Standard IO Abstraction Layer for Event Framework
@llm-version 1.0.0
@llm-date 2025-01-26

Standard IO abstraction that allows routing stdout/stderr to different handlers
based on message level and source. Similar to how GUI components are abstracted
into GTK4 literals, IO events are abstracted into structured events that can be
routed to CLI, logs, UI status stack, or other handlers.

## Architecture

IOEvent: Structured representation of a stdout/stderr message
  - message: The actual text
  - level: 'info', 'warning', 'error', 'debug', 'success'
  - source: 'startup', 'discovery', 'ui', 'bluetooth', etc
  - timestamp: When the event occurred

IORouter: Routes events to appropriate handlers
  - Maintains handlers per level
  - Allows filtering by source
  - Supports multiple handlers per level

IOHandler: Base class for output handlers
  - CLIHandler: Prints to stdout with formatting
  - LogHandler: Writes to log files
  - StatusStackHandler: Updates UI status stack
  - BufferHandler: Collects events for analysis
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Optional, Any
from enum import Enum
import logging
import json
import os
from pathlib import Path


class IOLevel(Enum):
    """Standard IO event levels"""
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class SystemCallType(Enum):
    """Types of system calls made by the GUI on behalf of the user"""
    KERNEL_CALL = "kernel_call"  # Direct kernel interaction
    D_BUS_CALL = "dbus_call"  # D-Bus IPC (e.g., BlueZ)
    SUBPROCESS_CALL = "subprocess_call"  # External process execution
    FILE_IO = "file_io"  # File system operations
    NETWORK_CALL = "network_call"  # Network operations
    AUDIO_CALL = "audio_call"  # Audio device operations


@dataclass
class IOEvent:
    """Structured representation of a stdout/stderr message"""
    message: str
    level: IOLevel
    source: str  # 'startup', 'discovery', 'ui', 'bluetooth', etc
    timestamp: datetime = field(default_factory=datetime.now)
    system_call_type: Optional[SystemCallType] = None  # Type of system call if applicable
    system_call_target: Optional[str] = None  # Target of system call (e.g., 'org.bluez', 'arecord')

    def __str__(self) -> str:
        """Format event as string"""
        level_emoji = {
            IOLevel.DEBUG: "🔍",
            IOLevel.INFO: "ℹ️",
            IOLevel.SUCCESS: "✅",
            IOLevel.WARNING: "⚠️",
            IOLevel.ERROR: "❌",
        }
        emoji = level_emoji.get(self.level, "•")

        # Add system call information if present
        system_call_info = ""
        if self.system_call_type:
            call_emoji = {
                SystemCallType.KERNEL_CALL: "🔴",
                SystemCallType.D_BUS_CALL: "🔵",
                SystemCallType.SUBPROCESS_CALL: "⚙️",
                SystemCallType.FILE_IO: "📁",
                SystemCallType.NETWORK_CALL: "🌐",
                SystemCallType.AUDIO_CALL: "🎤",
            }
            call_icon = call_emoji.get(self.system_call_type, "•")
            target_info = f" → {self.system_call_target}" if self.system_call_target else ""
            system_call_info = f" {call_icon}[{self.system_call_type.value}]{target_info}"

        return f"{emoji} [{self.source}] {self.message}{system_call_info}"


class IOHandler:
    """Base class for IO event handlers"""
    
    def handle(self, event: IOEvent) -> None:
        """Handle an IO event"""
        raise NotImplementedError


class EscapeCharacterProcessor:
    """Processes escape sequences in messages"""

    @staticmethod
    def process(text: str) -> str:
        """
        Process escape sequences in text.
        Converts \\n to actual newlines, \\t to tabs, etc.
        """
        # Replace escape sequences
        text = text.replace("\\n", "\n")
        text = text.replace("\\t", "\t")
        text = text.replace("\\r", "\r")
        text = text.replace("\\\\", "\\")
        return text

    @staticmethod
    def emit_blank_line() -> None:
        """Emit a blank line to stdout"""
        print()


class CLIHandler(IOHandler):
    """Handler that prints to stdout with formatting"""

    def __init__(self, include_timestamp: bool = False, process_escapes: bool = True):
        self.include_timestamp = include_timestamp
        self.process_escapes = process_escapes

    def handle(self, event: IOEvent) -> None:
        """Print event to stdout"""
        output = str(event)

        # Process escape sequences if enabled
        if self.process_escapes:
            output = EscapeCharacterProcessor.process(output)

        if self.include_timestamp:
            time_str = event.timestamp.strftime("%H:%M:%S")
            output = f"[{time_str}] {output}"
        print(output)


class LogHandler(IOHandler):
    """Handler that writes to log files"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def handle(self, event: IOEvent) -> None:
        """Log event using Python logging"""
        level_map = {
            IOLevel.DEBUG: self.logger.debug,
            IOLevel.INFO: self.logger.info,
            IOLevel.SUCCESS: self.logger.info,  # Success is info level
            IOLevel.WARNING: self.logger.warning,
            IOLevel.ERROR: self.logger.error,
        }
        handler = level_map.get(IOLevel.INFO)
        handler(f"[{event.source}] {event.message}")


class BufferHandler(IOHandler):
    """Handler that collects events for analysis"""

    def __init__(self, max_events: int = 1000):
        self.events: List[IOEvent] = []
        self.max_events = max_events

    def handle(self, event: IOEvent) -> None:
        """Buffer event"""
        self.events.append(event)
        # Keep buffer size bounded
        if len(self.events) > self.max_events:
            self.events.pop(0)

    def get_events_by_level(self, level: IOLevel) -> List[IOEvent]:
        """Get all events of a specific level"""
        return [e for e in self.events if e.level == level]

    def get_events_by_source(self, source: str) -> List[IOEvent]:
        """Get all events from a specific source"""
        return [e for e in self.events if e.source == source]

    def clear(self) -> None:
        """Clear all buffered events"""
        self.events.clear()


class DelimiterHandler(IOHandler):
    """Handler that groups output by source with clear delimiters"""

    def __init__(self, wrapped_handler: IOHandler, delimiter_char: str = "═"):
        self.wrapped_handler = wrapped_handler
        self.delimiter_char = delimiter_char
        self.current_source: Optional[str] = None
        self.delimiter_width = 70

    def handle(self, event: IOEvent) -> None:
        """Handle event with delimiter grouping"""
        # Emit delimiter if source changed
        if event.source != self.current_source:
            self._emit_delimiter(event.source)
            self.current_source = event.source

        # Emit the actual event
        self.wrapped_handler.handle(event)

    def _emit_delimiter(self, source: str) -> None:
        """Emit a section delimiter with blank lines"""
        delimiter_line = self.delimiter_char * self.delimiter_width
        # Use escape sequences for formatting
        print(f"\n{delimiter_line}")
        print(f"[{source.upper()}]")
        print(f"{delimiter_line}")
        # Emit blank line using escape processor
        EscapeCharacterProcessor.emit_blank_line()

    def emit_footer(self) -> None:
        """Emit a footer delimiter"""
        footer_line = "-" * self.delimiter_width
        print(f"{footer_line}")
        EscapeCharacterProcessor.emit_blank_line()


class StatusStackHandler(IOHandler):
    """Handler that routes IO events to UI status stack component"""

    def __init__(self, status_stack: Optional[Any] = None, max_messages: int = 5):
        """
        Initialize StatusStackHandler

        Args:
            status_stack: Reference to StatusStack UI component (can be set later)
            max_messages: Maximum number of messages to keep in stack
        """
        self.status_stack = status_stack
        self.max_messages = max_messages
        self.message_queue: List[str] = []

    def set_status_stack(self, status_stack: Any) -> None:
        """Set the status stack component reference"""
        self.status_stack = status_stack

    def handle(self, event: IOEvent) -> None:
        """Route event to status stack"""
        # Format message with emoji
        message = str(event)

        # Add to queue
        self.message_queue.append(message)
        if len(self.message_queue) > self.max_messages:
            self.message_queue.pop(0)

        # Try to update status stack if it has the method
        if self.status_stack is not None:
            try:
                if hasattr(self.status_stack, 'add_message'):
                    self.status_stack.add_message(message)
                elif hasattr(self.status_stack, 'push'):
                    self.status_stack.push(message)
            except Exception as e:
                # Silently fail if status stack is not available
                pass

    def get_messages(self) -> List[str]:
        """Get all queued messages"""
        return self.message_queue.copy()

    def clear_messages(self) -> None:
        """Clear all queued messages"""
        self.message_queue.clear()


class FileLogHandler(IOHandler):
    """Handler that writes IO events to persistent log files"""

    def __init__(self, log_dir: str = "/tmp/unhinged/logs", max_file_size: int = 10 * 1024 * 1024):
        """
        Initialize FileLogHandler

        Args:
            log_dir: Directory to store log files
            max_file_size: Maximum size of log file before rotation (default 10MB)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size = max_file_size
        self.current_log_file = self.log_dir / "unhinged.log"

    def handle(self, event: IOEvent) -> None:
        """Write event to log file"""
        try:
            # Check if we need to rotate
            if self.current_log_file.exists() and self.current_log_file.stat().st_size > self.max_file_size:
                self._rotate_log()

            # Format log entry
            timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{event.level.value.upper()}] [{event.source}] {event.message}\n"

            # Write to log file
            with open(self.current_log_file, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            # Silently fail if we can't write to log
            pass

    def _rotate_log(self) -> None:
        """Rotate log file"""
        try:
            # Find next available backup number
            backup_num = 1
            while (self.log_dir / f"unhinged.log.{backup_num}").exists():
                backup_num += 1

            # Rename current log to backup
            backup_file = self.log_dir / f"unhinged.log.{backup_num}"
            self.current_log_file.rename(backup_file)
        except Exception:
            pass


class JSONHandler(IOHandler):
    """Handler that outputs IO events as structured JSON"""

    def __init__(self, output_file: Optional[str] = None):
        """
        Initialize JSONHandler

        Args:
            output_file: File to write JSON events to (if None, uses in-memory buffer)
        """
        self.output_file = output_file
        self.events: List[Dict[str, Any]] = []

    def handle(self, event: IOEvent) -> None:
        """Convert event to JSON and store/output"""
        try:
            event_dict = {
                "timestamp": event.timestamp.isoformat(),
                "level": event.level.value,
                "source": event.source,
                "message": event.message
            }

            self.events.append(event_dict)

            # Write to file if specified
            if self.output_file:
                with open(self.output_file, 'a') as f:
                    f.write(json.dumps(event_dict) + '\n')
        except Exception as e:
            # Silently fail if we can't write JSON
            pass

    def get_events_json(self) -> str:
        """Get all events as JSON array"""
        return json.dumps(self.events, indent=2)

    def clear_events(self) -> None:
        """Clear all buffered events"""
        self.events.clear()


class RemoteHandler(IOHandler):
    """Handler that sends IO events to remote server for centralized logging"""

    def __init__(self, server_url: str, timeout: int = 5):
        """
        Initialize RemoteHandler

        Args:
            server_url: URL of remote logging server (e.g., http://localhost:8080/logs)
            timeout: Request timeout in seconds
        """
        self.server_url = server_url
        self.timeout = timeout
        self.queue: List[Dict[str, Any]] = []
        self.batch_size = 10

    def handle(self, event: IOEvent) -> None:
        """Queue event for remote transmission"""
        try:
            event_dict = {
                "timestamp": event.timestamp.isoformat(),
                "level": event.level.value,
                "source": event.source,
                "message": event.message
            }

            self.queue.append(event_dict)

            # Send batch if queue is full
            if len(self.queue) >= self.batch_size:
                self._send_batch()
        except Exception as e:
            # Silently fail if we can't queue event
            pass

    def _send_batch(self) -> None:
        """Send queued events to remote server"""
        if not self.queue:
            return

        try:
            import urllib.request
            import urllib.error

            # Prepare batch payload
            payload = json.dumps({"events": self.queue}).encode('utf-8')

            # Create request
            req = urllib.request.Request(
                self.server_url,
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            # Send request
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                if response.status == 200:
                    self.queue.clear()
        except Exception as e:
            # Silently fail if we can't send to remote server
            pass

    def flush(self) -> None:
        """Flush any remaining queued events"""
        self._send_batch()

    def get_queue_size(self) -> int:
        """Get number of events in queue"""
        return len(self.queue)


class IORouter:
    """Routes IO events to appropriate handlers"""
    
    def __init__(self):
        self.handlers: Dict[IOLevel, List[IOHandler]] = {
            level: [] for level in IOLevel
        }
        self.global_handlers: List[IOHandler] = []
    
    def register_handler(self, handler: IOHandler, level: Optional[IOLevel] = None) -> None:
        """Register a handler for a specific level or globally"""
        if level is None:
            self.global_handlers.append(handler)
        else:
            self.handlers[level].append(handler)
    
    def unregister_handler(self, handler: IOHandler, level: Optional[IOLevel] = None) -> None:
        """Unregister a handler"""
        if level is None:
            if handler in self.global_handlers:
                self.global_handlers.remove(handler)
        else:
            if handler in self.handlers[level]:
                self.handlers[level].remove(handler)
    
    def emit(self, event: IOEvent) -> None:
        """Emit an IO event to all registered handlers"""
        # Call global handlers
        for handler in self.global_handlers:
            try:
                handler.handle(event)
            except Exception as e:
                print(f"Error in IO handler: {e}")
        
        # Call level-specific handlers
        for handler in self.handlers[event.level]:
            try:
                handler.handle(event)
            except Exception as e:
                print(f"Error in IO handler: {e}")
    
    def emit_info(self, message: str, source: str) -> None:
        """Emit an info event"""
        self.emit(IOEvent(message, IOLevel.INFO, source))
    
    def emit_success(self, message: str, source: str) -> None:
        """Emit a success event"""
        self.emit(IOEvent(message, IOLevel.SUCCESS, source))
    
    def emit_warning(self, message: str, source: str) -> None:
        """Emit a warning event"""
        self.emit(IOEvent(message, IOLevel.WARNING, source))
    
    def emit_error(self, message: str, source: str) -> None:
        """Emit an error event"""
        self.emit(IOEvent(message, IOLevel.ERROR, source))
    
    def emit_debug(self, message: str, source: str) -> None:
        """Emit a debug event"""
        self.emit(IOEvent(message, IOLevel.DEBUG, source))

    def emit_system_call(self, message: str, source: str, call_type: SystemCallType,
                        target: Optional[str] = None, level: IOLevel = IOLevel.INFO) -> None:
        """
        Emit a system call event with kernel interaction documentation.

        Args:
            message: Description of the system call
            source: Source of the event (e.g., 'bluetooth', 'audio')
            call_type: Type of system call (KERNEL_CALL, D_BUS_CALL, etc.)
            target: Target of the system call (e.g., 'org.bluez', 'arecord')
            level: Event level (default INFO)
        """
        event = IOEvent(
            message=message,
            level=level,
            source=source,
            system_call_type=call_type,
            system_call_target=target
        )
        self.emit(event)

    def emit_blank_line(self) -> None:
        """Emit a blank line to stdout"""
        EscapeCharacterProcessor.emit_blank_line()


# Global IO router instance
_global_io_router: Optional[IORouter] = None
_global_delimiter_handler: Optional[DelimiterHandler] = None


def get_io_router() -> IORouter:
    """Get or create the global IO router"""
    global _global_io_router
    if _global_io_router is None:
        _global_io_router = IORouter()
        # Add default CLI handler with delimiters
        cli_handler = CLIHandler(include_timestamp=False)
        delimiter_handler = DelimiterHandler(cli_handler)
        _global_io_router.register_handler(delimiter_handler)
    return _global_io_router


def get_delimiter_handler() -> Optional[DelimiterHandler]:
    """Get the global delimiter handler if it exists"""
    global _global_delimiter_handler
    # Try to find it from the router
    router = get_io_router()
    for handlers in router.handlers.values():
        for handler in handlers:
            if isinstance(handler, DelimiterHandler):
                return handler
    for handler in router.global_handlers:
        if isinstance(handler, DelimiterHandler):
            return handler
    return None


def emit_io_event(message: str, level: IOLevel, source: str) -> None:
    """Emit an IO event using the global router"""
    router = get_io_router()
    router.emit(IOEvent(message, level, source))


def emit_info(message: str, source: str) -> None:
    """Emit an info event"""
    get_io_router().emit_info(message, source)


def emit_success(message: str, source: str) -> None:
    """Emit a success event"""
    get_io_router().emit_success(message, source)


def emit_warning(message: str, source: str) -> None:
    """Emit a warning event"""
    get_io_router().emit_warning(message, source)


def emit_error(message: str, source: str) -> None:
    """Emit an error event"""
    get_io_router().emit_error(message, source)


def emit_debug(message: str, source: str) -> None:
    """Emit a debug event"""
    get_io_router().emit_debug(message, source)

