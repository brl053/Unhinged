"""Higher-order graph control flow constructs.

@llm-type library.graph.control_flow
@llm-does ForLoopGraph, WhileLoopGraph, BreakNode, ContinueNode for graph orchestration

These are meta-constructs that wrap graph execution, not node execution.
They enable algorithms (BFS, DFS, crawlers) to be expressed as graph compositions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .context import CDCEventType
from .graph import Graph, GraphExecutor
from .nodes import GraphNode

if TYPE_CHECKING:
    from .context import SessionContext


class LoopBreakError(Exception):
    """Signal to break out of enclosing loop."""


class LoopContinueError(Exception):
    """Signal to skip to next iteration."""


# =============================================================================
# ForLoopGraph - Iterate over collection
# =============================================================================


class ForLoopGraph(GraphNode):
    """Execute body graph for each item in a collection.

    Acts as recursion primitive for iteration-based algorithms.
    """

    def __init__(
        self,
        node_id: str = "for_loop",
        items: list[Any] | None = None,
        body_graph: Graph | None = None,
        item_input_node: str | None = None,
    ) -> None:
        super().__init__(node_id)
        self.items = items or []
        self.body_graph = body_graph
        self.item_input_node = item_input_node
        self._session_ctx: SessionContext | None = None

    async def _execute_iteration(self, idx: int, item: Any, outputs: list[dict[str, Any]]) -> dict[str, Any] | None:
        """Execute a single loop iteration. Returns early-exit result or None to continue."""
        if not self.body_graph:
            return None

        if self._session_ctx:
            self._session_ctx.emit(CDCEventType.LOOP_ITERATION_START, {"index": idx, "item": item})

        # Prepare inputs for ALL nodes in body graph with loop context
        loop_context = {"stdin": str(item), "item": item, "index": idx}
        body_inputs: dict[str, dict[str, Any]] = {nid: dict(loop_context) for nid in self.body_graph.nodes}

        # Execute body graph
        executor = GraphExecutor(session_ctx=self._session_ctx)
        result = await executor.execute(self.body_graph, initial_inputs=body_inputs)

        # Check for break/continue signals
        should_break, should_skip = self._check_control_signals(result)

        if self._session_ctx:
            self._session_ctx.emit(CDCEventType.LOOP_ITERATION_END, {"index": idx})

        if should_break:
            return {"success": True, "iterations": idx + 1, "outputs": outputs, "terminated_early": True}

        if not should_skip:
            outputs.append({"index": idx, "item": item, "result": result})
        return None

    def _check_control_signals(self, result: Any) -> tuple[bool, bool]:
        """Check for break/continue signals in node results. Returns (should_break, should_skip)."""
        should_break = False
        should_skip = False
        for node_result in result.node_results.values():
            if node_result.output.get("break_triggered"):
                should_break = True
                break
            if node_result.output.get("continue_triggered"):
                should_skip = True
        return should_break, should_skip

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        input_data = input_data or {}

        if not self.body_graph:
            return {"success": True, "iterations": 0, "outputs": [], "error": None}

        outputs: list[dict[str, Any]] = []
        iteration_indices: list[int] = []

        for idx, item in enumerate(self.items):
            iteration_result = await self._execute_iteration(idx, item, outputs)
            if iteration_result is not None:
                return iteration_result
            iteration_indices.append(idx)

        return {
            "success": True,
            "iterations": len(self.items),
            "outputs": outputs,
            "iteration_indices": iteration_indices,
        }


# =============================================================================
# WhileLoopGraph - Execute until condition fails
# =============================================================================


class WhileLoopGraph(GraphNode):
    """Execute body graph until condition evaluates false.

    Includes max_iterations safety to prevent infinite loops.
    """

    def __init__(
        self,
        node_id: str = "while_loop",
        condition: str = "False",
        body_graph: Graph | None = None,
        max_iterations: int = 100,
    ) -> None:
        super().__init__(node_id)
        self.condition = condition
        self.body_graph = body_graph
        self.max_iterations = max_iterations
        self._session_ctx: SessionContext | None = None

    def _evaluate_condition(self, context: dict[str, Any]) -> bool:
        """Evaluate condition string in given context."""
        try:
            return bool(eval(self.condition, {"__builtins__": {}}, context))  # noqa: S307
        except Exception:
            return False

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        input_data = input_data or {}
        context = dict(input_data)
        context["loop_count"] = 0

        if not self.body_graph:
            return {"success": True, "iterations": 0, "termination_reason": "no_body"}

        outputs: list[dict[str, Any]] = []
        iterations = 0

        while self._evaluate_condition(context) and iterations < self.max_iterations:
            if self._session_ctx:
                self._session_ctx.emit(CDCEventType.LOOP_ITERATION_START, {"iteration": iterations})

            executor = GraphExecutor(session_ctx=self._session_ctx)
            result = await executor.execute(self.body_graph)

            outputs.append({"iteration": iterations, "result": result})
            iterations += 1
            context["loop_count"] = iterations

            if self._session_ctx:
                self._session_ctx.emit(CDCEventType.LOOP_ITERATION_END, {"iteration": iterations})

        termination = "condition_false" if iterations < self.max_iterations else "max_iterations"

        return {
            "success": True,
            "iterations": iterations,
            "outputs": outputs,
            "termination_reason": termination,
        }


# =============================================================================
# BreakNode - Early loop termination
# =============================================================================


class BreakNode(GraphNode):
    """Signal early termination of enclosing loop."""

    def __init__(self, node_id: str = "break", condition: str = "True") -> None:
        super().__init__(node_id)
        self.condition = condition

    def _evaluate_condition(self, context: dict[str, Any]) -> bool:
        """Evaluate condition string in given context."""
        try:
            return bool(eval(self.condition, {"__builtins__": {}}, context))  # noqa: S307
        except Exception:
            return False

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        input_data = input_data or {}
        triggered = self._evaluate_condition(input_data)
        return {"triggered": triggered, "break_triggered": triggered}


# =============================================================================
# ContinueNode - Skip to next iteration
# =============================================================================


class ContinueNode(GraphNode):
    """Signal skip to next iteration of enclosing loop."""

    def __init__(self, node_id: str = "continue", condition: str = "True") -> None:
        super().__init__(node_id)
        self.condition = condition

    def _evaluate_condition(self, context: dict[str, Any]) -> bool:
        """Evaluate condition string in given context."""
        try:
            return bool(eval(self.condition, {"__builtins__": {}}, context))  # noqa: S307
        except Exception:
            return False

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        input_data = input_data or {}
        triggered = self._evaluate_condition(input_data)
        return {"triggered": triggered, "continue_triggered": triggered}
