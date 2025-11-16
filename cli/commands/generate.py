"""Generate commands: text generation from prompts."""

import sys
from pathlib import Path

import click

from cli.utils import log_error, log_info, log_success
from libs.services.text_generation_service import TextGenerationService


@click.group()
def generate():
    """Generate content: text, images, audio.

    Usage:
      unhinged generate text "your prompt here"
      unhinged generate text < input.txt
      cat prompt.txt | unhinged generate text
    """
    pass


@generate.command()
@click.argument("prompt", required=False, default="")
@click.option(
    "-m",
    "--model",
    default="llama2",
    help="LLM model to use (default: llama2)",
)
@click.option(
    "-p",
    "--provider",
    default="ollama",
    help="LLM provider: ollama, openai, anthropic (default: ollama)",
)
@click.option(
    "-t",
    "--tokens",
    type=int,
    default=512,
    help="Maximum tokens to generate (default: 512)",
)
@click.option(
    "--temperature",
    type=float,
    default=0.7,
    help="Sampling temperature 0.0-1.0 (default: 0.7)",
)
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True),
    help="Read prompt from file instead of argument",
)
def text(prompt, model, provider, tokens, temperature, file):
    """Generate text from a prompt.

    PROMPT can be provided as:
      - Command argument: unhinged generate text "write a haiku"
      - File: unhinged generate text -f prompt.txt
      - Stdin: echo "write a haiku" | unhinged generate text

    Examples:
      unhinged generate text "write me a haiku about the moon on an autumn night"
      unhinged generate text -m mistral "explain quantum computing"
      unhinged generate text -p openai -m gpt-4 "write a poem"
      cat prompt.txt | unhinged generate text
    """
    try:
        # Determine prompt source
        if file:
            # Read from file
            prompt_text = Path(file).read_text().strip()
            log_info(f"Reading prompt from: {file}")
        elif prompt:
            # Use command argument
            prompt_text = prompt
        else:
            # Try to read from stdin
            if not sys.stdin.isatty():
                prompt_text = sys.stdin.read().strip()
                log_info("Reading prompt from stdin")
            else:
                log_error("No prompt provided. Use: unhinged generate text --help")
                sys.exit(1)

        if not prompt_text:
            log_error("Prompt cannot be empty")
            sys.exit(1)

        log_info(f"Generating text with {provider}/{model}...")

        # Initialize service and generate
        service = TextGenerationService(model=model, provider=provider)
        result = service.generate(
            prompt=prompt_text,
            max_tokens=tokens,
            temperature=temperature,
        )

        # Output result
        click.echo(result)
        log_success(f"Generated {len(result)} characters")

    except Exception as e:
        log_error(f"Text generation failed: {e}")
        sys.exit(1)
