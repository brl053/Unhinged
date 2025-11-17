"""Intent analysis graph for `unhinged query`.

@llm-type library.query_planner.intent_graph
@llm-does provide LLM-backed IntentAnalysisGraph for general-purpose query classification
"""

from __future__ import annotations

import json
import logging
from typing import Any, cast

from libs.python.graph import Graph, GraphNode

logger = logging.getLogger(__name__)

INTENT_NODE_ID = "llm_intent"

# Intent taxonomy: maps user intents to domain classifiers
# Extensible for DevEx, storage, networking, etc.
INTENT_TAXONOMY = {
    "diagnose": {
        "domains": [
            "audio/headphone_volume",
            "audio/system_volume",
            "storage/disk_usage",
            "network/connectivity",
            "gpu/utilization",
            "system/performance",
        ],
        "description": "System diagnostics and troubleshooting",
    },
    "generate": {
        "domains": [
            "content/text",
            "content/image",
            "content/video",
            "code/snippet",
        ],
        "description": "Content and code generation",
    },
    "analyze": {
        "domains": [
            "code/static_analysis",
            "code/dependency_graph",
            "data/metrics",
        ],
        "description": "Code and data analysis",
    },
}


class LLMIntentNode(GraphNode):
    """Graph node that performs LLM-backed intent classification.

    Uses a large reasoning model to classify natural language queries into
    structured intent/domain/confidence with reasoning. The system prompt
    includes intent taxonomy, term etymology/connotation/denotation, and
    structured output schema.

    This is the front-door classifier for all `unhinged query` workflows.
    """

    def __init__(
        self,
        node_id: str,
        model: str = "claude-3-5-sonnet-20241022",
        provider: str = "anthropic",
    ):
        """Initialize LLM intent node.

        Parameters
        ----------
        node_id : str
            Unique identifier for this node.
        model : str
            LLM model to use (default: Claude 3.5 Sonnet for reasoning).
        provider : str
            LLM provider (anthropic, openai, ollama).
        """
        super().__init__(node_id)
        self.model = model
        self.provider = provider
        self._client: Any = None

    def _get_system_prompt(self) -> str:
        """Build system prompt with intent taxonomy and term semantics."""
        taxonomy_yaml = json.dumps(INTENT_TAXONOMY, indent=2)
        return f"""You are an expert intent classifier for system diagnostics and automation.

Your task: Analyze the user's natural language query and classify it into:
1. **intent**: The high-level action (diagnose, generate, analyze, etc.)
2. **domain**: The specific subdomain (audio/headphone_volume, storage/disk_usage, etc.)
3. **confidence**: 0.0-1.0 confidence in your classification
4. **reasoning**: Brief explanation of your classification

## Intent Taxonomy

{taxonomy_yaml}

## Term Semantics

When analyzing queries, consider:
- **Etymology**: Word origins and historical meaning
- **Connotation**: Emotional/cultural associations (e.g., "low" = insufficient, inadequate)
- **Denotation**: Literal/technical meaning (e.g., "volume" = amplitude, storage capacity)

Examples:
- "audio is too low" → intent=diagnose, domain=audio/system_volume (connotation: insufficient)
- "my headphones are quiet" → intent=diagnose, domain=audio/headphone_volume (denotation: amplitude)
- "disk is full" → intent=diagnose, domain=storage/disk_usage (connotation: capacity exceeded)

## Output Format

Return ONLY valid JSON (no markdown, no explanation):
{{
  "intent": "<intent>",
  "domain": "<domain>",
  "confidence": <0.0-1.0>,
  "reasoning": "<brief explanation>"
}}

If the query does not match any known intent/domain, return:
{{
  "intent": "unknown",
  "domain": "unknown",
  "confidence": 0.0,
  "reasoning": "<why it doesn't match>"
}}
"""

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Classify intent using LLM reasoning.

        Parameters
        ----------
        input_data : Optional[Dict[str, Any]]
            Must contain "stdin" key with the user's natural language query.

        Returns
        -------
        Dict[str, Any]
            Structured output with intent, domain, confidence, reasoning, and stdout.
        """
        if not input_data or "stdin" not in input_data:
            return {
                "success": False,
                "error": "LLMIntentNode requires 'stdin' with query string",
                "intent": "unknown",
                "domain": "unknown",
                "confidence": 0.0,
                "reason": "missing stdin",
            }

        query = str(input_data["stdin"]).strip()

        try:
            # Lazy-load LLM client
            if self._client is None:
                self._client = self._load_client()

            # Call LLM with system prompt
            response_text = await self._call_llm(query)

            # Parse JSON response
            result = json.loads(response_text)

            # Validate required fields
            if not all(k in result for k in ["intent", "domain", "confidence", "reasoning"]):
                raise ValueError(f"LLM response missing required fields: {result}")

            return {
                "success": True,
                "intent": result["intent"],
                "domain": result["domain"],
                "confidence": float(result["confidence"]),
                "reasoning": result["reasoning"],
                "stdout": json.dumps(result),
            }

        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse LLM response as JSON: {exc}")
            return {
                "success": False,
                "error": f"LLM response was not valid JSON: {exc}",
                "intent": "unknown",
                "domain": "unknown",
                "confidence": 0.0,
                "reason": "json_parse_error",
            }
        except Exception as exc:
            logger.error(f"LLM intent classification failed: {exc}")
            return {
                "success": False,
                "error": str(exc),
                "intent": "unknown",
                "domain": "unknown",
                "confidence": 0.0,
                "reason": "llm_error",
            }

    def _load_client(self) -> Any:
        """Lazy-load LLM client based on provider."""
        if self.provider == "anthropic":
            from anthropic import Anthropic

            return Anthropic()
        elif self.provider == "openai":
            from openai import OpenAI

            return OpenAI()
        elif self.provider == "ollama":
            from ollama import Client

            return Client(host="http://localhost:1500")
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    async def _call_llm(self, query: str) -> str:
        """Call LLM with system prompt and return response text.

        Note: Currently synchronous; can be made async with asyncio.to_thread
        if needed for performance.
        """
        system_prompt = self._get_system_prompt()

        if self._client is None:
            raise RuntimeError("LLM client not initialized")

        if self.provider == "anthropic":
            response = self._client.messages.create(
                model=self.model,
                max_tokens=512,
                system=system_prompt,
                messages=[{"role": "user", "content": query}],
            )
            return cast(str, response.content[0].text)

        elif self.provider == "openai":
            response = self._client.chat.completions.create(
                model=self.model,
                max_tokens=512,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
            )
            return cast(str, response.choices[0].message.content)

        elif self.provider == "ollama":
            response = self._client.generate(
                model=self.model,
                prompt=f"{system_prompt}\n\nUser query: {query}",
                stream=False,
            )
            return cast(str, response.get("response", "").strip())

        else:
            raise ValueError(f"Unknown provider: {self.provider}")


def build_intent_analysis_graph(
    model: str = "claude-3-5-sonnet-20241022",
    provider: str = "anthropic",
) -> Graph:
    """Construct the LLM-backed IntentAnalysisGraph.

    Parameters
    ----------
    model : str
        LLM model to use (default: Claude 3.5 Sonnet).
    provider : str
        LLM provider (anthropic, openai, ollama).

    Returns
    -------
    Graph
        A graph with a single LLMIntentNode that classifies queries.
    """
    graph = Graph()
    graph.add_node(LLMIntentNode(node_id=INTENT_NODE_ID, model=model, provider=provider))
    return graph
