"""State management for Unhinged native TUI.

Immutable state with CDC event emission.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from libs.python.graph.context import CDCEvent, SessionContext


class Screen(Enum):
    """Current screen in the TUI."""

    LANDING = auto()  # Session selection
    MAIN = auto()  # Main voice interface (future)


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
    status: str = "Press W/S to navigate, E to select, Q to quit"

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
