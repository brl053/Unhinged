"""Core graph library primitives for Unhinged.

@llm-type library.graph
@llm-does provide base node abstractions and DAG executor for orchestration
"""

from __future__ import annotations

from .checks import AuditAction, ContextLoadCheck, ContextPersistAction, RubricGradeAction, RubricMatchCheck
from .context import CDCEvent, CDCEventType, ContextStore, Mutation, MutationType, SessionContext, SessionSummary
from .graph import Graph, GraphExecutionResult, GraphExecutor, NodeExecutionResult
from .loader import GraphLoadError, load_graph_from_dict, load_graph_from_json
from .nodes import (
    APINode,
    GraphNode,
    LLMNode,
    RecallNode,
    RubricGradeNode,
    StructuredOutputNode,
    SubgraphNode,
    UnixCommandNode,
    UserInputNode,
)
from .pipeline_steps import (
    AssembleFinalPromptStep,
    ContextWindowCheckStep,
    GarbageCompressionStep,
    InjectSystemPromptStep,
)
from .prompt_pipeline import (
    PipelineStep,
    PromptPayload,
    PromptPipeline,
    StepOutput,
    StepResult,
)
from .protocol import (
    CheckResult,
    ExecutionProtocol,
    FlightContext,
    FlightRecord,
    FlightStage,
    GradeResult,
    PostFlightAction,
    PreFlightCheck,
    Verdict,
)
from .scoring import DEFAULT_RUBRIC, ScoringRubric, match_best_graph, score_text_to_graph
from .strace import (
    FILTER_FILE,
    FILTER_IO,
    FILTER_MEMORY,
    FILTER_NETWORK,
    FILTER_PROCESS,
    SyscallRecord,
    is_strace_available,
    parse_strace_output,
    run_with_strace,
)

__all__ = [
    # nodes
    "GraphNode",
    "SubgraphNode",
    "UnixCommandNode",
    "UserInputNode",
    "APINode",
    "RecallNode",
    "RubricGradeNode",
    "LLMNode",
    "StructuredOutputNode",
    # graph
    "Graph",
    # loader
    "load_graph_from_json",
    "load_graph_from_dict",
    "GraphLoadError",
    "GraphExecutor",
    "NodeExecutionResult",
    "GraphExecutionResult",
    # protocol
    "ExecutionProtocol",
    "FlightContext",
    "FlightRecord",
    "FlightStage",
    "CheckResult",
    "Verdict",
    "GradeResult",
    "PreFlightCheck",
    "PostFlightAction",
    # checks
    "RubricMatchCheck",
    "RubricGradeAction",
    "AuditAction",
    "ContextLoadCheck",
    "ContextPersistAction",
    # context (nervous system / CDC)
    "SessionContext",
    "SessionSummary",
    "ContextStore",
    "Mutation",
    "MutationType",
    "CDCEvent",
    "CDCEventType",
    # scoring
    "ScoringRubric",
    "DEFAULT_RUBRIC",
    "score_text_to_graph",
    "match_best_graph",
    # strace (kernel syscalls)
    "run_with_strace",
    "is_strace_available",
    "parse_strace_output",
    "SyscallRecord",
    "FILTER_IO",
    "FILTER_NETWORK",
    "FILTER_PROCESS",
    "FILTER_MEMORY",
    "FILTER_FILE",
    # prompt pipeline (pre-flight prompt assembly)
    "PromptPipeline",
    "PipelineStep",
    "PromptPayload",
    "StepOutput",
    "StepResult",
    "InjectSystemPromptStep",
    "ContextWindowCheckStep",
    "GarbageCompressionStep",
    "AssembleFinalPromptStep",
]
