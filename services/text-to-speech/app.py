#!/usr/bin/env python3
"""
Text-to-Speech Service for Unhinged Project
Provides local TTS capabilities using Coqui TTS
"""

import os
import tempfile
import logging
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables
tts_model = None
OUTPUT_FOLDER = '/app/outputs'

# Configuration
TTS_MODEL_NAME = os.getenv('TTS_MODEL_NAME', 'tts_models/en/ljspeech/tacotron2-DDC')
TTS_CACHE_DIR = os.getenv('TTS_CACHE_DIR', '/app/models')

# Ensure directories exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(TTS_CACHE_DIR, exist_ok=True)

def load_tts_model():
    """Load Coqui TTS model on startup"""
    global tts_model
    try:
        logger.info(f"Loading TTS model: {TTS_MODEL_NAME}")
        from TTS.api import TTS
        
        # Initialize TTS with model
        tts_model = TTS(
            model_name=TTS_MODEL_NAME,
            progress_bar=False,
            gpu=torch.cuda.is_available()
        )
        logger.info("TTS model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load TTS model: {e}")
        return False

def ensure_model_loaded():
    """Ensure the TTS model is loaded, load it if not"""
    global tts_model
    if tts_model is None:
        logger.info("Model not loaded, loading now...")
        load_tts_model()
    return tts_model is not None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'text-to-speech',
        'model_loaded': tts_model is not None,
        'model_name': TTS_MODEL_NAME,
        'gpu_available': torch.cuda.is_available()
    })

@app.route('/info', methods=['GET'])
def service_info():
    """Service information endpoint"""
    return jsonify({
        'service': 'text-to-speech',
        'version': '1.0.0',
        'description': 'Local Text-to-Speech using Coqui TTS',
        'model': TTS_MODEL_NAME,
        'endpoints': {
            '/synthesize': 'POST - Convert text to speech',
            '/health': 'GET - Health check',
            '/info': 'GET - Service information'
        }
    })

@app.route('/synthesize', methods=['POST'])
def synthesize_speech():
    """Convert text to speech using Coqui TTS"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        speaker = data.get('speaker', None)  # For multi-speaker models
        language = data.get('language', 'en')
        
        # Ensure model is loaded
        if not ensure_model_loaded():
            return jsonify({'error': 'TTS model failed to load'}), 500
        
        # Generate speech using Coqui TTS
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav', dir=OUTPUT_FOLDER) as temp_file:
            output_path = temp_file.name
            
            # Generate speech
            if speaker and hasattr(tts_model, 'speakers') and tts_model.speakers:
                # Multi-speaker model
                tts_model.tts_to_file(
                    text=text,
                    speaker=speaker,
                    file_path=output_path
                )
            else:
                # Single speaker model
                tts_model.tts_to_file(
                    text=text,
                    file_path=output_path
                )
            
            return send_file(
                output_path,
                as_attachment=True,
                download_name=f'speech_{hash(text)}.wav',
                mimetype='audio/wav'
            )
            
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        return jsonify({'error': f'Synthesis failed: {str(e)}'}), 500

@app.route('/speakers', methods=['GET'])
def get_speakers():
    """Get available speakers for multi-speaker models"""
    try:
        if not ensure_model_loaded():
            return jsonify({'error': 'TTS model not loaded'}), 500
            
        speakers = []
        if hasattr(tts_model, 'speakers') and tts_model.speakers:
            speakers = tts_model.speakers
            
        return jsonify({
            'speakers': speakers,
            'count': len(speakers),
            'model_supports_speakers': len(speakers) > 0
        })
        
    except Exception as e:
        logger.error(f"Error getting speakers: {e}")
        return jsonify({'error': f'Failed to get speakers: {str(e)}'}), 500

# Load TTS model when module is imported
logger.info("Initializing Text-to-Speech Service...")
if not load_tts_model():
    logger.error("Failed to load TTS model during initialization")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False, threaded=True)
