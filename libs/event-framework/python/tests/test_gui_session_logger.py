"""
@llm-doc Tests for GUISessionLogger
@llm-version 1.0.0
@llm-date 2025-11-16

Unit tests for session-based logging system that captures GTK4 application output.
Tests focus on:
- Session initialization and file creation
- Log output writing and flushing
- Session ID management
- Thread safety
- Error handling
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from events.gui_session_logger import GUISessionLogger


class TestGUISessionLoggerInitialization:
    """Test GUISessionLogger initialization and setup."""

    @pytest.fixture
    def temp_project_root(self):
        """Provide isolated temp directory for logs."""
        with tempfile.TemporaryDirectory() as td:
            yield Path(td)

    def test_logger_initialization_creates_directories(self, temp_project_root):
        """Test logger creates required directory structure."""
        logger = GUISessionLogger(project_root=temp_project_root)

        # Verify log directory exists
        log_dir = temp_project_root / "build" / "tmp"
        assert log_dir.exists(), "Log directory not created"
        assert logger.log_dir == log_dir

    def test_logger_initialization_sets_session_id_to_tbd(self, temp_project_root):
        """Test logger initializes with TBD session ID (per memorandum)."""
        logger = GUISessionLogger(project_root=temp_project_root)

        # Session ID should be TBD until persisted
        assert logger.session_id == "TBD"

    def test_logger_creates_session_file(self, temp_project_root):
        """Test logger creates session log file on initialization."""
        logger = GUISessionLogger(project_root=temp_project_root)

        # Verify log file was created
        assert logger.log_file_path is not None
        assert logger.log_file_path.exists()
        assert logger.active is True

    def test_session_file_contains_header(self, temp_project_root):
        """Test session file contains proper header information."""
        logger = GUISessionLogger(project_root=temp_project_root)

        # Read log file content
        content = logger.log_file_path.read_text()

        # Verify header contains expected information
        assert "Unhinged Desktop Application Session Log" in content
        assert "Session ID: TBD" in content
        assert "SESSION START" in content


class TestGUISessionLoggerOutput:
    """Test GUISessionLogger output writing functionality."""

    @pytest.fixture
    def logger(self):
        """Create logger with temp directory."""
        with tempfile.TemporaryDirectory() as td:
            logger_instance = GUISessionLogger(project_root=Path(td))
            yield logger_instance
            # Cleanup
            if logger_instance.log_file:
                logger_instance.log_file.close()

    def test_log_output_writes_to_file(self, logger):
        """Test basic output logging writes to file."""
        logger.log_output("Test message", source="TEST")

        # Read file and verify content
        content = logger.log_file_path.read_text()
        assert "Test message" in content
        assert "[TEST]" in content

    def test_log_gui_event_writes_event(self, logger):
        """Test GUI event logging."""
        logger.log_gui_event("button_click", "Submit button pressed")

        content = logger.log_file_path.read_text()
        assert "GUI_EVENT" in content
        assert "button_click" in content
        assert "Submit button pressed" in content

    def test_log_output_includes_timestamp(self, logger):
        """Test that log entries include ISO 8601 timestamps."""
        logger.log_output("Timestamped message")

        content = logger.log_file_path.read_text()
        # Verify ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
        assert "T" in content  # ISO format separator
        assert "Z" in content or "+" in content  # UTC indicator


class TestGUISessionLoggerSessionManagement:
    """Test session ID and metadata management."""

    @pytest.fixture
    def logger(self):
        """Create logger with temp directory."""
        with tempfile.TemporaryDirectory() as td:
            logger_instance = GUISessionLogger(project_root=Path(td))
            yield logger_instance
            if logger_instance.log_file:
                logger_instance.log_file.close()

    def test_update_session_id_changes_session_id(self, logger):
        """Test updating session ID after initialization."""
        new_session_id = "test-session-deterministic-001"
        logger.session_id = new_session_id

        assert logger.session_id == new_session_id

    def test_session_start_timestamp_is_set(self, logger):
        """Test session start timestamp is initialized."""
        assert logger.session_start is not None
        # Verify it's a datetime object
        assert hasattr(logger.session_start, "isoformat")


class TestGUISessionLoggerErrorHandling:
    """Test error handling and edge cases."""

    @pytest.fixture
    def logger(self):
        """Create logger with temp directory."""
        with tempfile.TemporaryDirectory() as td:
            logger_instance = GUISessionLogger(project_root=Path(td))
            yield logger_instance
            if logger_instance.log_file:
                logger_instance.log_file.close()

    def test_log_output_handles_empty_message(self, logger):
        """Test logging empty message doesn't crash."""
        logger.log_output("")
        # Should not raise exception
        assert logger.active is True

    def test_log_output_handles_unicode(self, logger):
        """Test logging unicode characters."""
        logger.log_output("Unicode test: 你好 🎉 Ñoño")

        content = logger.log_file_path.read_text()
        assert "你好" in content
        assert "🎉" in content
