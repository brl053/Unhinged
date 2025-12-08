"""Built-in pipeline steps for prompt assembly.

@llm-type library.graph.pipeline_steps
@llm-does concrete implementations of prompt pipeline steps
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .prompt_pipeline import PipelineStep, PromptPayload, StepOutput, StepResult

if TYPE_CHECKING:
    from .context import SessionContext


class InjectSystemPromptStep(PipelineStep):
    """Inject the system prompt (philosophy, brand, rules).

    This is the "rules of conversation" - how we want the LLM to behave.
    """

    def __init__(self, system_prompt: str) -> None:
        self._system_prompt = system_prompt

    @property
    def step_id(self) -> str:
        return "inject_system_prompt"

    def execute(self, payload: PromptPayload, session: SessionContext | None = None) -> StepOutput:
        payload.system_prompt = self._system_prompt
        return StepOutput(
            result=StepResult.CONTINUE,
            metrics={"chars": len(self._system_prompt)},
        )


class ContextWindowCheckStep(PipelineStep):
    """Check context window usage and emit metrics."""

    def __init__(self, warn_threshold: float = 0.8, abort_threshold: float = 0.95) -> None:
        self._warn_threshold = warn_threshold
        self._abort_threshold = abort_threshold

    @property
    def step_id(self) -> str:
        return "context_window_check"

    def execute(self, payload: PromptPayload, session: SessionContext | None = None) -> StepOutput:
        payload.estimate_tokens()
        usage = payload.context_usage_ratio()

        metrics = {
            "token_estimate": payload.token_count_estimate,
            "context_window": payload.context_window_size,
            "usage_ratio": round(usage, 4),
        }

        if usage >= self._abort_threshold:
            return StepOutput(
                result=StepResult.ABORT,
                reason=f"context window {usage:.1%} full, exceeds abort threshold",
                metrics=metrics,
            )
        elif usage >= self._warn_threshold:
            return StepOutput(
                result=StepResult.CONTINUE,
                reason=f"context window {usage:.1%} full, approaching limit",
                metrics=metrics,
            )

        return StepOutput(result=StepResult.CONTINUE, metrics=metrics)


class GarbageCompressionStep(PipelineStep):
    """Compress old message history to preserve context window.

    Garbage compression: ask LLM to summarize old messages while:
    - Preserving axioms (core truths/rules)
    - Preserving recent concrete examples
    - Dropping old verbose examples

    Treats context like an LRU cache - old stuff gets compressed.
    """

    def __init__(
        self,
        compress_threshold: float = 0.7,
        keep_recent_n: int = 10,
        compression_prompt: str | None = None,
    ) -> None:
        self._compress_threshold = compress_threshold
        self._keep_recent_n = keep_recent_n
        self._compression_prompt = compression_prompt or self._default_compression_prompt()

    @staticmethod
    def _default_compression_prompt() -> str:
        return """Compress the following conversation history.
Preserve:
- Core axioms and rules established
- Key decisions made
- Recent concrete examples (last 5)

Remove:
- Verbose explanations already understood
- Redundant examples
- Pleasantries and filler

Return a compressed summary that retains semantic meaning."""

    @property
    def step_id(self) -> str:
        return "garbage_compression"

    def execute(self, payload: PromptPayload, session: SessionContext | None = None) -> StepOutput:
        payload.estimate_tokens()
        usage = payload.context_usage_ratio()

        if usage < self._compress_threshold:
            return StepOutput(
                result=StepResult.CONTINUE,
                metrics={"skipped": True, "reason": "below threshold"},
            )

        if len(payload.message_history) <= self._keep_recent_n:
            return StepOutput(
                result=StepResult.CONTINUE,
                metrics={"skipped": True, "reason": "not enough history"},
            )

        # Split history: old (to compress) and recent (to keep)
        old_messages = payload.message_history[: -self._keep_recent_n]
        recent_messages = payload.message_history[-self._keep_recent_n :]

        # TODO: Actually call LLM for compression
        # For now, just truncate old messages as placeholder
        old_summary = f"[compressed {len(old_messages)} messages]"

        # Rebuild history with compression marker + recent
        payload.message_history = [
            {"role": "system", "content": old_summary},
            *recent_messages,
        ]
        payload.compression_count += 1

        return StepOutput(
            result=StepResult.CONTINUE,
            metrics={
                "compressed_count": len(old_messages),
                "kept_count": len(recent_messages),
                "total_compressions": payload.compression_count,
            },
        )


class AssembleFinalPromptStep(PipelineStep):
    """Final step: assemble all pieces into the final prompt string."""

    @property
    def step_id(self) -> str:
        return "assemble_final"

    def execute(self, payload: PromptPayload, session: SessionContext | None = None) -> StepOutput:
        parts = []

        if payload.system_prompt:
            parts.append(f"[system]\n{payload.system_prompt}\n[/system]")

        for block in payload.context_blocks:
            parts.append(f"[context]\n{block}\n[/context]")

        for msg in payload.message_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            parts.append(f"[{role}]\n{content}\n[/{role}]")

        parts.append(f"[user]\n{payload.user_input}\n[/user]")

        payload.final_prompt = "\n\n".join(parts)
        payload.estimate_tokens()

        return StepOutput(
            result=StepResult.CONTINUE,
            metrics={
                "final_tokens": payload.token_count_estimate,
                "final_chars": len(payload.final_prompt),
            },
        )
