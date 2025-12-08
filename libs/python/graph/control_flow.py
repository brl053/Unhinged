"""Higher-order graph control flow constructs.

@llm-type library.graph.control_flow
@llm-does ForLoopGraph, WhileLoopGraph, BreakNode, ContinueNode for graph orchestration

These are meta-constructs that wrap graph execution, not node execution.
They enable algorithms (BFS, DFS, crawlers) to be expressed as graph compositions.
"""

from __future__ import annotations

from typing import Any

from .graph import Graph
from .nodes import GraphNode

# =============================================================================
# STUB: ForLoopGraph - TDD implementation pending
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

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        # STUB: Return failure to make tests fail properly
        return {
            "success": False,
            "iterations": 0,
            "outputs": [],
            "error": "ForLoopGraph not implemented",
        }


# =============================================================================
# STUB: WhileLoopGraph - TDD implementation pending
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

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        # STUB: Return failure to make tests fail properly
        return {
            "success": False,
            "iterations": 0,
            "termination_reason": "WhileLoopGraph not implemented",
        }


# =============================================================================
# STUB: BreakNode - TDD implementation pending
# =============================================================================


class BreakNode(GraphNode):
    """Signal early termination of enclosing loop."""

    def __init__(self, node_id: str = "break", condition: str = "True") -> None:
        super().__init__(node_id)
        self.condition = condition

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        # STUB: Return not triggered to make tests fail properly
        return {"triggered": False, "error": "BreakNode not implemented"}


# =============================================================================
# STUB: ContinueNode - TDD implementation pending
# =============================================================================


class ContinueNode(GraphNode):
    """Signal skip to next iteration of enclosing loop."""

    def __init__(self, node_id: str = "continue", condition: str = "True") -> None:
        super().__init__(node_id)
        self.condition = condition

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        # STUB: Return not triggered to make tests fail properly
        return {"triggered": False, "error": "ContinueNode not implemented"}
