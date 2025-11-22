#!/usr/bin/env python3
"""Node executors for graph-service using Python services (no gRPC).

@llm-type service.executor
@llm-does execute NodeType-based nodes via local Python service clients
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from events import create_service_logger

from libs.python.models.graph.schema import Node, NodeType
from libs.services.text_generation_service import TextGenerationService
from libs.services.transcription_service import TranscriptionService
from libs.services.tts_service import TTSService

events = create_service_logger("node-executors", "2.0.0 (python-services)")


class NodeExecutor(ABC):
    """Abstract base class for node executors."""

    @abstractmethod
    async def execute(self, node: Node, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the node and return output data."""
        ...


class SpeechToTextExecutor(NodeExecutor):
    """Executor for speech-to-text nodes using TranscriptionService."""

    def __init__(self) -> None:
        self.service = TranscriptionService()

    async def execute(self, node: Node, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute speech-to-text conversion.

        Expected config:
        - model_size: Whisper model size (optional)

        Expected input_data:
        - audio_path: path to an audio file, or
        - audio_bytes: raw audio bytes
        """

        try:
            audio_path = input_data.get("audio_path")
            audio_bytes = input_data.get("audio_bytes")

            if audio_path is not None:
                transcript = self.service.transcribe_audio(audio_path)
            elif audio_bytes is not None:
                transcript = self.service.transcribe_audio_data(audio_bytes)
            else:
                raise ValueError("SpeechToTextExecutor requires 'audio_path' or 'audio_bytes' in input_data")

            events.info(
                "STT node executed",
                {
                    "node_id": node.id,
                    "transcript_length": len(transcript),
                },
            )

            return {
                "transcript": transcript,
            }

        except Exception as exc:  # pragma: no cover - integration oriented
            events.error("STT node execution failed", exception=exc, metadata={"node_id": node.id})
            raise


class TextToSpeechExecutor(NodeExecutor):
    """Executor for text-to-speech nodes using TTSService."""

    def __init__(self) -> None:
        self.service = TTSService()

    async def execute(self, node: Node, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute text-to-speech conversion.

        Expected config keys (optional): voice, speed, emotion.
        Expected input_data: {"text": str}
        """

        config = dict(node.config)

        try:
            text = str(input_data.get("text", ""))
            if not text:
                raise ValueError("TextToSpeechExecutor requires 'text' in input_data")

            voice = config.get("voice", "nova")
            speed = float(config.get("speed", 1.0))
            emotion = config.get("emotion", "neutral")

            result = self.service.generate_voiceover(text=text, voice=voice, speed=speed, emotion=emotion)

            events.info(
                "TTS node executed",
                {
                    "node_id": node.id,
                    "text_length": len(text),
                    "audio_path": result.get("audio_path"),
                },
            )

            return result

        except Exception as exc:  # pragma: no cover - integration oriented
            events.error("TTS node execution failed", exception=exc, metadata={"node_id": node.id})
            raise


class LLMChatExecutor(NodeExecutor):
    """Executor for LLM chat nodes using TextGenerationService."""

    def __init__(self) -> None:
        # Default model/provider are configured in the service itself
        self.service = TextGenerationService()

    async def execute(self, node: Node, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute LLM chat completion.

        Expected input_data keys (first non-empty is used): text, transcript.
        """

        config = dict(node.config)

        try:
            prompt = str(input_data.get("text") or input_data.get("transcript") or "")
            if not prompt:
                raise ValueError("LLMChatExecutor requires 'text' or 'transcript' in input_data")

            max_tokens = int(config.get("max_tokens", 512))
            temperature = float(config.get("temperature", 0.7))

            response_text = self.service.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            events.info(
                "LLM chat node executed",
                {
                    "node_id": node.id,
                    "input_length": len(prompt),
                    "response_length": len(response_text),
                },
            )

            return {
                "response_text": response_text,
            }

        except Exception as exc:  # pragma: no cover - integration oriented
            events.error(
                "LLM chat node execution failed",
                exception=exc,
                metadata={"node_id": node.id},
            )
            raise


class DataTransformExecutor(NodeExecutor):
    """Executor for data transformation nodes."""

    async def execute(self, node: Node, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute data transformation based on simple config-driven rules."""
        try:
            config = dict(node.config)
            transform_type = config.get("transform_type", "passthrough")

            if transform_type == "passthrough":
                return input_data
            if transform_type == "extract_field":
                field_name = config.get("field_name", "text")
                return {field_name: input_data.get(field_name, "")}
            if transform_type == "rename_field":
                old_name = config.get("old_name", "input")
                new_name = config.get("new_name", "output")
                return {new_name: input_data.get(old_name, "")}

            # Fallback: no-op
            return input_data

        except Exception as exc:  # pragma: no cover - config/usage errors
            events.error(
                "Data transform node execution failed",
                exception=exc,
                metadata={"node_id": node.id},
            )
            raise


class CustomServiceExecutor(NodeExecutor):
    """Placeholder executor for custom service nodes.

    Currently this is a stub that simply echoes input and config metadata; it is
    left as an extension point for bespoke integrations.
    """

    async def execute(self, node: Node, input_data: dict[str, Any]) -> dict[str, Any]:
        config = dict(node.config)
        service_name = config.get("service_name", "custom")
        operation = config.get("operation", "process")

        events.info(
            "Custom service node executed (stub)",
            {
                "node_id": node.id,
                "service_name": service_name,
                "operation": operation,
            },
        )

        return {
            "service_name": service_name,
            "operation": operation,
            "input": input_data,
        }


class CommandOrchestrationExecutor(NodeExecutor):
    """Executor for command orchestration nodes.

    Currently this delegates to the libs.python.command_orchestration helpers.
    """

    async def execute(self, node: Node, input_data: dict[str, Any]) -> dict[str, Any]:
        from libs.python.command_orchestration import (
            CommandExecutor,
            DAGBuilder,
            ManPageIndexer,
            SemanticSearchEngine,
        )

        config = dict(node.config)
        prompt = config.get("prompt") or input_data.get("prompt") or ""

        try:
            # Step 1: Index man pages
            indexer = ManPageIndexer()
            entries = indexer.build_index()

            # Step 2: Search for relevant commands
            search_engine = SemanticSearchEngine(entries)
            search_results = search_engine.search(prompt, limit=5)

            # Step 3: Build DAG from commands
            commands = [r.command for r in search_results]
            dag_builder = DAGBuilder()
            dag = dag_builder.build_from_commands(commands)

            # Step 4: Execute DAG
            executor = CommandExecutor()
            execution_result = await executor.execute_dag(dag)

            events.info(
                "Command orchestration executed",
                {
                    "node_id": node.id,
                    "prompt": prompt,
                    "commands": len(commands),
                    "success": execution_result.success,
                },
            )

            return {
                "prompt": prompt,
                "commands": commands,
                "search_results": [
                    {
                        "command": r.command,
                        "similarity": r.similarity,
                        "reasoning": r.reasoning,
                    }
                    for r in search_results
                ],
                "execution_success": execution_result.success,
                "execution_results": {
                    cmd_node_id: {
                        "returncode": result.returncode,
                        "stdout": result.stdout[:500],
                        "stderr": result.stderr[:500],
                    }
                    for cmd_node_id, result in execution_result.results.items()
                },
            }

        except Exception as exc:  # pragma: no cover - shell/integration heavy
            events.error(
                "Command orchestration execution failed",
                exception=exc,
                metadata={"node_id": node.id},
            )
            raise


class NodeExecutorFactory:
    """Factory for creating node executors bound to NodeType values."""

    def __init__(self) -> None:
        self.executors: dict[NodeType, NodeExecutor] = {
            NodeType.SPEECH_TO_TEXT: SpeechToTextExecutor(),
            NodeType.TEXT_TO_SPEECH: TextToSpeechExecutor(),
            NodeType.LLM_CHAT: LLMChatExecutor(),
            NodeType.LLM_COMPLETION: LLMChatExecutor(),  # Reuse chat executor
            NodeType.DATA_TRANSFORM: DataTransformExecutor(),
            NodeType.CUSTOM_SERVICE: CustomServiceExecutor(),
        }

        events.info(
            "Node executor factory initialized",
            {"supported_types": [t.name for t in self.executors]},
        )

    def get_executor(self, node_type: NodeType) -> NodeExecutor:
        """Get executor for node type."""
        if node_type not in self.executors:
            raise ValueError(f"Unsupported node type: {node_type}")

        return self.executors[node_type]
