#!/usr/bin/env python3
"""
Graph service gRPC client for executing graphs and streaming events.

Provides async interface to graph service for graph execution and monitoring.
"""

import sys
import asyncio
from pathlib import Path
from typing import Optional, Callable, Any, AsyncGenerator
from dataclasses import dataclass

import grpc

# Add generated proto clients to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "generated" / "python" / "clients"))

try:
    from unhinged_proto_clients import (
        graph_service_pb2,
        graph_service_pb2_grpc,
    )
except ImportError as e:
    print(f"❌ Proto clients not found: {e}")
    print("Run 'make generate' to generate proto clients")
    sys.exit(1)


@dataclass
class ExecutionEvent:
    """Represents a graph execution event."""
    execution_id: str
    event_type: str
    node_id: Optional[str] = None
    event_data: Optional[dict] = None
    timestamp: Optional[Any] = None


class GraphServiceClient:
    """Async gRPC client for graph service."""
    
    def __init__(self, host: str = "localhost", port: int = 9096):
        """
        Initialize graph service client.
        
        Args:
            host: Graph service host
            port: Graph service port
        """
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
    
    async def connect(self):
        """Connect to graph service."""
        try:
            self.channel = grpc.aio.secure_channel(
                f"{self.host}:{self.port}",
                grpc.ssl_channel_credentials()
            )
            self.stub = graph_service_pb2_grpc.GraphServiceStub(self.channel)
            print(f"✅ Connected to graph service at {self.host}:{self.port}")
        except Exception as e:
            print(f"❌ Failed to connect to graph service: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from graph service."""
        if self.channel:
            await self.channel.close()
            print("✅ Disconnected from graph service")
    
    async def create_graph(self, graph: graph_service_pb2.Graph) -> str:
        """
        Create a graph in the service.
        
        Args:
            graph: Graph protobuf message
            
        Returns:
            Graph ID
        """
        if not self.stub:
            raise RuntimeError("Not connected to graph service")
        
        try:
            request = graph_service_pb2.CreateGraphRequest()
            request.graph.CopyFrom(graph)
            
            response = await self.stub.CreateGraph(request)
            
            if response.response.success:
                print(f"✅ Graph created: {graph.name} ({graph.id})")
                return graph.id
            else:
                raise RuntimeError(f"Failed to create graph: {response.response.message}")
        
        except Exception as e:
            print(f"❌ Error creating graph: {e}")
            raise
    
    async def execute_graph(
        self,
        graph_id: str,
        input_data: Optional[dict] = None,
        execution_id: Optional[str] = None
    ) -> str:
        """
        Execute a graph.
        
        Args:
            graph_id: Graph ID to execute
            input_data: Optional input parameters
            execution_id: Optional execution ID
            
        Returns:
            Execution ID
        """
        if not self.stub:
            raise RuntimeError("Not connected to graph service")
        
        try:
            request = graph_service_pb2.ExecuteGraphRequest()
            request.id = graph_id
            
            if input_data:
                request.input_data.update(input_data)
            
            if execution_id:
                request.execution_id = execution_id
            
            response = await self.stub.ExecuteGraph(request)
            
            if response.response.success:
                print(f"✅ Graph execution started: {response.execution_id}")
                return response.execution_id
            else:
                raise RuntimeError(f"Failed to execute graph: {response.response.message}")
        
        except Exception as e:
            print(f"❌ Error executing graph: {e}")
            raise
    
    async def stream_execution(
        self,
        execution_id: str
    ) -> AsyncGenerator[ExecutionEvent, None]:
        """
        Stream execution events for a graph execution.
        
        Args:
            execution_id: Execution ID to stream
            
        Yields:
            ExecutionEvent objects
        """
        if not self.stub:
            raise RuntimeError("Not connected to graph service")
        
        try:
            request = graph_service_pb2.StreamExecutionRequest()
            request.execution_id = execution_id
            
            async for event in self.stub.StreamExecution(request):
                # Convert protobuf event to ExecutionEvent
                exec_event = ExecutionEvent(
                    execution_id=event.execution_id,
                    event_type=graph_service_pb2.ExecutionEventType.Name(event.event_type),
                    node_id=event.node_id if event.node_id else None,
                    event_data=dict(event.event_data) if event.event_data else None,
                    timestamp=event.timestamp
                )
                
                yield exec_event
        
        except Exception as e:
            print(f"❌ Error streaming execution: {e}")
            raise
    
    async def get_execution(self, execution_id: str) -> dict:
        """
        Get execution status and results.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Execution details
        """
        if not self.stub:
            raise RuntimeError("Not connected to graph service")
        
        try:
            request = graph_service_pb2.GetExecutionRequest()
            request.execution_id = execution_id
            
            response = await self.stub.GetExecution(request)
            
            if response.response.success:
                return {
                    'execution_id': response.execution_id,
                    'graph_id': response.graph_id,
                    'status': graph_service_pb2.ExecutionStatus.Name(response.status),
                    'started_at': response.started_at,
                    'completed_at': response.completed_at,
                    'result_data': dict(response.result_data) if response.result_data else None,
                    'error_message': response.error_message,
                    'node_executions': [
                        {
                            'node_id': ne.node_id,
                            'status': graph_service_pb2.ExecutionStatus.Name(ne.status),
                            'started_at': ne.started_at,
                            'completed_at': ne.completed_at,
                            'output_data': dict(ne.output_data) if ne.output_data else None,
                            'error_message': ne.error_message
                        }
                        for ne in response.node_executions
                    ]
                }
            else:
                raise RuntimeError(f"Failed to get execution: {response.response.message}")
        
        except Exception as e:
            print(f"❌ Error getting execution: {e}")
            raise
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a running execution.
        
        Args:
            execution_id: Execution ID to cancel
            
        Returns:
            True if cancelled successfully
        """
        if not self.stub:
            raise RuntimeError("Not connected to graph service")
        
        try:
            request = graph_service_pb2.CancelExecutionRequest()
            request.execution_id = execution_id
            
            response = await self.stub.CancelExecution(request)
            
            if response.response.success:
                print(f"✅ Execution cancelled: {execution_id}")
                return True
            else:
                raise RuntimeError(f"Failed to cancel execution: {response.response.message}")
        
        except Exception as e:
            print(f"❌ Error cancelling execution: {e}")
            raise

