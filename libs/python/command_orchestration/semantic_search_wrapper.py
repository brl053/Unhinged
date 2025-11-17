"""Semantic Search Engine wrapper with LLM-backed reasoning.

@llm-type library.command_orchestration.semantic_search_wrapper
@llm-does wrap SemanticSearchEngine to add LLM-backed reasoning for command selection
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, cast

from libs.python.command_orchestration.reasoning_engine import ReasoningEngine
from libs.python.command_orchestration.semantic_search import (
    SearchResult,
    SemanticSearchEngine,
)

logger = logging.getLogger(__name__)


class SemanticSearchWithReasoning:
    """Wraps SemanticSearchEngine to add LLM-backed reasoning.

    Enhances search results with LLM-generated explanations for why each
    command was selected, replacing static reasoning strings.
    """

    def __init__(
        self,
        search_engine: SemanticSearchEngine,
        reasoning_engine: ReasoningEngine | None = None,
        model: str = "claude-3-5-sonnet-20241022",
        provider: str = "anthropic",
    ):
        """Initialize wrapper with search and reasoning engines.

        Parameters
        ----------
        search_engine : SemanticSearchEngine
            The underlying semantic search engine
        reasoning_engine : Optional[ReasoningEngine]
            Optional pre-configured reasoning engine. If None, creates new one.
        model : str
            LLM model to use (default: Claude 3.5 Sonnet)
        provider : str
            LLM provider (anthropic, openai, ollama)
        """
        self.search_engine = search_engine
        self.reasoning_engine = reasoning_engine or ReasoningEngine(
            model=model, provider=provider
        )

    async def search_with_reasoning(
        self,
        prompt: str,
        limit: int = 10,
        use_llm_reasoning: bool = True,
    ) -> list[SearchResult]:
        """Search for commands and optionally enhance with LLM reasoning.

        Parameters
        ----------
        prompt : str
            Natural language search query
        limit : int
            Maximum number of results to return
        use_llm_reasoning : bool
            If True, use LLM for reasoning. If False, use static reasoning.

        Returns
        -------
        List[SearchResult]
            Search results with reasoning
        """
        try:
            # Get base search results
            results = self.search_engine.search(prompt, limit=limit)

            if not use_llm_reasoning or not results:
                return cast(list[SearchResult], results)

            # Extract commands for LLM reasoning
            commands = [r.command for r in results]
            similarity_scores = [r.similarity for r in results]

            # Generate LLM-backed reasoning
            try:
                command_reasoning = await self.reasoning_engine.reason_command_selection(
                    query=prompt,
                    commands=commands,
                    similarity_scores=similarity_scores,
                )

                # Update results with LLM reasoning
                for result in results:
                    if result.command in command_reasoning:
                        result.reasoning = command_reasoning[result.command]

            except Exception as exc:
                logger.warning(
                    f"LLM reasoning failed, using static reasoning: {exc}"
                )
                # Fall back to static reasoning (already in results)

            return cast(list[SearchResult], results)

        except Exception as exc:
            logger.error(f"Search with reasoning failed: {exc}")
            raise

    def search(self, prompt: str, limit: int = 10) -> list[SearchResult]:
        """Synchronous search (delegates to underlying engine).

        Parameters
        ----------
        prompt : str
            Natural language search query
        limit : int
            Maximum number of results

        Returns
        -------
        List[SearchResult]
            Search results with static reasoning
        """
        results = self.search_engine.search(prompt, limit=limit)
        return cast(list[SearchResult], results)

    async def search_async(
        self,
        prompt: str,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Asynchronous search with LLM reasoning.

        Parameters
        ----------
        prompt : str
            Natural language search query
        limit : int
            Maximum number of results

        Returns
        -------
        List[SearchResult]
            Search results with LLM-backed reasoning
        """
        return await self.search_with_reasoning(
            prompt=prompt,
            limit=limit,
            use_llm_reasoning=True,
        )

