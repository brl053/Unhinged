"""Parse commands: script parsing and analysis."""

import json
import sys
from pathlib import Path

import click

from cli.utils import log_error, log_info, log_success

# Import service
try:
    from libs.python.clients import ScriptParserService
except ImportError:
    from libs.python.clients.script_parser_service import ScriptParserService


@click.group()
def parse():
    """Parse scripts into structured format.

    Usage:
      unhinged parse script "script content"
      unhinged parse script -f script.txt
      cat script.txt | unhinged parse script
    """
    pass


@parse.command()
@click.argument("text", nargs=-1, required=False)
@click.option(
    "-d",
    "--duration",
    type=int,
    help="Target video duration in seconds (optional)",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Save parsed script to file (default: stdout)",
)
@click.option(
    "--format",
    type=click.Choice(["json", "text"]),
    default="json",
    help="Output format (default: json)",
)
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True),
    help="Read script from file instead of argument",
)
def script(text, duration, output, format, file):
    """Parse script into scenes and segments.

    TEXT can be provided as:
      - Command arguments (joined with spaces): unhinged parse script hello world
      - Quoted argument: unhinged parse script "hello world"
      - File: unhinged parse script -f script.txt
      - Stdin: echo "hello world" | unhinged parse script

    Examples:
      unhinged parse script "This is a test. It works well."
      unhinged parse script -f script.txt -o parsed.json
      unhinged parse script -f script.txt -d 30 --format text
      cat script.txt | unhinged parse script
    """
    try:
        # Get text from file or argument or stdin
        if file:
            script_text = Path(file).read_text().strip()
        elif text:
            script_text = " ".join(text)
        else:
            script_text = click.get_text_stream("stdin").read().strip()

        if not script_text:
            log_error("Script cannot be empty")
            sys.exit(1)

        log_info(f"Parsing script ({len(script_text)} chars)...")

        # Initialize service
        service = ScriptParserService()

        # Parse script
        result = service.parse_script(script_text, target_duration=duration)

        # Format output
        if format == "json":
            output_data = {
                "scenes": result.get("scenes", []),
                "total_duration": result.get("total_duration"),
                "word_count": result.get("word_count"),
                "scene_count": result.get("scene_count"),
                "metadata": result.get("metadata"),
            }
            output_text = json.dumps(output_data, indent=2)
        else:
            # Text format
            lines = []
            for scene in result.get("scenes", []):
                lines.append(f"Scene {scene.get('id', '?')}: {scene.get('text', '')[:50]}...")
                lines.append(f"  Duration: {scene.get('duration', 0):.1f}s")
                lines.append(f"  Visual: {scene.get('visual_cue', 'N/A')}")
                lines.append(f"  Emotion: {scene.get('emotion', 'N/A')}")
                lines.append("")
            output_text = "\n".join(lines)

        # Output result
        if output:
            Path(output).write_text(output_text)
            log_success(f"Parsed script saved to: {output}")
        else:
            click.echo(output_text)

        log_success(f"Parsing complete: {len(result.get('scenes', []))} scenes")

    except Exception as e:
        log_error(f"Script parsing failed: {e}")
        sys.exit(1)
