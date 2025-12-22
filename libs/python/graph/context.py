"""
@llm-type library.graph.context
@llm-does session context management with CDC-style changelog

Session Context
---------------

Mutable state container that flows through the execution protocol.
Changes are tracked as a changelog (CDC pattern) for audit and replay.

Session Lifecycle:
    - Sessions are created during PRE-FLIGHT
    - Sessions can be RESUMED if the user selects a previous session
    - Sessions are persisted during POST-FLIGHT for audit and recall
    - Session data persists in document store with timestamps

The session ID is always a UUID. The context store provides methods
to list previous sessions (for a landing page) and resume them.

Usage in 3-stage SOP:
    PRE-FLIGHT:  create (new) or resume (existing)
    IN-FLIGHT:   mutate (tracked changes)
    POST-FLIGHT: persist (write to store for audit/recall)

The context is the "nervous system" - carries state across stages
while maintaining a record of all mutations.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from libs.python.cache import LRUCache


class MutationType(Enum):
    """Type of context mutation."""

    # TODO: Add "archive"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


# TODO:P1:Graduate this pattern to have an accompanying schema for each event type.
# - This can be implemented in variety of manners.
# - The intention is to have more information included in the event payload. This information can be used for filtering, searching, and analysis.
# - This will also increase the success of the LLM's ability to understand the context of the event.
# - This will, in effect, "graduate" this pattern from a simple enum to a full-blown class hierarchy.
# - CDCEvent.data is where we store a generic payload. We cannot add any logic (bussiness, validation, etc.) in a consistent and extensible manner without first graduating the pattern.
# - This is a big ask. The pre-commit hooks, which run linting and static analysis as well as other quality gates, will slow this work and make it considerably frustrating as this pattern is currently using `Any`.
class CDCEventType(Enum):
    """Type of CDC event for the session feed."""

    # State mutations
    STATE_CREATE = "state.create"
    STATE_UPDATE = "state.update"
    STATE_DELETE = "state.delete"

    # Chat messages
    MSG_USER = "msg.user"
    MSG_SYSTEM = "msg.system"
    MSG_ERROR = "msg.error"

    # Execution events (graph level)
    EXEC_START = "exec.start"
    EXEC_STDOUT = "exec.stdout"
    EXEC_STDERR = "exec.stderr"
    EXEC_EXIT = "exec.exit"

    # Node-level execution
    NODE_START = "node.start"
    NODE_OUTPUT = "node.output"
    NODE_SUCCESS = "node.success"
    NODE_FAILED = "node.failed"
    NODE_SKIPPED = "node.skipped"

    # Edge transitions
    EDGE_EVAL = "edge.eval"
    EDGE_TAKEN = "edge.taken"
    EDGE_BLOCKED = "edge.blocked"

    # Pre/post flight
    FLIGHT_CHECK = "flight.check"
    FLIGHT_ACTION = "flight.action"

    # Embedding events
    EMBED_START = "embed.start"
    EMBED_SUCCESS = "embed.success"
    EMBED_FAILED = "embed.failed"

    # System events (strace, kernel)
    SYS_CALL = "sys.call"
    SYS_LOG = "sys.log"

    # Pipeline events (prompt assembly)
    PIPELINE_STEP = "pipeline.step"
    PIPELINE_COMPRESS = "pipeline.compress"
    PIPELINE_COMPLETE = "pipeline.complete"

    # Loop control flow events
    LOOP_ITERATION_START = "loop.iteration.start"
    LOOP_ITERATION_END = "loop.iteration.end"

    # Identity/calibration events
    IDENTITY_HYDRATED = "identity.hydrated"
    ECALIBRATION_UPDATED = "ecalibration.updated"

    # Rubric grading events (post-flight quality gate)
    RUBRIC_GRADE = "rubric.grade"

    # Human feedback events (async human-in-the-loop)
    HUMAN_FEEDBACK_REQUIRED = "human.feedback.required"
    HUMAN_FEEDBACK_RESPONSE = "human.feedback.response"


# TODO: Rename to Event -- There will be an increasing amount of event types directly correlated with features over time.
# This work will first require the engineer to gather all existing use cases, ideate on the new class hierarchy, and then implement.
# CDCEventType should help here.
#
# User signoff is required at the class heirarchy and naming.
@dataclass
class CDCEvent:
    """Single event in the CDC feed.

    This is the universal event type for the session's nervous system.
    Everything that happens in a session flows through here.
    """

    event_type: CDCEventType
    timestamp: datetime
    data: dict[str, Any]
    stage: str = ""  # pre_flight, in_flight, post_flight
    sequence: int = 0  # monotonic sequence number within session


# TODO: Pivot this pattern to "Delta".
# - This is the diff between two things, and is determined both by "an" event as well as "between" events if applicable.
# - A Mutation is a type of Delta.
# - An example of a Delta that is not a Mutation is an increase in some telemetry metric.
#   - In this example, it is an Observation where the Delta carries some significance relative to the user.
# - User signoff on naming required.
@dataclass
class Mutation:
    """Single mutation record in the changelog."""

    key: str
    mutation_type: MutationType
    old_value: Any
    new_value: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    stage: str = ""  # pre_flight, in_flight, post_flight


CDCCallback = Callable[[CDCEvent], None]


# TODO:
# - Enable strace by default.
# - Dedupe "changelog" and "cdc_feed" features. See TODO on Changelog.
@dataclass
class SessionContext:
    """Mutable session state with full CDC feed.

    The context carries session data through all execution stages.
    The CDC feed captures EVERYTHING:
    - State mutations (key/value changes)
    - Chat messages (user input, system responses)
    - Execution output (stdout, stderr, exit codes)
    - Flight checks and actions
    - Embedding events
    - System calls (if strace enabled)

    Node outputs are stored in an LRU cache (libs/python/cache.LRUCache)
    for automatic eviction when the session grows large.
    Access via set_output()/get_output().
    """

    session_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    _data: dict[str, Any] = field(default_factory=dict)
    _changelog: list[Mutation] = field(default_factory=list)
    _cdc_feed: list[CDCEvent] = field(default_factory=list)
    _current_stage: str = ""
    _sequence: int = 0
    _live_callback: CDCCallback | None = None
    # LRU cache for node outputs - initialized in __post_init__
    _outputs_cache: LRUCache | None = field(default=None, repr=False)
    _outputs_max_size: int = 100  # Max nodes to keep in cache

    def __post_init__(self) -> None:
        """Initialize LRU cache with eviction callback."""
        from libs.python.cache import LRUCache

        if self._outputs_cache is None:
            self._outputs_cache = LRUCache(
                max_size=self._outputs_max_size,
                on_evict=self._on_output_evict,
            )
        else:
            # Restored from serialization - wire up callback
            self._outputs_cache.set_on_evict(self._on_output_evict)

    def _on_output_evict(self, key: str, value: Any) -> None:
        """Called by LRUCache when an output is evicted."""
        self.emit(
            CDCEventType.STATE_DELETE,
            {"key": f"outputs.{key}", "reason": "lru_eviction"},
        )

    def set_live_callback(self, callback: CDCCallback | None) -> None:
        """Set a callback to receive CDC events in real-time."""
        self._live_callback = callback

    def set_outputs_max_size(self, max_size: int) -> None:
        """Set max number of node outputs to keep (LRU eviction)."""
        self._outputs_max_size = max_size
        if self._outputs_cache:
            self._outputs_cache._max_size = max_size

    def set_output(self, node_id: str, output: dict[str, Any]) -> None:
        """Store a node output in the LRU cache.

        Automatically evicts oldest outputs when over max_size.
        Emits CDC event for the mutation.
        """
        if self._outputs_cache is None:
            return
        is_update = self._outputs_cache.get(node_id) is not None

        # Store in cache (eviction handled by LRUCache with callback)
        self._outputs_cache.set(node_id, output)

        # Emit CDC event for the set
        cdc_type = CDCEventType.STATE_UPDATE if is_update else CDCEventType.STATE_CREATE
        self.emit(cdc_type, {"key": f"outputs.{node_id}", "output": output})

    def get_output(self, node_id: str, default: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Get a node output from the cache. Moves to most-recently-used."""
        if self._outputs_cache is None:
            return default
        result: dict[str, Any] | None = self._outputs_cache.get(node_id, default)
        return result

    def get_all_outputs(self) -> dict[str, dict[str, Any]]:
        """Get all cached outputs as a dict (for template interpolation)."""
        if self._outputs_cache is None:
            return {}
        return dict(self._outputs_cache.items())

    def outputs_stats(self) -> dict[str, Any]:
        """Get stats about the outputs cache."""
        if self._outputs_cache is None:
            return {}
        return self._outputs_cache.stats()

    def set_stage(self, stage: str) -> None:
        """Set current execution stage for mutation tracking."""
        self._current_stage = stage

    def _next_seq(self) -> int:
        """Get next sequence number."""
        self._sequence += 1
        return self._sequence

    def emit(self, event_type: CDCEventType, data: dict[str, Any]) -> None:
        """Emit a CDC event to the feed.

        This is the primary method for capturing everything that happens.
        """
        event = CDCEvent(
            event_type=event_type,
            timestamp=datetime.utcnow(),
            data=data,
            stage=self._current_stage,
            sequence=self._next_seq(),
        )
        self._cdc_feed.append(event)

        # Notify live callback if set
        if self._live_callback:
            self._live_callback(event)

    def msg_user(self, text: str) -> None:
        """Log a user message."""
        self.emit(CDCEventType.MSG_USER, {"text": text})

    def msg_system(self, text: str) -> None:
        """Log a system message."""
        self.emit(CDCEventType.MSG_SYSTEM, {"text": text})

    def msg_error(self, text: str) -> None:
        """Log an error message."""
        self.emit(CDCEventType.MSG_ERROR, {"text": text})

    def exec_start(self, graph_id: str, execution_id: str) -> None:
        """Log execution start."""
        self.emit(
            CDCEventType.EXEC_START,
            {
                "graph_id": graph_id,
                "execution_id": execution_id,
            },
        )

    def exec_stdout(self, line: str) -> None:
        """Log stdout line from execution."""
        self.emit(CDCEventType.EXEC_STDOUT, {"line": line})

    def exec_stderr(self, line: str) -> None:
        """Log stderr line from execution."""
        self.emit(CDCEventType.EXEC_STDERR, {"line": line})

    def exec_exit(self, code: int) -> None:
        """Log execution exit."""
        self.emit(CDCEventType.EXEC_EXIT, {"code": code})

    # Node-level execution events
    def node_start(self, node_id: str, node_type: str, input_data: dict[str, Any] | None = None) -> None:
        """Log node execution start."""
        self.emit(
            CDCEventType.NODE_START,
            {
                "node_id": node_id,
                "node_type": node_type,
                "input": input_data or {},
            },
        )

    def node_output(self, node_id: str, output: dict[str, Any]) -> None:
        """Log node output (stdout, result, etc)."""
        self.emit(
            CDCEventType.NODE_OUTPUT,
            {
                "node_id": node_id,
                "output": output,
            },
        )

    def node_success(self, node_id: str, output: dict[str, Any]) -> None:
        """Log successful node completion."""
        self.emit(
            CDCEventType.NODE_SUCCESS,
            {
                "node_id": node_id,
                "output": output,
            },
        )

    def node_failed(self, node_id: str, error: str) -> None:
        """Log node execution failure."""
        self.emit(
            CDCEventType.NODE_FAILED,
            {
                "node_id": node_id,
                "error": error,
            },
        )

    def node_skipped(self, node_id: str, reason: str = "") -> None:
        """Log node skipped (edge condition not met)."""
        self.emit(
            CDCEventType.NODE_SKIPPED,
            {
                "node_id": node_id,
                "reason": reason,
            },
        )

    def edge_eval(self, source: str, target: str, condition: str | None, result: bool) -> None:
        """Log edge condition evaluation."""
        self.emit(
            CDCEventType.EDGE_EVAL,
            {
                "source": source,
                "target": target,
                "condition": condition,
                "result": result,
            },
        )

    def edge_taken(self, source: str, target: str) -> None:
        """Log edge traversal (control flow from source to target)."""
        self.emit(
            CDCEventType.EDGE_TAKEN,
            {
                "source": source,
                "target": target,
            },
        )

    def edge_blocked(self, source: str, target: str, condition: str) -> None:
        """Log blocked edge (condition evaluated to False)."""
        self.emit(
            CDCEventType.EDGE_BLOCKED,
            {
                "source": source,
                "target": target,
                "condition": condition,
            },
        )

    def flight_check(self, check_name: str, passed: bool, reason: str = "") -> None:
        """Log a pre-flight check result."""
        self.emit(
            CDCEventType.FLIGHT_CHECK,
            {
                "check": check_name,
                "passed": passed,
                "reason": reason,
            },
        )

    def flight_action(self, action_name: str, success: bool) -> None:
        """Log a post-flight action result."""
        self.emit(
            CDCEventType.FLIGHT_ACTION,
            {
                "action": action_name,
                "success": success,
            },
        )

    def syscall(self, call: str, args: list, result: Any = None) -> None:
        """Log a system call (from strace)."""
        self.emit(
            CDCEventType.SYS_CALL,
            {
                "call": call,
                "args": args,
                "result": result,
            },
        )

    def syslog(self, level: str, message: str) -> None:
        """Log a kernel/system log message."""
        self.emit(
            CDCEventType.SYS_LOG,
            {
                "level": level,
                "message": message,
            },
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from context.

        Special handling for 'outputs' key - returns the LRU cache contents.
        """
        if key == "outputs":
            return self.get_all_outputs()
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a value, recording the mutation."""
        old_value = self._data.get(key)
        mutation_type = MutationType.UPDATE if key in self._data else MutationType.CREATE

        self._data[key] = value
        self._changelog.append(
            Mutation(
                key=key,
                mutation_type=mutation_type,
                old_value=old_value,
                new_value=value,
                stage=self._current_stage,
            )
        )
        # Also emit to CDC feed
        cdc_type = CDCEventType.STATE_UPDATE if mutation_type == MutationType.UPDATE else CDCEventType.STATE_CREATE
        self.emit(cdc_type, {"key": key, "old": old_value, "new": value})

    def delete(self, key: str) -> None:
        """Delete a key, recording the mutation."""
        if key in self._data:
            old_value = self._data.pop(key)
            self._changelog.append(
                Mutation(
                    key=key,
                    mutation_type=MutationType.DELETE,
                    old_value=old_value,
                    new_value=None,
                    stage=self._current_stage,
                )
            )
            self.emit(CDCEventType.STATE_DELETE, {"key": key, "old": old_value})

    def data(self) -> dict[str, Any]:
        """Get snapshot of current data."""
        return dict(self._data)

    def changelog(self) -> list[Mutation]:
        """Get the mutation changelog (legacy)."""
        return list(self._changelog)

    def cdc_feed(self) -> list[CDCEvent]:
        """Get the full CDC feed."""
        return list(self._cdc_feed)

    def to_dict(self) -> dict[str, Any]:
        """Serialize context for persistence."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "data": self._data,
            "sequence": self._sequence,
            # LRU outputs cache - use LRUCache.to_dict()
            "outputs_cache": self._outputs_cache.to_dict() if self._outputs_cache else {},
            "outputs_max_size": self._outputs_max_size,
            "changelog": [
                {
                    "key": m.key,
                    "type": m.mutation_type.value,
                    "old": m.old_value,
                    "new": m.new_value,
                    "timestamp": m.timestamp.isoformat(),
                    "stage": m.stage,
                }
                for m in self._changelog
            ],
            "cdc_feed": [
                {
                    "type": e.event_type.value,
                    "timestamp": e.timestamp.isoformat(),
                    "data": e.data,
                    "stage": e.stage,
                    "seq": e.sequence,
                }
                for e in self._cdc_feed
            ],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SessionContext:
        """Deserialize context from persistence."""
        from libs.python.cache import LRUCache

        max_size = d.get("outputs_max_size", 100)

        # Create LRUCache and restore from serialized data
        cache = LRUCache(max_size=max_size)
        cache_data = d.get("outputs_cache", {})
        if cache_data:
            cache.from_dict(cache_data)

        ctx = cls(
            session_id=d["session_id"],
            created_at=datetime.fromisoformat(d["created_at"]),
            _outputs_cache=cache,
            _outputs_max_size=max_size,
        )
        ctx._data = dict(d.get("data", {}))
        ctx._sequence = d.get("sequence", 0)

        # Changelog and CDC feed are not restored - they're append-only per execution
        # But we preserve the sequence counter for continuity
        return ctx


@dataclass
class SessionSummary:
    """Summary of a session for landing page display."""

    session_id: str
    created_at: datetime
    last_updated: datetime
    mutation_count: int

    def __str__(self) -> str:
        ts = self.last_updated.strftime("%Y-%m-%d %H:%M:%S")
        return f"{self.session_id[:8]}... | {ts} | {self.mutation_count} mutations"


class ContextStore:
    """Persistence layer for session contexts.

    Lifecycle:
        PRE-FLIGHT:  create() for new session, or resume() for existing
        IN-FLIGHT:   mutate context (tracked in changelog)
        POST-FLIGHT: persist() to write to document store for audit/recall

    The landing page shows list_sessions() to let user pick a previous
    session to resume, or start a new one.
    """

    COLLECTION = "session_contexts"

    def __init__(self) -> None:
        self._store: Any = None  # DocumentStore, lazy-loaded

    def _get_store(self):
        """Lazy-load document store."""
        if self._store is None:
            try:
                from libs.python.persistence import get_document_store

                self._store = get_document_store()
            except ImportError:
                pass
        return self._store

    def create(self, session_id: str) -> SessionContext:
        """Create a fresh session context.

        Called during PRE-FLIGHT to start a new session.
        """
        return SessionContext(session_id=session_id)

    def resume(self, session_id: str) -> SessionContext | None:
        """Resume an existing session from storage.

        Called during PRE-FLIGHT when user selects a previous session.
        Returns None if session not found.
        """
        store = self._get_store()
        if store is None:
            return None

        try:
            docs = store.query(
                self.COLLECTION,
                filters={"session_id": session_id},
                limit=1,
            )
            if docs:
                return SessionContext.from_dict(docs[0].data)
        except Exception:
            pass
        return None

    def _doc_to_summary(self, doc) -> SessionSummary:
        """Convert a document to a SessionSummary."""
        data = doc.data
        created = datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat()))
        changelog = data.get("changelog", [])
        last_ts = datetime.fromisoformat(changelog[-1].get("timestamp", created.isoformat())) if changelog else created
        return SessionSummary(
            session_id=data.get("session_id", doc.id),
            created_at=created,
            last_updated=last_ts,
            mutation_count=len(changelog),
        )

    def list_sessions(self, limit: int = 20) -> list[SessionSummary]:
        """List previous sessions for landing page. Returns sessions ordered by most recent first."""
        store = self._get_store()
        if store is None:
            return []

        try:
            docs = store.query(self.COLLECTION, limit=limit)
            summaries = [self._doc_to_summary(doc) for doc in docs]
            summaries.sort(key=lambda s: s.last_updated, reverse=True)
            return summaries
        except Exception:
            return []

    # Keep upsert as alias for backwards compatibility
    def upsert(self, session_id: str) -> SessionContext:
        """Alias for create(). For backwards compatibility."""
        return self.create(session_id)

    def persist(self, context: SessionContext) -> bool:
        """Write context and changelog to store.

        Called during POST-FLIGHT to record session state and mutations.
        Returns True if successful, False otherwise.
        """
        store = self._get_store()
        if store is None:
            return False

        try:
            data = context.to_dict()

            # Check if exists
            docs = store.query(
                self.COLLECTION,
                filters={"session_id": context.session_id},
                limit=1,
            )

            if docs:
                # Update existing
                store.update(self.COLLECTION, docs[0].id, data)
            else:
                # Create new
                store.create(self.COLLECTION, data)

            # Persist full CDC feed (includes changelog mutations + everything else)
            self._persist_cdc_feed(context)

            return True
        except Exception:
            return False

    def _cdc_event_to_doc(self, session_id: str, event) -> dict:
        """Convert a CDC event to a document dict."""
        return {
            "session_id": session_id,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "data": event.data,
            "stage": event.stage,
            "sequence": event.sequence,
        }

    def _persist_cdc_feed(self, context: SessionContext) -> None:
        """Write all CDC events to the session_cdc collection. Best-effort."""
        store = self._get_store()
        if store is None or not context.cdc_feed():
            return

        try:
            for event in context.cdc_feed():
                store.create("session_cdc", self._cdc_event_to_doc(context.session_id, event))
        except Exception:
            pass  # CDC is best-effort
