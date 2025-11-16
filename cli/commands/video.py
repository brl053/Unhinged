"""Video generation commands."""

import sys
from pathlib import Path

import click

from cli.utils import log_error, log_info, log_success

# Import service
try:
    from libs.services import VideoGenerationService
except ImportError:
    from libs.services.video_generation_service import VideoGenerationService


@click.group()
def video():
    """Generate videos from text prompts.

    Usage:
      unhinged video generate "a sunset over mountains"
      unhinged video generate "a cat" -d 10 --fps 30
      cat script.txt | unhinged video generate
    """
    pass


@video.command()
@click.argument("prompt", nargs=-1, required=False)
@click.option(
    "-a",
    "--approach",
    type=click.Choice(["frame-interp", "svd"]),
    default="frame-interp",
    help="Generation approach (default: frame-interp)",
)
@click.option(
    "-d",
    "--duration",
    type=int,
    default=30,
    help="Video duration in seconds (default: 30)",
)
@click.option(
    "--fps",
    type=int,
    default=24,
    help="Frames per second (default: 24)",
)
@click.option(
    "-w",
    "--width",
    type=int,
    default=512,
    help="Video width in pixels (default: 512)",
)
@click.option(
    "-h",
    "--height",
    type=int,
    default=512,
    help="Video height in pixels (default: 512)",
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
    help="Read prompt from file instead of argument",
)
def generate(prompt, approach, duration, fps, width, height, output, file):
    """Generate video from a text prompt.

    PROMPT can be provided as:
      - Command arguments (joined with spaces): unhinged video generate a sunset
      - Quoted argument: unhinged video generate "a sunset over mountains"
      - File: unhinged video generate -f prompt.txt
      - Stdin: echo "a sunset" | unhinged video generate

    Examples:
      unhinged video generate "a sunset over mountains" -d 10
      unhinged video generate "a cat playing" --fps 30 -w 768 -h 768
      unhinged video generate "nature scene" -a svd -d 5
    """
    try:
        # Get prompt from file or argument or stdin
        if file:
            prompt_text = Path(file).read_text().strip()
        elif prompt:
            prompt_text = " ".join(prompt)
        else:
            prompt_text = click.get_text_stream("stdin").read().strip()

        if not prompt_text:
            log_error("Prompt cannot be empty")
            sys.exit(1)

        log_info(f"Generating video: {prompt_text[:50]}...")

        # Initialize service
        service = VideoGenerationService()

        # Generate video
        result = service.generate_video(
            prompt=prompt_text,
            approach=approach,
            duration=duration,
            fps=fps,
            width=width,
            height=height,
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
        log_info(f"Duration: {duration}s, FPS: {fps}, Resolution: {width}x{height}")

    except Exception as e:
        log_error(f"Video generation failed: {e}")
        sys.exit(1)
