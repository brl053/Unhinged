"""Prompt Assembly Pipeline.

@llm-type library.graph.prompt
@llm-does pre-flight prompt building as ordered chain of steps

The prompt pipeline is a linked list of steps that transform raw user input
into the final LLM payload. Each step can:
- Add context (system prompt, history, examples)
- Compress/summarize old context (garbage compression)
- Track context window usage
- Inject philosophy/brand rules

The pipeline runs during PRE-FLIGHT before execution.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .context import SessionContext


class StepResult(Enum):
    """Result of a pipeline step."""

    CONTINUE = "continue"  # proceed to next step
    ABORT = "abort"  # halt pipeline
    SKIP = "skip"  # skip remaining steps, use current payload


@dataclass
class PromptPayload:
    """The evolving prompt payload as it flows through the pipeline.

    This is the accumulator - each step reads and writes to it.
    """

    # The raw user input
    user_input: str = ""

    # System prompt (philosophy, rules, brand)
    system_prompt: str = ""

    # Message history (may be compressed)
    message_history: list[dict[str, str]] = field(default_factory=list)

    # Injected context (RAG results, tool outputs, etc)
    context_blocks: list[str] = field(default_factory=list)

    # Final assembled prompt (set by final step)
    final_prompt: str = ""

    # Metrics
    token_count_estimate: int = 0
    context_window_size: int = 128000  # default, can be configured
    compression_count: int = 0

    # Audit trail
    steps_executed: list[str] = field(default_factory=list)
    step_metrics: dict[str, dict[str, Any]] = field(default_factory=dict)

    def context_usage_ratio(self) -> float:
        """How much of the context window is used (0.0 to 1.0)."""
        if self.context_window_size == 0:
            return 0.0
        return self.token_count_estimate / self.context_window_size

    def estimate_tokens(self) -> int:
        """Rough token estimate (chars / 4)."""
        total_chars = len(self.system_prompt) + len(self.user_input)
        for msg in self.message_history:
            total_chars += len(msg.get("content", ""))
        for block in self.context_blocks:
            total_chars += len(block)
        self.token_count_estimate = total_chars // 4
        return self.token_count_estimate


@dataclass
class StepOutput:
    """Output from a pipeline step."""

    result: StepResult
    reason: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)


class PipelineStep(ABC):
    """Abstract base for a prompt pipeline step.

    Steps form a linked list. Each step:
    1. Reads the current PromptPayload
    2. Mutates it (add context, compress, etc)
    3. Returns StepOutput indicating next action
    """

    @property
    @abstractmethod
    def step_id(self) -> str:
        """Unique identifier for this step."""

    @abstractmethod
    def execute(self, payload: PromptPayload, session: SessionContext | None = None) -> StepOutput:
        """Execute the step, mutating payload in place."""


class PromptPipeline:
    """Ordered chain of steps that build the final prompt.

    This is the pre-flight prompt assembly. Steps run in order.
    The pipeline can be configured per-session or globally.
    """

    def __init__(self, context_window_size: int = 128000) -> None:
        self._steps: list[PipelineStep] = []
        self._context_window_size = context_window_size

    def add_step(self, step: PipelineStep) -> PromptPipeline:
        """Add a step to the end of the pipeline. Returns self for chaining."""
        self._steps.append(step)
        return self

    def insert_step(self, index: int, step: PipelineStep) -> PromptPipeline:
        """Insert a step at a specific position."""
        self._steps.insert(index, step)
        return self

    def run(
        self,
        user_input: str,
        session: SessionContext | None = None,
        initial_history: list[dict[str, str]] | None = None,
    ) -> tuple[PromptPayload, list[StepOutput]]:
        """Run the pipeline and return the final payload.

        Returns:
            (final_payload, list_of_step_outputs)
        """
        payload = PromptPayload(
            user_input=user_input,
            message_history=initial_history or [],
            context_window_size=self._context_window_size,
        )

        outputs: list[StepOutput] = []

        for step in self._steps:
            # Emit CDC event if session available
            if session:
                from .context import CDCEventType

                session.emit(CDCEventType.PIPELINE_STEP, {"step": step.step_id, "action": "start"})

            output = step.execute(payload, session)
            outputs.append(output)
            payload.steps_executed.append(step.step_id)
            payload.step_metrics[step.step_id] = output.metrics

            # Update token estimate after each step
            payload.estimate_tokens()

            if output.result == StepResult.ABORT or output.result == StepResult.SKIP:
                break

        return payload, outputs
