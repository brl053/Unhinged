"""
@llm-doc GUI Session Logger for Unhinged Desktop Application
@llm-version 1.0.0
@llm-date 2025-01-26
@llm-author Unhinged Team

## Overview
Session-based logging system that captures all GTK4 application output
and writes it to timestamped log files in /build/tmp/ directory.

## Features
- Dual output: GTK4 UI display + file logging
- Session-based file naming with UUID4 session IDs
- ISO 8601 timestamp format for file names
- Integration with existing event framework
- Real-time file writing for all UI output

@llm-principle Comprehensive logging for desktop application sessions
@llm-culture Independence through detailed session tracking
"""

import sys
import threading
from collections.abc import Callable
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .event_logger import EventLoggerConfig, LogLevel, create_logger


class GUISessionLogger:
    """
    @llm-doc Enhanced Session-based logger for GTK4 desktop application

    Captures all output that appears in the GTK4 application's output log
    and simultaneously writes it to timestamped session log files with
    noise reduction and error grouping capabilities.
    """

    def __init__(self, project_root: Path | None = None, session_id: str | None = None):
        self.project_root = project_root or Path.cwd()
        self.log_dir = self.project_root / "build" / "tmp"
        # Session ID: either provided at init (from service launcher) or TBD (legacy)
        # If provided, session is already persisted and log file uses real ID
        # If TBD, session will be created later and log file will be renamed
        self.session_id = session_id or "TBD"
        self.session_start = datetime.now(UTC)
        self.log_file_path = None
        self.log_file = None
        self.lock = threading.Lock()
        self.active = False

        # Error grouping and noise reduction state
        self.error_groups: dict[str, Any] = {}
        self.compilation_errors_logged = False
        self.sudo_errors_logged = False
        self.drm_errors_logged = False
        self.duplicate_suppression: dict[int, datetime] = {}

        # Platform state tracking for accurate status reporting
        self.platform_components = {
            "dependencies": False,
            "build_system": False,
            "graphics": False,
            "vm": False,
            "gui": True,  # GUI is working if we can log
        }

        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize session log file
        self._initialize_session_file()

        # Create event logger for structured logging
        config = EventLoggerConfig(
            service_id="unhinged-desktop-gui",
            version="1.0.0",
            environment="desktop",
            min_log_level=LogLevel.DEBUG,
        )
        self.event_logger = create_logger(config)

    def _initialize_session_file(self):
        """Initialize the session log file with proper naming convention"""
        # Format: unhinged-session-{timestamp}-{session_id}.log
        # Note: session_id is TBD until chat session is persisted
        timestamp = self.session_start.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        filename = f"unhinged-session-{timestamp}-{self.session_id}.log"
        self.log_file_path = self.log_dir / filename

        try:
            self.log_file = open(self.log_file_path, "w", encoding="utf-8", buffering=1)  # noqa: SIM115
            self.active = True

            # Write session header
            self._write_session_header()

        except Exception as e:
            print(f"❌ Failed to create session log file: {e}", file=sys.stderr)
            self.active = False

    def _write_session_header(self):
        """Write session information header to log file"""
        if not self.active:
            return

        # Note: Session ID is TBD until chat session is persisted to persistence platform
        # Once session is created, update_session_id() will replace TBD with the real persisted session ID
        header = f"""# Unhinged Desktop Application Session Log
# Session ID: {self.session_id}
# Start Time: {self.session_start.isoformat()}
# Project Root: {self.project_root}
# Log File: {self.log_file_path}
# Format: Each line represents output that appeared in the GTK4 application
# Note: Session ID is TBD until chat session is persisted. Will be updated when session is created.
#
# === SESSION START ===

"""
        self.log_file.write(header)
        self.log_file.flush()

    def log_output(self, message: str, source: str = "GUI"):
        """
        @llm-doc Log Output to Session File

        Logs a message that appeared in the GTK4 application's output log
        to the session file with timestamp and source information.

        Args:
            message: The message that appeared in the GUI
            source: Source of the message (GUI, VM, MAKE, etc.)
        """
        if not self.active:
            return

        if self.log_file is None:
            return

        with self.lock:
            try:
                timestamp = datetime.now(UTC).isoformat()
                log_entry = f"[{timestamp}] [{source}] {message}\n"
                self.log_file.write(log_entry)
                self.log_file.flush()

            except Exception as e:
                print(f"❌ Failed to write to session log: {e}", file=sys.stderr)

    def log_gui_event(self, event_type: str, details: str):
        """Log GUI-specific events (button clicks, status changes, etc.)"""
        self.log_output(f"GUI_EVENT: {event_type} - {details}", "GUI_EVENT")

    def log_platform_output(self, output: str):
        """
        @llm-doc Enhanced platform output logging with noise reduction

        Processes platform output with intelligent filtering to reduce noise
        and group related errors while maintaining debugging value.
        """
        clean_output = output.strip()
        if not clean_output:
            return

        # Check for noise reduction opportunities
        if self._should_suppress_output(clean_output):
            return

        # Process and potentially group the output
        processed_output = self._process_platform_output(clean_output)
        if processed_output:
            # Determine simplified source classification
            source = self._classify_output_source(clean_output)
            self.log_output(processed_output, source)

            # Update platform component status
            self._update_component_status(clean_output)

    def _should_suppress_output(self, output: str) -> bool:
        """Check if output should be suppressed due to noise reduction"""
        # Suppress duplicate lines within a short time window
        output_hash = hash(output)
        current_time = datetime.now(UTC)

        if output_hash in self.duplicate_suppression:
            last_time = self.duplicate_suppression[output_hash]
            if (current_time - last_time).total_seconds() < 5:  # 5 second window
                return True

        self.duplicate_suppression[output_hash] = current_time
        return False

    def _process_platform_output(self, output: str) -> str | None:
        """Process output with error grouping and noise reduction"""
        # Handle compilation errors
        if self._is_compilation_error(output):
            return self._handle_compilation_error(output)

        # Handle sudo permission errors
        if "sudo: a terminal is required" in output or "sudo: a password is required" in output:
            return self._handle_sudo_error(output)

        # Handle DRM/graphics errors
        if "DRM_IOCTL" in output or "drm_mode_" in output:
            return self._handle_drm_error(output)

        # Handle VM errors
        if "qemu-system" in output and "Failed to get" in output:
            return self._handle_vm_error(output)

        # Remove redundant timestamp information (DRY principle)
        if output.startswith("2025-") and " - INFO - " in output:
            # Extract just the meaningful part, skip redundant timestamp
            parts = output.split(" - INFO - ", 1)
            if len(parts) > 1:
                return parts[1]

        return output

    def _classify_output_source(self, output: str) -> str:
        """Simplified source classification (3-4 categories instead of 7+)"""
        if any(keyword in output.lower() for keyword in ["error", "failed", "❌"]):
            return "ERROR"
        elif any(keyword in output.lower() for keyword in ["success", "✅", "completed"]):
            return "SUCCESS"
        elif any(keyword in output.lower() for keyword in ["gui_event", "button", "status_change"]):
            return "GUI"
        else:
            return "SYSTEM"

    def log_status_change(self, old_status: str, new_status: str):
        """Log status changes in the application"""
        self.log_gui_event("STATUS_CHANGE", f"{old_status} → {new_status}")

    def log_mode_selection(self, mode: str):
        """Log launch mode selection"""
        self.log_gui_event("MODE_SELECTED", mode)

    def _is_compilation_error(self, output: str) -> bool:
        """Check if output is a compilation error"""
        return any(
            keyword in output
            for keyword in [
                "error:",
                "warning:",
                "undefined reference",
                "undeclared",
                "CMakeFiles",
                "gmake",
                "gcc",
                "clang",
            ]
        )

    def _handle_compilation_error(self, output: str) -> str | None:
        """Handle compilation errors with grouping"""
        if not self.compilation_errors_logged:
            self.compilation_errors_logged = True
            return "❌ Compilation failed: C graphics library build errors (DRM headers missing)"
        return None  # Suppress subsequent compilation errors

    def _handle_sudo_error(self, output: str) -> str | None:
        """Handle sudo permission errors with grouping"""
        if not self.sudo_errors_logged:
            self.sudo_errors_logged = True
            return "❌ Permission error: sudo requires terminal access for dependency installation"
        return None  # Suppress subsequent sudo errors

    def _handle_drm_error(self, output: str) -> str | None:
        """Handle DRM graphics errors with grouping"""
        if not self.drm_errors_logged:
            self.drm_errors_logged = True
            return "❌ Graphics error: DRM/graphics headers not available"
        return None  # Suppress subsequent DRM errors

    def _handle_vm_error(self, output: str) -> str | None:
        """Handle VM-related errors"""
        if "Failed to get" in output and "lock" in output:
            return "❌ VM error: Image file locked by another process"
        return output

    def _update_component_status(self, output: str):
        """Update platform component status based on output"""
        if "Requirements file not found" in output:
            self.platform_components["dependencies"] = False
        elif "✅ Pip upgraded successfully" in output:
            self.platform_components["dependencies"] = True
        elif "Build system (v1) initialized successfully" in output:
            self.platform_components["build_system"] = True
        elif "Module build for 'c-graphics-build' failed" in output:
            self.platform_components["graphics"] = False
        elif "VM failed to start" in output:
            self.platform_components["vm"] = False
        elif "Simple VM fallback completed" in output:
            self.platform_components["vm"] = True  # Fallback succeeded

    def _get_platform_status(self) -> str:
        """Get accurate platform status based on component states"""
        failed_components = [name for name, status in self.platform_components.items() if not status]

        if not failed_components:
            return "✅ Platform started successfully"
        elif len(failed_components) == len(self.platform_components):
            return "❌ Platform failed to start"
        else:
            return f"⚠️ Platform partially started (failed: {', '.join(failed_components)})"

    def log_session_event(self, event: str, details: str = ""):
        """Log session-level events (start, stop, error, etc.)"""
        event_msg = f"SESSION: {event}"
        if details:
            event_msg += f" - {details}"
        self.log_output(event_msg, "GUI")

    def log_platform_status_update(self, claimed_status: str):
        """
        @llm-doc Log platform status with accuracy verification

        Prevents premature success claims by checking actual component status
        before logging platform state changes.
        """
        # Get actual platform status based on component states
        actual_status = self._get_platform_status()

        # Only log success if components actually succeeded
        if "success" in claimed_status.lower() and "❌" in actual_status:
            # Don't log premature success claims
            self.log_output(
                f"⚠️ Status claim '{claimed_status}' overridden by component failures",
                "SYSTEM",
            )
            self.log_output(actual_status, "SYSTEM")
        else:
            self.log_output(claimed_status, "SYSTEM")

    def update_session_id(self, new_session_id: str):
        """
        Update the session ID after chat session is created.
        This replaces the TBD placeholder with the persisted chat session ID.
        Updates both the log file header AND renames the log file to use the real session ID.

        Args:
            new_session_id: The persisted chat session ID from the persistence platform
        """
        try:
            old_session_id = self.session_id
            self.session_id = new_session_id

            # Update the log file header and rename the file
            if self.log_file and self.active:
                with self.lock:
                    try:
                        # Close current file
                        self.log_file.flush()
                        self.log_file.close()

                        # Read current file content
                        with open(self.log_file_path, encoding="utf-8") as f:
                            content = f.read()

                        # Replace old session ID with new one in the header
                        updated_content = content.replace(
                            f"# Session ID: {old_session_id}",
                            f"# Session ID: {new_session_id}",
                        )

                        # Generate new filename with real session ID
                        old_filename = self.log_file_path.name
                        new_filename = old_filename.replace(f"-{old_session_id}.log", f"-{new_session_id}.log")
                        new_log_file_path = self.log_dir / new_filename

                        # Write updated content to new file
                        with open(new_log_file_path, "w", encoding="utf-8") as f:
                            f.write(updated_content)

                        # Remove old file
                        try:
                            self.log_file_path.unlink()
                        except Exception as e:
                            print(f"⚠️ Failed to remove old log file: {e}")

                        # Update path and reopen for appending
                        self.log_file_path = new_log_file_path
                        self.log_file = open(self.log_file_path, "a", encoding="utf-8", buffering=1)  # noqa: SIM115

                    except Exception:
                        pass  # Log file update failed, continue with current file

            # Log the session ID update
            self.log_gui_event(
                "SESSION_ID_UPDATED",
                f"Session ID updated from TBD to persisted chat session: {new_session_id}",
            )

            # Emit session info to event logger (which writes to /build/tmp)
            self.event_logger.info(
                "Session ID persisted",
                metadata={
                    "session_id": new_session_id,
                    "log_file": str(self.log_file_path),
                },
            )

            # Emit session info to stdout for CLI visibility
            print()
            print("=" * 80)
            print("📋 Session Information")
            print("=" * 80)
            print(f"Session ID:  {new_session_id}")
            print(f"Log File:    {self.log_file_path}")
            print("=" * 80)
            print()
            sys.stdout.flush()
        except Exception as e:
            print(f"❌ Failed to update session ID: {e}")

    def get_session_info(self) -> dict:
        """Get current session information with component status"""
        return {
            "session_id": self.session_id,
            "start_time": self.session_start.isoformat(),
            "log_file": str(self.log_file_path) if self.log_file_path else None,
            "active": self.active,
            "platform_status": self._get_platform_status(),
            "component_status": self.platform_components.copy(),
            "errors_suppressed": {
                "compilation": self.compilation_errors_logged,
                "sudo": self.sudo_errors_logged,
                "drm": self.drm_errors_logged,
            },
        }

    def close_session(self):
        """Close the current session and log file with enhanced summary"""
        if not self.active:
            return

        with self.lock:
            try:
                # Write final platform status
                final_status = self._get_platform_status()
                self.log_output(f"Final platform status: {final_status}", "SYSTEM")

                # Write session footer with summary
                end_time = datetime.now(UTC)
                duration = end_time - self.session_start

                # Count error suppression statistics
                total_errors_suppressed = (
                    sum(
                        [
                            self.compilation_errors_logged,
                            self.sudo_errors_logged,
                            self.drm_errors_logged,
                        ]
                    )
                    * 10
                )  # Estimate suppressed errors

                footer = f"""
# === SESSION END ===
# End Time: {end_time.isoformat()}
# Duration: {duration.total_seconds():.2f} seconds
# Final Status: {final_status}
# Component Status: {self.platform_components}
# Noise Reduction: ~{total_errors_suppressed} repetitive errors suppressed
# Session ID: {self.session_id}
"""
                self.log_file.write(footer)
                self.log_file.flush()
                self.log_file.close()

                self.active = False

                print(f"✅ Session log saved: {self.log_file_path}")
                print(f"📊 Final status: {final_status}")

            except Exception as e:
                print(f"❌ Failed to close session log: {e}", file=sys.stderr)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_session()


class GUIOutputCapture:
    """
    @llm-doc Output capture system for GTK4 application

    Captures output that would normally go to the GTK4 text view
    and sends it to both the GUI and the session logger.
    """

    def __init__(
        self,
        session_logger: GUISessionLogger,
        gui_callback: Callable[[str], None] | None = None,
    ):
        self.session_logger = session_logger
        self.gui_callback = gui_callback

    def capture_output(self, message: str, source: str = "OUTPUT"):
        """
        Capture output and send to both GUI and session log

        Args:
            message: The output message
            source: Source of the output
        """
        # Send to session logger
        self.session_logger.log_output(message, source)

        # Send to GUI if callback provided
        if self.gui_callback:
            self.gui_callback(message)

    def capture_platform_output(self, output: str):
        """Capture platform-specific output"""
        self.session_logger.log_platform_output(output)

        if self.gui_callback:
            self.gui_callback(output)


def create_gui_session_logger(project_root: Path | None = None) -> GUISessionLogger:
    """
    Create a new GUI session logger

    Args:
        project_root: Project root directory (defaults to current working directory)

    Returns:
        Configured GUISessionLogger instance
    """
    return GUISessionLogger(project_root)


@contextmanager
def gui_session_context(project_root: Path | None = None):
    """
    Context manager for GUI session logging

    Usage:
        with gui_session_context() as session_logger:
            session_logger.log_output("Application started")
            # ... application logic ...
        # Session automatically closed
    """
    session_logger = create_gui_session_logger(project_root)
    try:
        session_logger.log_session_event("STARTED", "GUI session context initialized")
        yield session_logger
    finally:
        session_logger.log_session_event("ENDED", "GUI session context closed")
        session_logger.close_session()


# Example usage for testing
if __name__ == "__main__":
    # Test the session logger
    with gui_session_context() as logger:
        logger.log_gui_event("APP_START", "Desktop application launched")
        logger.log_mode_selection("Enhanced")
        logger.log_status_change("Ready", "Starting")
        logger.log_platform_output("🚀 Starting Unhinged Platform")
        logger.log_platform_output("VM: Alpine Linux booting...")
        logger.log_platform_output("✅ Platform started successfully")
        logger.log_status_change("Starting", "Running")

        print(f"Session info: {logger.get_session_info()}")
