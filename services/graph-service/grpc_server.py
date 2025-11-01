#!/usr/bin/env python3
"""
@llm-type service.grpc
@llm-does Graph execution gRPC server implementation
"""

import asyncio
import sys
from concurrent import futures
from pathlib import Path

import grpc

# Add generated proto clients to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "generated" / "python" / "clients"))

try:
    from unhinged_proto_clients import (
        common_pb2,
        graph_service_pb2,
        graph_service_pb2_grpc,
    )
except ImportError as e:
    print(f"❌ Proto clients not found: {e}")
    print("Run 'make generate' to generate proto clients")
    sys.exit(1)

from events import create_service_logger
from graph_executor import GraphExecutor

# Initialize event logger
events = create_service_logger("graph-grpc-server", "1.0.0")

class GraphServiceImpl(graph_service_pb2_grpc.GraphServiceServicer):
    """Graph service implementation"""

    def __init__(self):
        self.executor = GraphExecutor()
        events.info("Graph service initialized")

    async def CreateGraph(self, request, context):
        """Create a new Graph definition"""
        try:
            graph_id = await self.executor.create_graph(request.graph)

            response = graph_service_pb2.CreateGraphResponse()
            response.response.success = True
            response.response.message = "Graph created successfully"
            response.id = graph_id

            events.info("Graph created", {"graph_id": graph_id, "name": request.graph.name})
            return response

        except Exception as e:
            events.error("Failed to create Graph", exception=e)
            response = graph_service_pb2.CreateGraphResponse()
            response.response.success = False
            response.response.message = f"Failed to create Graph: {str(e)}"
            return response

    async def GetGraph(self, request, context):
        """Get Graph definition by ID"""
        try:
            graph = await self.executor.get_graph(request.id)

            response = graph_service_pb2.GetGraphResponse()
            response.response.success = True
            response.response.message = "Graph retrieved successfully"
            response.graph.CopyFrom(graph)

            return response

        except Exception as e:
            events.error("Failed to get Graph", exception=e, metadata={"id": request.id})
            response = graph_service_pb2.GetGraphResponse()
            response.response.success = False
            response.response.message = f"Failed to get Graph: {str(e)}"
            return response

    async def ListGraphs(self, request, context):
        """List all Graph definitions"""
        try:
            graphs = await self.executor.list_graphs(request.pagination, request.filters, request.graph_type)

            response = graph_service_pb2.ListGraphsResponse()
            response.response.success = True
            response.response.message = f"Found {len(graphs)} graphs"
            response.graphs.extend(graphs)

            return response

        except Exception as e:
            events.error("Failed to list Graphs", exception=e)
            response = graph_service_pb2.ListGraphsResponse()
            response.response.success = False
            response.response.message = f"Failed to list Graphs: {str(e)}"
            return response

    async def DeleteGraph(self, request, context):
        """Delete a Graph definition"""
        try:
            await self.executor.delete_graph(request.id)

            response = graph_service_pb2.DeleteGraphResponse()
            response.response.success = True
            response.response.message = "Graph deleted successfully"

            events.info("Graph deleted", {"graph_id": request.id})
            return response

        except Exception as e:
            events.error("Failed to delete Graph", exception=e, metadata={"id": request.id})
            response = graph_service_pb2.DeleteGraphResponse()
            response.response.success = False
            response.response.message = f"Failed to delete Graph: {str(e)}"
            return response

    async def ExecuteGraph(self, request, context):
        """Execute a Graph"""
        try:
            execution_id = await self.executor.execute_graph(
                request.id,
                request.input_data,
                request.execution_id
            )

            response = graph_service_pb2.ExecuteGraphResponse()
            response.response.success = True
            response.response.message = "Graph execution started"
            response.execution_id = execution_id
            response.status = graph_service_pb2.PENDING

            events.info("Graph execution started", {
                "graph_id": request.id,
                "execution_id": execution_id
            })
            return response

        except Exception as e:
            events.error("Failed to execute Graph", exception=e, metadata={"id": request.id})
            response = graph_service_pb2.ExecuteGraphResponse()
            response.response.success = False
            response.response.message = f"Failed to execute Graph: {str(e)}"
            return response

    async def StreamExecution(self, request, context):
        """Stream execution events"""
        try:
            async for event in self.executor.stream_execution(request.execution_id):
                yield event
        except Exception as e:
            events.error("Failed to stream execution", exception=e,
                        metadata={"execution_id": request.execution_id})

    async def GetExecution(self, request, context):
        """Get execution status and results"""
        try:
            execution = await self.executor.get_execution(request.execution_id)

            response = graph_service_pb2.GetExecutionResponse()
            response.response.success = True
            response.response.message = "Execution retrieved successfully"
            response.CopyFrom(execution)

            return response

        except Exception as e:
            events.error("Failed to get execution", exception=e,
                        metadata={"execution_id": request.execution_id})
            response = graph_service_pb2.GetExecutionResponse()
            response.response.success = False
            response.response.message = f"Failed to get execution: {str(e)}"
            return response

    async def CancelExecution(self, request, context):
        """Cancel a running execution"""
        try:
            await self.executor.cancel_execution(request.execution_id)

            response = graph_service_pb2.CancelExecutionResponse()
            response.response.success = True
            response.response.message = "Execution cancelled successfully"

            events.info("Execution cancelled", {"execution_id": request.execution_id})
            return response

        except Exception as e:
            events.error("Failed to cancel execution", exception=e,
                        metadata={"execution_id": request.execution_id})
            response = graph_service_pb2.CancelExecutionResponse()
            response.response.success = False
            response.response.message = f"Failed to cancel execution: {str(e)}"
            return response

    async def HealthCheck(self, request, context):
        """Health check endpoint"""
        response = common_pb2.HealthCheckResponse()
        response.status = common_pb2.HealthCheckResponse.SERVING
        response.message = "Graph service is healthy"
        return response

def serve():
    """Start the gRPC server"""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    graph_service_pb2_grpc.add_GraphServiceServicer_to_server(GraphServiceImpl(), server)

    listen_addr = '[::]:9096'
    server.add_insecure_port(listen_addr)

    events.info("Starting Graph gRPC server", {"address": listen_addr})

    async def serve_async():
        await server.start()
        events.info("Graph gRPC server started successfully")
        await server.wait_for_termination()

    asyncio.run(serve_async())

if __name__ == '__main__':
    serve()
