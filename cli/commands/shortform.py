"""Short-form video generation commands."""

import sys
from pathlib import Path

import click

from cli.utils import log_error, log_info, log_success

# Import service
try:
    from libs.python.clients import ShortFormVideoService
except ImportError:
    from libs.python.clients.shortform_video_service import ShortFormVideoService


@click.group()
def shortform():
    """Generate short-form videos (TikTok/Reels/Shorts).

    Usage:
      unhinged shortform generate "script content" --platform tiktok
      unhinged shortform generate -f script.txt --platform reels
      cat script.txt | unhinged shortform generate --platform shorts
    """
    pass


@shortform.command()
@click.argument("script", nargs=-1, required=False)
@click.option(
    "-p",
    "--platform",
    type=click.Choice(["tiktok", "reels", "shorts"]),
    default="tiktok",
    help="Target platform (default: tiktok)",
)
@click.option(
    "-v",
    "--voice",
    type=click.Choice(["nova", "echo", "sage", "shimmer"]),
    default="nova",
    help="Voice for narration (default: nova)",
)
@click.option(
    "-s",
    "--style",
    default="cinematic",
    help="Visual style (default: cinematic)",
)
@click.option(
    "-q",
    "--quality",
    type=click.Choice(["draft", "standard", "ultra"]),
    default="standard",
    help="Output quality (default: standard)",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Save video to file (default: stdout path)",
)
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True),
    help="Read script from file instead of argument",
)
def generate(script, platform, voice, style, quality, output, file):
    """Generate short-form video from script.

    SCRIPT can be provided as:
      - Command arguments (joined with spaces): unhinged shortform generate hello world
      - Quoted argument: unhinged shortform generate "hello world"
      - File: unhinged shortform generate -f script.txt
      - Stdin: echo "hello world" | unhinged shortform generate

    Examples:
      unhinged shortform generate "This is a test" --platform tiktok
      unhinged shortform generate -f script.txt --platform reels -v echo
      unhinged shortform generate -f script.txt --platform shorts -q ultra
      cat script.txt | unhinged shortform generate --platform tiktok
    """
    try:
        # Get script from file or argument or stdin
        if file:
            script_text = Path(file).read_text().strip()
        elif script:
            script_text = " ".join(script)
        else:
            script_text = click.get_text_stream("stdin").read().strip()

        if not script_text:
            log_error("Script cannot be empty")
            sys.exit(1)

        log_info(f"Generating {platform} short-form video...")

        # Initialize service
        service = ShortFormVideoService()

        # Generate video
        result = service.generate_from_script(
            script=script_text,
            platform=platform,
            voice=voice,
            style=style,
            quality=quality,
        )

        # Output result
        video_path = result.get("video_path", "")
        generation_time = result.get("generation_time", 0)

        if output:
            import shutil

            shutil.copy(video_path, output)
            log_success(f"Video saved to: {output}")
        else:
            log_success(f"Video generated: {video_path}")

        log_info(f"Generation time: {generation_time:.2f}s")
        log_info(f"Platform: {platform}, Voice: {voice}, Quality: {quality}")

    except Exception as e:
        log_error(f"Short-form video generation failed: {e}")
        sys.exit(1)
