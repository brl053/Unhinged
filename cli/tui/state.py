"""Application state for TUI.

Voice-first, single pane interface.
Press Enter to start/stop voice recording.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from libs.python.graph.context import CDCEvent, SessionContext


class VoiceState(Enum):
    """Voice recording state."""

    IDLE = auto()  # Ready, waiting for Enter
    RECORDING = auto()  # Recording voice input
    PROCESSING = auto()  # Transcribing audio
    ANALYZING = auto()  # Running intent analysis
    EXECUTING = auto()  # Running graph/command


@dataclass
class IntentResult:
    """Result from intent analysis graph with action routing."""

    intent: str = ""
    domain: str = ""
    confidence: float = 0.0
    reasoning: str = ""
    success: bool = False
    error: str = ""
    # Action routing fields (from hydrated prompt)
    action_type: str = ""  # linux, cli, graph, clarify, none
    command: str = ""  # Linux or CLI command if applicable
    graph_name: str = ""  # Graph name if action_type=graph


@dataclass
class AppState:
    """Complete application state.

    Single pane, voice-first design.
    """

    # Session context (CDC, persistence)
    session_id: str = ""
    session_ctx: "SessionContext | None" = None

    # Voice state
    voice: VoiceState = VoiceState.IDLE

    # Transcript history (most recent first)
    history: list[str] = field(default_factory=list)

    # Current transcription result
    last_transcript: str = ""

    # Intent analysis result
    intent_result: IntentResult | None = None

    # Graph data for visualization (dict form)
    graph_data: dict[str, Any] | None = None

    # Status message
    status: str = "Ready"

    # Running flag
    running: bool = True

    # Dirty flag (needs re-render)
    dirty: bool = True

    # Recording elapsed time (seconds)
    recording_seconds: int = 0

    # CDC events (last N for display)
    cdc_events: list["CDCEvent"] = field(default_factory=list)

    # Execution output (stdout/stderr from graph/command)
    execution_output: str = ""

    def add_cdc_event(self, event: "CDCEvent") -> "AppState":
        """Add a CDC event to the display list (keep last 20)."""
        events = [event] + self.cdc_events[:19]
        return self._replace(cdc_events=events, dirty=True)

    def start_recording(self) -> "AppState":
        """Start voice recording."""
        return self._replace(
            voice=VoiceState.RECORDING,
            status="🎤 Recording... Press Enter to stop.",
            recording_seconds=0,
            intent_result=None,
            graph_data=None,
            dirty=True,
        )

    def stop_recording(self) -> "AppState":
        """Stop recording, start processing."""
        return self._replace(
            voice=VoiceState.PROCESSING,
            status="⏳ Transcribing...",
            dirty=True,
        )

    def set_transcript(self, text: str) -> "AppState":
        """Set transcription result, move to analyzing."""
        new_history = [text] + self.history[:9]  # Keep last 10
        return self._replace(
            voice=VoiceState.ANALYZING,
            last_transcript=text,
            history=new_history,
            status="🧠 Analyzing intent...",
            dirty=True,
        )

    def set_intent_result(self, result: IntentResult, graph_data: dict[str, Any] | None = None) -> "AppState":
        """Set intent analysis result and return to idle."""
        if result.success:
            status = f"✓ Intent: {result.intent} | Domain: {result.domain} | Confidence: {result.confidence:.0%}"
        else:
            status = f"⚠ Analysis failed: {result.error}"
        return self._replace(
            voice=VoiceState.IDLE,
            intent_result=result,
            graph_data=graph_data,
            status=status,
            dirty=True,
        )

    def start_execution(self, name: str) -> "AppState":
        """Start graph/command execution."""
        return self._replace(
            voice=VoiceState.EXECUTING,
            status=f"⚙ Running: {name}",
            execution_output="",
            dirty=True,
        )

    def set_execution_output(self, output: str) -> "AppState":
        """Set execution output and return to idle."""
        return self._replace(
            voice=VoiceState.IDLE,
            execution_output=output,
            status="✓ Done",
            dirty=True,
        )

    def set_error(self, error: str) -> "AppState":
        """Set error state and return to idle."""
        return self._replace(
            voice=VoiceState.IDLE,
            status=f"❌ {error}",
            dirty=True,
        )

    def tick_recording(self) -> "AppState":
        """Increment recording timer."""
        return self._replace(
            recording_seconds=self.recording_seconds + 1,
            status=f"🎤 Recording... {self.recording_seconds + 1}s. Press Enter to stop.",
            dirty=True,
        )

    def quit(self) -> "AppState":
        """Signal application to quit."""
        return self._replace(running=False)

    def set_status(self, message: str) -> "AppState":
        """Set status message."""
        return self._replace(status=message, dirty=True)

    def mark_clean(self) -> "AppState":
        """Mark state as rendered (not dirty)."""
        return self._replace(dirty=False)

    def _replace(self, **changes) -> "AppState":
        """Return new state with specified changes."""
        return AppState(
            session_id=changes.get("session_id", self.session_id),
            session_ctx=changes.get("session_ctx", self.session_ctx),
            voice=changes.get("voice", self.voice),
            history=changes.get("history", self.history),
            last_transcript=changes.get("last_transcript", self.last_transcript),
            intent_result=changes.get("intent_result", self.intent_result),
            graph_data=changes.get("graph_data", self.graph_data),
            status=changes.get("status", self.status),
            running=changes.get("running", self.running),
            dirty=changes.get("dirty", self.dirty),
            recording_seconds=changes.get("recording_seconds", self.recording_seconds),
            cdc_events=changes.get("cdc_events", self.cdc_events),
            execution_output=changes.get("execution_output", self.execution_output),
        )


def create_initial_state(session_id: str, session_ctx: "SessionContext") -> AppState:
    """Create initial application state with session context."""
    return AppState(
        session_id=session_id,
        session_ctx=session_ctx,
        status=f"[{session_id[:8]}] Press Enter to speak. 'q' to quit.",
    )
