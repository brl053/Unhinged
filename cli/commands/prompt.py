"""CLI commands for prompt orchestration and template rendering.

@llm-type cli-prompt-commands
@llm-does Provides 'unhinged prompt' commands for rendering Jinja2 templates
"""

import json
from typing import Any

import click
import yaml

from libs.python.prompt_orchestration import UnhingedPromptRenderer


@click.group()
def prompt() -> None:
    """Prompt orchestration and template rendering commands."""
    pass


@prompt.command()
@click.argument("template_name")
@click.option(
    "--context",
    "-c",
    type=click.Path(exists=True),
    help="YAML file with context variables",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def render(template_name: str, context: str | None, output: str) -> None:
    """Render a Jinja2 template with context.

    Example:
        unhinged prompt render templates/memorandum.j2 -c context.yaml
    """
    renderer = UnhingedPromptRenderer()

    # Load context from YAML file if provided
    context_dict: dict[str, Any] = {}
    if context:
        with open(context) as f:
            context_dict = yaml.safe_load(f) or {}

    try:
        result = renderer.render_template(template_name, context_dict)

        if output == "json":
            click.echo(json.dumps({"template": template_name, "output": result}))
        else:
            click.echo(result)
    except Exception as e:
        click.echo(f"Error rendering template: {e}", err=True)
        raise click.Exit(1) from e


@prompt.command()
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def list_templates(output: str) -> None:
    """List all available templates."""
    renderer = UnhingedPromptRenderer()
    templates = renderer.list_templates()

    if output == "json":
        click.echo(json.dumps({"templates": templates}))
    else:
        click.echo("Available templates:")
        for template in templates:
            click.echo(f"  {template}")


@prompt.command()
@click.option("--to", "to_recipient", required=True, help="TO field")
@click.option("--from", "from_sender", required=True, help="FROM field")
@click.option("--subject", required=True, help="Subject/RE field")
@click.option("--summary", required=True, help="Executive summary")
@click.option(
    "--context",
    "-c",
    type=click.Path(exists=True),
    help="YAML file with additional context",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def memo(
    to_recipient: str,
    from_sender: str,
    subject: str,
    summary: str,
    context: str | None,
    output: str,
) -> None:
    """Generate a memorandum from template.

    Example:
        unhinged prompt memo --to "Chief" --from "Division" \\
            --subject "Test" --summary "Summary text"
    """
    renderer = UnhingedPromptRenderer()

    # Load additional context from YAML if provided
    extra_context: dict[str, Any] = {}
    if context:
        with open(context) as f:
            extra_context = yaml.safe_load(f) or {}

    try:
        result = renderer.render_memo(
            to_recipient=to_recipient,
            from_sender=from_sender,
            subject=subject,
            executive_summary=summary,
            sections=extra_context.get("sections"),
            findings=extra_context.get("findings"),
            recommendations=extra_context.get("recommendations"),
            disposition=extra_context.get("disposition"),
            distribution=extra_context.get("distribution"),
            classification=extra_context.get("classification"),
            tracking=extra_context.get("tracking"),
            footer_text=extra_context.get("footer_text"),
        )

        if output == "json":
            click.echo(json.dumps({"memo": result}))
        else:
            click.echo(result)
    except Exception as e:
        click.echo(f"Error generating memorandum: {e}", err=True)
        raise click.Exit(1) from e
