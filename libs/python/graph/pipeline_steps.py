"""Built-in pipeline steps for prompt assembly.

@llm-type library.graph.pipeline_steps
@llm-does concrete implementations of prompt pipeline steps
"""

from __future__ import annotations

import os
import platform
from typing import TYPE_CHECKING, Any

from .context import CDCEventType
from .prompt_pipeline import PipelineStep, PromptPayload, StepOutput, StepResult

if TYPE_CHECKING:
    from .context import SessionContext


# =============================================================================
# STATIC CAPABILITIES - What the system can do (not session-dependent)
# =============================================================================

SYSTEM_CAPABILITIES = """## System Capabilities

### Linux/GNU Commands
ls, cat, grep, find, sed, awk, head, tail, wc, sort, uniq, cut, tr, xargs,
chmod, chown, mkdir, rm, cp, mv, ln, touch, echo, printf, pwd, which, file,
stat, du, df, ps, top, htop, kill, pkill, pgrep, lsof, netstat, ss, ip, ping,
curl, wget, ssh, scp, rsync, tar, gzip, gunzip, zip, unzip, diff, patch,
git, docker, docker-compose, make, arecord, aplay, ffmpeg, nvidia-smi

### Unhinged CLI
unhinged --help, unhinged dev, unhinged transcribe mic, unhinged transcribe file,
unhinged tui, unhinged generate text

### Python
python3, pip, pytest, ruff, mypy
All libs under libs/python/* are importable
"""


def get_system_info() -> str:
    """Get current system information."""
    info = [
        f"OS: {platform.system()} {platform.release()}",
        f"Distro: {_get_distro()}",
        f"Shell: {os.environ.get('SHELL', '/bin/bash')}",
        f"CWD: {os.getcwd()}",
        f"Python: {platform.python_version()}",
    ]
    return "\n".join(info)


def _get_distro() -> str:
    """Get Linux distro name."""
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return "Unknown"


# =============================================================================
# CapabilitiesStep - Inject static system capabilities
# =============================================================================


class CapabilitiesStep(PipelineStep):
    """Inject static system capabilities into prompt.

    Capabilities are STATIC - Linux commands, CLI commands, Python libs.
    Not session-dependent. Just a constant string.
    """

    @property
    def step_id(self) -> str:
        return "capabilities"

    def execute(self, payload: PromptPayload, session: SessionContext | None = None) -> StepOutput:
        payload.context_blocks.append(SYSTEM_CAPABILITIES)
        return StepOutput(
            result=StepResult.CONTINUE,
            metrics={"chars": len(SYSTEM_CAPABILITIES)},
        )


# =============================================================================
# SystemInfoStep - Inject current system info (OS, distro, shell, cwd)
# =============================================================================


class SystemInfoStep(PipelineStep):
    """Inject current system information into prompt.

    System info: OS, distro, shell, cwd, Python version.
    """

    @property
    def step_id(self) -> str:
        return "system_info"

    def execute(self, payload: PromptPayload, session: SessionContext | None = None) -> StepOutput:
        info = get_system_info()
        block = f"## System Info\n{info}"
        payload.context_blocks.append(block)
        return StepOutput(
            result=StepResult.CONTINUE,
            metrics={"info": info},
        )


# =============================================================================
# SessionHydrationStep - Interpolate session keys into prompt
# =============================================================================


class SessionHydrationStep(PipelineStep):
    """Hydrate prompt with session context keys.

    Hydration = interpolating {{session.key}} from session.data().
    This is the ONLY meaning of hydration.
    """

    @property
    def step_id(self) -> str:
        return "session_hydration"

    def execute(self, payload: PromptPayload, session: SessionContext | None = None) -> StepOutput:
        if session is None:
            return StepOutput(
                result=StepResult.CONTINUE,
                metrics={"skipped": True, "reason": "no session"},
            )

        # Get all session keys
        data = session.data()
        keys = list(data.keys())

        if not keys:
            return StepOutput(
                result=StepResult.CONTINUE,
                metrics={"key_count": 0},
            )

        # Format session context for prompt
        lines = ["## Session Context", f"Keys: {', '.join(keys)}"]
        for key in keys[:10]:  # Limit to avoid bloat
            value = data[key]
            if isinstance(value, str) and len(value) > 200:
                value = value[:200] + "..."
            lines.append(f"- {key}: {value}")

        block = "\n".join(lines)
        payload.context_blocks.append(block)

        return StepOutput(
            result=StepResult.CONTINUE,
            metrics={"key_count": len(keys), "keys": keys[:10]},
        )


# =============================================================================
# IdentityHydrationStep - Inject deployment-time identity
# =============================================================================


class IdentityHydrationStep(PipelineStep):
    """Inject deployment-time identity into system prompt.

    Identity answers: WHO AM I? What role, codebase, capabilities?
    This is pre-session configuration, not user-specific.
    """

    def __init__(
        self,
        identity_config: dict[str, Any] | None = None,
        config_path: str | None = None,
    ) -> None:
        self._identity_config = identity_config
        self._config_path = config_path

    @property
    def step_id(self) -> str:
        return "identity_hydration"

    def _load_config(self) -> dict[str, Any] | None:
        """Load identity config from dict or YAML file."""
        if self._identity_config:
            return self._identity_config

        if self._config_path:
            from pathlib import Path

            import yaml

            path = Path(self._config_path)
            if not path.exists():
                return None
            with path.open() as f:
                loaded: dict[str, Any] = yaml.safe_load(f)
                return loaded

        return None

    def _format_identity_block(self, config: dict[str, Any]) -> str:
        """Format identity config into structured block."""
        lines = ["[identity]"]

        if "role" in config:
            lines.append(f"Role: {config['role']}")

        if "codebase" in config:
            lines.append(f"Codebase: {config['codebase']}")

        if "repo_root" in config:
            lines.append(f"Repository: {config['repo_root']}")

        if "capabilities" in config:
            caps = ", ".join(config["capabilities"])
            lines.append(f"Capabilities: {caps}")

        lines.append("[/identity]")
        return "\n".join(lines)

    def execute(self, payload: PromptPayload, session: SessionContext | None = None) -> StepOutput:
        config = self._load_config()

        if not config:
            return StepOutput(
                result=StepResult.ABORT,
                reason="No identity config provided - cannot hydrate identity",
                metrics={},
            )

        identity_block = self._format_identity_block(config)

        # Prepend identity to existing system prompt (don't replace)
        if payload.system_prompt:
            payload.system_prompt = f"{identity_block}\n\n{payload.system_prompt}"
        else:
            payload.system_prompt = identity_block

        # Emit CDC event if session provided
        if session:
            session.emit(CDCEventType.IDENTITY_HYDRATED, {"config": config})

        return StepOutput(
            result=StepResult.CONTINUE,
            metrics={
                "role": config.get("role", ""),
                "codebase": config.get("codebase", ""),
                "capabilities": config.get("capabilities", []),
            },
        )


# =============================================================================
# ECalibrationStep - Calibrate tone to match user style
# =============================================================================

# Profanity word list for rule-based detection
_PROFANITY_WORDS = frozenset(
    [
        "fuck",
        "fucking",
        "fucked",
        "shit",
        "damn",
        "hell",
        "ass",
        "bitch",
        "crap",
        "piss",
        "bastard",
        "dammit",
        "goddamn",
        "bullshit",
        "asshole",
    ]
)

# Informal markers
_INFORMAL_MARKERS = frozenset(
    [
        "yo",
        "lol",
        "lmao",
        "gonna",
        "wanna",
        "gotta",
        "kinda",
        "sorta",
        "yeah",
        "nah",
        "dude",
        "bro",
        "bruh",
        "tbh",
        "idk",
        "omg",
        "wtf",
    ]
)

# Formal markers
_FORMAL_MARKERS = frozenset(
    [
        "please",
        "kindly",
        "appreciate",
        "assistance",
        "regarding",
        "therefore",
        "however",
        "furthermore",
        "consequently",
        "nevertheless",
        "accordingly",
    ]
)


class ECalibrationStep(PipelineStep):
    """Calibrate LLM tone to match user communication style.

    E-Calibration: synchronize profanity, formality, pace to signal no hostility.
    Rule-based v1 (no LLM call).
    """

    def __init__(self) -> None:
        pass

    @property
    def step_id(self) -> str:
        return "e_calibration"

    def _detect_profanity_level(self, text: str) -> float:
        """Detect profanity level from 0.0 (clean) to 1.0 (heavy)."""
        words = text.lower().split()
        if not words:
            return 0.0
        profane_count = sum(1 for w in words if w.strip(".,!?") in _PROFANITY_WORDS)
        # Normalize: 2+ profane words = high level
        return min(1.0, profane_count / 2.0)

    def _detect_formality(self, text: str) -> float:
        """Detect formality level from 0.0 (casual) to 1.0 (formal)."""
        words = text.lower().split()
        if not words:
            return 0.5

        informal_count = sum(1 for w in words if w.strip(".,!?") in _INFORMAL_MARKERS)
        formal_count = sum(1 for w in words if w.strip(".,!?") in _FORMAL_MARKERS)

        # Base formality on marker ratio
        if informal_count > formal_count:
            return max(0.0, 0.5 - (informal_count * 0.15))
        elif formal_count > informal_count:
            return min(1.0, 0.5 + (formal_count * 0.15))
        return 0.5

    def _detect_pace(self, text: str) -> float:
        """Detect communication pace from 0.0 (terse) to 1.0 (verbose)."""
        words = text.split()
        # Short messages = terse, long = verbose
        if len(words) < 5:
            return 0.2
        elif len(words) > 20:
            return 0.8
        return 0.5

    def _generate_tone_guidance(self, profile: dict[str, Any]) -> str:
        """Generate tone guidance for system prompt."""
        profanity = profile.get("profanity_level", 0)
        formality = profile.get("formality", 0.5)

        guidance_parts = ["[tone-calibration]"]

        if profanity > 0.5:
            guidance_parts.append("User uses casual/profane language. Mirror relaxed tone.")
        elif formality > 0.7:
            guidance_parts.append("User is formal. Maintain professional tone.")
        else:
            guidance_parts.append("User is casual. Match conversational style.")

        guidance_parts.append("[/tone-calibration]")
        return "\n".join(guidance_parts)

    def execute(self, payload: PromptPayload, session: SessionContext | None = None) -> StepOutput:
        text = payload.user_input

        # Detect current message signals
        profanity = self._detect_profanity_level(text)
        formality = self._detect_formality(text)
        pace = self._detect_pace(text)

        # Get existing calibration from session (for adaptive updates)
        existing: dict[str, Any] = {}
        message_count = 1
        if session:
            existing = session.get("ecalibration") or {}
            message_count = existing.get("message_count", 0) + 1

            # Blend with existing calibration (exponential moving average)
            alpha = 0.3  # Weight for new observation
            if existing:
                profanity = alpha * profanity + (1 - alpha) * existing.get("profanity_level", 0)
                formality = alpha * formality + (1 - alpha) * existing.get("formality", 0.5)
                pace = alpha * pace + (1 - alpha) * existing.get("pace", 0.5)

        profile = {
            "profanity_level": profanity,
            "formality": formality,
            "pace": pace,
            "message_count": message_count,
        }

        # Store in session and emit CDC event
        if session:
            session.set("ecalibration", profile)
            session.emit(CDCEventType.ECALIBRATION_UPDATED, profile)

        # Add tone guidance to context
        guidance = self._generate_tone_guidance(profile)
        payload.context_blocks.append(guidance)

        return StepOutput(
            result=StepResult.CONTINUE,
            metrics=profile,
        )


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
