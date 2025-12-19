"""Main TUI application.

Voice-first, single pane interface.
Press Enter to start/stop voice recording.

This is the "hacky" way - no frameworks, just primitives.
Educational: this is what frameworks hide from you.
"""

import asyncio
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from cli.tui.input import Key, KeyboardInput
from cli.tui.state import AppState, IntentResult, VoiceState, create_initial_state


def render_main_pane(state: AppState) -> Panel:
    """Render the main content pane."""
    lines: list[Text | str] = []

    # Title
    lines.append(Text("🎙️ Unhinged Voice", style="bold cyan"))
    lines.append("")

    # Voice state indicator
    if state.voice == VoiceState.IDLE:
        lines.append(Text("[ READY ]", style="bold green"))
        lines.append("")
        lines.append(Text("Press Enter to speak", style="dim"))
    elif state.voice == VoiceState.RECORDING:
        lines.append(Text(f"● RECORDING  {state.recording_seconds}s", style="bold red"))
        lines.append("")
        lines.append(Text("Press Enter to stop", style="dim"))
    elif state.voice == VoiceState.PROCESSING:
        lines.append(Text("⏳ TRANSCRIBING...", style="bold yellow"))
        lines.append("")
        lines.append(Text("Please wait", style="dim"))
    elif state.voice == VoiceState.ANALYZING:
        lines.append(Text("🧠 ANALYZING...", style="bold magenta"))
        lines.append("")
        lines.append(Text("Running intent analysis graph", style="dim"))

    lines.append("")

    # Last transcript
    if state.last_transcript:
        lines.append(Text("─" * 50, style="dim"))
        lines.append(Text("Transcript:", style="bold white"))
        lines.append(Text(state.last_transcript, style="white"))
        lines.append("")

    # Intent result
    if state.intent_result and state.intent_result.success:
        lines.append(Text("─" * 50, style="dim"))
        lines.append(Text("Intent Analysis:", style="bold magenta"))
        lines.append(Text(f"  Intent:     {state.intent_result.intent}", style="cyan"))
        lines.append(Text(f"  Domain:     {state.intent_result.domain}", style="cyan"))
        lines.append(
            Text(
                f"  Confidence: {state.intent_result.confidence:.0%}",
                style="green" if state.intent_result.confidence > 0.7 else "yellow",
            )
        )
        lines.append("")
        lines.append(Text("  Reasoning:", style="dim"))
        # Wrap reasoning text
        reasoning = state.intent_result.reasoning
        if len(reasoning) > 60:
            for i in range(0, len(reasoning), 60):
                lines.append(Text(f"    {reasoning[i:i+60]}", style="dim italic"))
        else:
            lines.append(Text(f"    {reasoning}", style="dim italic"))
        lines.append("")

    # Graph visualization
    if state.graph_data:
        lines.append(Text("─" * 50, style="dim"))
        lines.append(Text("Orchestration Graph:", style="bold yellow"))
        lines.append(_render_graph_mini(state.graph_data))

    content = Group(*[line if isinstance(line, Text) else Text(line) for line in lines])

    return Panel(
        Align.center(content, vertical="middle"),
        title="[bold cyan]Unhinged[/bold cyan]",
        border_style="cyan",
    )


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

    # Simple linear visualization: node1 → node2 → node3
    node_ids = [n.get("id", "?") for n in nodes]
    node_names = {n.get("id"): n.get("type", n.get("id", "?"))[:12] for n in nodes}

    # Build adjacency
    outgoing: dict[str, list[str]] = {nid: [] for nid in node_ids}
    for edge in edges:
        src = edge.get("from", edge.get("source", ""))
        dst = edge.get("to", edge.get("target", ""))
        if src in outgoing:
            outgoing[src].append(dst)

    # Find roots (no incoming edges)
    incoming = {dst for e in edges for dst in [e.get("to", e.get("target", ""))]}
    roots = [nid for nid in node_ids if nid not in incoming]

    # Simple BFS to show flow
    visited = set()
    queue = roots if roots else node_ids[:1]
    flow_parts = []

    while queue:
        nid = queue.pop(0)
        if nid in visited:
            continue
        visited.add(nid)
        flow_parts.append(node_names.get(nid, nid))
        for child in outgoing.get(nid, []):
            if child not in visited:
                queue.append(child)

    # Render as flow
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


def transcribe_audio_sync(audio_path: Path, model: str = "base") -> str:
    """Transcribe audio file using Whisper (synchronous).

    This is CPU-bound work, so we run it in a thread pool.
    """
    from libs.python.clients import TranscriptionService

    service = TranscriptionService(model_size=model)
    return service.transcribe_audio(audio_path)


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

    try:
        # Create a session context for CDC logging
        session_id = f"tui-{uuid.uuid4().hex[:8]}"
        context_store = ContextStore()
        session_ctx = context_store.create(session_id)
        session_ctx.set_stage("intent_analysis")
        session_ctx.msg_user(query)

        # Build the intent analysis graph (local Ollama only)
        graph = build_intent_analysis_graph(provider="ollama", model="llama2")

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
            )

            # Log success
            session_ctx.msg_system(f"Intent: {intent_result.intent}, Domain: {intent_result.domain}")

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


def run_app(console: Console | None = None) -> None:
    """Run the interactive TUI application.

    Args:
        console: Optional Rich console (for testing). Uses stdout if None.
    """
    if console is None:
        console = Console()

    state = create_initial_state()
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
                    # Non-blocking key read with timeout
                    event = kb.read(timeout=0.1)

                    # Handle key events
                    if event:
                        # Quit
                        if event.key in (Key.CTRL_C, Key.CTRL_Q) or event.char == "q":
                            if state.voice == VoiceState.RECORDING:
                                loop.run_until_complete(recorder.stop_recording())
                            state = state.quit()

                        # Enter - toggle recording
                        elif event.key == Key.ENTER:
                            if state.voice == VoiceState.IDLE:
                                # Start recording
                                try:
                                    loop.run_until_complete(recorder.start_recording())
                                    state = state.start_recording()
                                except Exception as e:
                                    state = state.set_error(f"Mic error: {e}")

                            elif state.voice == VoiceState.RECORDING:
                                # Stop and transcribe
                                state = state.stop_recording()
                                live.update(render_state(state))

                                try:
                                    audio_path = loop.run_until_complete(recorder.stop_recording())
                                    if audio_path and audio_path.exists():
                                        text = loop.run_until_complete(
                                            asyncio.to_thread(transcribe_audio_sync, audio_path)
                                        )
                                        state = state.set_transcript(text)
                                        live.update(render_state(state))

                                        # Run intent analysis
                                        intent_result, graph_data = loop.run_until_complete(run_intent_analysis(text))
                                        state = state.set_intent_result(intent_result, graph_data)

                                        # Cleanup
                                        audio_path.unlink(missing_ok=True)
                                    else:
                                        state = state.set_error("No audio recorded")
                                except Exception as e:
                                    state = state.set_error(f"Error: {e}")

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

    except KeyboardInterrupt:
        if recorder.recording:
            loop.run_until_complete(recorder.stop_recording())
    finally:
        loop.close()
        # Clear screen on exit
        console.clear()
        console.print("👋 Goodbye from Unhinged!")


def main() -> None:
    """Entry point for the TUI application."""
    run_app()
