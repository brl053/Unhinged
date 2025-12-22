#!/usr/bin/env python3
"""
Text Generation Service

LLM-based text generation using local Ollama models.
Direct Python implementation - no gRPC overhead.

Local-only: All inference runs on-device via Ollama.
No external API calls.

Supported Models (Mistral family - Apache-2.0):
- mistral: Mistral 7B base model (default)
- mistral-nemo: Mistral Nemo 12B
- mixtral: Mixtral 8x7B (MoE)
- codestral: Code-focused variant
- devstral: Development/coding focused
"""

import logging
from typing import Any

import requests  # type: ignore

from .errors import ServiceNotRunningError

logger = logging.getLogger(__name__)

# Supported Mistral family models (Apache-2.0 licensed)
SUPPORTED_MODELS = frozenset(
    {
        "mistral",
        "mistral:latest",
        "mistral:7b",
        "mistral-nemo",
        "mistral-nemo:latest",
        "mixtral",
        "mixtral:latest",
        "mixtral:8x7b",
        "codestral",
        "codestral:latest",
        "devstral",
        "devstral:latest",
        "devstral-small",
    }
)


class TextGenerationService:
    """Text generation using Mistral family models via local Ollama.

    Only Apache-2.0 licensed Mistral models are supported:
    - mistral (7B) - General purpose, fast
    - mistral-nemo (12B) - More capable
    - mixtral (8x7B) - MoE, high quality
    - codestral - Code generation
    - devstral - Development tasks
    """

    def __init__(self, model: str = "mistral"):
        """
        Initialize text generation service.

        Args:
            model: Mistral family model name. Supported:
                   mistral, mistral-nemo, mixtral, codestral, devstral
        """
        # Normalize model name
        self.model = model.lower().strip()
        self.client: Any = None
        self.model_loaded = False

        # Warn if using unsupported model (but allow it for flexibility)
        base_model = self.model.split(":")[0]
        if base_model not in {m.split(":")[0] for m in SUPPORTED_MODELS}:
            logger.warning(
                f"Model '{model}' is not in supported Mistral family. "
                f"Supported: mistral, mistral-nemo, mixtral, codestral, devstral"
            )

        logger.info(f"TextGenerationService initialized (model: {self.model})")

    @staticmethod
    def list_available_models() -> list[str]:
        """List models available in local Ollama instance."""
        try:
            response = requests.get("http://localhost:1500/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

    @staticmethod
    def get_supported_models() -> frozenset[str]:
        """Return set of supported Mistral family model names."""
        return SUPPORTED_MODELS

    def _check_ollama_health(self) -> bool:
        """Check if Ollama service is available at localhost:1500 (external port)."""
        try:
            response = requests.get("http://localhost:1500/api/tags", timeout=2)
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

        from ollama import Client

        # Connect to Ollama on external port 1500 (mapped from internal 11434)
        self.client = Client(host="http://localhost:1500")
        logger.info(f"Ollama client initialized for model: {self.model}")

    def _load_client(self) -> None:
        """Load Ollama client (lazy loading)."""
        if self.model_loaded:
            return

        try:
            self._load_ollama_client()
            self.model_loaded = True
        except ImportError as e:
            logger.error(f"Failed to import ollama client: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
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
            logger.info(f"Generating text with ollama/{self.model}")

            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
            )
            text = str(response.get("response", "")).strip()

            logger.info(f"Generation complete: {len(text)} characters")
            return text

        except ConnectionError as e:
            error_msg = f"Connection error with Ollama: {e}\n" "Please ensure Ollama is running on port 1500."
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
            Dict with text, model, prompt_length, text_length.
        """
        text = self.generate(prompt, max_tokens, temperature)

        return {
            "text": text,
            "model": self.model,
            "prompt_length": len(prompt),
            "text_length": len(text),
        }
