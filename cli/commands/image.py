"""Image generation commands."""

import sys
from pathlib import Path

import click

from cli.utils import log_error, log_info, log_success

# Import service - handle both direct and pytest imports
try:
    from libs.services import ImageGenerationService
except ImportError:
    from libs.services.image_generation_service import ImageGenerationService


@click.group()
def image():
    """Generate images from text prompts.

    Usage:
      unhinged image generate "a sunset over mountains"
      unhinged image generate "a cat" -w 768 -h 768
      unhinged image generate "a dog" --steps 30 --guidance 8.0
    """
    pass


@image.command()
@click.argument("prompt", required=False, default="")
@click.option(
    "-w",
    "--width",
    type=int,
    default=512,
    help="Image width in pixels (default: 512)",
)
@click.option(
    "-h",
    "--height",
    type=int,
    default=512,
    help="Image height in pixels (default: 512)",
)
@click.option(
    "--steps",
    type=int,
    default=20,
    help="Inference steps 20-50, lower=faster (default: 20)",
)
@click.option(
    "--guidance",
    type=float,
    default=7.5,
    help="Guidance scale 1.0-20.0 (default: 7.5)",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Save image to file (default: stdout path)",
)
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True),
    help="Read prompt from file instead of argument",
)
def generate(prompt, width, height, steps, guidance, output, file):
    """Generate image from a text prompt."""
    try:
        # Get prompt from file or argument or stdin
        if file:
            prompt = Path(file).read_text().strip()
        elif not prompt:
            prompt = click.get_text_stream("stdin").read().strip()

        if not prompt:
            log_error("Prompt cannot be empty")
            sys.exit(1)

        log_info(f"Generating image: {prompt[:50]}...")

        # Initialize service
        service = ImageGenerationService()

        # Generate image
        result = service.generate_image(
            prompt=prompt,
            width=width,
            height=height,
            num_inference_steps=steps,
            guidance_scale=guidance,
        )

        # Output result
        image_path = result["image_path"]
        generation_time = result["generation_time"]

        if output:
            # Copy to output file
            import shutil

            shutil.copy(image_path, output)
            log_success(f"Image saved to: {output}")
            log_info(f"Generation time: {generation_time:.2f}s")
        else:
            log_success(f"Image generated: {image_path}")
            log_info(f"Generation time: {generation_time:.2f}s")
            log_info(f"Prompt: {prompt}")

    except Exception as e:
        log_error(f"Image generation failed: {e}")
        sys.exit(1)
