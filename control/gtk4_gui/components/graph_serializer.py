#!/usr/bin/env python3
"""
Graph serialization and deserialization for protobuf integration.

Converts between GraphCanvasWidget state and graph_service_pb2.Graph protobuf messages.
"""

import sys
import uuid
from pathlib import Path
from typing import Any

# Add generated proto clients to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "generated" / "python" / "clients"))

try:
    from unhinged_proto_clients import (
        common_pb2,
        graph_service_pb2,
    )
except ImportError as e:
    print(f"❌ Proto clients not found: {e}")
    print("Run 'make generate' to generate proto clients")
    sys.exit(1)


class GraphSerializer:
    """Serialize/deserialize graphs between canvas state and protobuf."""

    # Map canvas node types to protobuf NodeType enum
    NODE_TYPE_MAP = {
        'speech_to_text': graph_service_pb2.SPEECH_TO_TEXT,
        'text_to_speech': graph_service_pb2.TEXT_TO_SPEECH,
        'llm_chat': graph_service_pb2.LLM_CHAT,
        'llm_completion': graph_service_pb2.LLM_COMPLETION,
        'vision_ai': graph_service_pb2.VISION_AI,
        'image_generation': graph_service_pb2.IMAGE_GENERATION,
        'context_hydration': graph_service_pb2.CONTEXT_HYDRATION,
        'prompt_enhancement': graph_service_pb2.PROMPT_ENHANCEMENT,
        'data_transform': graph_service_pb2.DATA_TRANSFORM,
        'conditional': graph_service_pb2.CONDITIONAL,
        'loop_breaker': graph_service_pb2.LOOP_BREAKER,
        'http_request': graph_service_pb2.HTTP_REQUEST,
        'custom_service': graph_service_pb2.CUSTOM_SERVICE,
    }

    # Reverse map for deserialization
    REVERSE_NODE_TYPE_MAP = {v: k for k, v in NODE_TYPE_MAP.items()}

    # Map canvas graph types to protobuf GraphType enum
    GRAPH_TYPE_MAP = {
        'dag': graph_service_pb2.DAG,
        'cyclic': graph_service_pb2.CYCLIC,
        'cyclic_with_breakers': graph_service_pb2.CYCLIC_WITH_BREAKERS,
        'tree': graph_service_pb2.TREE,
        'unrestricted': graph_service_pb2.UNRESTRICTED,
    }

    # Reverse map for deserialization
    REVERSE_GRAPH_TYPE_MAP = {v: k for k, v in GRAPH_TYPE_MAP.items()}

    @staticmethod
    def serialize_graph(
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        graph_id: str = None,
        graph_name: str = "Untitled Graph",
        graph_type: str = "dag",
        description: str = ""
    ) -> graph_service_pb2.Graph:
        """
        Serialize canvas state to protobuf Graph message.
        
        Args:
            nodes: List of node dictionaries from canvas
            edges: List of edge dictionaries from canvas
            graph_id: Optional graph ID (generated if not provided)
            graph_name: Name of the graph
            graph_type: Type of graph (dag, cyclic, etc.)
            description: Graph description
            
        Returns:
            graph_service_pb2.Graph protobuf message
        """
        if not graph_id:
            graph_id = str(uuid.uuid4())

        # Create protobuf nodes
        proto_nodes = []
        for node in nodes:
            proto_node = graph_service_pb2.Node()
            proto_node.id = node.get('id', str(uuid.uuid4()))
            proto_node.name = node.get('label', 'Unnamed Node')

            # Map node type
            node_type_str = node.get('type', 'custom_service').lower()
            proto_node.type = GraphSerializer.NODE_TYPE_MAP.get(
                node_type_str,
                graph_service_pb2.CUSTOM_SERVICE
            )

            # Convert node data to protobuf Struct
            node_data = node.get('data', {})
            if node_data:
                proto_node.config.update(node_data)

            proto_nodes.append(proto_node)

        # Create protobuf edges
        proto_edges = []
        for edge in edges:
            proto_edge = graph_service_pb2.Edge()
            proto_edge.id = edge.get('id', str(uuid.uuid4()))
            proto_edge.source_node_id = edge.get('source', '')
            proto_edge.target_node_id = edge.get('target', '')
            proto_edge.source_output = edge.get('source_handle', '')
            proto_edge.target_input = edge.get('target_handle', '')

            proto_edges.append(proto_edge)

        # Create graph message
        graph = graph_service_pb2.Graph()
        graph.id = graph_id
        graph.name = graph_name
        graph.description = description

        # Map graph type
        graph_type_str = graph_type.lower()
        graph.type = GraphSerializer.GRAPH_TYPE_MAP.get(
            graph_type_str,
            graph_service_pb2.DAG
        )

        # Add nodes and edges
        graph.nodes.extend(proto_nodes)
        graph.edges.extend(proto_edges)

        return graph

    @staticmethod
    def deserialize_graph(graph: graph_service_pb2.Graph) -> tuple[list[dict], list[dict], dict]:
        """
        Deserialize protobuf Graph message to canvas state.
        
        Args:
            graph: graph_service_pb2.Graph protobuf message
            
        Returns:
            Tuple of (nodes, edges, metadata)
        """
        nodes = []
        edges = []

        # Deserialize nodes
        for proto_node in graph.nodes:
            node = {
                'id': proto_node.id,
                'label': proto_node.name,
                'type': GraphSerializer.REVERSE_NODE_TYPE_MAP.get(
                    proto_node.type,
                    'custom_service'
                ),
                'position': {'x': 100, 'y': 100},  # Default position
                'data': dict(proto_node.config) if proto_node.config else {},
                'status': 'idle'
            }
            nodes.append(node)

        # Deserialize edges
        for proto_edge in graph.edges:
            edge = {
                'id': proto_edge.id,
                'source': proto_edge.source_node_id,
                'target': proto_edge.target_node_id,
                'source_handle': proto_edge.source_output,
                'target_handle': proto_edge.target_input,
                'status': 'idle'
            }
            edges.append(edge)

        # Extract metadata
        metadata = {
            'graph_id': graph.id,
            'graph_name': graph.name,
            'graph_type': GraphSerializer.REVERSE_GRAPH_TYPE_MAP.get(
                graph.type,
                'dag'
            ),
            'description': graph.description,
        }

        return nodes, edges, metadata

    @staticmethod
    def json_to_struct(data: dict[str, Any]) -> 'google.protobuf.Struct':
        """Convert Python dict to protobuf Struct."""
        struct = common_pb2.Struct()
        if data:
            struct.update(data)
        return struct

    @staticmethod
    def struct_to_json(struct: 'google.protobuf.Struct') -> dict[str, Any]:
        """Convert protobuf Struct to Python dict."""
        return dict(struct) if struct else {}

