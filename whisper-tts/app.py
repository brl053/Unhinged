#!/usr/bin/env python3
"""
Whisper TTS Service for Unhinged Project
Provides both Speech-to-Text (Whisper) and Text-to-Speech (gTTS) capabilities
"""

import os
import tempfile
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from gtts import gTTS
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
            'service': 'whisper-tts',
            'version': '1.0.0',
            'capabilities': ['speech-to-text', 'text-to-speech']
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'service': 'whisper-tts'
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

@app.route('/synthesize', methods=['POST'])
def synthesize_speech():
    """Convert text to speech using gTTS"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        language = data.get('language', 'en')
        
        # Generate speech using gTTS
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            tts.save(temp_file.name)
            
            return send_file(
                temp_file.name,
                as_attachment=True,
                download_name='speech.mp3',
                mimetype='audio/mpeg'
            )
            
    except Exception as e:
        logger.error(f"Speech synthesis failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/info', methods=['GET'])
def service_info():
    """Get service information"""
    return jsonify({
        'service': 'whisper-tts',
        'version': '1.0.0',
        'capabilities': ['speech-to-text', 'text-to-speech'],
        'whisper_model': 'base',
        'tts_engine': 'gTTS',
        'supported_languages': ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh']
    }), 200

if __name__ == '__main__':
    logger.info("Starting Whisper TTS Service...")

    # Load Whisper model on startup
    if not load_whisper_model():
        logger.error("Failed to load Whisper model, exiting...")
        exit(1)

    logger.info("Whisper TTS Service ready!")

    # Run the Flask app
    app.run(host='0.0.0.0', port=8000, debug=False)
