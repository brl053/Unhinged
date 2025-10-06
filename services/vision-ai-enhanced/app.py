#!/usr/bin/env python3
"""
Enhanced Vision AI Service - Flask HTTP API
Provides advanced image analysis with multiple models and contextual understanding
"""

import os
import logging
import tempfile
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import torch
from typing import Dict, Any, Optional
import time
import json

from models.model_manager import model_manager, ModelType
from processors.vision_processor import vision_processor, VisionRequest, AnalysisType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = '/app/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Service state
service_ready = False
startup_time = None

def initialize_service():
    """Initialize the vision service with models"""
    global service_ready, startup_time
    
    try:
        logger.info("🔥 Initializing Enhanced Vision AI Service...")
        startup_time = time.time()
        
        # Load primary model (Qwen2-VL-7B)
        logger.info("Loading primary model: Qwen2-VL-7B-Instruct...")
        primary_result = model_manager.load_model(ModelType.QWEN2_VL_7B, quantize=True)
        
        if not primary_result.success:
            logger.warning(f"Failed to load primary model: {primary_result.error}")
            
            # Try loading BLIP as fallback
            logger.info("Loading fallback model: BLIP...")
            fallback_result = model_manager.load_model(ModelType.BLIP_BASE)
            
            if not fallback_result.success:
                logger.error(f"Failed to load fallback model: {fallback_result.error}")
                raise Exception("No models could be loaded")
        
        service_ready = True
        total_time = time.time() - startup_time
        logger.info(f"✅ Enhanced Vision AI Service ready in {total_time:.2f}s")
        
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        service_ready = False
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint"""
    try:
        system_status = model_manager.get_system_status()
        available_models = model_manager.get_available_models()
        
        health_data = {
            'status': 'healthy' if service_ready else 'initializing',
            'service': 'enhanced-vision-ai',
            'version': '2.0.0',
            'ready': service_ready,
            'startup_time': startup_time,
            'uptime': time.time() - startup_time if startup_time else 0,
            'system': system_status,
            'models': available_models,
            'capabilities': [
                'advanced-image-analysis',
                'screenshot-understanding',
                'ui-component-analysis',
                'ocr-extraction',
                'contextual-analysis',
                'multi-model-support'
            ]
        }
        
        return jsonify(health_data), 200 if service_ready else 503
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'service': 'enhanced-vision-ai'
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """Enhanced image analysis endpoint"""
    if not service_ready:
        return jsonify({'error': 'Service not ready'}), 503
    
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400

        # Get analysis parameters
        analysis_type = request.form.get('analysis_type', 'screenshot')
        prompt = request.form.get('prompt')
        max_tokens = int(request.form.get('max_tokens', 512))
        temperature = float(request.form.get('temperature', 0.1))
        preferred_model = request.form.get('preferred_model')
        context_json = request.form.get('context')
        
        # Parse context if provided
        context = None
        if context_json:
            try:
                context = json.loads(context_json)
            except json.JSONDecodeError:
                logger.warning("Invalid context JSON provided")

        # Save and load image
        temp_path = os.path.join(UPLOAD_FOLDER, f"temp_{int(time.time())}_{image_file.filename}")
        image_file.save(temp_path)
        
        try:
            image = Image.open(temp_path).convert('RGB')
            
            # Create vision request
            vision_request = VisionRequest(
                image=image,
                analysis_type=AnalysisType(analysis_type),
                prompt=prompt,
                context=context,
                max_tokens=max_tokens,
                temperature=temperature,
                preferred_model=ModelType(preferred_model) if preferred_model else None
            )
            
            # Process image
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(vision_processor.analyze_image(vision_request))
            loop.close()
            
            # Clean up
            os.remove(temp_path)
            
            # Return results
            return jsonify({
                'success': True,
                'description': result.description,
                'analysis_type': result.analysis_type.value,
                'model_used': result.model_used,
                'confidence': result.confidence,
                'processing_time': result.processing_time,
                'metadata': result.metadata,
                'extracted_text': result.extracted_text,
                'ui_elements': result.ui_elements,
                'tags': result.tags
            }), 200
            
        finally:
            # Ensure cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except ValueError as e:
        logger.error(f"Invalid request parameters: {e}")
        return jsonify({'error': f'Invalid parameters: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/describe', methods=['POST'])
def describe_image():
    """Simplified image description endpoint for backward compatibility"""
    if not service_ready:
        return jsonify({'error': 'Service not ready'}), 503
    
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        prompt = request.form.get('prompt', 'Describe this image in detail.')
        
        # Save and load image
        temp_path = os.path.join(UPLOAD_FOLDER, f"desc_{int(time.time())}_{image_file.filename}")
        image_file.save(temp_path)
        
        try:
            image = Image.open(temp_path).convert('RGB')
            
            # Create simple vision request
            vision_request = VisionRequest(
                image=image,
                analysis_type=AnalysisType.NATURAL_IMAGE,
                prompt=prompt,
                max_tokens=256
            )
            
            # Process image
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(vision_processor.analyze_image(vision_request))
            loop.close()
            
            # Clean up
            os.remove(temp_path)
            
            return jsonify({
                'description': result.description,
                'model_used': result.model_used,
                'confidence': result.confidence,
                'processing_time': result.processing_time
            }), 200
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logger.error(f"Image description failed: {e}")
        return jsonify({'error': f'Description failed: {str(e)}'}), 500

@app.route('/screenshot', methods=['POST'])
def analyze_screenshot():
    """Specialized screenshot analysis endpoint"""
    if not service_ready:
        return jsonify({'error': 'Service not ready'}), 503
    
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        context_json = request.form.get('context')
        
        # Parse context
        context = {}
        if context_json:
            try:
                context = json.loads(context_json)
            except json.JSONDecodeError:
                pass
        
        # Add screenshot-specific context
        context.update({
            'analysis_focus': 'ui_elements_and_workflow',
            'extract_text': True,
            'identify_interactive_elements': True
        })
        
        # Save and load image
        temp_path = os.path.join(UPLOAD_FOLDER, f"screenshot_{int(time.time())}_{image_file.filename}")
        image_file.save(temp_path)
        
        try:
            image = Image.open(temp_path).convert('RGB')
            
            vision_request = VisionRequest(
                image=image,
                analysis_type=AnalysisType.SCREENSHOT,
                context=context,
                max_tokens=1024,
                temperature=0.1
            )
            
            # Process screenshot
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(vision_processor.analyze_image(vision_request))
            loop.close()
            
            # Clean up
            os.remove(temp_path)
            
            return jsonify({
                'success': True,
                'analysis': result.description,
                'extracted_text': result.extracted_text,
                'ui_elements': result.ui_elements,
                'tags': result.tags,
                'model_used': result.model_used,
                'confidence': result.confidence,
                'processing_time': result.processing_time,
                'metadata': result.metadata
            }), 200
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logger.error(f"Screenshot analysis failed: {e}")
        return jsonify({'error': f'Screenshot analysis failed: {str(e)}'}), 500

if __name__ == '__main__':
    # Initialize service
    initialize_service()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=8001, debug=False)
