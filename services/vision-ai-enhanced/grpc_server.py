#!/usr/bin/env python3
"""
Vision AI gRPC Server - Pure Model Inference Only
Simplified service focused solely on AI/ML inference operations
"""

import grpc
from concurrent import futures
import logging
import time
import traceback
from typing import Optional
from io import BytesIO
from PIL import Image

# Import generated gRPC code (will be generated from proto files)
import vision_service_pb2
import vision_service_pb2_grpc

from processors.vision_processor import vision_processor, VisionRequest, AnalysisType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisionServiceImpl(vision_service_pb2_grpc.VisionServiceServicer):
    """
    Pure vision inference service implementation
    
    Focuses solely on model inference without business logic,
    authentication, routing, or orchestration concerns.
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.inference_count = 0
        logger.info("Vision AI gRPC service initialized")
    
    def Infer(self, request, context):
        """
        Perform pure model inference on image data
        """
        start_time = time.time()
        self.inference_count += 1
        
        try:
            # Validate request
            if not request.image_data:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Image data is required")
                return vision_service_pb2.VisionInferenceResponse()
            
            # Convert image data
            try:
                image = Image.open(BytesIO(request.image_data)).convert('RGB')
            except Exception as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"Invalid image data: {str(e)}")
                return vision_service_pb2.VisionInferenceResponse()
            
            # Map analysis type
            analysis_type_map = {
                'screenshot': AnalysisType.SCREENSHOT,
                'natural_image': AnalysisType.NATURAL_IMAGE,
                'document': AnalysisType.DOCUMENT,
                'ui_component': AnalysisType.UI_COMPONENT,
                'ocr_focused': AnalysisType.OCR_FOCUSED
            }
            
            analysis_type = analysis_type_map.get(
                request.analysis_type.lower(), 
                AnalysisType.SCREENSHOT
            )
            
            # Create vision request
            vision_request = VisionRequest(
                image=image,
                analysis_type=analysis_type,
                prompt=request.prompt or "Analyze this image in detail.",
                max_tokens=request.max_tokens or 1024,
                temperature=request.temperature or 0.1,
                model_preference=request.model or "qwen2-vl"
            )
            
            # Perform inference
            result = vision_processor.analyze_image(vision_request)
            
            processing_time = time.time() - start_time
            
            # Build response
            response = vision_service_pb2.VisionInferenceResponse(
                description=result.description,
                confidence=result.confidence,
                model_used=result.model_used,
                processing_time=processing_time,
                success=True
            )
            
            # Add metadata
            for key, value in result.metadata.items():
                response.metadata[key] = str(value)
            
            # Add extracted text if available
            if result.extracted_text:
                response.extracted_text = result.extracted_text
            
            # Add UI elements
            for ui_element in result.ui_elements:
                element = response.ui_elements.add()
                element.type = ui_element.type
                element.confidence = ui_element.confidence
                
                if ui_element.bounds:
                    element.bounds.x = ui_element.bounds.x
                    element.bounds.y = ui_element.bounds.y
                    element.bounds.width = ui_element.bounds.width
                    element.bounds.height = ui_element.bounds.height
                
                for prop_key, prop_value in ui_element.properties.items():
                    element.properties[prop_key] = str(prop_value)
            
            # Add tags
            response.tags.extend(result.tags)
            
            logger.info(f"Inference completed in {processing_time:.2f}s, confidence: {result.confidence:.2f}")
            return response
            
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
            logger.error(traceback.format_exc())
            
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Inference failed: {str(e)}")
            return vision_service_pb2.VisionInferenceResponse(
                success=False,
                error=str(e)
            )
    
    def GetAvailableModels(self, request, context):
        """
        Get list of available vision models
        """
        try:
            models = vision_processor.get_available_models()
            
            response = vision_service_pb2.ModelsResponse()
            
            for model_name, model_info in models.items():
                model = response.models.add()
                model.name = model_name
                model.display_name = model_info.get('display_name', model_name)
                model.description = model_info.get('description', '')
                model.available = model_info.get('available', False)
                model.memory_usage_mb = model_info.get('memory_usage_mb', 0)
                model.supported_types.extend(model_info.get('supported_types', []))
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get available models: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get models: {str(e)}")
            return vision_service_pb2.ModelsResponse()
    
    def GetModelMetrics(self, request, context):
        """
        Get performance metrics for a specific model
        """
        try:
            metrics = vision_processor.get_model_metrics(request.model)
            
            response = vision_service_pb2.ModelMetricsResponse(
                model=request.model,
                total_inferences=metrics.get('total_inferences', 0),
                average_processing_time=metrics.get('average_processing_time', 0.0),
                average_confidence=metrics.get('average_confidence', 0.0),
                memory_usage_mb=metrics.get('memory_usage_mb', 0),
                gpu_utilization=metrics.get('gpu_utilization', 0.0)
            )
            
            for key, value in metrics.get('additional_metrics', {}).items():
                response.additional_metrics[key] = float(value)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get model metrics: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get metrics: {str(e)}")
            return vision_service_pb2.ModelMetricsResponse()
    
    def GetHealth(self, request, context):
        """
        Health check endpoint
        """
        try:
            uptime = int(time.time() - self.start_time)
            
            # Check if models are loaded and ready
            health_status = vision_processor.check_health()
            
            response = vision_service_pb2.HealthResponse(
                healthy=health_status.get('healthy', False),
                status=health_status.get('status', 'UNKNOWN'),
                uptime_seconds=uptime,
                version="1.0.0"
            )
            
            # Add health details
            for key, value in health_status.get('details', {}).items():
                response.details[key] = str(value)
            
            response.details['inference_count'] = str(self.inference_count)
            response.details['uptime_seconds'] = str(uptime)
            
            return response
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return vision_service_pb2.HealthResponse(
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
        futures.ThreadPoolExecutor(max_workers=4),
        options=[
            ('grpc.keepalive_time_ms', 30000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.keepalive_permit_without_calls', True),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.http2.min_time_between_pings_ms', 10000),
            ('grpc.http2.min_ping_interval_without_data_ms', 300000),
            ('grpc.max_receive_message_length', 16 * 1024 * 1024),  # 16MB
            ('grpc.max_send_message_length', 16 * 1024 * 1024),     # 16MB
        ]
    )
    
    vision_service_pb2_grpc.add_VisionServiceServicer_to_server(
        VisionServiceImpl(), server
    )
    
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting Vision AI gRPC server on {listen_addr}")
    logger.info("Service ready for pure model inference operations")
    
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down Vision AI gRPC server...")
        server.stop(grace=5)

if __name__ == '__main__':
    serve()
