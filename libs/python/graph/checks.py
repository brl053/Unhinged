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
    GradeResult,
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
            data = self._build_audit_data(record)
            store.create(self._collection, data)

        except Exception:
            # audit is best-effort; do not fail execution
            pass

    def _build_audit_data(self, record: FlightRecord) -> dict[str, Any]:
        """Build audit data dictionary from record."""
        pre_flight = [
            {"check_id": c.check_id, "verdict": c.verdict.value, "reason": c.reason} for c in record.pre_flight_checks
        ]
        return {
            "graph_id": record.context.graph_id,
            "execution_id": record.context.execution_id,
            "input_data": record.context.input_data,
            "timestamp": record.context.timestamp.isoformat(),
            "pre_flight_checks": pre_flight,
            "in_flight_result": record.in_flight_result,
            "post_flight_actions": record.post_flight_actions,
            "aborted": record.aborted,
            "abort_reason": record.abort_reason,
            "completed_at": record.completed_at.isoformat() if record.completed_at else None,
        }


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


class RubricGradeAction(PostFlightAction):
    """Grade execution output against a stored rubric in post-flight.

    Rubrics are stored as documents with schema:
        {
            "name": "invoice_v1",
            "criteria": [
                {"field": "citations", "min_count": 1, "weight": 0.4},
                {"field": "diagnosis", "min_length": 20, "weight": 0.3},
                {"field": "action", "required": True, "weight": 0.3}
            ],
            "pass_threshold": 0.6
        }

    If rubric fails, record.rubric_grade.passed = False.
    Session can then offer re-run to user.
    """

    def __init__(self, rubric_name: str = "invoice_v1", collection: str = "rubrics") -> None:
        self._rubric_name = rubric_name
        self._collection = collection

    @property
    def action_id(self) -> str:
        return f"rubric_grade:{self._rubric_name}"

    def execute(self, record: FlightRecord) -> None:
        """Grade the in_flight_result against the rubric."""
        rubric = self._load_rubric()
        if rubric is None:
            # No rubric defined yet - pass by default
            record.rubric_grade = GradeResult(
                rubric_name=self._rubric_name,
                score=1.0,
                threshold=0.0,
                passed=True,
                feedback="no rubric defined - auto-pass",
            )
            return

        result = record.in_flight_result
        criteria = rubric.get("criteria", [])
        threshold = rubric.get("pass_threshold", 0.6)

        total_weight = sum(c.get("weight", 1.0) for c in criteria)
        weighted_score = 0.0
        criteria_scores: dict[str, float] = {}
        missing_fields: list[str] = []
        feedback_parts: list[str] = []

        for criterion in criteria:
            field = criterion.get("field", "")
            weight = criterion.get("weight", 1.0)
            field_value = result.get(field)

            score = self._grade_criterion(criterion, field_value)
            criteria_scores[field] = score
            weighted_score += score * weight

            if score < 1.0:
                if field_value is None:
                    missing_fields.append(field)
                    feedback_parts.append(f"missing: {field}")
                else:
                    feedback_parts.append(f"insufficient: {field} (score: {score:.2f})")

        final_score = weighted_score / total_weight if total_weight > 0 else 0.0
        passed = final_score >= threshold

        record.rubric_grade = GradeResult(
            rubric_name=self._rubric_name,
            score=final_score,
            threshold=threshold,
            passed=passed,
            criteria_scores=criteria_scores,
            missing_fields=missing_fields,
            feedback="; ".join(feedback_parts) if feedback_parts else "all criteria met",
        )

    def _load_rubric(self) -> dict[str, Any] | None:
        """Load rubric from document store."""
        try:
            from libs.python.persistence import get_document_store

            store = get_document_store()
            results = store.query(self._collection, {"name": self._rubric_name})
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
