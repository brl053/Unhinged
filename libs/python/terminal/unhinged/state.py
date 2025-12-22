"""State management for Unhinged native TUI.

Immutable state with CDC event emission.

State hierarchy:
- LandingState: Session selection screen
- MainState: Main voice interface with transcript and timeline
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from libs.python.graph.context import CDCEvent, SessionContext


class Screen(Enum):
    """Current screen in the TUI."""

    TOC = auto()  # Table of Contents (main landing)
    LANDING = auto()  # Session selection (legacy)
    MAIN = auto()  # Main voice interface
    GRAPHS = auto()  # Graph selection and management


class TerminalMode(Enum):
    """Terminal privilege mode."""

    USER = auto()  # Standard user terminal (daily driver)
    SUDOERS = auto()  # Elevated privileges terminal (more formal)


class VoiceMode(Enum):
    """Voice input state."""

    IDLE = auto()  # Not listening
    LISTENING = auto()  # Actively capturing audio
    PROCESSING = auto()  # Transcribing / waiting for response


class MenuOption(Enum):
    """Landing page menu options."""

    NEW_SESSION = auto()
    # Session slots are dynamic (index 0, 1, 2, ...)


@dataclass
class SessionSlot:
    """A session in the selection list."""

    session_id: str
    label: str
    timestamp: str
    mutation_count: int


class TOCItem(Enum):
    """Table of Contents menu items."""

    USER_TERMINAL = auto()  # Daily driver terminal
    SUDOERS_TERMINAL = auto()  # Elevated privileges terminal
    GRAPHS = auto()  # Graph management screen
    CODEX = auto()  # Node type reference


@dataclass
class TOCState:
    """State for the Table of Contents landing page.

    Main menu with three options:
    1. User Terminal - daily driver for non-dev tasks
    2. Sudoers Terminal - elevated privileges, more formal
    3. Graphs - graph management and selection
    """

    # Currently selected menu item
    selected_index: int = 0

    # Running flag
    running: bool = True

    # Status message
    status: str = "W/S: Navigate  |  E: Select  |  Q: Quit"

    # Result of selection (set before quit)
    selected_item: TOCItem | None = None

    @property
    def items(self) -> list[TOCItem]:
        """Available menu items."""
        return [TOCItem.USER_TERMINAL, TOCItem.SUDOERS_TERMINAL, TOCItem.GRAPHS, TOCItem.CODEX]

    @property
    def max_index(self) -> int:
        """Maximum valid selection index."""
        return len(self.items) - 1

    def nav_up(self) -> "TOCState":
        """Move selection up."""
        new_idx = max(0, self.selected_index - 1)
        return self._replace(selected_index=new_idx)

    def nav_down(self) -> "TOCState":
        """Move selection down."""
        new_idx = min(self.max_index, self.selected_index + 1)
        return self._replace(selected_index=new_idx)

    def select(self) -> "TOCState":
        """Select current item and signal quit."""
        item = self.items[self.selected_index]
        return self._replace(selected_item=item, running=False)

    def set_status(self, status: str) -> "TOCState":
        """Set status message."""
        return self._replace(status=status)

    def quit(self) -> "TOCState":
        """Signal quit without selection."""
        return self._replace(running=False)

    def _replace(self, **changes: Any) -> "TOCState":
        """Return new state with changes."""
        return TOCState(
            selected_index=changes.get("selected_index", self.selected_index),
            running=changes.get("running", self.running),
            status=changes.get("status", self.status),
            selected_item=changes.get("selected_item", self.selected_item),
        )


def create_toc_state() -> TOCState:
    """Create initial TOC state."""
    return TOCState()


@dataclass
class GraphSlot:
    """A graph in the selection list."""

    graph_id: str
    name: str
    description: str
    updated_at: str
    node_count: int = 0


@dataclass
class GraphsState:
    """State for the Graphs management screen.

    Features:
    - Create new graph
    - Text input for name/search
    - List of 10 most recent graphs
    """

    # Available graphs from store
    graphs: list[GraphSlot] = field(default_factory=list)

    # Currently selected index (0 = "Create Graph", 1 = text input, 2+ = graphs)
    selected_index: int = 0

    # Text input state
    input_text: str = ""
    input_focused: bool = False

    # Running flag
    running: bool = True

    # Result (graph_id if selected, "new" if create, None if back)
    selected_graph_id: str | None = None
    create_new: bool = False

    # Status message
    status: str = "W/S: Navigate  |  E: Select/Edit  |  Q: Back"

    @property
    def max_index(self) -> int:
        """Maximum valid selection index."""
        # 0 = Create Graph, 1 = Text Input, 2+ = graphs
        return 1 + len(self.graphs)

    def nav_up(self) -> "GraphsState":
        """Move selection up."""
        new_idx = max(0, self.selected_index - 1)
        return self._replace(selected_index=new_idx, input_focused=False)

    def nav_down(self) -> "GraphsState":
        """Move selection down."""
        new_idx = min(self.max_index, self.selected_index + 1)
        return self._replace(selected_index=new_idx, input_focused=False)

    def focus_input(self) -> "GraphsState":
        """Focus the text input field."""
        return self._replace(selected_index=1, input_focused=True)

    def unfocus_input(self) -> "GraphsState":
        """Unfocus the text input field."""
        return self._replace(input_focused=False)

    def append_char(self, char: str) -> "GraphsState":
        """Append character to input text."""
        if self.input_focused:
            return self._replace(input_text=self.input_text + char)
        return self

    def backspace(self) -> "GraphsState":
        """Remove last character from input."""
        if self.input_focused and self.input_text:
            return self._replace(input_text=self.input_text[:-1])
        return self

    def select(self) -> "GraphsState":
        """Select current item."""
        if self.selected_index == 0:
            # Create new graph
            return self._replace(create_new=True, running=False)
        elif self.selected_index == 1:
            # Focus text input
            return self._replace(input_focused=True)
        else:
            # Select graph
            idx = self.selected_index - 2
            if idx < len(self.graphs):
                graph = self.graphs[idx]
                return self._replace(selected_graph_id=graph.graph_id, running=False)
        return self

    def set_status(self, status: str) -> "GraphsState":
        """Set status message."""
        return self._replace(status=status)

    def quit(self) -> "GraphsState":
        """Signal quit (back to TOC)."""
        return self._replace(running=False)

    def _replace(self, **changes: Any) -> "GraphsState":
        """Return new state with changes."""
        return GraphsState(
            graphs=changes.get("graphs", self.graphs),
            selected_index=changes.get("selected_index", self.selected_index),
            input_text=changes.get("input_text", self.input_text),
            input_focused=changes.get("input_focused", self.input_focused),
            running=changes.get("running", self.running),
            selected_graph_id=changes.get("selected_graph_id", self.selected_graph_id),
            create_new=changes.get("create_new", self.create_new),
            status=changes.get("status", self.status),
        )


def create_graphs_state(graphs: list[GraphSlot] | None = None) -> GraphsState:
    """Create initial graphs state."""
    return GraphsState(graphs=graphs or [])


@dataclass
class LandingState:
    """State for the landing page.

    WASD navigation:
    - W/S: Move selection up/down
    - E: Interact with selection (create/resume session)
    - Q: Quit
    - C: Copy session ID
    """

    # Session context for CDC emission (created on landing)
    session_ctx: "SessionContext | None" = None

    # Available sessions from store
    sessions: list[SessionSlot] = field(default_factory=list)

    # Currently selected index (0 = "New Session", 1+ = existing sessions)
    selected_index: int = 0

    # Running flag
    running: bool = True

    # Status message
    status: str = "Press W/S to navigate, E to select, Q to back"

    # CDC events for display (last N)
    cdc_events: list["CDCEvent"] = field(default_factory=list)

    @property
    def max_index(self) -> int:
        """Maximum valid selection index."""
        return len(self.sessions)  # 0 = new, 1..N = sessions

    def nav_up(self) -> "LandingState":
        """Move selection up."""
        new_idx = max(0, self.selected_index - 1)
        return self._replace(selected_index=new_idx)

    def nav_down(self) -> "LandingState":
        """Move selection down."""
        new_idx = min(self.max_index, self.selected_index + 1)
        return self._replace(selected_index=new_idx)

    def add_cdc_event(self, event: "CDCEvent") -> "LandingState":
        """Add CDC event to display list."""
        events = [event] + self.cdc_events[:9]  # Keep last 10
        return self._replace(cdc_events=events)

    def set_status(self, status: str) -> "LandingState":
        """Set status message."""
        return self._replace(status=status)

    def quit(self) -> "LandingState":
        """Signal quit."""
        return self._replace(running=False)

    def _replace(self, **changes: Any) -> "LandingState":
        """Return new state with changes."""
        return LandingState(
            session_ctx=changes.get("session_ctx", self.session_ctx),
            sessions=changes.get("sessions", self.sessions),
            selected_index=changes.get("selected_index", self.selected_index),
            running=changes.get("running", self.running),
            status=changes.get("status", self.status),
            cdc_events=changes.get("cdc_events", self.cdc_events),
        )


def create_landing_state(session_ctx: "SessionContext | None" = None) -> LandingState:
    """Create initial landing state."""
    return LandingState(session_ctx=session_ctx)


# =============================================================================
# Main Page State
# =============================================================================


class Panel(Enum):
    """Panel that can be focused."""

    TRANSCRIPT = auto()
    TIMELINE = auto()


class TranscriptRole(Enum):
    """Who sent the transcript entry."""

    USER = auto()  # User voice input
    SYSTEM = auto()  # System response
    ERROR = auto()  # Error message


@dataclass
class TranscriptEntry:
    """Single entry in the conversation transcript."""

    role: TranscriptRole
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def format_time(self) -> str:
        """Format timestamp for display."""
        return self.timestamp.strftime("%H:%M:%S")


@dataclass
class MainState:
    """State for the main voice interface.

    Layout:
    ┌─────────────────────────────────────────────────────────────────┐
    │ TRANSCRIPT                                                       │
    │   [USER]: Show me all graphs                                    │
    │   [SYSTEM]: Here are your graphs: ...                           │
    ├─────────────────────────────────────────────────────────────────┤
    │ TIMELINE (CDC events)                                           │
    │   10:30:45 │ msg.user     │ Show me all graphs                  │
    │   10:30:46 │ node.start   │ IntentAnalysisNode                  │
    │   10:30:47 │ node.success │ ListGraphsNode                      │
    ├─────────────────────────────────────────────────────────────────┤
    │ STATUS: 🎤 Listening...  │ Session: abc123  │ 7 events          │
    └─────────────────────────────────────────────────────────────────┘

    Controls:
    - SPACE: Toggle voice (start/stop listening)
    - Q: Quit to landing
    - UP/DOWN or W/S: Scroll timeline
    """

    # Session context (carries CDC feed)
    session_ctx: "SessionContext"

    # Conversation transcript (user ↔ system)
    transcript: list[TranscriptEntry] = field(default_factory=list)

    # CDC timeline (all events, newest first for display)
    timeline: list["CDCEvent"] = field(default_factory=list)
    timeline_max: int = 50  # Max events to keep in memory
    timeline_scroll: int = 0  # Scroll offset for timeline view

    # Panel focus and selection (for navigation)
    focused_panel: Panel = Panel.TRANSCRIPT
    selected_transcript_row: int = 0  # Selected row in transcript panel
    selected_timeline_row: int = 0  # Selected row in timeline panel

    # Internal clipboard
    clipboard: str = ""

    # Voice state
    voice_mode: VoiceMode = VoiceMode.IDLE

    # Status bar
    status: str = "Press E to speak, Q to back"

    # Running flag
    running: bool = True

    @property
    def session_id(self) -> str:
        """Get session ID."""
        return self.session_ctx.session_id

    @property
    def event_count(self) -> int:
        """Total events in session."""
        return len(self.session_ctx._cdc_feed)

    def add_transcript(self, role: TranscriptRole, content: str) -> "MainState":
        """Add entry to transcript."""
        entry = TranscriptEntry(role=role, content=content)
        return self._replace(transcript=[*self.transcript, entry])

    def add_timeline_event(self, event: "CDCEvent") -> "MainState":
        """Add CDC event to timeline (newest first)."""
        events = [event] + self.timeline[: self.timeline_max - 1]
        return self._replace(timeline=events)

    def set_voice_mode(self, mode: VoiceMode) -> "MainState":
        """Set voice input mode."""
        return self._replace(voice_mode=mode)

    def set_status(self, status: str) -> "MainState":
        """Set status message."""
        return self._replace(status=status)

    def scroll_timeline_up(self) -> "MainState":
        """Scroll timeline up (show older events)."""
        max_scroll = max(0, len(self.timeline) - 10)
        new_scroll = min(self.timeline_scroll + 1, max_scroll)
        return self._replace(timeline_scroll=new_scroll)

    def scroll_timeline_down(self) -> "MainState":
        """Scroll timeline down (show newer events)."""
        new_scroll = max(0, self.timeline_scroll - 1)
        return self._replace(timeline_scroll=new_scroll)

    def cycle_panel(self) -> "MainState":
        """Cycle focus to next panel (Tab key)."""
        next_panel = Panel.TIMELINE if self.focused_panel == Panel.TRANSCRIPT else Panel.TRANSCRIPT
        return self._replace(focused_panel=next_panel)

    def nav_up(self) -> "MainState":
        """Move selection up in focused panel (W key)."""
        if self.focused_panel == Panel.TRANSCRIPT:
            new_row = max(0, self.selected_transcript_row - 1)
            return self._replace(selected_transcript_row=new_row)
        else:
            new_row = max(0, self.selected_timeline_row - 1)
            return self._replace(selected_timeline_row=new_row)

    def nav_down(self) -> "MainState":
        """Move selection down in focused panel (S key)."""
        if self.focused_panel == Panel.TRANSCRIPT:
            max_row = max(0, len(self.transcript) - 1)
            new_row = min(self.selected_transcript_row + 1, max_row)
            return self._replace(selected_transcript_row=new_row)
        else:
            max_row = max(0, len(self.timeline) - 1)
            new_row = min(self.selected_timeline_row + 1, max_row)
            return self._replace(selected_timeline_row=new_row)

    def get_selected_content(self) -> str:
        """Get content of currently selected row for copying."""
        if self.focused_panel == Panel.TRANSCRIPT:
            if 0 <= self.selected_transcript_row < len(self.transcript):
                entry = self.transcript[self.selected_transcript_row]
                return entry.content
        else:
            if 0 <= self.selected_timeline_row < len(self.timeline):
                event = self.timeline[self.selected_timeline_row]
                return f"{event.event_type.value}: {event.data}"
        return ""

    def quit(self) -> "MainState":
        """Signal quit."""
        return self._replace(running=False)

    def _replace(self, **changes: Any) -> "MainState":
        """Return new state with changes."""
        return MainState(
            session_ctx=changes.get("session_ctx", self.session_ctx),
            transcript=changes.get("transcript", self.transcript),
            timeline=changes.get("timeline", self.timeline),
            timeline_max=changes.get("timeline_max", self.timeline_max),
            timeline_scroll=changes.get("timeline_scroll", self.timeline_scroll),
            focused_panel=changes.get("focused_panel", self.focused_panel),
            selected_transcript_row=changes.get("selected_transcript_row", self.selected_transcript_row),
            selected_timeline_row=changes.get("selected_timeline_row", self.selected_timeline_row),
            voice_mode=changes.get("voice_mode", self.voice_mode),
            status=changes.get("status", self.status),
            running=changes.get("running", self.running),
        )


def create_main_state(session_ctx: "SessionContext") -> MainState:
    """Create initial main page state from session context."""
    return MainState(session_ctx=session_ctx)


# ---------------------------------------------------------------------------
# TUI Flight Observer
# ---------------------------------------------------------------------------


class TUIFlightObserver:
    """FlightObserver implementation for TUI state updates.

    Bridges the graph execution protocol to TUI state management.
    Updates transcript, timeline, and status bar based on CDC events.

    This follows the Observer pattern from libs/python/graph/protocol.py,
    keeping the graph engine authoritative and the TUI as a follower.
    """

    observer_id: str = "tui_state_observer"

    # Status messages for different node types
    STATUS_MAP: dict[str, str] = {
        "intent_classifier": "⏳ Classifying intent...",
        "engineering_plan": "⏳ Generating plan...",
        "intent_parser": "⏳ Parsing commands...",
        "llm_generate": "⏳ Generating with LLM...",
        "analyze": "⏳ Analyzing request...",
        "format_plan": "⏳ Formatting plan...",
        "command_executor": "⏳ Processing...",
    }

    def __init__(self, state_getter: Any, state_setter: Any) -> None:
        """Initialize with state access functions.

        Args:
            state_getter: Callable that returns current MainState
            state_setter: Callable that accepts new MainState
        """
        self._get_state = state_getter
        self._set_state = state_setter
        self._seen_user_texts: set[str] = set()  # Dedupe user messages
        self._seen_system_texts: set[str] = set()  # Dedupe system messages

    def on_event(self, stage: Any, event_type: str, data: dict[str, Any]) -> None:
        """Handle CDC events and update TUI state.

        Args:
            stage: FlightStage (PRE_FLIGHT, IN_FLIGHT, POST_FLIGHT)
            event_type: CDC event type string
            data: Event payload
        """
        state = self._get_state()
        if state is None:
            return

        # Update timeline (all events)
        # Note: Timeline is updated from CDCEvent objects via add_timeline_event,
        # but here we receive raw event_type + data. We could construct CDCEvent
        # or just focus on transcript/status which need special handling.

        # Update transcript from user/system messages (deduplicated)
        if event_type == "msg.user":
            text = data.get("text", "")
            if text and text not in self._seen_user_texts:
                self._seen_user_texts.add(text)
                state = state.add_transcript(TranscriptRole.USER, text)

        elif event_type == "msg.system":
            text = data.get("text", "")
            if text and text not in self._seen_system_texts:
                self._seen_system_texts.add(text)
                state = state.add_transcript(TranscriptRole.SYSTEM, text)

        # Update status bar based on node starts
        if event_type == "node.start":
            node_id = data.get("node_id", "")
            if node_id in self.STATUS_MAP:
                state = state.set_status(self.STATUS_MAP[node_id])

        self._set_state(state)

    def on_stage_enter(self, stage: Any) -> None:
        """Called when entering a flight stage."""
        pass  # Could show "PRE-FLIGHT", "IN-FLIGHT", etc.

    def on_stage_exit(self, stage: Any) -> None:
        """Called when exiting a flight stage."""
        pass

    def reset(self) -> None:
        """Reset deduplication state for new recording session."""
        self._seen_user_texts.clear()
        self._seen_system_texts.clear()
