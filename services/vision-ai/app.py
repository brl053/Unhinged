#!/usr/bin/env python3
"""
Vision AI Service - Flask HTTP API
Provides image analysis, description, and processing capabilities
"""

import os
import logging
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import cv2
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = '/app/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global model variables
vision_model = None
vision_processor = None

def load_vision_model():
    """Load the vision model for image analysis"""
    global vision_model, vision_processor
    
    try:
        logger.info("Loading BLIP vision model...")
        vision_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        vision_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        
        # Move to GPU if available
        if torch.cuda.is_available():
            vision_model = vision_model.cuda()
            logger.info("Vision model loaded on GPU")
        else:
            logger.info("Vision model loaded on CPU")
            
    except Exception as e:
        logger.error(f"Failed to load vision model: {e}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check if vision model is loaded
        model_status = vision_model is not None and vision_processor is not None
        
        # Check CUDA availability
        cuda_available = torch.cuda.is_available()
        
        return jsonify({
            'status': 'healthy',
            'vision_model_loaded': model_status,
            'cuda_available': cuda_available,
            'service': 'vision-ai',
            'version': '1.0.0',
            'capabilities': ['image-analysis', 'image-description', 'object-detection']
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'service': 'vision-ai'
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """Analyze an uploaded image and return description"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400

        # Save uploaded file temporarily
        temp_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(temp_path)

        # Load and process image
        image = Image.open(temp_path).convert('RGB')
        
        # Generate description using BLIP
        inputs = vision_processor(image, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        with torch.no_grad():
            out = vision_model.generate(**inputs, max_length=50)
        
        description = vision_processor.decode(out[0], skip_special_tokens=True)
        
        # Get image metadata
        width, height = image.size
        
        # Clean up temporary file
        os.remove(temp_path)

        return jsonify({
            'description': description,
            'metadata': {
                'width': width,
                'height': height,
                'format': image.format or 'Unknown',
                'mode': image.mode
            }
        }), 200

    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        return jsonify({'error': f'Image analysis failed: {str(e)}'}), 500

@app.route('/describe', methods=['POST'])
def describe_image():
    """Generate detailed description of an uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400

        # Get optional prompt for conditional generation
        prompt = request.form.get('prompt', '')

        # Save uploaded file temporarily
        temp_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(temp_path)

        # Load and process image
        image = Image.open(temp_path).convert('RGB')
        
        # Generate description with optional prompt
        if prompt:
            inputs = vision_processor(image, prompt, return_tensors="pt")
        else:
            inputs = vision_processor(image, return_tensors="pt")
            
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        with torch.no_grad():
            out = vision_model.generate(**inputs, max_length=100, num_beams=5)
        
        description = vision_processor.decode(out[0], skip_special_tokens=True)
        
        # Clean up temporary file
        os.remove(temp_path)

        return jsonify({
            'description': description,
            'prompt_used': prompt if prompt else 'No prompt provided'
        }), 200

    except Exception as e:
        logger.error(f"Image description failed: {e}")
        return jsonify({'error': f'Image description failed: {str(e)}'}), 500

if __name__ == '__main__':
    # Load the vision model on startup
    load_vision_model()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=8001, debug=False)
