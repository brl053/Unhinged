"""Main screen - Voice interface with transcript and CDC timeline.

Entry point: run_main(session_ctx)

Layout:
┌─────────────────────────────────────────────────────────────────┐
│ TRANSCRIPT                                                       │
│   [USER]: Show me all graphs                                    │
│   [SYSTEM]: Here are your graphs: ...                           │
├─────────────────────────────────────────────────────────────────┤
│ TIMELINE (CDC events)                                           │
│   10:30:45 │ msg.user     │ Show me all graphs                  │
│   10:30:46 │ node.start   │ IntentAnalysisNode                  │
├─────────────────────────────────────────────────────────────────┤
│ STATUS: 🎤 Listening...  │ Session: abc123  │ 7 events          │
└─────────────────────────────────────────────────────────────────┘

Controls:
- E: Toggle voice recording (start/stop)
- Q: Quit to landing
- W/S: Scroll timeline
"""

from __future__ import annotations

import subprocess
import tempfile
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libs.python.graph.context import CDCEvent, CDCEventType, SessionContext
from libs.python.terminal.cell import Color, Style
from libs.python.terminal.engine import Event, InputEvent
from libs.python.terminal.framebuffer import create_framebuffer
from libs.python.terminal.renderer import Renderer
from libs.python.terminal.terminal import Terminal
from libs.python.terminal.unhinged.state import (
    MainState,
    Panel,
    TranscriptRole,
    TUIFlightObserver,
    VoiceMode,
    create_main_state,
)

# Single worker for background processing (transcription + LLM)
_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="tui_worker")


@dataclass
class RecordingState:
    """Tracks background recording process."""

    proc: subprocess.Popen[bytes] | None = None
    audio_path: Path | None = None


@dataclass
class ProcessingState:
    """Tracks background processing (transcription + command execution)."""

    future: Future[dict[str, Any]] | None = None


def update(state: MainState, event: Event) -> MainState:
    """Update state based on input event (non-blocking updates only)."""
    if event.type == InputEvent.QUIT:
        return state.quit()

    if event.type == InputEvent.NAV_UP:
        return state.nav_up()

    if event.type == InputEvent.NAV_DOWN:
        return state.nav_down()

    if event.type == InputEvent.TAB:
        return state.cycle_panel()

    if event.type == InputEvent.COPY:
        return _copy_selected(state)

    # INTERACT (E key) is handled specially in the main loop for blocking recording
    return state


def _copy_selected(state: MainState) -> MainState:
    """Copy selected row content to system clipboard."""
    content = state.get_selected_content()
    if not content:
        return state.set_status("Nothing to copy")

    import subprocess

    try:
        subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=content.encode(),
            check=True,
            timeout=2,
        )
        return state._replace(clipboard=content).set_status(f"Copied {len(content)} chars")
    except FileNotFoundError:
        return state.set_status("Run: sudo apt install xclip")
    except Exception as e:
        return state.set_status(f"Copy failed: {e}")


def render(state: MainState, r: Renderer) -> None:
    """Render the main voice interface."""
    w = r.fb.width
    h = r.fb.height

    # Styles
    border_style = Style(fg=Color.CYAN)
    border_focused_style = Style(fg=Color.YELLOW)
    title_style = Style(fg=Color.CYAN).bold()
    title_focused_style = Style(fg=Color.YELLOW).bold()
    user_style = Style(fg=Color.GREEN)
    system_style = Style(fg=Color.WHITE)
    dim_style = Style(fg=Color.BRIGHT_BLACK)
    status_style = Style(fg=Color.YELLOW)
    event_type_style = Style(fg=Color.MAGENTA)
    # Selected row style: inverse colors (swap fg/bg)
    selected_style = Style(fg=Color.BLACK, bg=Color.WHITE)

    # Layout: transcript takes top 40%, timeline takes rest, status bar at bottom
    transcript_height = max(5, (h - 4) * 2 // 5)
    timeline_start = transcript_height + 1
    timeline_height = h - transcript_height - 4

    # Check which panel is focused
    transcript_focused = state.focused_panel == Panel.TRANSCRIPT
    timeline_focused = state.focused_panel == Panel.TIMELINE

    # Transcript panel (highlighted border if focused)
    t_border = border_focused_style if transcript_focused else border_style
    t_title = title_focused_style if transcript_focused else title_style
    title_prefix = "▶ " if transcript_focused else "  "
    r.panel(0, 0, w, transcript_height, title=f"{title_prefix}[ Transcript ]", style=t_border, title_style=t_title)

    # Render transcript entries (last N that fit)
    max_entries = transcript_height - 2
    visible_transcript = state.transcript[-max_entries:] if state.transcript else []
    # Calculate which visible index corresponds to selected row
    transcript_offset = max(0, len(state.transcript) - max_entries)
    for i, entry in enumerate(visible_transcript):
        y = 1 + i
        if y >= transcript_height - 1:
            break
        actual_idx = transcript_offset + i
        is_selected = transcript_focused and actual_idx == state.selected_transcript_row
        role_str = "[USER]" if entry.role == TranscriptRole.USER else "[SYS] "
        base_style = user_style if entry.role == TranscriptRole.USER else system_style
        style = selected_style if is_selected else base_style
        prefix = ">" if is_selected else " "
        text = f"{prefix}{entry.format_time()} {role_str} {entry.content}"
        r.text(1, y, text[: w - 2], style)

    if not visible_transcript:
        r.text(2, 2, "No messages yet. Press E to speak.", dim_style)

    # Timeline panel (highlighted border if focused)
    tl_border = border_focused_style if timeline_focused else border_style
    tl_title = title_focused_style if timeline_focused else title_style
    title_prefix = "▶ " if timeline_focused else "  "
    tl_panel_title = f"{title_prefix}[ Timeline ]"
    r.panel(0, timeline_start, w, timeline_height, title=tl_panel_title, style=tl_border, title_style=tl_title)

    # Render timeline events
    max_events = timeline_height - 2
    start_idx = state.timeline_scroll
    visible_events = state.timeline[start_idx : start_idx + max_events]
    for i, event in enumerate(visible_events):
        y = timeline_start + 1 + i
        if y >= timeline_start + timeline_height - 1:
            break
        actual_idx = start_idx + i
        is_selected = timeline_focused and actual_idx == state.selected_timeline_row
        time_str = event.timestamp.strftime("%H:%M:%S")
        event_type = event.event_type.value[:15].ljust(15)
        data_preview = str(event.data)[: w - 32] if event.data else ""
        prefix = ">" if is_selected else " "
        if is_selected:
            full_line = f"{prefix}{time_str}  {event_type} {data_preview}"
            r.text(1, y, full_line[: w - 2], selected_style)
        else:
            r.text(1, y, prefix + time_str, dim_style)
            r.text(12, y, event_type, event_type_style)
            r.text(28, y, data_preview, dim_style)

    if not visible_events:
        r.text(2, timeline_start + 1, "No events yet.", dim_style)

    # Status bar
    status_y = h - 2
    r.panel(0, status_y, w, 2, style=border_style)

    # Voice indicator
    voice_indicator = {
        VoiceMode.IDLE: "○",
        VoiceMode.LISTENING: "🎤",
        VoiceMode.PROCESSING: "⏳",
    }.get(state.voice_mode, "○")

    session_short = state.session_id[:8]
    event_count = state.event_count
    status_text = f"{voice_indicator} {state.status} │ Session: {session_short} │ {event_count} events"
    r.text(1, status_y + 1, status_text[: w - 2], status_style)


def _detect_alsa_device() -> str:
    """Detect best ALSA device (prefer pipewire if available)."""
    try:
        result = subprocess.run(
            ["arecord", "-L"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if "pipewire" in result.stdout:
            return "pipewire"
    except Exception:
        pass
    return "default"


def _start_recording(state: MainState, recording: RecordingState) -> tuple[MainState, RecordingState]:
    """Start background recording. Non-blocking."""
    device = _detect_alsa_device()

    # Create temp file
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    audio_path = Path(tmp.name)
    tmp.close()

    # Start arecord (non-blocking)
    try:
        proc = subprocess.Popen(
            ["arecord", "-D", device, "-q", "-f", "cd", "-t", "wav", str(audio_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        state.session_ctx.emit(CDCEventType.MSG_ERROR, {"text": "arecord not found"})
        return state.set_status("Error: arecord not found"), recording

    state.session_ctx.emit(CDCEventType.EXEC_START, {"action": "mic_record", "device": device})
    recording = RecordingState(proc=proc, audio_path=audio_path)
    return state.set_voice_mode(VoiceMode.LISTENING).set_status("🎤 Recording... Press E to stop"), recording


def _process_audio_worker(audio_path: Path, session_ctx: SessionContext) -> dict[str, Any]:
    """Worker function that runs in background thread.

    Does the heavy lifting: transcription + command processing.
    Returns dict with results to apply to main state.
    """
    result: dict[str, Any] = {
        "user_text": None,
        "response": None,
        "error": None,
    }

    try:
        session_ctx.emit(CDCEventType.EXEC_START, {"action": "transcribe", "path": str(audio_path)})

        from libs.python.clients.transcription_service import TranscriptionService

        service = TranscriptionService(model_size="base")
        text = service.transcribe_audio(audio_path)

        if text.strip():
            result["user_text"] = text
            session_ctx.msg_user(text)
            session_ctx.emit(CDCEventType.EXEC_EXIT, {"action": "transcribe", "chars": len(text)})

            # Process user utterance through command executor
            from libs.python.terminal.unhinged.command_executor import process_user_utterance

            response = process_user_utterance(text, session_ctx)
            result["response"] = response
        else:
            session_ctx.emit(CDCEventType.MSG_ERROR, {"text": "No speech detected"})
            session_ctx.emit(CDCEventType.EXEC_EXIT, {"action": "transcribe", "chars": 0})

    except Exception as e:
        session_ctx.emit(CDCEventType.MSG_ERROR, {"text": str(e)})
        result["error"] = str(e)

    finally:
        with suppress(Exception):
            audio_path.unlink()

    return result


def _stop_recording(
    state: MainState, recording: RecordingState, processing: ProcessingState
) -> tuple[MainState, RecordingState, ProcessingState]:
    """Stop recording and submit processing to background thread. Non-blocking."""
    if not recording.proc:
        return state, recording, processing

    # Stop the recording process (quick)
    recording.proc.terminate()
    with suppress(Exception):
        recording.proc.wait(timeout=2.0)

    audio_path = recording.audio_path
    state.session_ctx.emit(CDCEventType.EXEC_EXIT, {"action": "mic_record", "path": str(audio_path)})

    # Reset recording state
    recording = RecordingState()

    if not audio_path or not audio_path.exists():
        return state.set_voice_mode(VoiceMode.IDLE).set_status("No audio recorded"), recording, processing

    # Submit heavy work to background thread (non-blocking!)
    future = _executor.submit(_process_audio_worker, audio_path, state.session_ctx)
    processing = ProcessingState(future=future)

    state = state.set_voice_mode(VoiceMode.PROCESSING).set_status("⏳ Transcribing...")
    return state, recording, processing


def _poll_processing(state: MainState, processing: ProcessingState) -> tuple[MainState, ProcessingState]:
    """Poll for background processing completion. Non-blocking."""
    if processing.future is None:
        return state, processing

    if not processing.future.done():
        # Still running - sync timeline to show progress
        state = _sync_timeline(state)
        return state, processing

    # Processing complete - get result
    try:
        result = processing.future.result(timeout=0)  # Already done, no wait

        if result.get("error"):
            state = state.set_status(f"Error: {result['error']}")
        elif result.get("user_text"):
            state = state.add_transcript(TranscriptRole.USER, result["user_text"])
            if result.get("response"):
                state = state.add_transcript(TranscriptRole.SYSTEM, result["response"])
                state = state.set_status("✓ Done. Press E to speak again.")
            else:
                state = state.set_status(f"✓ {len(result['user_text'])} chars. Press E to speak again.")
        else:
            state = state.set_status("No speech detected. Press E to try again.")

    except Exception as e:
        state = state.set_status(f"Error: {e}")

    # Sync timeline one final time
    state = _sync_timeline(state)

    # Reset processing state
    processing = ProcessingState()
    return state.set_voice_mode(VoiceMode.IDLE), processing


def _sync_timeline(state: MainState) -> MainState:
    """Sync timeline from session_ctx's CDC feed.

    During blocking operations (transcription, command execution),
    events are emitted but the callback updates may be lost when
    _stop_recording returns a new state. This syncs any missing events.
    """
    # Get all events from session_ctx
    all_events = state.session_ctx._cdc_feed

    # Find events not yet in timeline (by comparing counts)
    current_count = len(state.timeline)
    if len(all_events) > current_count:
        # Add missing events
        for event in all_events[current_count:]:
            state = state.add_timeline_event(event)

    return state


def run_main(session_ctx: SessionContext) -> None:
    """Run the main voice interface screen with CDC event wiring."""
    import select
    import sys

    # Create initial state
    state = create_main_state(session_ctx)
    state = state.set_status("Press E to speak, W/S to scroll, Q to back")

    # Background recording state (polled each tick)
    recording = RecordingState()
    # Background processing state (transcription + command execution)
    processing = ProcessingState()

    # Create flight observer for transcript and status updates
    # Uses getter/setter pattern to access nonlocal state
    def get_state() -> MainState:
        return state

    def set_state(new_state: MainState) -> None:
        nonlocal state
        state = new_state

    flight_observer = TUIFlightObserver(get_state, set_state)

    # Wire CDC callback to update timeline and delegate to observer
    def on_cdc_event(event: CDCEvent) -> None:
        nonlocal state
        # Timeline always gets all events
        state = state.add_timeline_event(event)

        # Delegate transcript/status updates to observer (DRY, reusable)
        flight_observer.on_event(
            stage=None,  # Stage tracking is optional for now
            event_type=event.event_type.value,  # Convert enum to string
            data=event.data,
        )

    session_ctx.set_live_callback(on_cdc_event)

    # Emit session start
    session_ctx.emit(CDCEventType.STATE_CREATE, {"screen": "main", "session_id": session_ctx.session_id})

    # Setup terminal
    term = Terminal()
    try:
        term.enter_raw_mode()
        term.enter_alt_screen()
        term.clear()

        fb = create_framebuffer(term)
        renderer = Renderer(fb)

        # Initial render
        render(state, renderer)
        fb.flush(term)

        # Main loop - 0.1s tick
        while state.running:
            # Poll for background processing completion (non-blocking)
            state, processing = _poll_processing(state, processing)

            # Read input with timeout
            ready, _, _ = select.select([sys.stdin], [], [], 0.1)

            if ready:
                char = sys.stdin.read(1)
                if char:
                    event = _parse_char(char)

                    if event.type == InputEvent.INTERACT:
                        # Toggle recording (only if not currently processing)
                        if processing.future is not None:
                            # Already processing, ignore E key
                            pass
                        elif recording.proc is None:
                            # Start recording (non-blocking)
                            # Reset observer dedupe state for new conversation turn
                            flight_observer.reset()
                            state, recording = _start_recording(state, recording)
                        else:
                            # Stop recording and submit to background (non-blocking!)
                            state, recording, processing = _stop_recording(state, recording, processing)
                    else:
                        state = update(state, event)

            # Render (now happens every 0.1s regardless of processing!)
            renderer.clear()
            render(state, renderer)
            fb.flush(term)

    finally:
        # Cleanup: stop any active recording
        if recording.proc:
            recording.proc.terminate()
            with suppress(Exception):
                recording.proc.wait(timeout=1.0)
            if recording.audio_path:
                with suppress(Exception):
                    recording.audio_path.unlink()

        # Cancel any pending processing
        if processing.future and not processing.future.done():
            processing.future.cancel()

        session_ctx.set_live_callback(None)
        term.exit_alt_screen()
        term.exit_raw_mode()


def _parse_char(char: str) -> Event:
    """Parse a character into an input event."""
    byte_val = ord(char)

    if byte_val == 3:  # Ctrl+C
        return Event(type=InputEvent.QUIT)
    if byte_val == 9:  # Tab
        return Event(type=InputEvent.TAB)
    if byte_val in (10, 13):  # Enter
        return Event(type=InputEvent.ENTER)
    if byte_val == 27:  # Escape
        return Event(type=InputEvent.ESCAPE)

    key_map = {
        "q": InputEvent.QUIT,
        "w": InputEvent.NAV_UP,
        "s": InputEvent.NAV_DOWN,
        "a": InputEvent.NAV_LEFT,
        "d": InputEvent.NAV_RIGHT,
        "e": InputEvent.INTERACT,
        "c": InputEvent.COPY,
    }
    event_type = key_map.get(char.lower())
    if event_type is not None:
        return Event(type=event_type)

    if 32 <= byte_val < 127:
        return Event(type=InputEvent.CHAR, char=char)

    return Event(type=InputEvent.NONE)


if __name__ == "__main__":
    # Demo with a temporary session
    import uuid

    from libs.python.graph.context import ContextStore

    store = ContextStore()
    ctx = store.create(str(uuid.uuid4()))
    run_main(ctx)
