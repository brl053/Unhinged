"""
Unit tests for AudioHandler callback initialization and format detection.

Tests verify:
1. Callback attributes are properly initialized to None
2. Callbacks can be set and invoked without errors
3. Format detection occurs during initialization
4. Format cache prevents repeated detection
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from handlers.audio_handler import AudioHandler, RecordingState
from utils.audio_utils import clear_format_cache


class TestAudioHandlerCallbacks(unittest.TestCase):
    """Test callback initialization and lifecycle."""

    def setUp(self):
        """Clear format cache before each test."""
        clear_format_cache()

    def test_callbacks_initialize_to_none(self):
        """Verify callback attributes initialize to None."""
        handler = AudioHandler()

        self.assertIsNone(handler._state_callback)
        self.assertIsNone(handler._error_callback)
        self.assertIsNone(handler._progress_callback)

    def test_state_callback_can_be_set(self):
        """Verify state callback can be set and invoked."""
        handler = AudioHandler()
        callback_invoked = []

        def test_callback(state):
            callback_invoked.append(state)

        handler._state_callback = test_callback

        # Simulate state change
        handler._set_state(RecordingState.RECORDING)

        # Callback should have been invoked
        self.assertTrue(len(callback_invoked) > 0)
        self.assertEqual(callback_invoked[0], RecordingState.RECORDING)

    def test_error_callback_can_be_set(self):
        """Verify error callback can be set and invoked."""
        handler = AudioHandler()
        errors_caught = []

        def test_callback(error):
            errors_caught.append(error)

        handler._error_callback = test_callback

        # Simulate error
        test_error = Exception("Test error")
        handler._handle_error(test_error)

        # Callback should have been invoked
        self.assertTrue(len(errors_caught) > 0)

    def test_progress_callback_can_be_set(self):
        """Verify progress callback can be set without errors."""
        handler = AudioHandler()
        progress_values = []

        def test_callback(elapsed):
            progress_values.append(elapsed)

        handler._progress_callback = test_callback

        # Callback should be callable
        self.assertIsNotNone(handler._progress_callback)


class TestAudioHandlerFormatDetection(unittest.TestCase):
    """Test format detection and caching."""

    def setUp(self):
        """Clear format cache before each test."""
        clear_format_cache()

    def test_format_detected_during_init(self):
        """Verify format is detected during initialization."""
        handler = AudioHandler()

        # Format should be detected
        self.assertIsNotNone(handler._detected_format)
        self.assertIsNotNone(handler._detected_sample_width)

    def test_sample_width_mapping(self):
        """Verify sample width mapping is correct."""
        handler = AudioHandler()

        # Test known formats
        self.assertEqual(handler._get_sample_width("S16_LE"), 2)
        self.assertEqual(handler._get_sample_width("S24_3LE"), 3)
        self.assertEqual(handler._get_sample_width("S32_LE"), 4)
        self.assertEqual(handler._get_sample_width("U8"), 1)

    def test_format_cache_prevents_repeated_detection(self):
        """Verify format cache prevents repeated detection."""
        # First handler triggers detection
        handler1 = AudioHandler()
        format1 = handler1._detected_format

        # Second handler should use cache (instant)
        handler2 = AudioHandler()
        format2 = handler2._detected_format

        # Formats should match
        self.assertEqual(format1, format2)


if __name__ == "__main__":
    unittest.main()
