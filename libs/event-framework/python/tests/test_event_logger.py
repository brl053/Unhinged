"""
Tests for the Python event logging framework
"""

import io
import sys
from contextlib import redirect_stdout
from datetime import datetime
from unittest.mock import patch
from pathlib import Path

import pytest
import yaml

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from events import (
    EventLogger,
    EventLoggerConfig,
    LogLevel,
    OutputFormat,
    create_logger,
    create_service_logger
)


class TestLogLevel:
    """Test LogLevel enum functionality"""
    
    def test_log_level_values(self):
        """Test that log levels have correct numeric values"""
        assert LogLevel.DEBUG.value == 0
        assert LogLevel.INFO.value == 1
        assert LogLevel.WARN.value == 2
        assert LogLevel.ERROR.value == 3
    
    def test_from_value(self):
        """Test creating log level from numeric value"""
        assert LogLevel.from_value(0) == LogLevel.DEBUG
        assert LogLevel.from_value(1) == LogLevel.INFO
        assert LogLevel.from_value(2) == LogLevel.WARN
        assert LogLevel.from_value(3) == LogLevel.ERROR
        assert LogLevel.from_value(99) is None
    
    def test_from_name(self):
        """Test creating log level from string name"""
        assert LogLevel.from_name("DEBUG") == LogLevel.DEBUG
        assert LogLevel.from_name("info") == LogLevel.INFO
        assert LogLevel.from_name("Warn") == LogLevel.WARN
        assert LogLevel.from_name("ERROR") == LogLevel.ERROR
        assert LogLevel.from_name("invalid") is None


class TestEventLogger:
    """Test EventLogger functionality"""
    
    def test_create_logger(self):
        """Test creating a logger with factory function"""
        config = EventLoggerConfig(service_id="test-service")
        logger = create_logger(config)
        assert isinstance(logger, EventLogger)
    
    def test_create_service_logger(self):
        """Test creating a service logger"""
        logger = create_service_logger("test-service", version="1.0.0")
        assert isinstance(logger, EventLogger)
    
    def test_log_level_filtering(self):
        """Test that log level filtering works correctly"""
        config = EventLoggerConfig(
            service_id="test-service",
            min_log_level=LogLevel.WARN
        )
        logger = create_logger(config)
        
        assert not logger.is_enabled(LogLevel.DEBUG)
        assert not logger.is_enabled(LogLevel.INFO)
        assert logger.is_enabled(LogLevel.WARN)
        assert logger.is_enabled(LogLevel.ERROR)
    
    def test_yaml_output_format(self):
        """Test YAML output format"""
        config = EventLoggerConfig(
            service_id="test-service",
            output_format=OutputFormat.YAML,
            min_log_level=LogLevel.DEBUG
        )
        logger = create_logger(config)
        
        # Capture stdout
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            logger.info("Test message", {"key": "value"})
        
        output = captured_output.getvalue()
        
        # Parse as YAML to verify format
        parsed = yaml.safe_load(output)
        assert parsed["level"] == "INFO"
        assert parsed["level_value"] == 1
        assert parsed["message"] == "Test message"
        assert parsed["service_id"] == "test-service"
        assert parsed["metadata"]["key"] == "value"
        assert "timestamp" in parsed
    
    def test_json_output_format(self):
        """Test JSON output format"""
        config = EventLoggerConfig(
            service_id="test-service",
            output_format=OutputFormat.JSON,
            min_log_level=LogLevel.DEBUG
        )
        logger = create_logger(config)
        
        # Capture stdout
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            logger.info("Test message", {"key": "value"})
        
        output = captured_output.getvalue()
        
        # Should be valid JSON
        import json
        parsed = json.loads(output)
        assert parsed["level"] == "INFO"
        assert parsed["level_value"] == 1
        assert parsed["message"] == "Test message"
        assert parsed["service_id"] == "test-service"
        assert parsed["metadata"]["key"] == "value"
    
    def test_context_propagation(self):
        """Test context propagation to child loggers"""
        logger = create_service_logger("test-service")
        child_logger = logger.with_context({"request_id": "123"})
        
        # Capture stdout
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            child_logger.info("Test message")
        
        output = captured_output.getvalue()
        parsed = yaml.safe_load(output)
        
        assert "context" in parsed
        assert parsed["context"]["request_id"] == "123"
    
    def test_trace_context(self):
        """Test trace context propagation"""
        logger = create_service_logger("test-service")
        traced_logger = logger.with_trace("trace123", "span456")
        
        # Capture stdout
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            traced_logger.info("Test message")
        
        output = captured_output.getvalue()
        parsed = yaml.safe_load(output)
        
        assert parsed["trace_id"] == "trace123"
        assert parsed["span_id"] == "span456"
    
    def test_error_logging_with_exception(self):
        """Test error logging with exception details"""
        logger = create_service_logger("test-service")
        exception = ValueError("Test error")
        
        # Capture stdout
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            logger.error("Error occurred", exception=exception)
        
        output = captured_output.getvalue()
        parsed = yaml.safe_load(output)
        
        assert parsed["level"] == "ERROR"
        assert parsed["message"] == "Error occurred"
        assert "exception" in parsed
        assert parsed["exception"]["type"] == "ValueError"
        assert parsed["exception"]["message"] == "Test error"
        assert "stack_trace" in parsed["exception"]
    
    def test_all_log_levels(self):
        """Test all log levels produce output"""
        config = EventLoggerConfig(
            service_id="test-service",
            min_log_level=LogLevel.DEBUG
        )
        logger = create_logger(config)

        # Capture stdout
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warn("Warning message")
            logger.error("Error message")

        output = captured_output.getvalue()

        # Verify all log levels appear in output
        assert "Debug message" in output
        assert "Info message" in output
        assert "Warning message" in output
        assert "Error message" in output
    
    def test_metadata_handling(self):
        """Test metadata is properly included"""
        logger = create_service_logger("test-service")
        metadata = {
            "user_id": "user123",
            "request_type": "inference",
            "model": "llama3.2",
            "numeric_value": 42,
            "boolean_value": True
        }
        
        # Capture stdout
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            logger.info("Processing request", metadata)
        
        output = captured_output.getvalue()
        parsed = yaml.safe_load(output)
        
        assert parsed["metadata"] == metadata
    
    @patch('events.event_logger.trace.get_current_span')
    def test_opentelemetry_integration(self, mock_get_current_span):
        """Test OpenTelemetry integration when span is available"""
        # Mock OpenTelemetry span
        mock_span = mock_get_current_span.return_value
        mock_span_context = mock_span.get_span_context.return_value
        mock_span_context.is_valid = True
        mock_span_context.trace_id = 0x1234567890abcdef1234567890abcdef
        mock_span_context.span_id = 0xabcdef1234567890
        
        logger = create_service_logger("test-service")
        
        # Capture stdout
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            logger.info("Test message")
        
        output = captured_output.getvalue()
        parsed = yaml.safe_load(output)
        
        # Should include trace context from OpenTelemetry
        assert "trace_id" in parsed
        assert "span_id" in parsed
