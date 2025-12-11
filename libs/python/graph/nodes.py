"""Graph node primitives.

@llm-type library.graph.nodes
@llm-does define abstract GraphNode and UnixCommandNode for executing shell commands
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - import only for type checking
    from .context import SessionContext
    from .graph import Graph, GraphExecutionResult


class GraphNode(ABC):
    """Abstract base for all graph nodes in the Unhinged DAG framework."""

    def __init__(self, node_id: str) -> None:
        self.id = node_id

    @abstractmethod
    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute the node's work.

        Implementations should treat ``input_data`` as immutable input and
        return a new dict with serialisable values that can be routed to
        downstream nodes.
        """


class UnixCommandNode(GraphNode):
    """Graph node that executes a single UNIX shell command.

    The node runs the command using the system shell and returns a result
    dictionary with keys:

    - ``stdout``: decoded standard output (str)
    - ``stderr``: decoded standard error (str)
    - ``returncode``: integer exit code or ``None`` if timed out
    - ``success``: bool indicating whether the command exited with code 0
    """

    def __init__(self, node_id: str, command: str, timeout: float = 30.0) -> None:
        super().__init__(node_id)
        self.command = command
        self.timeout = timeout

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute the configured shell command.

        Parameters
        ----------
        input_data:
            Optional dictionary. If it contains a ``"stdin"`` key its value
            will be sent to the process as standard input. Supported value
            types are ``str`` and ``bytes``.
        """
        stdin_bytes: bytes | None = None
        if input_data is not None and "stdin" in input_data:
            value = input_data["stdin"]
            if isinstance(value, bytes):
                stdin_bytes = value
            elif isinstance(value, str):
                stdin_bytes = value.encode("utf-8")
            else:
                raise TypeError("stdin must be str or bytes")

        process = await asyncio.create_subprocess_shell(
            self.command,
            stdin=asyncio.subprocess.PIPE if stdin_bytes is not None else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(stdin_bytes),
                timeout=self.timeout,
            )
        except TimeoutError:
            process.kill()
            await process.communicate()
            return {
                "stdout": "",
                "stderr": f"Command timed out after {self.timeout} seconds",
                "returncode": None,
                "success": False,
            }

        stdout_text = stdout.decode("utf-8", errors="replace")
        stderr_text = stderr.decode("utf-8", errors="replace")

        return {
            "stdout": stdout_text.rstrip("\n"),
            "stderr": stderr_text.rstrip("\n"),
            "returncode": process.returncode,
            "success": process.returncode == 0,
        }


class UserInputNode(GraphNode):
    """Graph node that prompts user for input during execution.

    Supports confirmation prompts and alternative route selection.
    Returns user's choice as output for downstream branching.

    Output keys:
    - ``user_input``: The user's response (str)
    - ``confirmed``: Boolean indicating confirmation (for yes/no prompts)
    - ``selected_option``: Index of selected option (for multiple choice)
    """

    def __init__(
        self,
        node_id: str,
        prompt: str,
        options: list[str] | None = None,
        default: str | None = None,
    ) -> None:
        super().__init__(node_id)
        self.prompt = prompt
        self.options = options or []
        self.default = default

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Prompt user for input and return their response.

        If input_data contains 'selected_option' or 'user_input', use those instead of prompting.
        This allows tests and programmatic usage to provide input without stdin.
        """
        # If input is already provided (e.g., from tests or programmatic usage), use it
        if input_data and "selected_option" in input_data:
            return {
                "user_input": input_data.get("user_input", ""),
                "confirmed": input_data.get("confirmed", False),
                "selected_option": input_data["selected_option"],
                "success": True,
            }

        if input_data and "user_input" in input_data:
            return {
                "user_input": input_data["user_input"],
                "confirmed": input_data.get("confirmed", False),
                "success": True,
            }

        try:
            return self._collect_options() if self.options else self._collect_freeform()
        except (EOFError, KeyboardInterrupt):
            return {"user_input": None, "confirmed": False, "success": False, "error": "User cancelled input"}

    def _collect_options(self) -> dict[str, Any]:
        """Collect user selection from multiple choice options."""
        print(f"\n{self.prompt}")
        for i, option in enumerate(self.options, 1):
            print(f"  {i}. {option}")

        while True:
            choice = input("Select option (number): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.options):
                    return {"user_input": self.options[idx], "selected_option": idx, "success": True}
            except ValueError:
                pass
            print(f"Please enter a number between 1 and {len(self.options)}")

    def _collect_freeform(self) -> dict[str, Any]:
        """Collect free-form or yes/no user input."""
        response = input(f"\n{self.prompt} ").strip()
        if not response and self.default:
            response = self.default
        confirmed = response.lower() in ("yes", "y", "true", "1")
        return {"user_input": response, "confirmed": confirmed, "success": True}


class SubgraphNode(GraphNode):
    """Graph node that executes a nested ``Graph`` as a subgraph.

    The subgraph is executed via :class:`GraphExecutor` and its aggregated
    results are returned as a structured payload. An optional stdout_adapter
    can derive a single string from the subgraph result that will be exposed
    as ``stdout`` for downstream piping.
    """

    def __init__(
        self,
        node_id: str,
        subgraph: Graph,
        stdout_adapter: Callable[[GraphExecutionResult], str] | None = None,
    ) -> None:
        super().__init__(node_id)
        self.subgraph = subgraph
        self._stdout_adapter = stdout_adapter

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        from .graph import GraphExecutor  # Local import to avoid circular import

        executor = GraphExecutor()
        result = await executor.execute(self.subgraph, initial_inputs=input_data or {})

        output: dict[str, Any] = {
            "success": result.success,
            "subgraph": {
                "execution_order": result.execution_order,
                "node_results": {node_id: node_result.output for node_id, node_result in result.node_results.items()},
                "error_message": result.error_message,
            },
        }

        if self._stdout_adapter is not None:
            try:
                stdout_value = self._stdout_adapter(result)
            except Exception as exc:  # pragma: no cover - defensive
                # Adapter failures should not crash the graph; mark node as failed.
                output["success"] = False
                output["subgraph"]["adapter_error"] = str(exc)
            else:
                output["stdout"] = stdout_value

        return output


class RecallNode(GraphNode):
    """Graph node that performs semantic recall over persisted sessions.

    Queries the vector store for documents matching the input query.
    Used for self-reflection, context retrieval, and memory recall.

    Output keys:
    - ``results``: List of recall results with text, score, document_id
    - ``top_text``: Text of the highest-scoring result (for easy chaining)
    - ``success``: Boolean indicating whether recall succeeded
    """

    def __init__(
        self,
        node_id: str,
        collection: str | None = None,
        limit: int = 5,
        threshold: float = 0.5,
    ) -> None:
        super().__init__(node_id)
        self.collection = collection
        self.limit = limit
        self.threshold = threshold

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute semantic recall with query from input_data.

        Expects input_data to contain:
        - ``query``: The natural language query string
        """
        from libs.python.persistence.vector_bridge import VectorBridge

        input_data = input_data or {}
        query = input_data.get("query", "")

        if not query:
            return {
                "success": False,
                "error": "No query provided",
                "results": [],
                "top_text": "",
            }

        try:
            bridge = VectorBridge()
            results = bridge.recall(
                query=query,
                collection=self.collection,
                limit=self.limit,
                threshold=self.threshold,
            )
            return self._format_recall_results(results)
        except Exception as e:
            return {"success": False, "error": str(e), "results": [], "top_text": ""}

    def _format_recall_results(self, results) -> dict[str, Any]:
        """Format recall results into output dict."""
        formatted = [
            {"document_id": r.document_id, "collection": r.collection, "text": r.text, "score": r.score}
            for r in results
        ]
        return {"success": True, "results": formatted, "top_text": results[0].text if results else ""}


class APINode(GraphNode):
    """Generic graph node that executes operations via the driver registry.

    This node provides a unified interface for external API integrations.
    It delegates to registered drivers (e.g., google.gmail, social.discord)
    and exposes their results for downstream processing.

    The node is configured with:
    - driver_namespace: Dot-separated driver identifier (e.g., "google.gmail")
    - operation: Driver-specific operation name (e.g., "list_unread", "post_message")
    - params: Operation-specific parameters (optional, can be overridden by input_data)
    """

    def __init__(
        self,
        node_id: str,
        driver_namespace: str,
        operation: str,
        params: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(node_id)
        self.driver_namespace = driver_namespace
        self.operation = operation
        self.params = params or {}

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute driver operation with merged parameters.

        input_data can override or extend the node's configured params.
        The driver is retrieved from the global registry at execution time.
        """
        # Local import to avoid circular dependency and keep registry optional
        from libs.python.drivers.base import DriverError, get_global_registry

        input_data = input_data or {}

        # Merge params: input_data overrides node params
        merged_params = {**self.params, **input_data.get("params", {})}

        try:
            registry = get_global_registry()
            driver = registry.get(self.driver_namespace)
            result = await driver.execute(self.operation, merged_params)

            # Driver execute() returns {success, data?, error?}
            # We pass through the driver result structure
            return result

        except KeyError:  # Driver not found in registry
            return {
                "success": False,
                "error": f"Driver not registered: {self.driver_namespace}",
            }
        except DriverError as exc:  # Driver-specific error
            return {
                "success": False,
                "error": str(exc),
            }
        except Exception as exc:  # pragma: no cover - defensive
            return {
                "success": False,
                "error": f"Unexpected error: {exc}",
            }


class LLMNode(GraphNode):
    """Graph node that calls an LLM with template interpolation.

    Supports template variables that are interpolated before sending to the LLM:
    - {{node_id.field}} - Upstream node outputs
    - {{session.key}} - Session context data
    - {{env.VAR}} - Environment variables

    Configuration:
    - model: LLM model name (e.g., "gpt-4o-mini", "llama2")
    - provider: LLM provider (e.g., "openai", "ollama")
    - system_prompt: System prompt for the LLM
    - input_template: User prompt template with {{...}} placeholders
    - max_tokens: Maximum tokens in response (default: 1024)
    - temperature: Sampling temperature (default: 0.7)

    Output keys:
    - ``stdout``: Raw LLM response text (for downstream piping)
    - ``text``: Same as stdout (alias)
    - ``model``: Model used
    - ``provider``: Provider used
    - ``success``: Boolean indicating success
    """

    def __init__(
        self,
        node_id: str,
        model: str = "llama2",
        provider: str = "ollama",
        system_prompt: str = "",
        input_template: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> None:
        super().__init__(node_id)
        self.model = model
        self.provider = provider
        self.system_prompt = system_prompt
        self.input_template = input_template
        self.max_tokens = max_tokens
        self.temperature = temperature
        # Session context for {{session.*}} interpolation (set by executor)
        self._session: SessionContext | None = None

    def set_session(self, session: SessionContext | None) -> None:
        """Set session context for template interpolation."""
        self._session = session

    def hydrate(self, input_data: dict[str, Any] | None = None) -> dict[str, str]:
        """Return the hydrated (interpolated) prompts without executing.

        Useful for dry-run / preview mode to inspect what will be sent to the LLM.

        Returns:
            Dict with 'system_prompt', 'user_prompt', and 'full_prompt' keys.
        """
        from libs.python.graph.template import interpolate

        input_data = input_data or {}

        user_prompt = interpolate(
            template=self.input_template,
            nodes=input_data,
            session=self._session,
        )

        full_prompt = user_prompt
        if self.system_prompt:
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"

        return {
            "system_prompt": self.system_prompt,
            "user_prompt": user_prompt,
            "full_prompt": full_prompt,
        }

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute LLM call with interpolated template."""
        from libs.python.graph.template import interpolate

        input_data = input_data or {}

        # Interpolate template with nodes, session, and env
        prompt = interpolate(
            template=self.input_template,
            nodes=input_data,
            session=self._session,
        )

        # Build full prompt with system prompt
        full_prompt = prompt
        if self.system_prompt:
            full_prompt = f"{self.system_prompt}\n\n{prompt}"

        try:
            # Lazy import to avoid requiring LLM deps at import time
            from libs.python.clients.text_generation_service import TextGenerationService

            service = TextGenerationService(model=self.model, provider=self.provider)
            text = service.generate(
                prompt=full_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            return {
                "stdout": text,
                "text": text,
                "model": self.model,
                "provider": self.provider,
                "success": True,
            }
        except Exception as exc:
            return {
                "stdout": "",
                "text": "",
                "error": str(exc),
                "success": False,
            }


class StructuredOutputNode(LLMNode):
    """LLM node that validates output against a JSON schema.

    Extends LLMNode with JSON parsing and schema validation. If the LLM
    output is not valid JSON or doesn't match the schema, the node can
    retry up to max_retries times with feedback.

    Additional configuration:
    - json_schema: JSON schema dict for validation (optional)
    - max_retries: Number of retries on parse/validation failure (default: 2)

    Additional output keys:
    - ``parsed``: Parsed JSON object (if successful)
    - ``validation_errors``: List of validation errors (if any)
    """

    def __init__(
        self,
        node_id: str,
        model: str = "llama2",
        provider: str = "ollama",
        system_prompt: str = "",
        input_template: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        json_schema: dict[str, Any] | None = None,
        max_retries: int = 2,
    ) -> None:
        super().__init__(
            node_id=node_id,
            model=model,
            provider=provider,
            system_prompt=system_prompt,
            input_template=input_template,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        self.json_schema = json_schema
        self.max_retries = max_retries

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute LLM call and validate JSON output."""

        last_error = ""
        for attempt in range(self.max_retries + 1):
            # Add retry feedback to prompt if this is a retry
            retry_input = input_data
            if attempt > 0 and last_error:
                retry_input = dict(input_data or {})
                retry_input["_retry_feedback"] = (
                    f"Previous attempt failed: {last_error}. " "Please output valid JSON matching the required schema."
                )

            result = await super().execute(retry_input)

            if not result.get("success"):
                return result

            text = result.get("text", "")

            # Try to extract JSON from response
            parsed, parse_error = self._extract_json(text)
            if parse_error:
                last_error = parse_error
                continue

            # Validate against schema if provided
            if self.json_schema and parsed is not None:
                validation_errors = self._validate_schema(parsed)
                if validation_errors:
                    last_error = f"Schema validation failed: {validation_errors}"
                    result["validation_errors"] = validation_errors
                    continue

            # Success - add parsed output
            result["parsed"] = parsed
            result["validation_errors"] = []
            return result

        # All retries exhausted
        result = await super().execute(input_data)
        result["parsed"] = None
        result["validation_errors"] = [last_error]
        result["success"] = False
        result["error"] = f"Failed to get valid JSON after {self.max_retries + 1} attempts: {last_error}"
        return result

    def _extract_json(self, text: str) -> tuple[dict[str, Any] | None, str]:
        """Extract JSON from LLM response text.

        Handles common cases like markdown code blocks.
        Returns (parsed_dict, error_message).
        """
        import json
        import re

        # Try to find JSON in markdown code block
        code_block = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if code_block:
            text = code_block.group(1)

        # Try to find JSON object in text
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            text = json_match.group(0)

        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed, ""
            return None, f"Expected JSON object, got {type(parsed).__name__}"
        except json.JSONDecodeError as exc:
            return None, f"JSON parse error: {exc}"

    def _validate_schema(self, data: dict[str, Any]) -> list[str]:
        """Validate data against JSON schema. Returns list of errors."""
        if not self.json_schema:
            return []

        errors: list[str] = []

        # Simple schema validation (required fields, types)
        required = self.json_schema.get("required", [])
        properties = self.json_schema.get("properties", {})

        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        for field, spec in properties.items():
            if field in data:
                expected_type = spec.get("type")
                if expected_type and not self._check_type(data[field], expected_type):
                    errors.append(f"Field '{field}' should be {expected_type}")

        return errors

    def _check_type(self, value: Any, expected: str) -> bool:
        """Check if value matches expected JSON schema type."""
        type_map: dict[str, type | tuple[type, ...]] = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        expected_types = type_map.get(expected)
        if expected_types is None:
            return True  # Unknown type, assume valid
        return isinstance(value, expected_types)


class RubricGradeNode(GraphNode):
    """Graph node that grades input against a rubric.

    Used as a quality gate in graph execution. Can be followed by
    conditional edges to loop back on failure.

    Input keys (from upstream node):
    - ``citations``: List of citations (URLs, man pages, error codes)
    - ``diagnosis``: Proof-of-work diagnosis text
    - ``action``: Specific action plan

    Output keys:
    - ``score``: Float 0.0-1.0 weighted score
    - ``threshold``: Required score to pass
    - ``passed``: Boolean indicating pass/fail
    - ``feedback``: Human-readable feedback
    - ``missing_fields``: List of fields that failed criteria
    - ``success``: Always True (grading itself doesn't fail)
    """

    def __init__(
        self,
        node_id: str,
        rubric_name: str = "invoice_v1",
        threshold: float | None = None,
    ) -> None:
        super().__init__(node_id)
        self.rubric_name = rubric_name
        self._threshold_override = threshold

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Grade input_data against the rubric."""
        input_data = input_data or {}
        rubric = self._load_rubric()

        if rubric is None:
            # No rubric - auto-pass with warning
            return {
                "score": 1.0,
                "threshold": 0.0,
                "passed": True,
                "feedback": f"rubric '{self.rubric_name}' not found - auto-pass",
                "missing_fields": [],
                "success": True,
            }

        criteria = rubric.get("criteria", [])
        threshold = self._threshold_override or rubric.get("pass_threshold", 0.6)

        total_weight = sum(c.get("weight", 1.0) for c in criteria)
        weighted_score = 0.0
        missing_fields: list[str] = []
        feedback_parts: list[str] = []

        for criterion in criteria:
            field = criterion.get("field", "")
            weight = criterion.get("weight", 1.0)
            field_value = input_data.get(field)

            score = self._grade_criterion(criterion, field_value)
            weighted_score += score * weight

            if score < 1.0:
                if field_value is None:
                    missing_fields.append(field)
                    feedback_parts.append(f"missing: {field}")
                else:
                    feedback_parts.append(f"insufficient: {field} ({score:.0%})")

        final_score = weighted_score / total_weight if total_weight > 0 else 0.0
        passed = final_score >= threshold

        return {
            "score": round(final_score, 3),
            "threshold": threshold,
            "passed": passed,
            "feedback": "; ".join(feedback_parts) if feedback_parts else "all criteria met",
            "missing_fields": missing_fields,
            "success": True,
        }

    def _load_rubric(self) -> dict[str, Any] | None:
        """Load rubric from document store."""
        try:
            from libs.python.persistence import get_document_store

            store = get_document_store()
            results = store.query("rubrics", {"name": self.rubric_name})
            return results[0].data if results else None
        except Exception:
            return None

    def _grade_criterion(self, criterion: dict[str, Any], value: Any) -> float:
        """Grade a single criterion. Returns 0.0-1.0."""
        if value is None or (criterion.get("required") and not value):
            return 0.0

        min_count = criterion.get("min_count")
        if min_count is not None:
            return self._grade_min_count(value, min_count)

        min_length = criterion.get("min_length")
        if min_length is not None:
            return self._grade_min_length(value, min_length)

        return 1.0  # present and no specific check

    def _grade_min_count(self, value: Any, min_count: int) -> float:
        """Grade min_count criterion for list values."""
        if not isinstance(value, list):
            return 0.0
        return min(1.0, len(value) / float(min_count))

    def _grade_min_length(self, value: Any, min_length: int) -> float:
        """Grade min_length criterion for string values."""
        if not isinstance(value, str):
            return 0.0
        return min(1.0, len(value) / float(min_length))


class WebSearchNode(GraphNode):
    """Graph node that searches the web and returns results.

    Uses DuckDuckGo for search and fetches page content for LLM consumption.

    Configuration:
    - query_template: Template string with {{placeholders}} for search query
    - max_results: Number of results to fetch (default: 5)
    - max_content_chars: Max chars to extract per page (default: 3000)

    Output keys:
    - ``results``: List of search result dicts with title, url, snippet, body
    - ``text``: Formatted text version of results for LLM consumption
    - ``query``: The interpolated search query
    - ``success``: Boolean indicating success
    """

    def __init__(
        self,
        node_id: str,
        query_template: str = "{{input.query}}",
        max_results: int = 5,
        max_content_chars: int = 3000,
    ) -> None:
        super().__init__(node_id)
        self.query_template = query_template
        self.max_results = max_results
        self.max_content_chars = max_content_chars
        self._session: SessionContext | None = None

    def set_session(self, session: SessionContext | None) -> None:
        """Set session context for template interpolation."""
        self._session = session

    def hydrate(self, input_data: dict[str, Any] | None = None) -> dict[str, str]:
        """Return the hydrated (interpolated) query without executing.

        Returns:
            Dict with 'query' key.
        """
        from libs.python.graph.template import interpolate

        input_data = input_data or {}
        query = interpolate(
            template=self.query_template,
            nodes=input_data,
            session=self._session,
        )
        return {"query": query}

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute web search with interpolated query."""
        from libs.python.graph.template import interpolate

        input_data = input_data or {}

        # Interpolate query template
        query = interpolate(
            template=self.query_template,
            nodes=input_data,
            session=self._session,
        )

        if not query or query == self.query_template:
            return {
                "results": [],
                "text": "",
                "query": query,
                "error": "No query provided",
                "success": False,
            }

        try:
            from libs.python.drivers.web import search, search_as_text

            results = search(
                query=query,
                max_results=self.max_results,
                max_content_chars=self.max_content_chars,
            )

            # Convert to dicts for serialization
            result_dicts = [
                {
                    "title": r.title,
                    "url": r.url,
                    "snippet": r.snippet,
                    "body": r.body,
                }
                for r in results
            ]

            text = search_as_text(
                query=query,
                max_results=self.max_results,
                max_content_chars=self.max_content_chars,
            )

            return {
                "results": result_dicts,
                "text": text,
                "query": query,
                "stdout": text,  # For consistency with other nodes
                "success": True,
            }
        except Exception as exc:
            return {
                "results": [],
                "text": "",
                "query": query,
                "error": str(exc),
                "success": False,
            }


class HumanFeedbackNode(GraphNode):
    """Graph node that blocks for human input and returns the response.

    This creates a natural checkpoint in graph execution where the human
    can review output, provide feedback, or make decisions.

    Configuration:
    - prompt_template: Template string with {{placeholders}} shown to user
    - options: Optional list of valid options (empty = freeform input)

    Output keys:
    - ``stdout``: The human's input (for downstream piping)
    - ``text``: Same as stdout (alias)
    - ``selected_option``: If options provided, the index (1-based) selected
    - ``success``: Always True (human responded)
    """

    def __init__(
        self,
        node_id: str,
        prompt_template: str = "Provide feedback:",
        options: list[str] | None = None,
    ) -> None:
        super().__init__(node_id)
        self.prompt_template = prompt_template
        self.options = options or []
        self._session: SessionContext | None = None

    def set_session(self, session: SessionContext | None) -> None:
        """Set session context for template interpolation."""
        self._session = session

    def hydrate(self, input_data: dict[str, Any] | None = None) -> dict[str, str]:
        """Return the hydrated prompt without executing."""
        from libs.python.graph.template import interpolate

        input_data = input_data or {}
        prompt = interpolate(self.prompt_template, nodes=input_data, session=self._session)
        return {"prompt": prompt, "options": ", ".join(self.options) if self.options else "(freeform)"}

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Block for human input and return the response."""
        import asyncio

        from libs.python.graph.template import interpolate

        input_data = input_data or {}

        # Interpolate prompt template
        prompt = interpolate(self.prompt_template, nodes=input_data, session=self._session)

        # Display prompt and options
        print(f"\n=== HUMAN FEEDBACK REQUIRED ===\n{prompt}")
        if self.options:
            for i, opt in enumerate(self.options, 1):
                print(f"  [{i}] {opt}")
            print()

        # Get input (async to not block event loop)
        user_input = await asyncio.to_thread(input, "> ")
        user_input = user_input.strip()

        # Parse option selection if options provided
        selected_option = 0
        if self.options:
            try:
                idx = int(user_input)
                if 1 <= idx <= len(self.options):
                    selected_option = idx
                    user_input = self.options[idx - 1]
            except ValueError:
                pass  # Freeform input even when options provided

        return {
            "stdout": user_input,
            "text": user_input,
            "selected_option": selected_option,
            "success": True,
        }
