"""Transcribe commands: voice-to-text transcription."""

import sys
from pathlib import Path

import click

from cli.utils import log_error, log_info, log_success

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
