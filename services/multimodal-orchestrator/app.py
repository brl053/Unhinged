#!/usr/bin/env python3
"""
Multimodal Orchestrator Service - Flask HTTP API
Provides unified multimodal analysis workflows
"""

import os
import logging
import time
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any
import json
import base64
from io import BytesIO
from PIL import Image

from orchestrator import orchestrator, AnalysisRequest, WorkflowType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Service state
service_ready = False
startup_time = None

def initialize_service():
    """Initialize the multimodal orchestrator service"""
    global service_ready, startup_time
    
    try:
        logger.info("🔥 Initializing Multimodal Orchestrator Service...")
        startup_time = time.time()
        
        # The orchestrator initializes automatically
        # Wait a moment for initial health checks
        time.sleep(2)
        
        service_ready = True
        total_time = time.time() - startup_time
        logger.info(f"✅ Multimodal Orchestrator Service ready in {total_time:.2f}s")
        
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        service_ready = False
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        service_health = orchestrator.get_service_health()
        workflow_stats = orchestrator.get_workflow_stats()
        
        health_data = {
            'status': 'healthy' if service_ready else 'initializing',
            'service': 'multimodal-orchestrator',
            'version': '1.0.0',
            'ready': service_ready,
            'startup_time': startup_time,
            'uptime': time.time() - startup_time if startup_time else 0,
            'connected_services': service_health,
            'workflow_stats': workflow_stats,
            'capabilities': [
                'basic-analysis',
                'contextual-analysis',
                'iterative-refinement',
                'multi-model-consensus',
                'service-orchestration',
                'workflow-management'
            ]
        }
        
        return jsonify(health_data), 200 if service_ready else 503
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'service': 'multimodal-orchestrator'
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """Main multimodal analysis endpoint"""
    if not service_ready:
        return jsonify({'error': 'Service not ready'}), 503
    
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400

        # Get parameters
        workflow_type = request.form.get('workflow_type', 'contextual_analysis')
        analysis_type = request.form.get('analysis_type', 'screenshot')
        base_prompt = request.form.get('base_prompt')
        max_iterations = int(request.form.get('max_iterations', 2))
        require_consensus = request.form.get('require_consensus', 'false').lower() == 'true'
        
        # Parse context hints if provided
        context_hints = {}
        if request.form.get('context_hints'):
            try:
                context_hints = json.loads(request.form.get('context_hints'))
            except json.JSONDecodeError:
                logger.warning("Invalid context_hints JSON provided")

        # Read image data
        image_data = image_file.read()
        
        # Map workflow type
        workflow_enum = WorkflowType.CONTEXTUAL_ANALYSIS
        if workflow_type == 'basic_analysis':
            workflow_enum = WorkflowType.BASIC_ANALYSIS
        elif workflow_type == 'iterative_refinement':
            workflow_enum = WorkflowType.ITERATIVE_REFINEMENT
        elif workflow_type == 'multi_model_consensus':
            workflow_enum = WorkflowType.MULTI_MODEL_CONSENSUS
        
        # Create analysis request
        analysis_request = AnalysisRequest(
            image_data=image_data,
            workflow_type=workflow_enum,
            analysis_type=analysis_type,
            base_prompt=base_prompt,
            context_hints=context_hints,
            max_iterations=max_iterations,
            require_consensus=require_consensus
        )
        
        # Run analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(orchestrator.analyze_image(analysis_request))
        loop.close()
        
        # Format response
        response_data = {
            'success': result.success,
            'description': result.description,
            'confidence': result.confidence,
            'processing_time': result.processing_time,
            'workflow_used': result.workflow_used.value,
            'models_used': result.models_used,
            'iterations': result.iterations,
            'metadata': result.metadata
        }
        
        if result.error:
            response_data['error'] = result.error
        
        return jsonify(response_data), 200 if result.success else 500
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/analyze-screenshot', methods=['POST'])
def analyze_screenshot():
    """Specialized screenshot analysis endpoint"""
    if not service_ready:
        return jsonify({'error': 'Service not ready'}), 503
    
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        
        # Get optional parameters
        workflow_type = request.form.get('workflow_type', 'contextual_analysis')
        context_hints = {}
        
        if request.form.get('context_hints'):
            try:
                context_hints = json.loads(request.form.get('context_hints'))
            except json.JSONDecodeError:
                pass
        
        # Add screenshot-specific context
        context_hints.update({
            'analysis_focus': 'ui_elements_and_workflow',
            'extract_text': True,
            'identify_interactive_elements': True
        })
        
        # Read image data
        image_data = image_file.read()
        
        # Create analysis request optimized for screenshots
        analysis_request = AnalysisRequest(
            image_data=image_data,
            workflow_type=WorkflowType(workflow_type),
            analysis_type='screenshot',
            base_prompt="Analyze this screenshot focusing on UI elements, layout, text content, and user workflow. Identify all interactive elements and describe the current state of the interface.",
            context_hints=context_hints,
            max_iterations=2
        )
        
        # Run analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(orchestrator.analyze_image(analysis_request))
        loop.close()
        
        return jsonify({
            'success': result.success,
            'analysis': result.description,
            'confidence': result.confidence,
            'processing_time': result.processing_time,
            'workflow_used': result.workflow_used.value,
            'models_used': result.models_used,
            'iterations': result.iterations,
            'metadata': result.metadata,
            'error': result.error
        }), 200 if result.success else 500
        
    except Exception as e:
        logger.error(f"Screenshot analysis failed: {e}")
        return jsonify({'error': f'Screenshot analysis failed: {str(e)}'}), 500

@app.route('/workflows', methods=['GET'])
def list_workflows():
    """List available analysis workflows"""
    workflows = [
        {
            'type': 'basic_analysis',
            'name': 'Basic Analysis',
            'description': 'Simple image analysis using the best available vision model',
            'use_case': 'Quick analysis with minimal processing time'
        },
        {
            'type': 'contextual_analysis',
            'name': 'Contextual Analysis',
            'description': 'Enhanced analysis with project context and documentation',
            'use_case': 'Detailed analysis leveraging project knowledge'
        },
        {
            'type': 'iterative_refinement',
            'name': 'Iterative Refinement',
            'description': 'Multi-pass analysis for improved accuracy and detail',
            'use_case': 'High-quality analysis requiring maximum detail'
        },
        {
            'type': 'multi_model_consensus',
            'name': 'Multi-Model Consensus',
            'description': 'Analysis using multiple models for consensus results',
            'use_case': 'Critical analysis requiring high confidence'
        }
    ]
    
    return jsonify({
        'workflows': workflows,
        'default_workflow': 'contextual_analysis'
    }), 200

@app.route('/services', methods=['GET'])
def get_service_status():
    """Get status of connected services"""
    try:
        service_health = orchestrator.get_service_health()
        
        return jsonify({
            'services': service_health,
            'healthy_services': sum(1 for s in service_health.values() if s.get('healthy', False)),
            'total_services': len(service_health)
        }), 200
        
    except Exception as e:
        logger.error(f"Service status retrieval failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get orchestrator statistics"""
    try:
        workflow_stats = orchestrator.get_workflow_stats()
        service_health = orchestrator.get_service_health()
        
        return jsonify({
            'service_uptime': time.time() - startup_time if startup_time else 0,
            'workflow_stats': workflow_stats,
            'service_health': service_health,
            'total_requests': sum(stats.get('total_requests', 0) for stats in workflow_stats.values()),
            'success_rate': sum(stats.get('successful_requests', 0) for stats in workflow_stats.values()) / max(sum(stats.get('total_requests', 0) for stats in workflow_stats.values()), 1)
        }), 200
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test-workflow', methods=['POST'])
def test_workflow():
    """Test a specific workflow with a sample image"""
    if not service_ready:
        return jsonify({'error': 'Service not ready'}), 503
    
    try:
        data = request.get_json()
        workflow_type = data.get('workflow_type', 'basic_analysis')
        
        # Create a simple test image (1x1 pixel)
        from PIL import Image
        test_image = Image.new('RGB', (1, 1), color='white')
        img_buffer = BytesIO()
        test_image.save(img_buffer, format='JPEG')
        image_data = img_buffer.getvalue()
        
        # Create test request
        analysis_request = AnalysisRequest(
            image_data=image_data,
            workflow_type=WorkflowType(workflow_type),
            analysis_type='natural_image',
            base_prompt="This is a test image.",
            max_iterations=1
        )
        
        # Run test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(orchestrator.analyze_image(analysis_request))
        loop.close()
        
        return jsonify({
            'test_success': result.success,
            'workflow_tested': workflow_type,
            'processing_time': result.processing_time,
            'models_available': result.models_used,
            'error': result.error
        }), 200
        
    except Exception as e:
        logger.error(f"Workflow test failed: {e}")
        return jsonify({'error': f'Workflow test failed: {str(e)}'}), 500

if __name__ == '__main__':
    # Initialize service
    initialize_service()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=8003, debug=False)
