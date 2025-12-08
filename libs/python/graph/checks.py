"""
@llm-type library.graph.checks
@llm-does pre-flight and post-flight procedures for graph execution

Standard Procedures
-------------------

Pre-flight checks:
    - RubricMatchCheck: validates input matches graph selection criteria
    - ContextLoadCheck: upserts session context from store

Post-flight actions:
    - AuditAction: persists execution record to document store
    - ContextPersistAction: writes session context and CDC changelog
"""

from __future__ import annotations

from typing import Any

from .context import ContextStore, SessionContext
from .protocol import (
    CheckResult,
    FlightContext,
    FlightRecord,
    PostFlightAction,
    PreFlightCheck,
    Verdict,
)
from .scoring import DEFAULT_RUBRIC, ScoringRubric, score_text_to_graph


class RubricMatchCheck(PreFlightCheck):
    """Validate that input text matches graph criteria.

    The rubric defines scoring rules for matching user input to graphs.
    Scores below threshold result in ABORT.

    Uses shared scoring logic from libs/python/graph/scoring.py.
    """

    def __init__(
        self,
        rubric_id: str,
        graph_tags: list[str],
        graph_name: str,
        graph_description: str = "",
        rubric: ScoringRubric | None = None,
    ) -> None:
        self._rubric_id = rubric_id
        self._tags = graph_tags
        self._name = graph_name
        self._description = graph_description
        self._rubric = rubric or DEFAULT_RUBRIC

    @property
    def check_id(self) -> str:
        return f"rubric:{self._rubric_id}"

    def execute(self, context: FlightContext) -> CheckResult:
        """Score input against graph metadata."""
        input_text = context.input_data.get("text", "")
        if not input_text:
            return CheckResult(
                check_id=self.check_id,
                verdict=Verdict.ABORT,
                reason="no input text provided",
            )

        score = score_text_to_graph(
            text=input_text,
            tags=self._tags,
            name=self._name,
            description=self._description,
            rubric=self._rubric,
        )

        threshold = self._rubric.threshold

        if score < threshold:
            return CheckResult(
                check_id=self.check_id,
                verdict=Verdict.ABORT,
                reason=f"score {score:.1f} below threshold {threshold}",
                metadata={"score": score, "threshold": threshold},
            )

        return CheckResult(
            check_id=self.check_id,
            verdict=Verdict.PROCEED,
            reason=f"score {score:.1f} meets threshold",
            metadata={"score": score, "threshold": threshold},
        )


class AuditAction(PostFlightAction):
    """Persist execution record to document store."""

    def __init__(self, collection: str = "execution_audit") -> None:
        self._collection = collection

    @property
    def action_id(self) -> str:
        return f"audit:{self._collection}"

    def execute(self, record: FlightRecord) -> None:
        """Write record to document store."""
        try:
            from libs.python.persistence import get_document_store

            store = get_document_store()

            data: dict[str, Any] = {
                "graph_id": record.context.graph_id,
                "execution_id": record.context.execution_id,
                "input_data": record.context.input_data,
                "timestamp": record.context.timestamp.isoformat(),
                "pre_flight_checks": [
                    {
                        "check_id": c.check_id,
                        "verdict": c.verdict.value,
                        "reason": c.reason,
                    }
                    for c in record.pre_flight_checks
                ],
                "in_flight_result": record.in_flight_result,
                "post_flight_actions": record.post_flight_actions,
                "aborted": record.aborted,
                "abort_reason": record.abort_reason,
                "completed_at": record.completed_at.isoformat() if record.completed_at else None,
            }

            store.create(self._collection, data)

        except Exception:
            # audit is best-effort; do not fail execution
            pass


class ContextLoadCheck(PreFlightCheck):
    """Load or create session context during pre-flight.

    Upserts context from store and attaches to FlightContext metadata.
    Always returns PROCEED - context creation is not a blocker.
    """

    def __init__(self, session_id: str | None = None) -> None:
        self._session_id = session_id
        self._store = ContextStore()

    @property
    def check_id(self) -> str:
        return "context:load"

    def execute(self, context: FlightContext) -> CheckResult:
        """Load context and attach to flight metadata."""
        session_id = self._session_id or context.execution_id

        session_ctx = self._store.upsert(session_id)
        session_ctx.set_stage("pre_flight")

        # Attach to flight context metadata for downstream access
        context.metadata["session_context"] = session_ctx

        return CheckResult(
            check_id=self.check_id,
            verdict=Verdict.PROCEED,
            reason=f"session {session_id} loaded",
            metadata={"session_id": session_id, "keys": list(session_ctx.data().keys())},
        )


class ContextPersistAction(PostFlightAction):
    """Persist session context and CDC changelog during post-flight."""

    def __init__(self) -> None:
        self._store = ContextStore()

    @property
    def action_id(self) -> str:
        return "context:persist"

    def execute(self, record: FlightRecord) -> None:
        """Write context and changelog to store."""
        session_ctx: SessionContext | None = record.context.metadata.get("session_context")
        if session_ctx is None:
            return

        session_ctx.set_stage("post_flight")
        self._store.persist(session_ctx)
