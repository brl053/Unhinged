"""Intent analysis graph for `unhinged query`.

@llm-type library.query_planner.intent_graph
@llm-does provide LLM-backed IntentAnalysisGraph for general-purpose query classification
"""

from __future__ import annotations

import json
import logging
from typing import Any, cast

from libs.python.graph import Graph, GraphNode
from libs.python.query_planner.prompt_hydration import HydrationContext

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
        hydration: HydrationContext | None = None,
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
        hydration : HydrationContext | None
            Optional hydration context for grounded action routing.
        """
        super().__init__(node_id)
        self.model = model
        self.provider = provider
        self.hydration = hydration
        self._client: Any = None

    def _get_system_prompt(self) -> str:
        """Build system prompt with intent taxonomy, hydration, and action routing."""
        taxonomy_yaml = json.dumps(INTENT_TAXONOMY, indent=2)

        # Build hydration section if available
        hydration_section = ""
        if self.hydration:
            hydration_section = f"""
## Available Actions (Grounded Context)

{self.hydration.to_prompt_section()}

When the user's query matches an available action, prefer routing to it.
Use action_type to indicate what to execute:
- "linux": A Linux command from the list above
- "cli": An Unhinged CLI command
- "graph": An available graph workflow
- "clarify": Need more information from user
"""

        return f"""You are an expert intent classifier and action router for voice-driven system automation.

Your task: Analyze the user's natural language query and:
1. Classify the intent (diagnose, generate, analyze, execute)
2. Route to the best available action when possible
3. Provide actionable command/graph recommendations

## Intent Taxonomy

{taxonomy_yaml}
{hydration_section}

## Term Semantics

When analyzing queries, consider:
- **Etymology**: Word origins and historical meaning
- **Connotation**: Emotional/cultural associations (e.g., "low" = insufficient)
- **Denotation**: Literal/technical meaning (e.g., "volume" = amplitude)

Examples:
- "check my disk space" → intent=execute, action_type=linux, command="df -h"
- "run the email graph" → intent=execute, action_type=graph, graph_name="email-summary"
- "what's using my CPU" → intent=diagnose, action_type=linux, command="top -bn1 | head -20"

## Output Format

Return ONLY valid JSON (no markdown, no explanation):
{{
  "intent": "<diagnose|generate|analyze|execute|clarify|unknown>",
  "domain": "<specific subdomain or 'general'>",
  "action_type": "<linux|cli|graph|clarify|none>",
  "command": "<linux command or cli command or null>",
  "graph_name": "<graph name if action_type=graph, else null>",
  "confidence": <0.0-1.0>,
  "reasoning": "<brief explanation>"
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

            # Validate minimum required field (intent)
            if "intent" not in result:
                raise ValueError(f"LLM response missing 'intent' field: {result}")

            return {
                "success": True,
                "intent": result["intent"],
                "domain": result.get("domain", "general"),
                "confidence": float(result.get("confidence", 0.8)),
                "reasoning": result.get("reasoning", ""),
                # Action routing fields (from hydrated prompt)
                "action_type": result.get("action_type", ""),
                "command": result.get("command"),
                "graph_name": result.get("graph_name"),
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
    hydration: HydrationContext | None = None,
) -> Graph:
    """Construct the LLM-backed IntentAnalysisGraph.

    Parameters
    ----------
    model : str
        LLM model to use (default: Claude 3.5 Sonnet).
    provider : str
        LLM provider (anthropic, openai, ollama).
    hydration : HydrationContext | None
        Optional hydration context for grounded action routing.
        When provided, the LLM knows about available CLI commands,
        graphs, and Linux commands.

    Returns
    -------
    Graph
        A graph with a single LLMIntentNode that classifies queries.
    """
    graph = Graph()
    graph.add_node(
        LLMIntentNode(
            node_id=INTENT_NODE_ID,
            model=model,
            provider=provider,
            hydration=hydration,
        )
    )
    return graph
