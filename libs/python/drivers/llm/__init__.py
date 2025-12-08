"""LLM text generation drivers.

@llm-type library.drivers.llm
@llm-does expose TextGenerationService as a graph driver for APINode
"""

from __future__ import annotations

from .text_generation import LLMTextGenerationDriver

__all__ = ["LLMTextGenerationDriver"]
