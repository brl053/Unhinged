"""Main TUI application.

Voice-first, single pane interface.
Press Enter to start/stop voice recording.

This is the "hacky" way - no frameworks, just primitives.
Educational: this is what frameworks hide from you.
"""

import asyncio
import signal
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

import pyperclip
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from cli.tui.input import Key, KeyboardInput, KeyEvent
from cli.tui.state import AppState, IntentResult, VoiceState, create_initial_state
from libs.python.clients import TranscriptionService
from libs.python.graph.context import ContextStore


def _copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard using pyperclip."""
    if not text:
        return False
    try:
        pyperclip.copy(text)
        return True
    except pyperclip.PyperclipException:
        return False


def _build_clipboard_text(state: AppState) -> str:
    """Build text for clipboard from current state."""
    parts: list[str] = []

    if state.last_transcript:
        parts.append(f"Transcript: {state.last_transcript}")

    if state.intent_result and state.intent_result.success:
        r = state.intent_result
        parts.append(f"\nIntent: {r.intent}")
        parts.append(f"Domain: {r.domain}")
        parts.append(f"Confidence: {r.confidence:.0%}")
        if r.action_type:
            parts.append(f"Action Type: {r.action_type}")
        if r.command:
            parts.append(f"Command: {r.command}")
        if r.graph_name:
            parts.append(f"Graph: {r.graph_name}")
        if r.reasoning:
            parts.append(f"Reasoning: {r.reasoning}")

    return "\n".join(parts) if parts else ""


def _render_voice_state(state: AppState) -> list[Text | str]:
    """Render voice state indicator lines."""
    lines: list[Text | str] = []
    if state.voice == VoiceState.IDLE:
        lines.extend([Text("[ READY ]", style="bold green"), "", Text("Press Enter to speak", style="dim")])
    elif state.voice == VoiceState.RECORDING:
        lines.extend(
            [
                Text(f"● RECORDING  {state.recording_seconds}s", style="bold red"),
                "",
                Text("Press Enter to stop", style="dim"),
            ]
        )
    elif state.voice == VoiceState.PROCESSING:
        lines.extend([Text("⏳ TRANSCRIBING...", style="bold yellow"), "", Text("Please wait", style="dim")])
    elif state.voice == VoiceState.ANALYZING:
        lines.extend(
            [Text("🧠 ANALYZING...", style="bold magenta"), "", Text("Running intent analysis graph", style="dim")]
        )
    return lines


def _render_intent_result(result: IntentResult) -> list[Text | str]:
    """Render intent analysis result lines."""
    lines: list[Text | str] = [
        Text("─" * 50, style="dim"),
        Text("Intent Analysis:", style="bold magenta"),
        Text(f"  Intent:     {result.intent}", style="cyan"),
        Text(f"  Domain:     {result.domain}", style="cyan"),
        Text(f"  Confidence: {result.confidence:.0%}", style="green" if result.confidence > 0.7 else "yellow"),
    ]

    # Action routing (from hydrated prompt)
    if result.action_type:
        lines.extend(
            ["", Text("Suggested Action:", style="bold green"), Text(f"  Type: {result.action_type}", style="green")]
        )
        if result.command:
            lines.append(Text(f"  Command: {result.command}", style="bold white"))
        if result.graph_name:
            lines.append(Text(f"  Graph: {result.graph_name}", style="bold white"))

    lines.extend(["", Text("  Reasoning:", style="dim")])
    reasoning = result.reasoning
    if len(reasoning) > 60:
        for i in range(0, len(reasoning), 60):
            lines.append(Text(f"    {reasoning[i:i+60]}", style="dim italic"))
    else:
        lines.append(Text(f"    {reasoning}", style="dim italic"))
    lines.append("")
    return lines


def render_main_pane(state: AppState) -> Panel:
    """Render the main content pane."""
    lines: list[Text | str] = [Text("🎙️ Unhinged Voice", style="bold cyan"), ""]
    lines.extend(_render_voice_state(state))
    lines.append("")

    if state.last_transcript:
        lines.extend(
            [
                Text("─" * 50, style="dim"),
                Text("Transcript:", style="bold white"),
                Text(state.last_transcript, style="white"),
                "",
            ]
        )

    if state.intent_result and state.intent_result.success:
        lines.extend(_render_intent_result(state.intent_result))

    if state.graph_data:
        lines.extend(
            [
                Text("─" * 50, style="dim"),
                Text("Orchestration Graph:", style="bold yellow"),
                _render_graph_mini(state.graph_data),
            ]
        )

    content = Group(*[line if isinstance(line, Text) else Text(line) for line in lines])
    return Panel(Align.center(content, vertical="middle"), title="[bold cyan]Unhinged[/bold cyan]", border_style="cyan")


def _build_graph_flow(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[str]:
    """Build ordered flow of node names from graph data."""
    # Simple approach: just return node names in order (no complex graph traversal)
    return [n.get("type", n.get("id", "?"))[:12] for n in nodes]


def _render_graph_mini(graph_data: dict[str, Any]) -> Text:
    """Render a minimal inline graph visualization."""
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    name = graph_data.get("name", "Graph")

    text = Text()
    text.append(f"  {name}\n", style="bold")

    if not nodes:
        text.append("  (empty graph)", style="dim")
        return text

    flow_parts = _build_graph_flow(nodes, edges)

    # Render as flow: [node1 → node2 → node3]
    text.append("  [", style="dim")
    for i, part in enumerate(flow_parts):
        if i > 0:
            text.append(" → ", style="dim cyan")
        text.append(part, style="bold cyan")
    text.append("]", style="dim")

    return text


def render_status_bar(status: str) -> Panel:
    """Render the status bar at bottom."""
    return Panel(
        Text(status, style="dim"),
        style="dim",
        height=3,
    )


def render_state(state: AppState) -> Layout:
    """Render complete application state to Rich Layout."""
    layout = Layout(name="root")
    layout.split_column(
        Layout(name="main", ratio=1),
        Layout(name="status", size=3),
    )

    layout["main"].update(render_main_pane(state))
    layout["status"].update(render_status_bar(state.status))

    return layout


class VoiceRecorder:
    """Manages voice recording in background thread."""

    def __init__(self) -> None:
        self.audio_path: Path | None = None
        self.proc: Any = None
        self.recording: bool = False
        self.start_time: float = 0

    async def start_recording(self) -> Path:
        """Start recording, return path where audio will be saved."""
        import subprocess

        # Create temp file for audio
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        self.audio_path = Path(tmp.name)
        tmp.close()

        # Determine ALSA device
        alsa_device = "default"
        try:
            result = subprocess.run(
                ["arecord", "-L"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if "pipewire" in result.stdout:
                alsa_device = "pipewire"
        except Exception:
            pass

        # Start arecord
        self.proc = await asyncio.create_subprocess_exec(
            "arecord",
            "-D",
            alsa_device,
            "-q",
            "-f",
            "cd",
            "-t",
            "wav",
            str(self.audio_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        self.recording = True
        self.start_time = time.time()
        return self.audio_path

    async def stop_recording(self) -> Path | None:
        """Stop recording, return path to audio file."""
        if self.proc:
            self.proc.terminate()
            await self.proc.wait()
            self.proc = None

        self.recording = False
        return self.audio_path

    def get_elapsed(self) -> int:
        """Get elapsed recording time in seconds."""
        if self.recording:
            return int(time.time() - self.start_time)
        return 0


# Cached transcription service to avoid reloading model on every call
_transcription_service: TranscriptionService | None = None


def transcribe_audio_sync(audio_path: Path, model: str = "base") -> str:
    """Transcribe audio file using Whisper (synchronous).

    This is CPU-bound work, so we run it in a thread pool.
    Model is cached to avoid reloading on every transcription.
    """
    global _transcription_service

    if _transcription_service is None or _transcription_service.model_size != model:
        _transcription_service = TranscriptionService(model_size=model)
    return _transcription_service.transcribe_audio(audio_path)


async def run_intent_analysis(query: str) -> tuple[IntentResult, dict[str, Any] | None]:
    """Run intent analysis graph on the given query.

    Returns:
        Tuple of (IntentResult, graph_data dict for visualization)
    """
    import traceback
    import uuid

    from libs.python.graph import GraphExecutor
    from libs.python.graph.context import ContextStore
    from libs.python.query_planner import INTENT_NODE_ID, build_intent_analysis_graph
    from libs.python.query_planner.prompt_hydration import build_hydration_context

    try:
        # Create a session context for CDC logging
        session_id = f"tui-{uuid.uuid4().hex[:8]}"
        context_store = ContextStore()
        session_ctx = context_store.create(session_id)
        session_ctx.set_stage("intent_analysis")
        session_ctx.msg_user(query)

        # Build hydration context for grounded action routing
        hydration = build_hydration_context(session_ctx)

        # Build the intent analysis graph (local Ollama only) with hydration
        graph = build_intent_analysis_graph(provider="ollama", model="llama2", hydration=hydration)

        # Execute with session context for CDC
        executor = GraphExecutor(session_ctx)
        result = await executor.execute(
            graph,
            initial_inputs={INTENT_NODE_ID: {"stdin": query}},
        )

        # Extract result from the intent node
        if result.success and INTENT_NODE_ID in result.node_results:
            node_result = result.node_results[INTENT_NODE_ID]
            node_output = node_result.output

            intent_result = IntentResult(
                intent=node_output.get("intent", "unknown"),
                domain=node_output.get("domain", "unknown"),
                confidence=float(node_output.get("confidence", 0.0)),
                reasoning=node_output.get("reasoning", ""),
                success=node_output.get("success", False),
                action_type=node_output.get("action_type", ""),
                command=node_output.get("command") or "",
                graph_name=node_output.get("graph_name") or "",
            )

            # Log success with action routing info
            action_info = f", Action: {intent_result.action_type}" if intent_result.action_type else ""
            session_ctx.msg_system(f"Intent: {intent_result.intent}, Domain: {intent_result.domain}{action_info}")

            # Build graph data for visualization
            graph_data = {
                "name": "IntentAnalysis",
                "description": "Classifies user intent using LLM",
                "nodes": [
                    {"id": INTENT_NODE_ID, "type": "LLMIntentNode"},
                ],
                "edges": [],
            }

            return intent_result, graph_data
        else:
            # Extract error from node result or graph result
            error_msg = result.error_message or "Graph execution failed"
            if INTENT_NODE_ID in result.node_results:
                node_result = result.node_results[INTENT_NODE_ID]
                if node_result.error:
                    error_msg = node_result.error
                elif not node_result.success:
                    # Check output for error details
                    error_msg = node_result.output.get("error", error_msg)

            session_ctx.msg_error(error_msg)
            return IntentResult(success=False, error=error_msg), None

    except Exception as e:
        error_detail = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        # Log to stderr for debugging
        import sys

        print(f"[DEBUG] Intent analysis error: {error_detail}", file=sys.stderr)
        return IntentResult(success=False, error=str(e)), None


def _preload_transcription_model() -> None:
    """Preload Whisper model in background thread."""
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService(model_size="base")
        _transcription_service._load_model()


def _handle_start_recording(
    state: AppState,
    recorder: VoiceRecorder,
    loop: asyncio.AbstractEventLoop,
) -> AppState:
    """Handle starting voice recording."""
    try:
        loop.run_until_complete(recorder.start_recording())
        # Preload model while user is speaking
        loop.run_until_complete(asyncio.to_thread(_preload_transcription_model))
        return state.start_recording()
    except Exception as e:
        return state.set_error(f"Mic error: {e}")


def _handle_stop_recording(
    state: AppState,
    recorder: VoiceRecorder,
    loop: asyncio.AbstractEventLoop,
    live: Live,
) -> AppState:
    """Handle stopping recording and processing audio."""
    state = state.stop_recording()

    try:
        audio_path = loop.run_until_complete(recorder.stop_recording())
        if not audio_path or not audio_path.exists():
            return state.set_error("No audio recorded")

        # Transcribe and update UI immediately
        text = loop.run_until_complete(asyncio.to_thread(transcribe_audio_sync, audio_path))
        state = state.set_transcript(text)
        live.update(render_state(state))  # Show transcript NOW

        # Intent analysis - UI already shows transcript
        intent_result, graph_data = loop.run_until_complete(run_intent_analysis(text))
        state = state.set_intent_result(intent_result, graph_data)

        # Cleanup
        audio_path.unlink(missing_ok=True)
        return state

    except Exception as e:
        return state.set_error(f"Error: {e}")


def _process_event(
    state: AppState,
    event: KeyEvent | None,
    recorder: VoiceRecorder,
    loop: asyncio.AbstractEventLoop,
    live: Live,
    last_tick: float,
) -> tuple[AppState, float]:
    """Process a single keyboard event and update state."""
    if event:
        state = _handle_key_event(state, event, recorder, loop, live)
        if not state.running:
            return state, last_tick

    # Update recording timer every second
    if state.voice == VoiceState.RECORDING:
        now = time.time()
        if now - last_tick >= 1.0:
            state = state.tick_recording()
            last_tick = now

    # Update display if dirty
    if state.dirty:
        live.update(render_state(state))
        state = state.mark_clean()

    return state, last_tick


def _handle_key_event(
    state: AppState,
    event: KeyEvent,
    recorder: VoiceRecorder,
    loop: asyncio.AbstractEventLoop,
    live: Live,
) -> AppState:
    """Handle a single keyboard event."""
    if event.key in (Key.CTRL_C, Key.CTRL_Q) or event.char == "q":
        if state.voice == VoiceState.RECORDING:
            loop.run_until_complete(recorder.stop_recording())
        return state.quit()

    # 'c' to copy when idle (Alt+C is terminal-dependent)
    if event.char == "c" and state.voice == VoiceState.IDLE:
        clipboard_text = _build_clipboard_text(state)
        status = "Copied!" if _copy_to_clipboard(clipboard_text) else "Copy failed"
        return state.set_status(status)

    if event.key == Key.ENTER:
        if state.voice == VoiceState.IDLE:
            return _handle_start_recording(state, recorder, loop)
        if state.voice == VoiceState.RECORDING:
            live.update(render_state(state.stop_recording()))
            return _handle_stop_recording(state, recorder, loop, live)

    return state


# Global for disgraceful shutdown recovery
_shutdown_state: dict[str, Any] = {}


def _disgraceful_shutdown(signum: int, frame: Any) -> None:
    """Handle SIGINT/SIGTERM - attempt session persist."""
    ctx = _shutdown_state.get("session_ctx")
    store = _shutdown_state.get("context_store")
    if ctx and store:
        ctx.msg_system("disgraceful shutdown")
        store.persist(ctx)
    sys.exit(0)


def run_app(console: Console | None = None) -> None:
    """Run the interactive TUI application.

    Args:
        console: Optional Rich console (for testing). Uses stdout if None.
    """
    if console is None:
        console = Console()

    # Create session
    context_store = ContextStore()
    session_id = str(uuid.uuid4())
    session_ctx = context_store.create(session_id)

    # Register for disgraceful shutdown
    _shutdown_state["session_ctx"] = session_ctx
    _shutdown_state["context_store"] = context_store
    signal.signal(signal.SIGTERM, _disgraceful_shutdown)

    state = create_initial_state(session_id, session_ctx)
    recorder = VoiceRecorder()

    # Async event loop for recording
    loop = asyncio.new_event_loop()

    # Check if we're in a real terminal
    if not sys.stdin.isatty():
        console.print("[red]Error: Not running in a terminal[/red]")
        console.print("The TUI app requires an interactive terminal.")
        return

    # Clear screen
    console.clear()

    try:
        with (
            KeyboardInput() as kb,
            Live(
                render_state(state),
                console=console,
                refresh_per_second=10,
                screen=True,
            ) as live,
        ):
            last_tick = time.time()

            while state.running:
                event = kb.read(timeout=0.1)
                state, last_tick = _process_event(state, event, recorder, loop, live, last_tick)

    except KeyboardInterrupt:
        if recorder.recording:
            loop.run_until_complete(recorder.stop_recording())
    finally:
        # Graceful shutdown - persist session
        session_ctx.msg_system("graceful shutdown")
        context_store.persist(session_ctx)
        loop.close()
        # Clear screen on exit
        console.clear()
        console.print(f"Session {session_id[:8]} saved. Goodbye!")


def main() -> None:
    """Entry point for the TUI application."""
    run_app()
