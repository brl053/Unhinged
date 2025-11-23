"""Transcribe commands: voice-to-text transcription."""

import asyncio
import sys
import tempfile
import time
from contextlib import suppress
from pathlib import Path
from uuid import uuid4

import click

from cli.utils import log_error, log_info, log_success
from libs.python.persistence.event_store import persist_event
from unhinged_events import create_service_logger

# Import service - handle both direct and pytest imports
try:
    from libs.services import TranscriptionService
except ImportError:
    from libs.services.transcription_service import TranscriptionService


@click.group()
def transcribe():
    """Transcribe audio: speech-to-text conversion.

    Usage:
      unhinged transcribe audio input.wav
      unhinged transcribe audio input.mp3 -m large
    """
    pass


@transcribe.command()
@click.argument("audio_file", type=click.Path(exists=True))
@click.option(
    "-m",
    "--model",
    default="base",
    type=click.Choice(["tiny", "base", "small", "medium", "large"]),
    help="Whisper model size (default: base)",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Save transcript to file (default: stdout)",
)
@click.option(
    "--metadata",
    is_flag=True,
    help="Include metadata (language, segments, duration)",
)
def audio(audio_file, model, output, metadata):
    """Transcribe audio file to text.

    Supported formats: WAV, MP3, FLAC, OGG, M4A

    Examples:
      unhinged transcribe audio recording.wav
      unhinged transcribe audio meeting.mp3 -m large
      unhinged transcribe audio speech.wav -o transcript.txt
      unhinged transcribe audio audio.wav --metadata
    """
    try:
        audio_path = Path(audio_file)

        if not audio_path.exists():
            log_error(f"Audio file not found: {audio_file}")
            sys.exit(1)

        log_info(f"Transcribing audio: {audio_file} (model: {model})")

        # Initialize service
        service = TranscriptionService(model_size=model)

        # Transcribe
        if metadata:
            result = service.transcribe_with_metadata(audio_path)
            transcript = result["text"]
            language = result.get("language", "unknown")
            log_info(f"Language detected: {language}")
        else:
            transcript = service.transcribe_audio(audio_path)

        # Output result
        if output:
            output_path = Path(output)
            output_path.write_text(transcript)
            log_success(f"Transcript saved to: {output}")
        else:
            click.echo(transcript)

        log_success(f"Transcription complete: {len(transcript)} characters")

    except FileNotFoundError as e:
        log_error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        log_error(f"Transcription failed: {e}")
        sys.exit(1)


async def _record_mic_to_file(audio_path: Path, *, max_seconds: int | None) -> int:
    """Record microphone audio into ``audio_path`` until Enter or timeout.

    Returns the elapsed recording time in seconds.
    """

    try:
        proc = await asyncio.create_subprocess_exec(
            "arecord",
            "-q",
            "-f",
            "cd",
            "-t",
            "wav",
            str(audio_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError:
        log_error("arecord not found. Install 'alsa-utils' or configure a recorder.")
        sys.exit(1)

    start_time = time.time()
    stop_event = asyncio.Event()

    async def _ticker() -> None:
        while not stop_event.is_set():
            elapsed = int(time.time() - start_time)
            msg = f"[mic] Recording... {elapsed}s elapsed. Press Enter to stop."
            sys.stdout.write("\r" + msg)
            sys.stdout.flush()
            await asyncio.sleep(1)

        # Clear the line
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

    ticker_task = asyncio.create_task(_ticker())

    async def _wait_for_enter() -> None:
        await asyncio.to_thread(sys.stdin.readline)

    wait_tasks = [asyncio.create_task(_wait_for_enter())]
    if max_seconds is not None and max_seconds > 0:
        wait_tasks.append(asyncio.create_task(asyncio.sleep(max_seconds)))

    # Stop when user presses Enter or we hit max_seconds
    done, pending = await asyncio.wait(wait_tasks, return_when=asyncio.FIRST_COMPLETED)
    stop_event.set()
    for task in pending:
        task.cancel()

    with suppress(asyncio.CancelledError):  # pragma: no cover - defensive
        await ticker_task

    # Stop the recorder process
    proc.terminate()
    try:
        await asyncio.wait_for(proc.wait(), timeout=5.0)
    except TimeoutError:  # pragma: no cover - defensive
        proc.kill()
        await proc.wait()

    return int(time.time() - start_time)


async def _transcribe_recording(
    *,
    service: TranscriptionService,
    audio_path: Path,
    model: str,
    max_seconds: int | None,
    service_id: str,
    session_id: str,
    logger,
) -> tuple[str, int]:
    """Transcribe the recorded audio and emit events.

    Returns the transcript text and duration.
    """

    log_info("Transcribing recorded audio...")

    try:
        full_text = service.transcribe_audio(audio_path)
    except Exception as exc:  # Surface errors nicely
        log_error(f"Microphone transcription failed: {exc}")
        if logger is not None:
            with suppress(Exception):  # pragma: no cover - best-effort logging
                logger.error("mic session error", exception=exc)
        with suppress(Exception):  # pragma: no cover - best-effort persistence
            persist_event(
                service_id,
                "transcription.mic.session.error",
                {"error": str(exc)},
                level="ERROR",
                session_id=session_id,
            )
        raise

    return full_text, 0


async def _run_mic_session(model: str, max_seconds: int | None, output: str | None) -> None:
    """Core async implementation for ``mic`` command."""

    service_id = "cli-transcribe-mic"
    session_id = str(uuid4())

    try:
        logger = create_service_logger(service_id, version="1.0.0")
    except Exception:  # pragma: no cover - defensive
        logger = None

    service = TranscriptionService(model_size=model)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio_path = Path(tmp.name)

    log_info(f"Starting microphone recording (model={model}). Press Enter to stop and transcribe.")
    if logger is not None:
        with suppress(Exception):  # pragma: no cover - best-effort logging
            logger.info(
                "mic session start",
                {
                    "model_size": model,
                    "max_seconds": max_seconds,
                },
            )

    with suppress(Exception):  # pragma: no cover - best-effort persistence
        persist_event(
            service_id,
            "transcription.mic.session.start",
            {
                "model_size": model,
                "max_seconds": max_seconds,
            },
            level="INFO",
            session_id=session_id,
        )

    try:
        elapsed = await _record_mic_to_file(audio_path, max_seconds=max_seconds)
        full_text, _ = await _transcribe_recording(
            service=service,
            audio_path=audio_path,
            model=model,
            max_seconds=max_seconds,
            service_id=service_id,
            session_id=session_id,
            logger=logger,
        )
    finally:
        with suppress(Exception):  # pragma: no cover - best-effort cleanup
            audio_path.unlink(missing_ok=True)  # type: ignore[arg-type]

    log_success(
        f"Microphone transcription complete in {elapsed}s: {len(full_text)} characters",
    )

    if logger is not None:
        with suppress(Exception):  # pragma: no cover - best-effort logging
            logger.info(
                "mic session complete",
                {
                    "model_size": model,
                    "max_seconds": max_seconds,
                    "duration_seconds": elapsed,
                    "total_characters": len(full_text),
                },
            )

    with suppress(Exception):  # pragma: no cover - best-effort persistence
        persist_event(
            service_id,
            "transcription.mic.session.complete",
            {
                "model_size": model,
                "max_seconds": max_seconds,
                "duration_seconds": elapsed,
                "total_characters": len(full_text),
            },
            level="INFO",
            session_id=session_id,
        )

    click.echo()
    click.echo(full_text)

    if output and full_text:
        output_path = Path(output)
        output_path.write_text(full_text)
        log_success(f"Full transcript saved to: {output}")


@transcribe.command()
@click.option(
    "-m",
    "--model",
    default="base",
    type=click.Choice(["tiny", "base", "small", "medium", "large"]),
    help="Whisper model size (default: base)",
)
@click.option(
    "--max-seconds",
    default=None,
    type=int,
    help="Optional maximum recording duration in seconds (press Enter to stop earlier)",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Save full transcript to file after recording",
)
def mic(model, max_seconds, output):
    """Record a mic session, then transcribe once with full context.

    Recording starts immediately. Press Enter to stop recording and begin
    transcription. This avoids mid-word chunking and gives Whisper the
    full context of the session.
    """

    try:
        asyncio.run(_run_mic_session(model, max_seconds, output))
    except KeyboardInterrupt:
        log_info("Stopped microphone transcription by user request")
