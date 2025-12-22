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
class GradeResult:
    """Result of rubric grading in post-flight."""

    rubric_name: str
    score: float
    threshold: float
    passed: bool
    criteria_scores: dict[str, float] = field(default_factory=dict)
    missing_fields: list[str] = field(default_factory=list)
    feedback: str = ""


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
    # Post-flight rubric grading
    rubric_grade: GradeResult | None = None


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


class FlightObserver(ABC):
    """Abstract base for flight observers.

    Observers receive events during all flight stages in real-time.
    Used for live UI updates, progress tracking, streaming output.

    Unlike PostFlightAction (which runs after completion), observers
    are notified as events occur during execution.
    """

    @property
    @abstractmethod
    def observer_id(self) -> str:
        """Unique identifier for this observer."""

    @abstractmethod
    def on_event(self, stage: FlightStage, event_type: str, data: dict[str, Any]) -> None:
        """Called when an event occurs during any flight stage.

        Args:
            stage: Current flight stage (PRE_FLIGHT, IN_FLIGHT, POST_FLIGHT)
            event_type: Type of event (e.g., "node.start", "msg.user")
            data: Event payload
        """

    def on_stage_enter(self, stage: FlightStage) -> None:
        """Called when entering a flight stage. Optional override."""

    def on_stage_exit(self, stage: FlightStage) -> None:
        """Called when exiting a flight stage. Optional override."""


class ExecutionProtocol:
    """Orchestrates the 3-stage execution SOP.

    Pre-flight checks run sequentially. First ABORT halts.
    In-flight execution is delegated to a provided executor.
    Post-flight actions run sequentially after execution.
    Observers are notified of events during all stages.
    """

    def __init__(self) -> None:
        self._pre_flight_checks: list[PreFlightCheck] = []
        self._post_flight_actions: list[PostFlightAction] = []
        self._observers: list[FlightObserver] = []
        self._current_stage: FlightStage | None = None

    def register_check(self, check: PreFlightCheck) -> None:
        """Register a pre-flight check."""
        self._pre_flight_checks.append(check)

    def register_action(self, action: PostFlightAction) -> None:
        """Register a post-flight action."""
        self._post_flight_actions.append(action)

    def register_observer(self, observer: FlightObserver) -> None:
        """Register a flight observer for real-time event notifications."""
        self._observers.append(observer)

    def unregister_observer(self, observer: FlightObserver) -> None:
        """Unregister a flight observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, event_type: str, data: dict[str, Any]) -> None:
        """Notify all observers of an event in the current stage."""
        if self._current_stage is None:
            return
        for observer in self._observers:
            try:
                observer.on_event(self._current_stage, event_type, data)
            except Exception:
                # Observers should not break execution
                pass

    def _enter_stage(self, stage: FlightStage) -> None:
        """Enter a flight stage and notify observers."""
        self._current_stage = stage
        for observer in self._observers:
            try:
                observer.on_stage_enter(stage)
            except Exception:
                pass

    def _exit_stage(self, stage: FlightStage) -> None:
        """Exit a flight stage and notify observers."""
        for observer in self._observers:
            try:
                observer.on_stage_exit(stage)
            except Exception:
                pass
        self._current_stage = None

    def run_pre_flight(self, context: FlightContext) -> tuple[Verdict, list[CheckResult]]:
        """Execute all pre-flight checks.

        Returns (final_verdict, list_of_results).
        Final verdict is ABORT if any check returns ABORT.
        """
        self._enter_stage(FlightStage.PRE_FLIGHT)
        results: list[CheckResult] = []
        final_verdict = Verdict.PROCEED

        for check in self._pre_flight_checks:
            self.notify_observers("check.start", {"check_id": check.check_id})
            result = check.execute(context)
            results.append(result)
            self.notify_observers(
                "check.complete",
                {
                    "check_id": check.check_id,
                    "verdict": result.verdict.value,
                    "reason": result.reason,
                },
            )

            if result.verdict == Verdict.ABORT:
                final_verdict = Verdict.ABORT
                break
            elif result.verdict == Verdict.WARN and final_verdict != Verdict.ABORT:
                final_verdict = Verdict.WARN

        self._exit_stage(FlightStage.PRE_FLIGHT)
        return final_verdict, results

    def run_post_flight(self, record: FlightRecord) -> None:
        """Execute all post-flight actions."""
        self._enter_stage(FlightStage.POST_FLIGHT)
        for action in self._post_flight_actions:
            self.notify_observers("action.start", {"action_id": action.action_id})
            action.execute(record)
            record.post_flight_actions.append(action.action_id)
            self.notify_observers("action.complete", {"action_id": action.action_id})

        record.completed_at = datetime.utcnow()
        self._exit_stage(FlightStage.POST_FLIGHT)
