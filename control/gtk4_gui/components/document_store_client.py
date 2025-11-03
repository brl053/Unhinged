#!/usr/bin/env python3
"""
Document store gRPC client for saving and loading graphs.

Provides async interface to document store service for graph persistence.
"""

import json
import sys
from pathlib import Path
from typing import Any

import grpc

# Add generated proto clients to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "generated" / "python" / "clients"))

try:
    from unhinged_proto_clients import graph_service_pb2
except ImportError as e:
    print(f"❌ Proto clients not found: {e}")
    print("Run 'make generate' to generate proto clients")
    graph_service_pb2 = None

# Document store proto is optional - will be generated later
try:
    from unhinged_proto_clients import (
        document_store_pb2,
        document_store_pb2_grpc,
    )
except ImportError:
    document_store_pb2 = None
    document_store_pb2_grpc = None


class DocumentStoreClient:
    """Async gRPC client for document store service."""

    def __init__(self, host: str = "localhost", port: int = 9097):
        """
        Initialize document store client.
        
        Args:
            host: Document store service host
            port: Document store service port
        """
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None

    async def connect(self):
        """Connect to document store service."""
        if not document_store_pb2_grpc:
            raise RuntimeError("Document store proto not available. Run 'make generate' to generate proto clients")

        try:
            self.channel = grpc.aio.secure_channel(
                f"{self.host}:{self.port}",
                grpc.ssl_channel_credentials()
            )
            self.stub = document_store_pb2_grpc.DocumentStoreServiceStub(self.channel)
            print(f"✅ Connected to document store at {self.host}:{self.port}")
        except Exception as e:
            print(f"❌ Failed to connect to document store: {e}")
            raise

    async def disconnect(self):
        """Disconnect from document store service."""
        if self.channel:
            await self.channel.close()
            print("✅ Disconnected from document store")

    async def save_graph(
        self,
        graph: graph_service_pb2.Graph,
        namespace: str = "graphs",
        tags: list[str] = None,
        session_id: str = None
    ) -> str:
        """
        Save graph to document store.
        
        Args:
            graph: Graph protobuf message to save
            namespace: Document namespace
            tags: Optional tags for versioning
            session_id: Optional session ID
            
        Returns:
            Document UUID
        """
        if not self.stub:
            raise RuntimeError("Not connected to document store")

        try:
            # Serialize graph to JSON
            graph_json = json.dumps({
                'id': graph.id,
                'name': graph.name,
                'description': graph.description,
                'type': graph_service_pb2.GraphType.Name(graph.type),
                'nodes': [
                    {
                        'id': node.id,
                        'name': node.name,
                        'type': graph_service_pb2.NodeType.Name(node.type),
                        'config': dict(node.config) if node.config else {}
                    }
                    for node in graph.nodes
                ],
                'edges': [
                    {
                        'id': edge.id,
                        'source_node_id': edge.source_node_id,
                        'target_node_id': edge.target_node_id,
                        'source_output': edge.source_output,
                        'target_input': edge.target_input
                    }
                    for edge in graph.edges
                ]
            })

            # Create document
            document = document_store_pb2.Document()
            document.document_uuid = graph.id
            document.type = "graph"
            document.name = graph.name
            document.namespace = namespace
            document.body_json = graph_json
            document.session_id = session_id or ""

            if tags:
                document.tags.extend(tags)

            # Save to document store
            request = document_store_pb2.PutDocumentRequest()
            request.document.CopyFrom(document)

            response = await self.stub.PutDocument(request)

            if response.success:
                print(f"✅ Graph saved: {graph.name} ({graph.id})")
                return graph.id
            else:
                raise RuntimeError(f"Failed to save graph: {response.message}")

        except Exception as e:
            print(f"❌ Error saving graph: {e}")
            raise

    async def load_graph(
        self,
        graph_id: str,
        version: int | None = None,
        tag: str | None = None
    ) -> graph_service_pb2.Graph:
        """
        Load graph from document store.
        
        Args:
            graph_id: Graph ID to load
            version: Optional specific version
            tag: Optional tag (e.g., "production")
            
        Returns:
            Graph protobuf message
        """
        if not self.stub:
            raise RuntimeError("Not connected to document store")

        try:
            # Request document
            request = document_store_pb2.GetDocumentRequest()
            request.document_uuid = graph_id
            request.include_body = True

            if version:
                request.version = version
            if tag:
                request.tag = tag

            response = await self.stub.GetDocument(request)

            if not response.success:
                raise RuntimeError(f"Failed to load graph: {response.message}")

            # Deserialize graph from JSON
            graph_data = json.loads(response.document.body_json)

            graph = graph_service_pb2.Graph()
            graph.id = graph_data['id']
            graph.name = graph_data['name']
            graph.description = graph_data.get('description', '')
            graph.type = graph_service_pb2.GraphType.Value(graph_data['type'])

            # Reconstruct nodes
            for node_data in graph_data.get('nodes', []):
                node = graph_service_pb2.Node()
                node.id = node_data['id']
                node.name = node_data['name']
                node.type = graph_service_pb2.NodeType.Value(node_data['type'])

                if node_data.get('config'):
                    node.config.update(node_data['config'])

                graph.nodes.append(node)

            # Reconstruct edges
            for edge_data in graph_data.get('edges', []):
                edge = graph_service_pb2.Edge()
                edge.id = edge_data['id']
                edge.source_node_id = edge_data['source_node_id']
                edge.target_node_id = edge_data['target_node_id']
                edge.source_output = edge_data.get('source_output', '')
                edge.target_input = edge_data.get('target_input', '')

                graph.edges.append(edge)

            print(f"✅ Graph loaded: {graph.name} ({graph.id})")
            return graph

        except Exception as e:
            print(f"❌ Error loading graph: {e}")
            raise

    async def list_graphs(
        self,
        namespace: str = "graphs",
        tag: str | None = None,
        session_id: str | None = None
    ) -> list[dict[str, Any]]:
        """
        List graphs in document store.
        
        Args:
            namespace: Document namespace
            tag: Optional tag filter
            session_id: Optional session filter
            
        Returns:
            List of graph metadata
        """
        if not self.stub:
            raise RuntimeError("Not connected to document store")

        try:
            request = document_store_pb2.ListDocumentsRequest()
            request.namespace = namespace
            request.type = "graph"
            request.include_body = False
            request.latest_versions_only = True

            if tag:
                request.tag = tag
            if session_id:
                request.session_id = session_id

            response = await self.stub.ListDocuments(request)

            graphs = []
            for doc in response.documents:
                graphs.append({
                    'id': doc.document_uuid,
                    'name': doc.name,
                    'version': doc.version,
                    'tags': list(doc.tags),
                    'created_at': doc.created_at,
                })

            print(f"✅ Listed {len(graphs)} graphs")
            return graphs

        except Exception as e:
            print(f"❌ Error listing graphs: {e}")
            raise

    async def delete_graph(
        self,
        graph_id: str,
        deleted_by: str = "user",
        deleted_by_type: str = "person"
    ) -> bool:
        """
        Delete graph from document store.

        Args:
            graph_id: Graph ID to delete
            deleted_by: User who deleted the graph
            deleted_by_type: Type of user (person, admin, system)

        Returns:
            True if deletion was successful
        """
        if not self.stub:
            raise RuntimeError("Not connected to document store")

        try:
            request = document_store_pb2.DeleteDocumentRequest()
            request.document_uuid = graph_id
            request.deleted_by = deleted_by
            request.deleted_by_type = deleted_by_type

            response = await self.stub.DeleteDocument(request)

            if response.success:
                print(f"✅ Graph deleted: {graph_id}")
                return True
            else:
                raise RuntimeError(f"Failed to delete graph: {response.message}")

        except Exception as e:
            print(f"❌ Error deleting graph: {e}")
            raise

