#!/usr/bin/env python3
"""
@llm-type service.executor
@llm-does Node executors for different AI service types
"""

import json
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import grpc

# Add generated proto clients to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "generated" / "python" / "clients"))

try:
    from unhinged_proto_clients import (
        audio_pb2,
        audio_pb2_grpc,
        chat_pb2,
        chat_pb2_grpc,
        graph_service_pb2,
        llm_pb2,
        llm_pb2_grpc,
    )
except ImportError as e:
    print(f"❌ Proto clients not found: {e}")
    print("Run 'make generate' to generate proto clients")

from events import create_service_logger

# Initialize event logger
events = create_service_logger("node-executors", "1.0.0")


class NodeExecutor(ABC):
    """Abstract base class for node executors"""

    @abstractmethod
    async def execute(self, node: graph_service_pb2.Node, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the node and return output data"""
        pass


class SpeechToTextExecutor(NodeExecutor):
    """Executor for speech-to-text nodes"""

    async def execute(self, node: graph_service_pb2.Node, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute speech-to-text conversion"""
        try:
            # Extract configuration
            config = json.loads(node.config) if isinstance(node.config, str) else dict(node.config)
            service_endpoint = config.get("service_endpoint", "localhost:9091")

            # Create gRPC channel
            async with grpc.aio.insecure_channel(service_endpoint) as channel:
                stub = audio_pb2_grpc.AudioServiceStub(channel)

                # Prepare request
                request = audio_pb2.STTRequest()
                # TODO: Set audio data from input_data

                # Call service
                response = await stub.SpeechToText(request)

                events.info(
                    "STT node executed",
                    {
                        "node_id": node.id,
                        "transcript_length": len(response.transcript) if response.transcript else 0,
                    },
                )

                return {
                    "transcript": response.transcript,
                    "confidence": response.confidence,
                }

        except Exception as e:
            events.error("STT node execution failed", exception=e, metadata={"node_id": node.id})
            raise


class TextToSpeechExecutor(NodeExecutor):
    """Executor for text-to-speech nodes"""

    async def execute(self, node: graph_service_pb2.Node, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute text-to-speech conversion"""
        try:
            # Extract configuration
            config = json.loads(node.config) if isinstance(node.config, str) else dict(node.config)
            service_endpoint = config.get("service_endpoint", "localhost:9092")

            # Create gRPC channel
            async with grpc.aio.insecure_channel(service_endpoint) as channel:
                stub = audio_pb2_grpc.AudioServiceStub(channel)

                # Prepare request
                request = audio_pb2.TTSRequest()
                request.text = input_data.get("text", "")
                request.voice_id = config.get("voice", "nova")

                # Call service (streaming response)
                audio_chunks = []
                async for chunk in stub.TextToSpeech(request):
                    audio_chunks.append(chunk)

                events.info(
                    "TTS node executed",
                    {
                        "node_id": node.id,
                        "text_length": len(request.text),
                        "chunks_received": len(audio_chunks),
                    },
                )

                return {
                    "audio_chunks": audio_chunks,
                    "format": config.get("format", "mp3"),
                }

        except Exception as e:
            events.error("TTS node execution failed", exception=e, metadata={"node_id": node.id})
            raise


class LLMChatExecutor(NodeExecutor):
    """Executor for LLM chat nodes"""

    async def execute(self, node: graph_service_pb2.Node, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute LLM chat completion"""
        try:
            # Extract configuration
            config = json.loads(node.config) if isinstance(node.config, str) else dict(node.config)
            service_endpoint = config.get("service_endpoint", "localhost:9095")

            # Create gRPC channel
            async with grpc.aio.insecure_channel(service_endpoint) as channel:
                stub = chat_pb2_grpc.ChatServiceStub(channel)

                # Prepare request
                request = chat_pb2.SendMessageRequest()
                request.content = input_data.get("text", input_data.get("transcript", ""))
                request.role = chat_pb2.USER

                # Call service
                response = await stub.SendMessage(request)

                events.info(
                    "LLM chat node executed",
                    {
                        "node_id": node.id,
                        "input_length": len(request.content),
                        "response_length": len(response.message.content) if response.message else 0,
                    },
                )

                return {
                    "response_text": response.message.content if response.message else "",
                    "message_id": response.message.message_id if response.message else "",
                }

        except Exception as e:
            events.error(
                "LLM chat node execution failed",
                exception=e,
                metadata={"node_id": node.id},
            )
            raise


class DataTransformExecutor(NodeExecutor):
    """Executor for data transformation nodes"""

    async def execute(self, node: graph_service_pb2.Node, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute data transformation"""
        try:
            # Extract configuration
            config = json.loads(node.config) if isinstance(node.config, str) else dict(node.config)
            transform_type = config.get("transform_type", "passthrough")

            if transform_type == "passthrough":
                return input_data
            elif transform_type == "extract_field":
                field_name = config.get("field_name", "text")
                return {field_name: input_data.get(field_name, "")}
            elif transform_type == "rename_field":
                old_name = config.get("old_name", "input")
                new_name = config.get("new_name", "output")
                return {new_name: input_data.get(old_name, "")}
            else:
                # Custom transformation logic can be added here
                return input_data

        except Exception as e:
            events.error(
                "Data transform node execution failed",
                exception=e,
                metadata={"node_id": node.id},
            )
            raise


class CustomServiceExecutor(NodeExecutor):
    """Executor for custom service nodes"""

    async def execute(self, node: graph_service_pb2.Node, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute custom service call"""
        try:
            # Extract configuration
            config = json.loads(node.config) if isinstance(node.config, str) else dict(node.config)
            service_endpoint = config.get("service_endpoint", "localhost:9090")
            method = config.get("method", "Process")

            # For now, return mock data
            # TODO: Implement generic gRPC client for custom services

            events.info(
                "Custom service node executed",
                {
                    "node_id": node.id,
                    "service_endpoint": service_endpoint,
                    "method": method,
                },
            )

            return {"result": "custom_service_output", "processed": True}

        except Exception as e:
            events.error(
                "Custom service node execution failed",
                exception=e,
                metadata={"node_id": node.id},
            )
            raise


class CommandOrchestrationExecutor(NodeExecutor):
    """Executor for command orchestration nodes"""

    async def execute(self, node: graph_service_pb2.Node, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute command orchestration workflow"""
        try:
            from libs.python.command_orchestration import (
                CommandExecutor,
                DAGBuilder,
                ManPageIndexer,
                SemanticSearchEngine,
            )

            # Extract configuration
            config = json.loads(node.config) if isinstance(node.config, str) else dict(node.config)
            prompt = config.get("prompt", "")

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
                    node_id: {
                        "returncode": result.returncode,
                        "stdout": result.stdout[:500],
                        "stderr": result.stderr[:500],
                    }
                    for node_id, result in execution_result.results.items()
                },
            }

        except Exception as e:
            events.error(
                "Command orchestration execution failed",
                exception=e,
                metadata={"node_id": node.id},
            )
            raise


class NodeExecutorFactory:
    """Factory for creating node executors"""

    def __init__(self):
        self.executors = {
            graph_service_pb2.SPEECH_TO_TEXT: SpeechToTextExecutor(),
            graph_service_pb2.TEXT_TO_SPEECH: TextToSpeechExecutor(),
            graph_service_pb2.LLM_CHAT: LLMChatExecutor(),
            graph_service_pb2.LLM_COMPLETION: LLMChatExecutor(),  # Reuse chat executor
            graph_service_pb2.DATA_TRANSFORM: DataTransformExecutor(),
            graph_service_pb2.CUSTOM_SERVICE: CustomServiceExecutor(),
            graph_service_pb2.COMMAND_ORCHESTRATION: CommandOrchestrationExecutor(),
        }

        events.info(
            "Node executor factory initialized",
            {"supported_types": list(self.executors.keys())},
        )

    def get_executor(self, node_type: int) -> NodeExecutor:
        """Get executor for node type"""
        if node_type not in self.executors:
            raise ValueError(f"Unsupported node type: {node_type}")

        return self.executors[node_type]
