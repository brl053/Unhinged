"""Graph node primitives.

@llm-type library.graph.nodes
@llm-does define abstract GraphNode and UnixCommandNode for executing shell commands
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:  # pragma: no cover - import only for type checking
    from .graph import Graph, GraphExecutionResult


class GraphNode(ABC):
    """Abstract base for all graph nodes in the Unhinged DAG framework."""

    def __init__(self, node_id: str) -> None:
        self.id = node_id

    @abstractmethod
    async def execute(self, input_data: Optional[dict[str, Any]] = None) -> dict[str, Any]:
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

    async def execute(self, input_data: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Execute the configured shell command.

        Parameters
        ----------
        input_data:
            Optional dictionary. If it contains a ``"stdin"`` key its value
            will be sent to the process as standard input. Supported value
            types are ``str`` and ``bytes``.
        """
        stdin_bytes: Optional[bytes] = None
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
        except asyncio.TimeoutError:
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
        stdout_adapter: Optional[Callable[[GraphExecutionResult], str]] = None,
    ) -> None:
        super().__init__(node_id)
        self.subgraph = subgraph
        self._stdout_adapter = stdout_adapter

    async def execute(self, input_data: Optional[dict[str, Any]] = None) -> dict[str, Any]:
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
