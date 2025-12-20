"""Landing page - Session selection and creation.

Entry point: run_landing()

WASD navigation with CDC event emission.
"""

import uuid

from libs.python.terminal.cell import Color, Style
from libs.python.terminal.engine import Engine, Event, InputEvent
from libs.python.terminal.renderer import Renderer
from libs.python.terminal.unhinged.state import (
    LandingState,
    SessionSlot,
    create_landing_state,
)

# Lazy imports to avoid circular deps
_context_store = None
_CDCEventType = None


def _get_context_store():
    """Lazy load context store."""
    global _context_store
    if _context_store is None:
        from libs.python.graph.context import ContextStore

        _context_store = ContextStore()
    return _context_store


def _get_cdc_event_type():
    """Lazy load CDCEventType enum."""
    global _CDCEventType
    if _CDCEventType is None:
        from libs.python.graph.context import CDCEventType

        _CDCEventType = CDCEventType
    return _CDCEventType


def _load_sessions() -> list[SessionSlot]:
    """Load sessions from context store."""
    store = _get_context_store()
    summaries = store.list_sessions(limit=10)
    return [
        SessionSlot(
            session_id=s.session_id,
            label=f"{s.session_id[:8]}...",
            timestamp=s.last_updated.strftime("%Y-%m-%d %H:%M"),
            mutation_count=s.mutation_count,
        )
        for s in summaries
    ]


def _emit_nav_event(state: LandingState, direction: str, new_index: int) -> None:
    """Emit CDC event for navigation."""
    if state.session_ctx is None:
        return
    cdc_event_type = _get_cdc_event_type()
    state.session_ctx.emit(
        cdc_event_type.STATE_UPDATE,
        {
            "action": "nav",
            "direction": direction,
            "old_index": state.selected_index,
            "new_index": new_index,
        },
    )


def _emit_interact_event(state: LandingState, action: str, target: str) -> None:
    """Emit CDC event for interaction."""
    if state.session_ctx is None:
        return
    cdc_event_type = _get_cdc_event_type()
    state.session_ctx.emit(
        cdc_event_type.STATE_UPDATE,
        {
            "action": action,
            "target": target,
            "selected_index": state.selected_index,
        },
    )


def update(state: LandingState, event: Event) -> LandingState:
    """Update state based on input event."""

    if event.type == InputEvent.QUIT:
        return state.quit()

    if event.type == InputEvent.NAV_UP:
        new_state = state.nav_up()
        _emit_nav_event(state, "up", new_state.selected_index)
        return new_state

    if event.type == InputEvent.NAV_DOWN:
        new_state = state.nav_down()
        _emit_nav_event(state, "down", new_state.selected_index)
        return new_state

    if event.type == InputEvent.INTERACT:
        return _handle_interact(state)

    if event.type == InputEvent.COPY:
        return _handle_copy(state)

    return state


def _handle_interact(state: LandingState) -> LandingState:
    """Handle 'E' interact key."""
    if state.selected_index == 0:
        # Create new session
        new_id = str(uuid.uuid4())
        _emit_interact_event(state, "create_session", new_id)
        return state.set_status(f"Created session: {new_id[:8]}... (TODO: transition to main)")
    else:
        # Resume existing session
        idx = state.selected_index - 1
        if idx < len(state.sessions):
            session = state.sessions[idx]
            _emit_interact_event(state, "resume_session", session.session_id)
            return state.set_status(f"Resuming: {session.label} (TODO: transition to main)")
    return state


def _handle_copy(state: LandingState) -> LandingState:
    """Handle 'C' copy key."""
    if state.selected_index == 0:
        return state.set_status("Nothing to copy (New Session selected)")
    idx = state.selected_index - 1
    if idx < len(state.sessions):
        session = state.sessions[idx]
        _emit_interact_event(state, "copy", session.session_id)
        # TODO: Actually copy to clipboard
        return state.set_status(f"Copied: {session.session_id}")
    return state


def render(state: LandingState, r: Renderer) -> None:
    """Render the landing page."""
    w = r.fb.width
    h = r.fb.height

    # Styles
    border_style = Style(fg=Color.CYAN)
    title_style = Style(fg=Color.CYAN).bold()
    selected_style = Style(fg=Color.BLACK, bg=Color.CYAN)
    normal_style = Style(fg=Color.WHITE)
    dim_style = Style(fg=Color.BRIGHT_BLACK)
    status_style = Style(fg=Color.YELLOW)

    # Main frame
    r.panel(0, 0, w, h - 2, title="[ Unhinged ]", style=border_style, title_style=title_style)

    # Logo / header area
    r.text(2, 2, "Session Selection", title_style)
    r.text(2, 3, "─" * (w - 4), dim_style)

    # Menu items
    menu_y = 5

    # Option 0: New Session
    prefix = ">" if state.selected_index == 0 else " "
    style = selected_style if state.selected_index == 0 else normal_style
    r.text(2, menu_y, f"{prefix} [+] New Session", style)
    menu_y += 2

    # Existing sessions
    for i, session in enumerate(state.sessions):
        idx = i + 1
        prefix = ">" if state.selected_index == idx else " "
        style = selected_style if state.selected_index == idx else normal_style
        label = f"{prefix} [{i+1}] {session.label}  {session.timestamp}  ({session.mutation_count} events)"
        r.text(2, menu_y, label[: w - 4], style)
        menu_y += 1

    # Help text
    help_y = h - 5
    r.text(2, help_y, "W/S: Navigate  |  E: Select  |  C: Copy ID  |  Q: Quit", dim_style)

    # Status bar
    r.panel(0, h - 2, w, 2, style=border_style)
    r.text(2, h - 1, state.status[: w - 4], status_style)


def run_landing() -> str | None:
    """Run the landing page. Returns selected session ID or None if quit."""
    from libs.python.graph.context import ContextStore

    # Create a temporary session context for CDC during landing
    # (real session created/resumed on selection)
    store = ContextStore()
    temp_ctx = store.create("landing-" + str(uuid.uuid4())[:8])

    # Load existing sessions
    sessions = _load_sessions()

    # Initial state
    initial = create_landing_state(session_ctx=temp_ctx)
    initial = LandingState(
        session_ctx=temp_ctx,
        sessions=sessions,
        selected_index=0,
        running=True,
        status=f"Found {len(sessions)} previous session(s). Press E to select.",
        cdc_events=[],
    )

    # Run engine
    engine = Engine()

    # We need to capture the final state to return session choice
    final_state: list[LandingState] = [initial]

    def _update(state: LandingState, event: Event) -> LandingState:
        new_state = update(state, event)
        final_state[0] = new_state
        return new_state

    engine.run(_update, render, initial)

    # Return session ID if one was selected
    # For now, just return None (quit)
    return None


if __name__ == "__main__":
    run_landing()
