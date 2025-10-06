#!/usr/bin/env python3
"""
Context LLM gRPC Server - Pure LLM Operations Only
Simplified service focused solely on LLM operations and context processing
"""

import grpc
from concurrent import futures
import logging
import time
import traceback
from typing import List, Dict, Any

# Import generated gRPC code (will be generated from proto files)
import context_service_pb2
import context_service_pb2_grpc

from context_manager import context_manager
from llm_providers import create_llm_provider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextServiceImpl(context_service_pb2_grpc.ContextServiceServicer):
    """
    Pure LLM operations service implementation
    
    Focuses solely on LLM operations and context processing without
    business logic, authentication, routing, or orchestration concerns.
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.llm_provider = create_llm_provider()
        self.generation_count = 0
        logger.info("Context LLM gRPC service initialized")
    
    def GeneratePrompt(self, request, context):
        """
        Generate enhanced prompt with project context
        """
        start_time = time.time()
        self.generation_count += 1
        
        try:
            # Validate request
            if not request.base_prompt:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Base prompt is required")
                return context_service_pb2.PromptGenerationResponse()
            
            # Extract context information
            context_items = []
            if request.context_types:
                for context_type in request.context_types:
                    items = context_manager.get_context_items(
                        context_type, 
                        limit=request.max_context_items or 3
                    )
                    context_items.extend(items)
            
            # Build context string
            context_text = ""
            if context_items:
                context_text = "\n".join([
                    f"- {item.title}: {item.content[:200]}..."
                    for item in context_items[:request.max_context_items or 3]
                ])
            
            # Generate enhanced prompt
            prompt_request = f"""
            Enhance this analysis prompt with the provided context:
            
            Base Prompt: {request.base_prompt}
            Analysis Type: {request.analysis_type}
            
            Context Information:
            {context_text}
            
            Create a detailed, contextual prompt for image analysis that incorporates
            the relevant context information to provide more accurate and specific analysis.
            """
            
            enhanced_prompt = self.llm_provider.generate_text(
                prompt_request,
                max_tokens=request.max_tokens or 1000,
                temperature=request.temperature or 0.3,
                model=request.model or "default"
            )
            
            processing_time = time.time() - start_time
            
            # Build response
            response = context_service_pb2.PromptGenerationResponse(
                enhanced_prompt=enhanced_prompt,
                context_items_used=len(context_items),
                processing_time=processing_time,
                model_used=self.llm_provider.get_current_model(),
                success=True
            )
            
            # Add context items to response
            for item in context_items:
                context_item = response.context_items.add()
                context_item.id = item.id
                context_item.type = item.type
                context_item.title = item.title
                context_item.content = item.content[:500]  # Truncate for response
                context_item.file_path = item.file_path
                context_item.tags.extend(item.tags)
                context_item.relevance_score = item.relevance_score
                context_item.last_modified = int(item.last_modified.timestamp())
            
            logger.info(f"Prompt generation completed in {processing_time:.2f}s, {len(context_items)} context items used")
            return response
            
        except Exception as e:
            logger.error(f"Prompt generation failed: {str(e)}")
            logger.error(traceback.format_exc())
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Prompt generation failed: {str(e)}")
            return context_service_pb2.PromptGenerationResponse(
                success=False,
                error=str(e)
            )
    
    def SearchContext(self, request, context):
        """
        Search project context and documentation
        """
        start_time = time.time()
        
        try:
            # Validate request
            if not request.query:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Search query is required")
                return context_service_pb2.ContextSearchResponse()
            
            # Perform context search
            results = context_manager.search_context(
                query=request.query,
                context_types=list(request.context_types) if request.context_types else None,
                max_results=request.max_results or 10,
                min_relevance=request.min_relevance or 0.0
            )
            
            processing_time = time.time() - start_time
            
            # Build response
            response = context_service_pb2.ContextSearchResponse(
                query=request.query,
                total_results=len(results),
                processing_time=processing_time
            )
            
            # Add search results
            for item in results:
                result_item = response.results.add()
                result_item.id = item.id
                result_item.type = item.type
                result_item.title = item.title
                result_item.content = item.content
                result_item.file_path = item.file_path
                result_item.tags.extend(item.tags)
                result_item.relevance_score = item.relevance_score
                result_item.last_modified = int(item.last_modified.timestamp())
                
                # Add metadata
                for key, value in item.metadata.items():
                    result_item.metadata[key] = str(value)
            
            logger.info(f"Context search completed in {processing_time:.2f}s, {len(results)} results found")
            return response
            
        except Exception as e:
            logger.error(f"Context search failed: {str(e)}")
            logger.error(traceback.format_exc())
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Context search failed: {str(e)}")
            return context_service_pb2.ContextSearchResponse()
    
    def GenerateText(self, request, context):
        """
        Generate text using LLM
        """
        start_time = time.time()
        
        try:
            # Validate request
            if not request.prompt:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Prompt is required")
                return context_service_pb2.TextGenerationResponse()
            
            # Generate text
            generated_text = self.llm_provider.generate_text(
                prompt=request.prompt,
                max_tokens=request.max_tokens or 500,
                temperature=request.temperature or 0.7,
                top_p=request.top_p or 0.9,
                stop_sequences=list(request.stop_sequences) if request.stop_sequences else None,
                model=request.model or "default"
            )
            
            processing_time = time.time() - start_time
            
            # Build response
            response = context_service_pb2.TextGenerationResponse(
                text=generated_text,
                model_used=self.llm_provider.get_current_model(),
                tokens_generated=len(generated_text.split()),  # Rough estimate
                processing_time=processing_time,
                success=True
            )
            
            logger.info(f"Text generation completed in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            logger.error(traceback.format_exc())
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Text generation failed: {str(e)}")
            return context_service_pb2.TextGenerationResponse(
                success=False,
                error=str(e)
            )
    
    def GetAvailableModels(self, request, context):
        """
        Get available LLM models
        """
        try:
            models = self.llm_provider.get_available_models()
            
            response = context_service_pb2.LLMModelsResponse()
            
            for model_name, model_info in models.items():
                model = response.models.add()
                model.name = model_name
                model.display_name = model_info.get('display_name', model_name)
                model.description = model_info.get('description', '')
                model.available = model_info.get('available', False)
                model.provider = model_info.get('provider', 'unknown')
                model.max_tokens = model_info.get('max_tokens', 4096)
                model.capabilities.extend(model_info.get('capabilities', []))
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get available models: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get models: {str(e)}")
            return context_service_pb2.LLMModelsResponse()
    
    def GetHealth(self, request, context):
        """
        Health check endpoint
        """
        try:
            uptime = int(time.time() - self.start_time)
            
            # Check LLM provider health
            llm_healthy = self.llm_provider.check_health()
            
            # Check context manager health
            context_healthy = context_manager.check_health()
            
            overall_healthy = llm_healthy and context_healthy
            
            response = context_service_pb2.HealthResponse(
                healthy=overall_healthy,
                status="HEALTHY" if overall_healthy else "DEGRADED",
                uptime_seconds=uptime,
                version="1.0.0"
            )
            
            # Add health details
            response.details['llm_provider_healthy'] = str(llm_healthy)
            response.details['context_manager_healthy'] = str(context_healthy)
            response.details['generation_count'] = str(self.generation_count)
            response.details['uptime_seconds'] = str(uptime)
            response.details['current_model'] = self.llm_provider.get_current_model()
            
            return response
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return context_service_pb2.HealthResponse(
                healthy=False,
                status="ERROR",
                uptime_seconds=int(time.time() - self.start_time),
                version="1.0.0"
            )

def serve():
    """
    Start the gRPC server
    """
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=2),
        options=[
            ('grpc.keepalive_time_ms', 30000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.keepalive_permit_without_calls', True),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.http2.min_time_between_pings_ms', 10000),
            ('grpc.http2.min_ping_interval_without_data_ms', 300000),
            ('grpc.max_receive_message_length', 4 * 1024 * 1024),   # 4MB
            ('grpc.max_send_message_length', 4 * 1024 * 1024),      # 4MB
        ]
    )
    
    context_service_pb2_grpc.add_ContextServiceServicer_to_server(
        ContextServiceImpl(), server
    )
    
    listen_addr = '[::]:50052'
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting Context LLM gRPC server on {listen_addr}")
    logger.info("Service ready for pure LLM operations")
    
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down Context LLM gRPC server...")
        server.stop(grace=5)

if __name__ == '__main__':
    serve()
