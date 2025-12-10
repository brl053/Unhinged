"""Chat commands: multi-turn conversations."""

import sys
from pathlib import Path

import click

from cli.utils import log_error, log_info, log_success

# Import services
try:
    from libs.python.clients import ChatService, TextGenerationService
except ImportError:
    from libs.python.clients.chat_service import ChatService
    from libs.python.clients.text_generation_service import TextGenerationService


@click.group()
def chat():
    """Chat with AI: multi-turn conversations.

    Usage:
      unhinged chat "What is quantum computing?"
      unhinged chat -f conversation.txt
      echo "Tell me a joke" | unhinged chat
    """
    pass


@chat.command()
@click.argument("prompt", nargs=-1, required=False)
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
def ask(prompt, model, provider, tokens, temperature, file):
    """Chat with AI: send a message and get a response.

    PROMPT can be provided as:
      - Command arguments (joined with spaces): unhinged chat what is AI
      - Quoted argument: unhinged chat "what is AI?"
      - File: unhinged chat -f question.txt
      - Stdin: echo "what is AI?" | unhinged chat

    Examples:
      unhinged chat "explain quantum computing"
      unhinged chat -m mistral "write a poem about the moon"
      unhinged chat -p openai -m gpt-4 "summarize this text"
      cat question.txt | unhinged chat
    """
    try:
        # Determine prompt source
        if file:
            prompt_text = Path(file).read_text().strip()
            log_info(f"Reading prompt from: {file}")
        elif prompt:
            prompt_text = " ".join(prompt)
        else:
            if not sys.stdin.isatty():
                prompt_text = sys.stdin.read().strip()
                log_info("Reading prompt from stdin")
            else:
                log_error("No prompt provided. Use: unhinged chat --help")
                sys.exit(1)

        if not prompt_text:
            log_error("Prompt cannot be empty")
            sys.exit(1)

        log_info(f"Chatting with {provider}/{model}...")

        # Initialize services
        chat_service = ChatService()
        text_service = TextGenerationService(model=model, provider=provider)

        # Create conversation
        conversation = chat_service.create_conversation(metadata={"model": model, "provider": provider})

        # Add user message
        chat_service.send_message(conversation.conversation_id, "user", prompt_text)

        # Generate response
        response = text_service.generate(
            prompt=prompt_text,
            max_tokens=tokens,
            temperature=temperature,
        )

        # Add assistant message
        chat_service.send_message(conversation.conversation_id, "assistant", response)

        # Output result
        click.echo(response)
        log_success(f"Generated {len(response)} characters")
        log_info(f"Conversation ID: {conversation.conversation_id}")

    except Exception as e:
        log_error(f"Chat failed: {e}")
        sys.exit(1)
