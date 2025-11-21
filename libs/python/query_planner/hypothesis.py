"""Hypothesis and alternative route tracking for query diagnostics.

@llm-type library.query_planner.hypothesis
@llm-does track alternative diagnostic routes and user choices during execution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


@dataclass
class Hypothesis:
    """Represents a diagnostic hypothesis or alternative route.

    A hypothesis is a specific diagnostic path chosen by the user or system
    when multiple alternatives are available.
    """

    id: str
    name: str
    description: str
    plan: Any  # QueryPlan (avoid circular import)
    user_choice: bool = False  # True if user explicitly selected this
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "user_choice": self.user_choice,
            "plan": self.plan.to_json_compatible(),
            "metadata": dict(self.metadata),
        }


@dataclass
class HypothesisSet:
    """Collection of alternative diagnostic hypotheses.

    Tracks multiple possible diagnostic routes and which one was selected.
    """

    query: str
    hypotheses: list[Hypothesis] = field(default_factory=list)
    selected_hypothesis_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_hypothesis(self, hypothesis: Hypothesis) -> None:
        """Add a hypothesis to the set."""
        if any(h.id == hypothesis.id for h in self.hypotheses):
            raise ValueError(f"Hypothesis {hypothesis.id} already exists")
        self.hypotheses.append(hypothesis)

    def select_hypothesis(self, hypothesis_id: str) -> None:
        """Mark a hypothesis as selected."""
        if not any(h.id == hypothesis_id for h in self.hypotheses):
            raise ValueError(f"Hypothesis {hypothesis_id} not found")
        self.selected_hypothesis_id = hypothesis_id

    def get_selected(self) -> Hypothesis | None:
        """Get the currently selected hypothesis."""
        if not self.selected_hypothesis_id:
            return None
        return next(
            (h for h in self.hypotheses if h.id == self.selected_hypothesis_id),
            None,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "selected_hypothesis_id": self.selected_hypothesis_id,
            "metadata": dict(self.metadata),
        }
