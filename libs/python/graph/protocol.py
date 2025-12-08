"""
@llm-type library.graph.protocol
@llm-does 3-stage execution protocol for graph workflows

Execution Protocol
------------------

Standard Operating Procedure for graph execution:

    1. PRE-FLIGHT  - validation, authorization, rubric matching
    2. IN-FLIGHT   - stateless execution, isolated, scalable
    3. POST-FLIGHT - audit, persistence, output transformation

Middleware hooks into stages 1 and 3. Stage 2 remains pure.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class FlightStage(Enum):
    """Execution stage identifier."""

    PRE_FLIGHT = "pre_flight"
    IN_FLIGHT = "in_flight"
    POST_FLIGHT = "post_flight"


class Verdict(Enum):
    """Result of a pre-flight check."""

    PROCEED = "proceed"
    ABORT = "abort"
    WARN = "warn"


@dataclass
class CheckResult:
    """Result from a single pre-flight check."""

    check_id: str
    verdict: Verdict
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FlightContext:
    """Immutable context passed through all stages."""

    graph_id: str
    execution_id: str
    input_data: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FlightRecord:
    """Audit record of a complete execution."""

    context: FlightContext
    pre_flight_checks: list[CheckResult] = field(default_factory=list)
    in_flight_result: dict[str, Any] = field(default_factory=dict)
    post_flight_actions: list[str] = field(default_factory=list)
    completed_at: datetime | None = None
    aborted: bool = False
    abort_reason: str = ""


class PreFlightCheck(ABC):
    """Abstract base for pre-flight validation checks.

    Implementations examine the FlightContext and return a CheckResult.
    Any check returning ABORT halts execution before in-flight.
    """

    @property
    @abstractmethod
    def check_id(self) -> str:
        """Unique identifier for this check."""

    @abstractmethod
    def execute(self, context: FlightContext) -> CheckResult:
        """Run the check against the given context."""


class PostFlightAction(ABC):
    """Abstract base for post-flight actions.

    Implementations receive the complete FlightRecord after execution.
    Used for audit logging, persistence, notifications.
    """

    @property
    @abstractmethod
    def action_id(self) -> str:
        """Unique identifier for this action."""

    @abstractmethod
    def execute(self, record: FlightRecord) -> None:
        """Execute the post-flight action."""


class ExecutionProtocol:
    """Orchestrates the 3-stage execution SOP.

    Pre-flight checks run sequentially. First ABORT halts.
    In-flight execution is delegated to a provided executor.
    Post-flight actions run sequentially after execution.
    """

    def __init__(self) -> None:
        self._pre_flight_checks: list[PreFlightCheck] = []
        self._post_flight_actions: list[PostFlightAction] = []

    def register_check(self, check: PreFlightCheck) -> None:
        """Register a pre-flight check."""
        self._pre_flight_checks.append(check)

    def register_action(self, action: PostFlightAction) -> None:
        """Register a post-flight action."""
        self._post_flight_actions.append(action)

    def run_pre_flight(self, context: FlightContext) -> tuple[Verdict, list[CheckResult]]:
        """Execute all pre-flight checks.

        Returns (final_verdict, list_of_results).
        Final verdict is ABORT if any check returns ABORT.
        """
        results: list[CheckResult] = []
        final_verdict = Verdict.PROCEED

        for check in self._pre_flight_checks:
            result = check.execute(context)
            results.append(result)

            if result.verdict == Verdict.ABORT:
                final_verdict = Verdict.ABORT
                break
            elif result.verdict == Verdict.WARN and final_verdict != Verdict.ABORT:
                final_verdict = Verdict.WARN

        return final_verdict, results

    def run_post_flight(self, record: FlightRecord) -> None:
        """Execute all post-flight actions."""
        for action in self._post_flight_actions:
            action.execute(record)
            record.post_flight_actions.append(action.action_id)

        record.completed_at = datetime.utcnow()
