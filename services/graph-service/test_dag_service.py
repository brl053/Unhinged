#!/usr/bin/env python3
"""
@llm-type service.test
@llm-does Test script for Graph service functionality
"""

import asyncio
import json
import sys
from pathlib import Path

# Add generated proto clients to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "generated" / "python" / "clients"))

try:
    from google.protobuf import struct_pb2
    from unhinged_proto_clients import graph_service_pb2
except ImportError as e:
    print(f"❌ Proto clients not found: {e}")
    print("Run 'make generate' to generate proto clients")
    sys.exit(1)

from graph_executor import GraphExecutor


async def test_voice_pipeline_graph():
    """Test the voice pipeline Graph"""
    print("🧪 Testing Voice Pipeline Graph...")

    # Create Graph executor
    executor = GraphExecutor()

    # Create voice pipeline Graph
    graph = graph_service_pb2.Graph()
    graph.id = "voice-pipeline-test"
    graph.name = "Voice Pipeline Test"
    graph.description = "Test voice input to voice output pipeline"
    graph.graph_type = graph_service_pb2.DAG

    # Create nodes
    stt_node = graph.nodes.add()
    stt_node.id = "stt1"
    stt_node.name = "Speech to Text"
    stt_node.type = graph_service_pb2.SPEECH_TO_TEXT
    stt_config = struct_pb2.Struct()
    stt_config.update({"model": "whisper-large-v3", "service_endpoint": "localhost:9091"})
    stt_node.config.CopyFrom(stt_config)

    llm_node = graph.nodes.add()
    llm_node.id = "llm1"
    llm_node.name = "LLM Processing"
    llm_node.type = graph_service_pb2.LLM_CHAT
    llm_config = struct_pb2.Struct()
    llm_config.update({"model": "llama3.1:8b", "service_endpoint": "localhost:9095"})
    llm_node.config.CopyFrom(llm_config)

    tts_node = graph.nodes.add()
    tts_node.id = "tts1"
    tts_node.name = "Text to Speech"
    tts_node.type = graph_service_pb2.TEXT_TO_SPEECH
    tts_config = struct_pb2.Struct()
    tts_config.update({"voice": "nova", "service_endpoint": "localhost:9092"})
    tts_node.config.CopyFrom(tts_config)

    # Create edges
    edge1 = graph.edges.add()
    edge1.id = "stt_to_llm"
    edge1.source_node_id = "stt1"
    edge1.target_node_id = "llm1"
    edge1.source_output = "transcript"
    edge1.target_input = "text"

    edge2 = graph.edges.add()
    edge2.id = "llm_to_tts"
    edge2.source_node_id = "llm1"
    edge2.target_node_id = "tts1"
    edge2.source_output = "response_text"
    edge2.target_input = "text"

    try:
        # Test Graph creation
        print("📝 Creating Graph...")
        graph_id = await executor.create_graph(graph)
        print(f"✅ Graph created with ID: {graph_id}")

        # Test Graph retrieval
        print("📖 Retrieving Graph...")
        retrieved_graph = await executor.get_graph(graph_id)
        print(f"✅ Graph retrieved: {retrieved_graph.name}")

        # Test Graph listing
        print("📋 Listing Graphs...")
        graphs = await executor.list_graphs(None, None, graph_service_pb2.GRAPH_TYPE_UNSPECIFIED)
        print(f"✅ Found {len(graphs)} Graphs")

        # Test Graph execution (mock)
        print("🚀 Starting Graph execution...")
        input_data = struct_pb2.Struct()
        input_data.update({"audio_file": "test_audio.wav"})

        execution_id = await executor.execute_graph(graph_id, input_data)
        print(f"✅ Graph execution started with ID: {execution_id}")

        # Wait a bit for execution to progress
        await asyncio.sleep(2)

        # Test execution status
        print("📊 Checking execution status...")
        execution = await executor.get_execution(execution_id)
        print(f"✅ Execution status: {execution.status}")

        # Test Graph deletion
        print("🗑️ Deleting Graph...")
        await executor.delete_graph(graph_id)
        print("✅ Graph deleted successfully")

        print("\n🎉 All tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise


async def test_simple_graph():
    """Test a simple data transformation Graph"""
    print("\n🧪 Testing Simple Data Transform Graph...")

    executor = GraphExecutor()

    # Create simple Graph
    graph = graph_service_pb2.Graph()
    graph.id = "simple-transform-test"
    graph.name = "Simple Transform Test"
    graph.description = "Test simple data transformation"
    graph.graph_type = graph_service_pb2.DAG

    # Single transform node
    transform_node = graph.nodes.add()
    transform_node.id = "transform1"
    transform_node.name = "Data Transform"
    transform_node.type = graph_service_pb2.DATA_TRANSFORM
    transform_config = struct_pb2.Struct()
    transform_config.update({"transform_type": "passthrough"})
    transform_node.config.CopyFrom(transform_config)

    try:
        # Create and execute
        graph_id = await executor.create_graph(graph)
        print(f"✅ Simple Graph created: {graph_id}")

        input_data = struct_pb2.Struct()
        input_data.update({"message": "Hello, Graph!"})

        execution_id = await executor.execute_graph(graph_id, input_data)
        print(f"✅ Simple Graph execution started: {execution_id}")

        # Wait for completion
        await asyncio.sleep(1)

        execution = await executor.get_execution(execution_id)
        print(f"✅ Simple Graph execution status: {execution.status}")

        print("🎉 Simple Graph test passed!")

    except Exception as e:
        import traceback

        print(f"❌ Simple Graph test failed: {e}")
        traceback.print_exc()
        raise


async def main():
    """Run all tests"""
    print("🚀 Starting Graph Service Tests\n")

    try:
        await test_simple_graph()
        await test_voice_pipeline_graph()
        print("\n✅ All Graph service tests completed successfully!")

    except Exception as e:
        import traceback

        print(f"\n❌ Graph service tests failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
