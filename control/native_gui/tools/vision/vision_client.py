
import logging; gui_logger = logging.getLogger(__name__)

"""
Vision Service Client for AI-powered image analysis
Integrates with vision service via gRPC for object detection, OCR, and image understanding.
"""

import grpc
import sys
import os
import base64
import time
from typing import Optional, Dict, List, Any
from pathlib import Path
import numpy as np
import cv2

# Add the generated clients to the path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent / "generated" / "python" / "clients"))

# Import protobuf clients
try:
    from unhinged_proto_clients import vision_service_pb2, vision_service_pb2_grpc, common_pb2
    VISION_PROTO_AVAILABLE = True
    gui_logger.info(" Vision protobuf clients available", {"event_type": "activation"})
except ImportError as e:
    gui_logger.warn(f" Vision protobuf clients not available: {e}")
    VISION_PROTO_AVAILABLE = False


class VisionClient:
    """Client for vision AI service"""
    
    def __init__(self, host: str = "localhost", port: int = 1192):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
        self.available_models = []
        
        self._setup_grpc_connection()
    
    def _setup_grpc_connection(self):
        """Setup gRPC connection to vision service"""
        if not VISION_PROTO_AVAILABLE:
            gui_logger.error(" Vision protobuf clients not available")
            return
        
        try:
            # Create gRPC channel
            self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
            
            # Test connection with timeout
            grpc.channel_ready_future(self.channel).result(timeout=5)
            
            # Create service stub
            self.stub = vision_service_pb2_grpc.VisionServiceStub(self.channel)
            
            # Test service health
            health_response = self.stub.GetHealth(vision_service_pb2.Empty())
            
            if health_response.healthy:
                
                # Load available models
                self._load_available_models()
            else:
                gui_logger.warn(f" Vision service unhealthy: {health_response.status}")
                
        except grpc.RpcError as e:
            gui_logger.error(f" gRPC connection failed: {e}")
            self.channel = None
            self.stub = None
        except Exception as e:
            gui_logger.error(f" Vision service connection error: {e}")
            self.channel = None
            self.stub = None
    
    def _load_available_models(self):
        """Load list of available vision models"""
        try:
            if not self.stub:
                return
            
            response = self.stub.GetAvailableModels(vision_service_pb2.Empty())
            self.available_models = []
            
            for model_info in response.models:
                model = {
                    'name': model_info.name,
                    'display_name': model_info.display_name,
                    'description': model_info.description,
                    'available': model_info.available,
                    'memory_usage_mb': model_info.memory_usage_mb,
                    'supported_types': list(model_info.supported_types)
                }
                self.available_models.append(model)
            
            for model in self.available_models[:3]:  # Show first 3
                status = "✅" if model['available'] else "❌"
                
        except Exception as e:
            gui_logger.warn(f" Failed to load models: {e}")
    
    def is_connected(self) -> bool:
        """Check if connected to vision service"""
        return self.channel is not None and self.stub is not None
    
    def analyze_image(self, image_data: bytes, prompt: str = "Describe this image", 
                     model: str = "qwen2-vl", analysis_type: str = "natural_image") -> Dict[str, Any]:
        """Analyze image using vision AI"""
        if not self.is_connected():
            return {
                'success': False,
                'error': 'Not connected to vision service',
                'description': '',
                'confidence': 0.0
            }
        
        try:
            # Create inference request
            request = vision_service_pb2.VisionInferenceRequest()
            request.image_data = image_data
            request.model = model
            request.prompt = prompt
            request.analysis_type = analysis_type
            request.max_tokens = 500
            request.temperature = 0.7
            
            # Call vision service
            response = self.stub.Infer(request)
            
            # Convert response to dict
            result = {
                'success': response.success,
                'description': response.description,
                'confidence': response.confidence,
                'model_used': response.model_used,
                'processing_time': response.processing_time,
                'extracted_text': response.extracted_text,
                'tags': list(response.tags),
                'error': response.error,
                'metadata': dict(response.metadata)
            }
            
            # Convert UI elements
            result['ui_elements'] = []
            for ui_element in response.ui_elements:
                element = {
                    'type': ui_element.type,
                    'confidence': ui_element.confidence,
                    'bounds': {
                        'x': ui_element.bounds.x,
                        'y': ui_element.bounds.y,
                        'width': ui_element.bounds.width,
                        'height': ui_element.bounds.height
                    },
                    'properties': dict(ui_element.properties)
                }
                result['ui_elements'].append(element)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Vision analysis failed: {str(e)}',
                'description': '',
                'confidence': 0.0
            }
    
    def analyze_frame(self, frame: np.ndarray, prompt: str = "Describe this image", 
                     model: str = "qwen2-vl") -> Dict[str, Any]:
        """Analyze OpenCV frame using vision AI"""
        try:
            # Convert frame to JPEG bytes
            _, buffer = cv2.imencode('.jpg', frame)
            image_bytes = buffer.tobytes()
            
            return self.analyze_image(image_bytes, prompt, model, "natural_image")
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Frame analysis failed: {str(e)}',
                'description': '',
                'confidence': 0.0
            }
    
    def analyze_screenshot(self, image_data: bytes, prompt: str = "Describe this screenshot") -> Dict[str, Any]:
        """Analyze screenshot for UI elements and content"""
        return self.analyze_image(image_data, prompt, "qwen2-vl", "screenshot")
    
    def extract_text_ocr(self, image_data: bytes) -> Dict[str, Any]:
        """Extract text from image using OCR"""
        return self.analyze_image(image_data, "Extract all text from this image", "qwen2-vl", "document")
    
    def detect_ui_elements(self, image_data: bytes) -> Dict[str, Any]:
        """Detect UI elements in screenshot"""
        return self.analyze_image(image_data, "Identify all UI elements, buttons, inputs, and interactive components", 
                                "qwen2-vl", "ui_component")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available vision models"""
        return self.available_models.copy()
    
    def get_model_metrics(self, model: str) -> Dict[str, Any]:
        """Get performance metrics for a model"""
        if not self.is_connected():
            return {}
        
        try:
            request = vision_service_pb2.ModelMetricsRequest()
            request.model = model
            
            response = self.stub.GetModelMetrics(request)
            
            return {
                'model': response.model,
                'total_inferences': response.total_inferences,
                'average_processing_time': response.average_processing_time,
                'average_confidence': response.average_confidence,
                'memory_usage_mb': response.memory_usage_mb,
                'gpu_utilization': response.gpu_utilization,
                'additional_metrics': dict(response.additional_metrics)
            }
            
        except Exception as e:
            gui_logger.warn(f" Failed to get model metrics: {e}")
            return {}
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get vision service information"""
        info = {
            'connected': self.is_connected(),
            'host': self.host,
            'port': self.port,
            'available_models': len(self.available_models),
            'proto_available': VISION_PROTO_AVAILABLE
        }
        
        if self.is_connected():
            try:
                health_response = self.stub.GetHealth(vision_service_pb2.Empty())
                info.update({
                    'healthy': health_response.healthy,
                    'status': health_response.status,
                    'uptime_seconds': health_response.uptime_seconds,
                    'version': health_response.version,
                    'details': dict(health_response.details)
                })
            except Exception as e:
                info['health_error'] = str(e)
        
        return info
    
    def close(self):
        """Close gRPC connection"""
        if self.channel:
            self.channel.close()
            self.channel = None
            self.stub = None
            gui_logger.info(" Vision service connection closed", {"event_type": "activation"})


# Test function
def test_vision_client():
    """Test vision client functionality"""
    gui_logger.info(" Testing vision client...", {"event_type": "activation"})
    
    try:
        client = VisionClient()
        
        # Test connection
        info = client.get_service_info()
        
        # Test with dummy image if connected
        if client.is_connected():
            # Create test image
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            cv2.putText(test_image, 'TEST', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            result = client.analyze_frame(test_image, "What do you see?")
        
        client.close()
        gui_logger.info(" Vision client test completed", {"status": "success"})
        
    except Exception as e:
        gui_logger.error(f" Vision client test failed: {e}")


if __name__ == "__main__":
    test_vision_client()
