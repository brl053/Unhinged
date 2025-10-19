#!/usr/bin/env python3
"""
Speech-to-Text Service for Unhinged Project
Provides Speech-to-Text capabilities using OpenAI Whisper
"""

import os
import tempfile
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables
whisper_model = None
UPLOAD_FOLDER = '/app/uploads'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_whisper_model():
    """Load Whisper model on startup"""
    global whisper_model
    try:
        logger.info("Loading Whisper model...")
        # Use base model for faster startup, can be changed to larger models
        whisper_model = whisper.load_model("base")
        logger.info("Whisper model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {e}")
        return False

# Load Whisper model when module is imported
logger.info("Initializing Whisper TTS Service...")
if not load_whisper_model():
    logger.error("Failed to load Whisper model during initialization")
    # Don't exit here since we're being imported, just log the error

def ensure_model_loaded():
    """Ensure the Whisper model is loaded, load it if not"""
    global whisper_model
    if whisper_model is None:
        logger.info("Model not loaded, loading now...")
        load_whisper_model()
    return whisper_model is not None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check if Whisper model is loaded
        model_status = whisper_model is not None

        # Check CUDA availability
        cuda_available = torch.cuda.is_available()

        return jsonify({
            'status': 'healthy',
            'whisper_model_loaded': model_status,
            'cuda_available': cuda_available,
            'service': 'speech-to-text',
            'version': '1.0.0',
            'capabilities': ['speech-to-text']
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'service': 'speech-to-text'
        }), 500

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """Convert speech to text using Whisper"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400

        # Save uploaded file temporarily
        temp_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
        audio_file.save(temp_path)

        # Ensure model is loaded before transcribing
        global whisper_model
        if whisper_model is None:
            logger.info("Loading Whisper model on-demand...")
            if not load_whisper_model():
                return jsonify({'error': 'Whisper model failed to load'}), 500

        # Transcribe using Whisper
        result = whisper_model.transcribe(temp_path)

        # Clean up temporary file
        os.remove(temp_path)

        return jsonify({
            'text': result['text'],
            'language': result.get('language', 'unknown')
        }), 200

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return jsonify({'error': str(e)}), 500

# TTS functionality removed - now handled by dedicated text-to-speech service

@app.route('/info', methods=['GET'])
def service_info():
    """Get service information"""
    return jsonify({
        'service': 'speech-to-text',
        'version': '1.0.0',
        'capabilities': ['speech-to-text'],
        'whisper_model': 'base',
        'supported_languages': ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh'],
        'endpoints': {
            '/transcribe': 'POST - Convert speech to text',
            '/health': 'GET - Health check',
            '/info': 'GET - Service information'
        }
    }), 200

if __name__ == '__main__':
    logger.info("Starting Speech-to-Text Service...")

    # Load Whisper model on startup
    if not load_whisper_model():
        logger.error("Failed to load Whisper model, exiting...")
        exit(1)

    logger.info("Speech-to-Text Service ready!")

    # Run the Flask app
    app.run(host='0.0.0.0', port=8000, debug=False)
