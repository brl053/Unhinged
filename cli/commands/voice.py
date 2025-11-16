"""Voice/Text-to-Speech commands."""

import sys
from pathlib import Path

import click

from cli.utils import log_error, log_info, log_success

# Import service - handle both direct and pytest imports
try:
    from libs.services import TTSService
except ImportError:
    from libs.services.tts_service import TTSService


@click.group()
def voice():
    """Generate voice/audio from text.

    Usage:
      unhinged voice generate "Hello world"
      unhinged voice generate "Hello world" -v nova
      unhinged voice generate "Hello world" --speed 1.5
      cat script.txt | unhinged voice generate
    """
    pass


@voice.command()
@click.argument("text", required=False, default="")
@click.option(
    "-v",
    "--voice",
    type=click.Choice(["nova", "echo", "sage", "shimmer"]),
    default="nova",
    help="Voice to use (default: nova)",
)
@click.option(
    "--speed",
    type=float,
    default=1.0,
    help="Speech speed 0.5-2.0 (default: 1.0)",
)
@click.option(
    "-e",
    "--emotion",
    type=click.Choice(["neutral", "happy", "sad", "angry"]),
    default="neutral",
    help="Emotion/tone (default: neutral)",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Save audio to file (default: stdout path)",
)
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True),
    help="Read text from file instead of argument",
)
def generate(text, voice, speed, emotion, output, file):
    """Generate voice/audio from text."""
    try:
        # Get text from file or argument or stdin
        if file:
            text = Path(file).read_text().strip()
        elif not text:
            text = click.get_text_stream("stdin").read().strip()

        if not text:
            log_error("Text cannot be empty")
            sys.exit(1)

        log_info(f"Generating voice: {text[:50]}...")

        # Initialize service
        service = TTSService()

        # Generate voiceover
        result = service.generate_voiceover(
            text=text,
            voice=voice,
            speed=speed,
            emotion=emotion,
        )

        # Output result
        audio_path = result["audio_path"]
        duration = result.get("duration", 0)

        if output:
            # Copy to output file
            import shutil

            shutil.copy(audio_path, output)
            log_success(f"Audio saved to: {output}")
            log_info(f"Duration: {duration:.2f}s")
        else:
            log_success(f"Audio generated: {audio_path}")
            log_info(f"Duration: {duration:.2f}s")
            log_info(f"Voice: {voice}, Speed: {speed}x, Emotion: {emotion}")

    except Exception as e:
        log_error(f"Voice generation failed: {e}")
        sys.exit(1)
