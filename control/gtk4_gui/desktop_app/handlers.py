"""
@llm-doc Desktop App Event Handlers
@llm-version 1.0.0
@llm-date 2025-11-15

Event handlers for recording, transcription, and audio errors.
"""


class RecordingHandlers:
    """Handles recording-related events."""

    @staticmethod
    def on_recording_state_changed(app, state):
        """Handle recording state changes from AudioHandler."""
        try:
            if hasattr(app, "session_logger") and app.session_logger:
                app.session_logger.log_gui_event("RECORDING_STATE_CHANGED", f"Recording state: {state}")

            if state.name in ("RECORDING", "PROCESSING", "IDLE"):
                pass

        except Exception as e:
            print(f"❌ Recording state change error: {e}")

    @staticmethod
    def on_transcription_result(app, transcript):
        """Handle transcription results from AudioHandler."""
        try:
            if transcript:
                if hasattr(app, "chatroom_view") and app.chatroom_view:
                    app.chatroom_view.add_voice_transcript(transcript)
                else:
                    app.show_toast(f"Transcript: {transcript}")

                if hasattr(app, "session_logger") and app.session_logger:
                    app.session_logger.log_gui_event("TRANSCRIPTION_SUCCESS", f"Transcript: {transcript}")
            else:
                app.show_toast("No transcription received")

        except Exception as e:
            print(f"❌ Transcription result error: {e}")
            app.show_toast(f"Transcription error: {e}")

    @staticmethod
    def on_audio_error(app, error_data):
        """Handle audio errors from AudioHandler."""
        try:
            if isinstance(error_data, dict):
                error_msg = error_data.get("error", "Unknown error")
                device = error_data.get("device", "unknown")
                details = error_data.get("details", {})
                stderr_output = details.get("arecord_stderr", "")

                if stderr_output:
                    full_msg = f"Audio error on {device}: {error_msg}\n\nDetails: {stderr_output}"
                else:
                    full_msg = f"Audio error on {device}: {error_msg}"
            else:
                full_msg = f"Audio error: {str(error_data)}"

            toast_msg = full_msg.split("\n")[0][:100]
            app.show_toast(toast_msg)

            if hasattr(app, "session_logger") and app.session_logger:
                app.session_logger.log_gui_event("AUDIO_ERROR", full_msg)

        except Exception as e:
            print(f"❌ Audio error handler error: {e}")


class RecordingControl:
    """Handles recording start/stop operations."""

    @staticmethod
    def start_recording(app):
        """Start toggle recording using AudioHandler."""
        try:
            if not hasattr(app, "audio_handler"):
                RecordingControl.init_audio_handler(app)

            app.audio_handler.start_recording()
            app.show_toast("Recording... (click to stop)")

            if app.session_logger:
                app.session_logger.log_gui_event("TOGGLE_RECORDING_START", "Started toggle recording")

        except Exception as e:
            print(f"❌ Start toggle recording error: {e}")
            app.show_toast(f"Recording failed: {e}")

    @staticmethod
    def stop_recording(app):
        """Stop toggle recording using AudioHandler."""
        try:
            if hasattr(app, "audio_handler") and app.audio_handler:
                app.audio_handler.stop_recording()
                app.show_toast("Processing recording...")

                if app.session_logger:
                    app.session_logger.log_gui_event("TOGGLE_RECORDING_STOP", "Stopped toggle recording")
            else:
                print("⚠️ AudioHandler not available")

        except Exception as e:
            print(f"❌ Stop toggle recording error: {e}")
            app.show_toast(f"Stop recording failed: {e}")

    @staticmethod
    def init_audio_handler(app):
        """Initialize the AudioHandler."""
        try:
            from ..handlers.audio_handler import AudioHandler

            app.audio_handler = AudioHandler(
                event_bus=app.event_bus,
                session_logger=getattr(app, "session_logger", None),
            )

        except Exception as e:
            print(f"⚠️ Failed to initialize AudioHandler: {e}")
            app.audio_handler = None
