#!/usr/bin/env python3
"""
Multimodal AI API Gateway
Unified API endpoint for the multimodal AI processing pipeline
"""

import os
import logging
import time
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Service configuration
SERVICES = {
    'orchestrator': {
        'url': os.getenv('ORCHESTRATOR_URL', 'http://localhost:8003'),
        'timeout': 300
    },
    'vision': {
        'url': os.getenv('VISION_URL', 'http://localhost:8001'),
        'timeout': 180
    },
    'context': {
        'url': os.getenv('CONTEXT_URL', 'http://localhost:8002'),
        'timeout': 60
    }
}

# Global HTTP client
http_client = httpx.AsyncClient(timeout=300.0)

@app.route('/health', methods=['GET'])
def health_check():
    """API Gateway health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'multimodal-api-gateway',
        'version': '1.0.0',
        'timestamp': time.time(),
        'services': SERVICES
    }), 200

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """
    Main multimodal analysis endpoint
    Routes to the orchestrator service
    """
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400

        # Prepare form data for forwarding
        files = {'image': (image_file.filename, image_file.read(), image_file.content_type)}
        
        # Get form parameters
        form_data = {}
        for key in request.form:
            form_data[key] = request.form[key]
        
        # Set default workflow if not specified
        if 'workflow_type' not in form_data:
            form_data['workflow_type'] = 'contextual_analysis'
        
        # Forward to orchestrator
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            forward_to_service('orchestrator', '/analyze', files=files, data=form_data)
        )
        loop.close()
        
        return jsonify(result), 200 if result.get('success', False) else 500
        
    except Exception as e:
        logger.error(f"Analysis request failed: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/analyze-screenshot', methods=['POST'])
def analyze_screenshot():
    """
    Specialized screenshot analysis endpoint
    Optimized for UI/screenshot analysis
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        files = {'image': (image_file.filename, image_file.read(), image_file.content_type)}
        
        # Prepare screenshot-optimized parameters
        form_data = {
            'workflow_type': request.form.get('workflow_type', 'contextual_analysis'),
            'analysis_type': 'screenshot',
            'context_hints': json.dumps({
                'ui_analysis': True,
                'extract_text': True,
                'identify_components': True
            })
        }
        
        # Add any additional form data
        for key in request.form:
            if key not in form_data:
                form_data[key] = request.form[key]
        
        # Forward to orchestrator
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            forward_to_service('orchestrator', '/analyze-screenshot', files=files, data=form_data)
        )
        loop.close()
        
        return jsonify(result), 200 if result.get('success', False) else 500
        
    except Exception as e:
        logger.error(f"Screenshot analysis failed: {e}")
        return jsonify({'error': f'Screenshot analysis failed: {str(e)}'}), 500

@app.route('/vision/analyze', methods=['POST'])
def direct_vision_analysis():
    """
    Direct access to vision service
    Bypasses orchestrator for simple analysis
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        files = {'image': (image_file.filename, image_file.read(), image_file.content_type)}
        
        # Get form parameters
        form_data = {}
        for key in request.form:
            form_data[key] = request.form[key]
        
        # Forward to vision service
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            forward_to_service('vision', '/analyze', files=files, data=form_data)
        )
        loop.close()
        
        return jsonify(result), 200 if result.get('success', False) else 500
        
    except Exception as e:
        logger.error(f"Direct vision analysis failed: {e}")
        return jsonify({'error': f'Vision analysis failed: {str(e)}'}), 500

@app.route('/context/generate-prompt', methods=['POST'])
def generate_contextual_prompt():
    """
    Generate contextual prompt using LLM service
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Forward to context service
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            forward_to_service('context', '/generate-prompt', json_data=data)
        )
        loop.close()
        
        return jsonify(result), 200 if result.get('success', False) else 500
        
    except Exception as e:
        logger.error(f"Prompt generation failed: {e}")
        return jsonify({'error': f'Prompt generation failed: {str(e)}'}), 500

@app.route('/context/search', methods=['POST'])
def search_context():
    """
    Search project context and documentation
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query parameter required'}), 400
        
        # Forward to context service
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            forward_to_service('context', '/search-context', json_data=data)
        )
        loop.close()
        
        return jsonify(result), 200 if result.get('success', False) else 500
        
    except Exception as e:
        logger.error(f"Context search failed: {e}")
        return jsonify({'error': f'Context search failed: {str(e)}'}), 500

@app.route('/workflows', methods=['GET'])
def list_workflows():
    """
    List available analysis workflows
    """
    try:
        # Forward to orchestrator
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            forward_to_service('orchestrator', '/workflows')
        )
        loop.close()
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Workflow listing failed: {e}")
        return jsonify({'error': f'Workflow listing failed: {str(e)}'}), 500

@app.route('/service-status', methods=['GET'])
def get_service_status():
    """
    Get status of all backend services
    """
    try:
        # Check each service
        service_status = {}
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        for service_name, config in SERVICES.items():
            try:
                result = loop.run_until_complete(
                    forward_to_service(service_name, '/health')
                )
                service_status[service_name] = {
                    'status': 'healthy',
                    'url': config['url'],
                    'response': result
                }
            except Exception as e:
                service_status[service_name] = {
                    'status': 'unhealthy',
                    'url': config['url'],
                    'error': str(e)
                }
        
        loop.close()
        
        healthy_count = sum(1 for s in service_status.values() if s['status'] == 'healthy')
        
        return jsonify({
            'gateway_status': 'healthy',
            'services': service_status,
            'healthy_services': healthy_count,
            'total_services': len(SERVICES),
            'overall_health': 'healthy' if healthy_count == len(SERVICES) else 'degraded'
        }), 200
        
    except Exception as e:
        logger.error(f"Service status check failed: {e}")
        return jsonify({'error': f'Service status check failed: {str(e)}'}), 500

@app.route('/api-docs', methods=['GET'])
def api_documentation():
    """
    API documentation endpoint
    """
    docs = {
        'title': 'Multimodal AI Processing Pipeline API',
        'version': '1.0.0',
        'description': 'Unified API for advanced image analysis with contextual understanding',
        'endpoints': {
            'POST /analyze': {
                'description': 'Main multimodal analysis endpoint',
                'parameters': {
                    'image': 'Image file (required)',
                    'workflow_type': 'Analysis workflow (basic_analysis, contextual_analysis, iterative_refinement, multi_model_consensus)',
                    'analysis_type': 'Type of analysis (screenshot, natural_image, document, ui_component)',
                    'base_prompt': 'Custom analysis prompt (optional)',
                    'max_iterations': 'Maximum refinement iterations (default: 2)',
                    'context_hints': 'JSON object with context hints'
                },
                'example': 'curl -X POST -F "image=@screenshot.png" -F "workflow_type=contextual_analysis" http://localhost:8000/analyze'
            },
            'POST /analyze-screenshot': {
                'description': 'Specialized screenshot analysis',
                'parameters': {
                    'image': 'Screenshot image file (required)',
                    'workflow_type': 'Analysis workflow (optional, defaults to contextual_analysis)'
                },
                'example': 'curl -X POST -F "image=@screenshot.png" http://localhost:8000/analyze-screenshot'
            },
            'POST /vision/analyze': {
                'description': 'Direct vision service access',
                'parameters': {
                    'image': 'Image file (required)',
                    'analysis_type': 'Type of analysis',
                    'prompt': 'Analysis prompt (optional)'
                }
            },
            'POST /context/generate-prompt': {
                'description': 'Generate contextual analysis prompt',
                'parameters': {
                    'base_prompt': 'Base prompt text',
                    'analysis_type': 'Type of analysis',
                    'context_types': 'Array of context types to include'
                }
            },
            'GET /workflows': {
                'description': 'List available analysis workflows'
            },
            'GET /service-status': {
                'description': 'Get status of all backend services'
            },
            'GET /health': {
                'description': 'API Gateway health check'
            }
        }
    }
    
    return jsonify(docs), 200

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def forward_to_service(
    service_name: str, 
    endpoint: str, 
    files: Optional[Dict] = None,
    data: Optional[Dict] = None,
    json_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Forward request to backend service with retry logic
    """
    service_config = SERVICES[service_name]
    url = f"{service_config['url']}{endpoint}"
    
    try:
        if files:
            # Multipart form request
            response = await http_client.post(
                url,
                files=files,
                data=data,
                timeout=service_config['timeout']
            )
        elif json_data:
            # JSON request
            response = await http_client.post(
                url,
                json=json_data,
                timeout=service_config['timeout']
            )
        else:
            # GET request
            response = await http_client.get(
                url,
                timeout=service_config['timeout']
            )
        
        response.raise_for_status()
        return response.json()
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error forwarding to {service_name}: {e.response.status_code}")
        try:
            error_detail = e.response.json()
        except:
            error_detail = {'error': f'HTTP {e.response.status_code}'}
        raise Exception(f"Service {service_name} error: {error_detail}")
    
    except httpx.TimeoutException:
        logger.error(f"Timeout forwarding to {service_name}")
        raise Exception(f"Service {service_name} timeout")
    
    except Exception as e:
        logger.error(f"Error forwarding to {service_name}: {e}")
        raise Exception(f"Service {service_name} unavailable: {str(e)}")

if __name__ == '__main__':
    # Get configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"🚀 Multimodal AI API Gateway starting on {host}:{port}")
    
    # Start Flask server
    app.run(host=host, port=port, debug=debug, threaded=True)
