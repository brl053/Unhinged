"""Reasoning Engine for command orchestration.

@llm-type library.command_orchestration.reasoning_engine
@llm-does provide LLM-backed reasoning for command selection, DAG edges, and result interpretation
Uses local Ollama service (on-premise, no external API calls)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, cast

from libs.services.text_generation_service import TextGenerationService

logger = logging.getLogger(__name__)


@dataclass
class ExecutionTrace:
    """Complete reasoning trace for command orchestration pipeline."""

    query: str
    intent_reasoning: str
    command_selection_reasoning: dict[str, str]
    dag_edge_reasoning: dict[tuple[str, str], str]
    execution_result_reasoning: dict[str, str]
    summary: str


class ReasoningEngine:
    """Generate LLM-backed reasoning for command orchestration.

    Provides reasoning at three critical points:
    1. Command Selection: Why specific commands were chosen
    2. DAG Edge Reasoning: How data flows through pipeline
    3. Result Interpretation: What execution results mean

    Uses local Ollama service (on-premise, no external API calls).
    Defaults to Mistral model for reasoning.
    """

    def __init__(
        self,
        model: str = "mistral",
        provider: str = "ollama",
    ):
        """Initialize reasoning engine.

        Parameters
        ----------
        model : str
            LLM model to use (default: mistral for local Ollama).
        provider : str
            LLM provider (default: ollama for on-premise deployment).
        """
        self.model = model
        self.provider = provider
        self._service: TextGenerationService | None = None

    def _get_command_selection_prompt(self) -> str:
        """System prompt for command selection reasoning."""
        return """You are an expert at explaining why specific Linux commands are relevant to a user's problem.

Given a user query and a list of selected commands, generate a brief explanation for each command
explaining why it was chosen and what information it provides.

Consider:
- How the command relates to the user's problem
- What information the command provides
- How it contributes to solving the problem

Format: Return ONLY valid JSON with no markdown or explanation:
{
  "command_name": "Brief one-sentence explanation of why this command was chosen"
}

Example:
{
  "pactl": "Lists audio sinks and their volume levels to diagnose system audio output",
  "amixer": "Shows ALSA mixer controls for additional volume and mute diagnostics"
}
"""

    def _get_dag_edge_prompt(self) -> str:
        """System prompt for DAG edge reasoning."""
        return """You are an expert at explaining data flow in command pipelines.

Given two commands connected by a pipe (stdout → stdin), explain why command B follows command A,
what data is being passed, and what transformation occurs.

Format: Return ONLY valid JSON with no markdown:
{
  "reasoning": "One sentence explaining the data flow relationship"
}

Example for 'pactl list sinks | grep -i volume':
{
  "reasoning": "grep filters pactl output to show only lines containing 'volume' for focused diagnostics"
}
"""

    def _get_result_interpretation_prompt(self) -> str:
        """System prompt for result interpretation."""
        return """You are an expert at interpreting Linux command output.

Given a command, its exit code, stdout, and stderr, generate a brief interpretation of what
the result means and what it tells us about the system state.

Format: Return ONLY valid JSON:
{
  "interpretation": "One sentence summarizing the result's significance"
}

Example:
{
  "interpretation": "PipeWire is running as the audio server, handling audio routing and mixing"
}
"""

    def _load_service(self) -> TextGenerationService:
        """Lazy-load TextGenerationService for on-premise LLM access."""
        if self._service is None:
            self._service = TextGenerationService(model=self.model, provider=self.provider)
        return self._service

    async def _call_llm(self, system_prompt: str, user_message: str) -> str:
        """Call LLM with system prompt and return response text.

        Uses local TextGenerationService (Ollama) for on-premise deployment.
        No external API calls.
        Runs in executor to avoid blocking async event loop.
        """
        import asyncio

        service = self._load_service()

        # Combine system prompt and user message for Ollama
        full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nResponse:"

        try:
            # Run blocking LLM call in executor to avoid blocking event loop
            loop = asyncio.get_event_loop()
            response_text = await loop.run_in_executor(
                None,
                lambda: service.generate(prompt=full_prompt, max_tokens=512),
            )
            return response_text
        except Exception as exc:
            logger.error(f"LLM call failed: {exc}")
            raise

    async def reason_command_selection(
        self,
        query: str,
        commands: list[str],
        similarity_scores: list[float] | None = None,
    ) -> dict[str, str]:
        """Generate reasoning for why commands were selected.

        Parameters
        ----------
        query : str
            User's natural language query
        commands : List[str]
            List of selected commands
        similarity_scores : Optional[List[float]]
            Optional similarity scores for each command

        Returns
        -------
        Dict[str, str]
            Mapping of command name to reasoning text
        """
        try:
            commands_str = "\n".join(f"- {cmd}" for cmd in commands)
            user_message = f"""User query: {query}

Selected commands:
{commands_str}

Generate reasoning for why each command was selected."""

            system_prompt = self._get_command_selection_prompt()
            response_text = await self._call_llm(system_prompt, user_message)
            result = json.loads(response_text)

            if not isinstance(result, dict):
                raise ValueError(f"Expected dict, got {type(result)}")

            return result

        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse command selection reasoning: {exc}")
            return dict.fromkeys(commands, "Command selected for diagnostics")
        except Exception as exc:
            logger.error(f"Command selection reasoning failed: {exc}")
            return dict.fromkeys(commands, "Command selected for diagnostics")

    async def reason_dag_edge(
        self,
        from_command: str,
        to_command: str,
        data_flow: str = "stdout → stdin",
    ) -> str:
        """Generate reasoning for DAG edge (data flow).

        Parameters
        ----------
        from_command : str
            Source command
        to_command : str
            Destination command
        data_flow : str
            Description of data flow (default: "stdout → stdin")

        Returns
        -------
        str
            Reasoning for the edge
        """
        try:
            user_message = f"""From command: {from_command}
To command: {to_command}
Data flow: {data_flow}

Explain why {to_command} follows {from_command} and what transformation occurs."""

            system_prompt = self._get_dag_edge_prompt()
            response_text = await self._call_llm(system_prompt, user_message)
            result = json.loads(response_text)

            reasoning = result.get("reasoning", "Data flows from one command to the next")
            return cast(str, reasoning)

        except Exception as exc:
            logger.error(f"DAG edge reasoning failed: {exc}")
            return f"{to_command} processes output from {from_command}"

    async def reason_execution_result(
        self,
        command: str,
        exit_code: int,
        stdout: str,
        stderr: str,
    ) -> str:
        """Generate interpretation of execution result.

        Parameters
        ----------
        command : str
            Command that was executed
        exit_code : int
            Exit code from command
        stdout : str
            Standard output
        stderr : str
            Standard error

        Returns
        -------
        str
            Interpretation of the result
        """
        try:
            output_preview = stdout[:500] if stdout else "(no output)"
            user_message = f"""Command: {command}
Exit code: {exit_code}
Output: {output_preview}

Interpret what this result tells us about the system state."""

            system_prompt = self._get_result_interpretation_prompt()
            response_text = await self._call_llm(system_prompt, user_message)
            result = json.loads(response_text)

            interpretation = result.get("interpretation", "Command executed successfully")
            return cast(str, interpretation)

        except Exception as exc:
            logger.error(f"Result interpretation failed: {exc}")
            status = "succeeded" if exit_code == 0 else "failed"
            return f"Command {status} with exit code {exit_code}"

    async def reason_remediation(
        self,
        query: str,
        diagnostic_output: str,
    ) -> dict[str, Any]:
        """Generate YAML-structured remediation commands.

        @llm-yaml-reasoning: Generate remediation commands in YAML format

        Parameters
        ----------
        query : str
            Original user query
        diagnostic_output : str
            Combined diagnostic output from all executed nodes

        Returns
        -------
        Dict[str, Any]
            Parsed remediation data with diagnosis and remediation_commands
        """

        system_prompt = """Output ONLY valid YAML with this exact structure:

diagnosis: "Brief problem explanation with specific device info"
remediation_commands:
  - command: "exact shell command"
    description: "One sentence what this does"
    read_only: false
    confidence: 0.95

CRITICAL:
- Use specific device identifiers (e.g., 'amixer -c 1' for card 1)
- Extract card numbers from diagnostic output (look for 'card 1', 'Bus 001 Device 004')
- Only suggest safe, non-destructive commands
- Output ONLY the YAML. No markdown. No explanations."""

        user_message = f"""Query: {query}

Diagnostic output:
{diagnostic_output}

Generate remediation YAML:"""

        try:
            response_text = await self._call_llm(system_prompt, user_message)
            return self._parse_and_validate_yaml(response_text)
        except Exception as exc:
            logger.error(f"Remediation reasoning failed: {exc}")
            return {"diagnosis": "", "remediation_commands": []}

    def _parse_and_validate_yaml(self, text: str) -> dict[str, Any]:
        """Parse YAML response and validate against schema.

        Parameters
        ----------
        text : str
            Raw response text from LLM

        Returns
        -------
        Dict[str, Any]
            Validated remediation data
        """
        import re

        import yaml

        # Extract YAML block (remove markdown if present)
        yaml_text = re.sub(r"```ya?ml\s*|\s*```", "", text)

        # Find YAML content
        match = re.search(r"(diagnosis:.*?)(?=\n[A-Z]|\Z)", yaml_text, re.DOTALL)
        if match:
            yaml_text = match.group(1)

        # Parse YAML
        try:
            data = yaml.safe_load(yaml_text)
        except yaml.YAMLError as e:
            logger.error(f"YAML parse error: {e}")
            return {"diagnosis": "", "remediation_commands": []}

        # Validate structure
        if not isinstance(data, dict):
            return {"diagnosis": "", "remediation_commands": []}

        if not isinstance(data.get("remediation_commands"), list):
            data["remediation_commands"] = []

        # Ensure required fields
        for cmd in data["remediation_commands"]:
            if not isinstance(cmd, dict):
                continue
            cmd.setdefault("confidence", 0.85)
            cmd.setdefault("read_only", False)

        data.setdefault("diagnosis", "")

        return data
