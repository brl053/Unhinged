#!/usr/bin/env python3
"""
Text Generation Service

LLM-based text generation using local or remote models.
Direct Python implementation - no gRPC overhead.
"""

import logging
from typing import Any

import requests  # type: ignore

from libs.services.errors import ServiceNotRunningError

logger = logging.getLogger(__name__)


class TextGenerationService:
    """Text generation using LLM models (Ollama, OpenAI, Anthropic, etc.)"""

    def __init__(self, model: str = "llama2", provider: str = "ollama"):
        """
        Initialize text generation service.

        Args:
            model: Model name (e.g., "llama2", "mistral", "gpt-4")
            provider: Provider (ollama, openai, anthropic)
        """
        self.model = model
        self.provider = provider
        self.client = None
        self.model_loaded = False

        logger.info(f"TextGenerationService initialized (model: {model}, provider: {provider})")

    def _check_ollama_health(self) -> bool:
        """Check if Ollama service is available at localhost:11434."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout, Exception):
            return False

    def _load_ollama_client(self) -> None:
        """Load Ollama client with health check."""
        if not self._check_ollama_health():
            logger.error("Ollama service is not running")
            raise ServiceNotRunningError(
                service_name="Ollama",
                port=11434,
                install_url="https://ollama.com/download",
            )

        import ollama

        self.client = ollama
        logger.info(f"Ollama client initialized for model: {self.model}")

    def _load_openai_client(self) -> None:
        """Load OpenAI client."""
        from openai import OpenAI

        self.client = OpenAI()
        logger.info("OpenAI client initialized")

    def _load_anthropic_client(self) -> None:
        """Load Anthropic client."""
        from anthropic import Anthropic

        self.client = Anthropic()
        logger.info("Anthropic client initialized")

    def _load_client(self) -> None:
        """Load LLM client (lazy loading)"""
        if self.model_loaded:
            return

        try:
            if self.provider == "ollama":
                self._load_ollama_client()
            elif self.provider == "openai":
                self._load_openai_client()
            elif self.provider == "anthropic":
                self._load_anthropic_client()
            else:
                raise ValueError(f"Unknown provider: {self.provider}")

            self.model_loaded = True

        except ImportError as e:
            logger.error(f"Failed to import {self.provider} client: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider} client: {e}")
            raise

    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Top-p sampling parameter

        Returns:
            Generated text

        Raises:
            RuntimeError: If generation fails
        """
        self._load_client()

        if self.client is None:
            raise RuntimeError("LLM client failed to load")

        try:
            logger.info(f"Generating text with {self.provider}/{self.model}")

            if self.provider == "ollama":
                response = self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    stream=False,
                )
                text = response.get("response", "").strip()

            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                )
                text = response.choices[0].message.content.strip()

            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                )
                text = response.content[0].text.strip()

            logger.info(f"Generation complete: {len(text)} characters")
            return text

        except ConnectionError as e:
            error_msg = (
                f"Connection error with {self.provider}: {e}\n" "Please ensure the service is running and accessible."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise RuntimeError(f"Failed to generate text: {e}") from e

    def generate_with_metadata(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """
        Generate text and return detailed metadata.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Dict with text, model, tokens_generated, etc.
        """
        text = self.generate(prompt, max_tokens, temperature)

        return {
            "text": text,
            "model": self.model,
            "provider": self.provider,
            "prompt_length": len(prompt),
            "text_length": len(text),
        }
