#!/usr/bin/env python3
"""
@llm-type cli.command.graph_session
@llm-does interactive voice-driven graph session with CDC integration

Interactive session for voice-driven graph execution.
Extracted from graph.py to reduce file length.
"""

import asyncio
import base64
import sys
from pathlib import Path
from typing import Any

from libs.python.graph.context import CDCEventType


async def record_and_transcribe() -> str:
    """Record mic input and transcribe. Returns transcribed text."""
    import signal
    import subprocess
    import tempfile
    from contextlib import suppress

    # Detect ALSA device
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

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio_path = Path(tmp.name)

    print("speak now. press enter when done.")
    sys.stdout.flush()

    proc = await asyncio.create_subprocess_exec(
        "arecord",
        "-D",
        alsa_device,
        "-q",
        "-f",
        "cd",
        "-t",
        "wav",
        str(audio_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    # Wait for enter
    await asyncio.to_thread(sys.stdin.readline)

    # Stop recording
    if proc.returncode is None:
        with suppress(ProcessLookupError):
            proc.send_signal(signal.SIGINT)
        try:
            await asyncio.wait_for(proc.wait(), timeout=3.0)
        except TimeoutError:
            with suppress(ProcessLookupError):
                proc.terminate()
            await proc.wait()

    # Check if valid file
    if not audio_path.exists() or audio_path.stat().st_size < 100:
        audio_path.unlink(missing_ok=True)
        return ""

    # Transcribe
    try:
        from libs.python.clients import TranscriptionService
    except ImportError:
        from libs.python.clients.transcription_service import TranscriptionService

    service = TranscriptionService(model_size="base")
    text = service.transcribe_audio(audio_path)
    audio_path.unlink(missing_ok=True)
    return text.strip()


def match_graph(text: str, graphs: list) -> tuple[Any, float]:
    """Match text to a graph by tags and name. Returns (graph_doc, score).

    Uses shared scoring logic from libs/python/graph/scoring.py.
    """
    from libs.python.graph.scoring import match_best_graph

    return match_best_graph(text, graphs)


def _new_session_id() -> str:
    """Generate a new session ID."""
    import uuid as uuid_mod

    return str(uuid_mod.uuid4())


def _parse_session_choice(line: str, sessions: list) -> tuple[str, bool] | None:
    """Parse user input to find session. Returns (session_id, is_resume) or None."""
    # Try to parse as number
    try:
        idx = int(line) - 1
        if 0 <= idx < len(sessions):
            return sessions[idx].session_id, True
    except ValueError:
        pass

    # Treat as session ID prefix
    for s in sessions:
        if s.session_id.startswith(line):
            return s.session_id, True

    return None


def display_landing_page(context_store, doc_store) -> tuple[str, bool]:
    """Display landing page and return (session_id, is_resume)."""
    print()
    print("unhinged session")
    print("----------------")
    print()

    sessions = context_store.list_sessions(limit=10)

    if not sessions:
        print("no previous sessions")
        print()
        print("starting new session")
        return _new_session_id(), False

    print("previous sessions:")
    for i, s in enumerate(sessions, 1):
        print(f"  [{i}] {s}")
    print()
    print("enter number to resume, or 'new' for new session")
    print("> ", end="")
    sys.stdout.flush()

    try:
        line = sys.stdin.readline().strip().lower()
    except EOFError:
        return _new_session_id(), False

    if not line or line in ("new", "n"):
        new_id = _new_session_id()
        print(f"session: {new_id[:8]}...")
        return new_id, False

    result = _parse_session_choice(line, sessions)
    if result:
        print(f"resuming: {result[0][:8]}...")
        return result

    new_id = _new_session_id()
    print(f"session: {new_id[:8]}...")
    return new_id, False


def embed_observer(event) -> None:
    """Observer callback for embedding transparency."""
    print(f"  [embed] {event}")


def get_system_prompt() -> str:
    """Return the system prompt (philosophy, brand, rules).

    This is the 'rules of conversation' that shapes LLM behavior.
    """
    return """You are Unhinged, a voice-driven graph execution assistant.

Philosophy:
- Execute user intent through graph workflows
- Minimal output, maximum clarity
- No filler, no pleasantries
- Report errors directly

Execution context:
- User speaks, you match to stored graphs
- Graphs are pre-validated workflows
- You confirm before execution
- You report stdout/stderr faithfully

Output format:
- ASCII only, no emoji
- Sparse, militarized tone
- Report facts, not interpretations"""


# Global session state for disgraceful shutdown recovery
_session_state: dict = {}


def save_session_state(session_id: str, session_ctx, context_store) -> None:
    """Save session state for recovery after disgraceful shutdown."""
    _session_state["session_id"] = session_id
    _session_state["session_ctx"] = session_ctx
    _session_state["context_store"] = context_store


def attempt_recovery_persist() -> None:
    """Attempt to persist session on disgraceful shutdown.

    Called from signal handlers or exception handlers.
    Best-effort - may fail silently if system is in bad state.
    """
    if not _session_state:
        return

    try:
        session_id = _session_state.get("session_id")
        session_ctx = _session_state.get("session_ctx")
        context_store = _session_state.get("context_store")

        if session_ctx and context_store:
            print()
            print("disgraceful shutdown - attempting recovery persist...")
            session_ctx.set("shutdown_type", "disgraceful")
            if context_store.persist(session_ctx):
                sid_display = session_id[:8] if session_id else "unknown"
                print(f"recovery saved: {sid_display}...")
            else:
                print("recovery persist failed")
    except Exception:
        pass  # Best effort


async def run_session() -> None:  # noqa: C901
    """Interactive voice-driven graph session."""
    import uuid as uuid_mod

    try:
        from libs.python.graph import ContextStore
        from libs.python.persistence import (
            EmbeddingDocumentStore,
            get_document_store,
        )
    except ImportError:
        print("error: document store not available")
        return

    doc_store = get_document_store()
    context_store = ContextStore()

    # === LANDING PAGE: session selection ===
    session_id, is_resume = display_landing_page(context_store, doc_store)

    # Create or resume session context
    if is_resume:
        session_ctx = context_store.resume(session_id)
        if session_ctx is None:
            print("warning: could not load session, starting fresh")
            session_ctx = context_store.create(session_id)
    else:
        session_ctx = context_store.create(session_id)

    # Register embedding observer for transparency
    if isinstance(doc_store, EmbeddingDocumentStore):
        doc_store.add_observer(embed_observer)

    # Save session state for disgraceful shutdown recovery
    save_session_state(session_id, session_ctx, context_store)

    print()
    print("voice-driven graph execution")
    print("commands: voice, list, quit")
    print()

    while True:
        print("> ", end="")
        sys.stdout.flush()

        # Read text input first
        try:
            line = await asyncio.to_thread(sys.stdin.readline)
        except EOFError:
            break

        line = line.strip().lower()

        if not line:
            continue

        if line in ("quit", "exit", "q"):
            break

        if line == "list":
            docs = doc_store.query("graphs", limit=50)
            if not docs:
                print("no graphs stored")
            else:
                for doc in docs:
                    name = doc.data.get("name", "unnamed")
                    tags = ", ".join(doc.data.get("tags", []))
                    print(f"  {name}" + (f" [{tags}]" if tags else ""))
            print()
            continue

        if line == "voice" or line == "v":
            text = await record_and_transcribe()
            if not text:
                session_ctx.msg_system("no speech detected")
                print("(no speech detected)")
                print()
                continue
            print(f"heard: {text}")
        else:
            text = line

        # Log user input to CDC feed
        session_ctx.msg_user(text)
        session_ctx.set("last_input", text)

        # Match to graph using execution protocol
        docs = doc_store.query("graphs", limit=50)
        if not docs:
            session_ctx.msg_system("no graphs to match against")
            print("no graphs to match against")
            print()
            continue

        match, score = match_graph(text, docs)

        if not match or score < 1.0:
            session_ctx.msg_system(f"no matching graph (best score: {score:.1f})")
            print("no matching graph found")
            print()
            continue

        name = match.data.get("name", "unnamed")
        session_ctx.msg_system(f"matched: {name} (score: {score:.1f})")
        print(f"matched: {name} (score: {score:.1f})")
        print("run? [y/n] ", end="")
        sys.stdout.flush()

        confirm = await asyncio.to_thread(sys.stdin.readline)
        if confirm.strip().lower() not in ("y", "yes"):
            session_ctx.msg_user("skipped")
            print("skipped")
            print()
            continue

        # Execute graph (inline to avoid deep nesting)
        await _execute_graph(match, text, session_id, session_ctx, uuid_mod)

    # === GRACEFUL SHUTDOWN ===
    # Persist session state on clean exit
    print("persisting session...")
    if context_store.persist(session_ctx):
        print(f"session saved: {session_id[:8]}...")
    else:
        print("warning: session persist failed")
    print("goodbye")


async def _execute_graph(match, text: str, session_id: str, session_ctx, uuid_mod) -> None:
    """Execute a matched graph through the 3-stage protocol.

    Extracted to reduce nesting depth in run_session.
    """

    from libs.python.graph import (
        AssembleFinalPromptStep,
        AuditAction,
        ContextWindowCheckStep,
        ExecutionProtocol,
        FlightContext,
        FlightRecord,
        GarbageCompressionStep,
        InjectSystemPromptStep,
        PromptPipeline,
        RubricMatchCheck,
        StepResult,
        Verdict,
    )

    # Build protocol with pre-flight and post-flight procedures
    protocol = ExecutionProtocol()

    # Pre-flight: rubric validation
    protocol.register_check(
        RubricMatchCheck(
            rubric_id="graph_match_v1",
            graph_tags=match.data.get("tags", []),
            graph_name=match.data.get("name", ""),
            graph_description=match.data.get("description", ""),
        )
    )

    # Post-flight: audit to document store
    protocol.register_action(AuditAction(collection="execution_audit"))

    # Create flight context (link to session)
    execution_id = str(uuid_mod.uuid4())
    flight_context = FlightContext(
        graph_id=match.id,
        execution_id=execution_id,
        input_data={"text": text, "session_id": session_id},
    )

    # Track execution in session
    session_ctx.set("last_execution_id", execution_id)
    session_ctx.set("last_graph_id", match.id)
    session_ctx.set_stage("pre_flight")

    # Initialize flight record
    record = FlightRecord(context=flight_context)

    # === PRE-FLIGHT STEP 0: PROMPT ASSEMBLY PIPELINE ===
    cdc_feed = session_ctx.cdc_feed()
    message_history = []
    for event in cdc_feed:
        if event.event_type == CDCEventType.MSG_USER:
            message_history.append({"role": "user", "content": event.data.get("text", "")})
        elif event.event_type == CDCEventType.MSG_SYSTEM:
            message_history.append({"role": "assistant", "content": event.data.get("text", "")})

    system_prompt = get_system_prompt()

    # Build and run prompt pipeline
    pipeline = PromptPipeline(context_window_size=128000)
    pipeline.add_step(InjectSystemPromptStep(system_prompt))
    pipeline.add_step(ContextWindowCheckStep(warn_threshold=0.8, abort_threshold=0.95))
    pipeline.add_step(GarbageCompressionStep(compress_threshold=0.7, keep_recent_n=20))
    pipeline.add_step(AssembleFinalPromptStep())

    prompt_payload, pipeline_outputs = pipeline.run(
        user_input=text,
        session=session_ctx,
        initial_history=message_history,
    )

    # Log pipeline metrics to CDC
    session_ctx.emit(
        CDCEventType.PIPELINE_COMPLETE,
        {
            "steps": prompt_payload.steps_executed,
            "token_estimate": prompt_payload.token_count_estimate,
            "context_usage": round(prompt_payload.context_usage_ratio(), 4),
            "compression_count": prompt_payload.compression_count,
        },
    )

    # Check if pipeline aborted
    pipeline_aborted = any(o.result == StepResult.ABORT for o in pipeline_outputs)
    if pipeline_aborted:
        abort_reason = next((o.reason for o in pipeline_outputs if o.result == StepResult.ABORT), "pipeline abort")
        session_ctx.msg_error(f"pre-flight abort: {abort_reason}")
        print(f"pre-flight abort: {abort_reason}")
        record.aborted = True
        record.abort_reason = abort_reason
        protocol.run_post_flight(record)
        print()
        return

    # Store assembled prompt in flight context
    flight_context.metadata["prompt_payload"] = {
        "final_prompt": prompt_payload.final_prompt,
        "token_estimate": prompt_payload.token_count_estimate,
        "context_usage": prompt_payload.context_usage_ratio(),
    }

    # === STAGE 1: PRE-FLIGHT CHECKS ===
    verdict, checks = protocol.run_pre_flight(flight_context)
    record.pre_flight_checks = checks

    for check in checks:
        session_ctx.flight_check(
            check_name=check.check_id,
            passed=check.verdict != Verdict.ABORT,
            reason=check.reason,
        )

    if verdict == Verdict.ABORT:
        reason = checks[-1].reason if checks else "unknown"
        session_ctx.msg_error(f"pre-flight abort: {reason}")
        print(f"pre-flight abort: {reason}")
        record.aborted = True
        record.abort_reason = reason
        protocol.run_post_flight(record)
        print()
        return

    # === STAGE 2: IN-FLIGHT ===
    await _run_in_flight(match, session_ctx, record, protocol)


async def _run_in_flight(match, session_ctx, record, protocol) -> None:
    """Execute the in-flight stage of graph execution.

    Runs the graph script and captures stdout/stderr with optional strace.
    """
    import os
    import subprocess
    import sys
    import tempfile

    from libs.python.graph import FILTER_IO, is_strace_available, run_with_strace

    name = match.data.get("name", "unnamed")
    session_ctx.set_stage("in_flight")
    session_ctx.exec_start(match.id, record.context.execution_id)
    session_ctx.msg_system(f"running {name}...")
    print(f"running {name}...")

    content = match.data.get("content", "")
    encoding = match.data.get("encoding", "")
    content_bytes = base64.b64decode(content) if encoding == "base64" else content.encode("utf-8")

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".py", delete=False) as f:
        f.write(content_bytes)
        temp_path = f.name

    try:
        use_strace = is_strace_available()

        if use_strace:
            session_ctx.msg_system("strace: capturing syscalls...")
            result, syscalls = run_with_strace(
                [sys.executable, temp_path],
                capture_output=True,
                trace_filter=FILTER_IO,
            )
            for sc in syscalls:
                session_ctx.syscall(sc.name, sc.args, sc.result)
            if syscalls:
                session_ctx.msg_system(f"strace: captured {len(syscalls)} syscalls")
        else:
            result = subprocess.run([sys.executable, temp_path], capture_output=True, text=True)

        record.in_flight_result = {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

        if result.stdout:
            for line in result.stdout.splitlines():
                session_ctx.exec_stdout(line)
            print(result.stdout)
        if result.stderr:
            for line in result.stderr.splitlines():
                session_ctx.exec_stderr(line)
            print(result.stderr, file=sys.stderr)

        session_ctx.exec_exit(result.returncode)
        if result.returncode == 0:
            session_ctx.msg_system("done")
            print("done")
        else:
            session_ctx.msg_error(f"failed (exit {result.returncode})")
            print(f"failed (exit {result.returncode})")
    finally:
        os.unlink(temp_path)

    # === STAGE 3: POST-FLIGHT ===
    session_ctx.set_stage("post_flight")
    protocol.run_post_flight(record)
    session_ctx.flight_action("audit", success=True)
    print()
