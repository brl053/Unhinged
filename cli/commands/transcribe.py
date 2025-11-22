"""Transcribe commands: voice-to-text transcription."""

import asyncio
import sys
from pathlib import Path

import click

from cli.utils import log_error, log_info, log_success

# Import service - handle both direct and pytest imports
try:
    from libs.services import TranscriptionService
except ImportError:
    from libs.services.transcription_service import TranscriptionService

from libs.python.drivers.transcription import MicTranscriptionDriver


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


@transcribe.command()
@click.option(
    "-m",
    "--model",
    default="base",
    type=click.Choice(["tiny", "base", "small", "medium", "large"]),
    help="Whisper model size (default: base)",
)
@click.option(
    "--chunk-seconds",
    default=5,
    show_default=True,
    type=int,
    help="Approximate duration of each audio chunk in seconds",
)
@click.option(
    "--max-seconds",
    default=None,
    type=int,
    help="Optional maximum total recording duration in seconds (Ctrl+C to stop earlier)",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Save full transcript to file after recording",
)
@click.option(
    "--plain",
    is_flag=True,
    help="Print just text lines per chunk (no timestamps)",
)
def mic(model, chunk_seconds, max_seconds, output, plain):
    """Transcribe live microphone input with rolling updates."""

    recorded_chunks: list[str] = []

    async def _run() -> None:
        """Run the microphone transcription loop."""
        driver = MicTranscriptionDriver()

        def _on_segment(seg) -> None:
            text = getattr(seg, "text", "").strip()
            if not text:
                return
            print(f"[mic] Segment {getattr(seg, 'sequence', '?')}: {text}")
            recorded_chunks.append(text)
            if plain:
                click.echo(text)
            else:
                click.echo(f"[{seg.start_time:05.1f}-{seg.end_time:05.1f}s] {text}")

        log_info(
            f"Starting microphone transcription (model={model}, chunk={chunk_seconds}s, max={max_seconds or '\u221e'}s)"
        )
        print("[mic] Listening now, speak...")

        try:
            result = await driver.execute(
                "mic_stream",
                {
                    "chunk_seconds": chunk_seconds,
                    "max_seconds": max_seconds,
                    "model_size": model,
                    "on_segment": _on_segment,
                },
            )
        except Exception as exc:  # Surface driver errors nicely
            log_error(f"Microphone transcription failed: {exc}")
            sys.exit(1)

        if not result.get("success"):
            log_error(f"Microphone transcription failed: {result.get('error')}")
            sys.exit(1)

        session = result["data"]["session"]
        print(f"[mic] Recording stopped. Total segments: {len(session.segments)}")
        full_text = session.text
        log_success(
            f"Microphone transcription complete: {len(full_text)} characters across {len(session.segments)} chunks",
        )

        # At the end, print the whole transcript as one paragraph
        if full_text:
            click.echo()
            click.echo(full_text)

        if output and full_text:
            output_path = Path(output)
            output_path.write_text(full_text)
            log_success(f"Full transcript saved to: {output}")

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        # Best-effort: on Ctrl+C, print whatever transcript we have so far
        if recorded_chunks:
            partial = " ".join(t.strip() for t in recorded_chunks if t.strip())
            if partial:
                click.echo()
                click.echo(partial)
        log_info("Stopped microphone transcription by user request")
