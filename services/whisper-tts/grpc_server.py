#!/usr/bin/env python3
"""
Whisper TTS gRPC Server - Proto-Compliant Implementation
Provides both Speech-to-Text (Whisper) and Text-to-Speech (gTTS) capabilities
following the audio.proto contract definitions.
"""

import os
import tempfile
import logging
import asyncio
import grpc
from concurrent import futures
from typing import Iterator, AsyncIterator
import io

# Audio processing imports
from gtts import gTTS
import whisper
import torch

# Generated proto imports
import audio_pb2
import audio_pb2_grpc
import common_pb2
from google.protobuf import timestamp_pb2
import time

def set_current_timestamp(timestamp_field):
    """Helper function to set current timestamp"""
    timestamp_field.seconds = int(time.time())
    timestamp_field.nanos = int((time.time() % 1) * 1e9)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioServiceServicer(audio_pb2_grpc.AudioServiceServicer):
    """
    gRPC Audio Service implementation following proto contracts
    
    Implements all methods defined in audio.proto:
    - TextToSpeech: Streaming TTS output
    - SpeechToText: Streaming STT input
    - ProcessAudioFile: Batch processing
    - Voice management operations
    - Health checks
    """
    
    def __init__(self):
        self.whisper_model = None
        self.upload_folder = '/app/uploads'
        os.makedirs(self.upload_folder, exist_ok=True)
        self._load_whisper_model()
    
    def _load_whisper_model(self):
        """Load Whisper model on startup"""
        try:
            logger.info("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.whisper_model = None
    
    def TextToSpeech(self, request: audio_pb2.TTSRequest, context) -> Iterator[common_pb2.StreamChunk]:
        """
        Convert text to speech with streaming output
        
        Args:
            request: TTSRequest with text, voice_id, and options
            context: gRPC context
            
        Yields:
            StreamChunk: Audio data chunks for streaming
        """
        try:
            logger.info(f"TTS request: {request.text[:50]}... (voice: {request.voice_id})")
            
            # Extract language from voice_id (simple mapping)
            language = self._extract_language_from_voice(request.voice_id)
            
            # Generate speech using gTTS
            tts = gTTS(text=request.text, lang=language, slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                tts.save(temp_file.name)
                
                # Read audio data
                with open(temp_file.name, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                # Clean up temporary file
                os.unlink(temp_file.name)
            
            # Create TTS chunk payload
            tts_payload = audio_pb2.TTSChunkPayload()
            tts_payload.tts_id = f"tts_{hash(request.text)}"
            tts_payload.chunk_index = 1
            tts_payload.progress_percent = 100.0
            
            # Create audio metadata
            audio_metadata = audio_pb2.AudioMetadata()
            audio_metadata.format = audio_pb2.AUDIO_FORMAT_MP3
            audio_metadata.sample_rate = request.sample_rate if request.sample_rate > 0 else 22050
            audio_metadata.channels = request.channels if request.channels > 0 else 1
            audio_metadata.duration_seconds = self._estimate_duration(len(audio_data))
            audio_metadata.total_bytes = len(audio_data)
            
            tts_payload.audio_metadata.CopyFrom(audio_metadata)
            
            # Create stream chunk
            chunk = common_pb2.StreamChunk()
            chunk.stream_id = tts_payload.tts_id
            chunk.sequence_number = 1
            chunk.type = common_pb2.CHUNK_TYPE_DATA
            chunk.data = audio_data
            chunk.is_final = True
            chunk.status = common_pb2.CHUNK_STATUS_COMPLETE
            set_current_timestamp(chunk.timestamp)
            
            # Set structured payload
            chunk.structured.update({
                "tts_payload": {
                    "tts_id": tts_payload.tts_id,
                    "chunk_index": tts_payload.chunk_index,
                    "progress_percent": tts_payload.progress_percent
                }
            })
            
            yield chunk
            
        except Exception as e:
            logger.error(f"TTS processing failed: {e}")
            # Yield error chunk
            error_chunk = common_pb2.StreamChunk()
            error_chunk.stream_id = f"error_{hash(request.text)}"
            error_chunk.sequence_number = 1
            error_chunk.type = common_pb2.CHUNK_TYPE_ERROR
            error_chunk.text = f"TTS processing failed: {str(e)}"
            error_chunk.is_final = True
            error_chunk.status = common_pb2.CHUNK_STATUS_ERROR
            set_current_timestamp(error_chunk.timestamp)
            yield error_chunk
    
    def SpeechToText(self, request_iterator: Iterator[common_pb2.StreamChunk], context) -> audio_pb2.STTResponse:
        """
        Convert speech to text from streaming input
        
        Args:
            request_iterator: Iterator of StreamChunk with audio data
            context: gRPC context
            
        Returns:
            STTResponse: Transcription result with metadata
        """
        try:
            logger.info("STT request received")
            
            # Collect audio chunks
            audio_data = io.BytesIO()
            chunk_count = 0
            
            for chunk in request_iterator:
                if chunk.type == common_pb2.CHUNK_TYPE_DATA:
                    audio_data.write(chunk.data)
                    chunk_count += 1
                    logger.debug(f"Received audio chunk {chunk.sequence_number}, size: {len(chunk.data)}")
            
            if chunk_count == 0:
                raise ValueError("No audio data received")
            
            # Save audio to temporary file for Whisper processing
            audio_bytes = audio_data.getvalue()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            try:
                # Transcribe using Whisper
                if self.whisper_model is None:
                    raise RuntimeError("Whisper model not loaded")
                
                result = self.whisper_model.transcribe(temp_file_path)
                
                # Create response
                response = audio_pb2.STTResponse()
                
                # Set standard response
                response.response.success = True
                response.response.message = "Transcription completed successfully"
                set_current_timestamp(response.response.timestamp)
                
                # Set transcription data
                response.transcript = result['text']
                response.confidence = 0.9  # Whisper doesn't provide confidence, use default
                
                # Create transcript segments
                if 'segments' in result:
                    for segment_data in result['segments']:
                        segment = audio_pb2.TranscriptSegment()
                        segment.text = segment_data.get('text', '')
                        segment.start_time = segment_data.get('start', 0.0)
                        segment.end_time = segment_data.get('end', 0.0)
                        segment.confidence = 0.9  # Default confidence
                        response.segments.append(segment)
                else:
                    # Create single segment if no segments provided
                    segment = audio_pb2.TranscriptSegment()
                    segment.text = result['text']
                    segment.start_time = 0.0
                    segment.end_time = self._estimate_duration(len(audio_bytes))
                    segment.confidence = 0.9
                    response.segments.append(segment)
                
                # Set usage metrics
                usage = common_pb2.AudioUsage()
                usage.duration.seconds = int(self._estimate_duration(len(audio_bytes)))
                usage.bytes_processed = len(audio_bytes)
                usage.sample_rate = 16000  # Default Whisper sample rate
                usage.channels = 1  # Mono
                usage.format = "wav"
                response.usage.CopyFrom(usage)
                
                # Set metadata
                metadata = audio_pb2.STTMetadata()
                metadata.model = "whisper-base"
                metadata.language = result.get('language', 'en')
                metadata.processing_time_ms = 0.0  # Not tracked yet
                metadata.signal_to_noise_ratio = 0.0  # Not calculated
                metadata.speech_rate_wpm = 0.0  # Not calculated
                metadata.detected_languages.append(result.get('language', 'en'))
                metadata.has_background_noise = False  # Not detected
                metadata.has_multiple_speakers = False  # Not detected
                metadata.detected_quality = audio_pb2.AUDIO_QUALITY_STANDARD
                response.metadata.CopyFrom(metadata)
                
                return response
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"STT processing failed: {e}")
            # Return error response
            response = audio_pb2.STTResponse()
            response.response.success = False
            response.response.message = f"STT processing failed: {str(e)}"
            set_current_timestamp(response.response.timestamp)
            return response
    
    def ProcessAudioFile(self, request: audio_pb2.ProcessAudioRequest, context) -> audio_pb2.ProcessAudioResponse:
        """
        Process audio file for batch operations
        
        Args:
            request: ProcessAudioRequest with audio file and processing type
            context: gRPC context
            
        Returns:
            ProcessAudioResponse: Processing result
        """
        try:
            logger.info(f"Audio file processing request: {request.processing_type}")
            
            response = audio_pb2.ProcessAudioResponse()
            set_current_timestamp(response.response.timestamp)
            
            if request.processing_type == audio_pb2.PROCESSING_TYPE_TRANSCRIBE:
                # Convert attachment to stream chunks and transcribe
                audio_data = request.audio_file.data
                
                # Create mock stream chunk
                chunk = common_pb2.StreamChunk()
                chunk.data = audio_data
                chunk.type = common_pb2.CHUNK_TYPE_DATA
                chunk.is_final = True
                
                # Process as STT
                stt_response = self.SpeechToText([chunk], context)
                response.transcript = stt_response.transcript
                response.usage.CopyFrom(stt_response.usage)
                response.response.success = True
                response.response.message = "Transcription completed"
                
            else:
                response.response.success = False
                response.response.message = f"Processing type {request.processing_type} not implemented"
            
            return response
            
        except Exception as e:
            logger.error(f"Audio file processing failed: {e}")
            response = audio_pb2.ProcessAudioResponse()
            response.response.success = False
            response.response.message = f"Processing failed: {str(e)}"
            set_current_timestamp(response.response.timestamp)
            return response
    
    def ListVoices(self, request: audio_pb2.ListVoicesRequest, context) -> audio_pb2.ListVoicesResponse:
        """
        List available voices
        
        Args:
            request: ListVoicesRequest with filters
            context: gRPC context
            
        Returns:
            ListVoicesResponse: Available voices
        """
        try:
            response = audio_pb2.ListVoicesResponse()
            response.response.success = True
            response.response.message = "Voices listed successfully"
            set_current_timestamp(response.response.timestamp)
            
            # Create default voices (matching our Kotlin implementation)
            voices_data = [
                {
                    "id": "voice-en-us-female-1",
                    "name": "Emma",
                    "display_name": "Emma (US English)",
                    "description": "A friendly female voice with American English accent",
                    "language": "English",
                    "language_code": "en-US",
                    "gender": audio_pb2.VOICE_GENDER_FEMALE,
                    "age": audio_pb2.VOICE_AGE_YOUNG_ADULT,
                    "style": audio_pb2.VOICE_STYLE_FRIENDLY,
                    "is_available": True,
                    "is_premium": False,
                    "cost_per_character": 0.001
                },
                {
                    "id": "voice-en-us-male-1",
                    "name": "James",
                    "display_name": "James (US English)",
                    "description": "A professional male voice with American English accent",
                    "language": "English",
                    "language_code": "en-US",
                    "gender": audio_pb2.VOICE_GENDER_MALE,
                    "age": audio_pb2.VOICE_AGE_ADULT,
                    "style": audio_pb2.VOICE_STYLE_PROFESSIONAL,
                    "is_available": True,
                    "is_premium": False,
                    "cost_per_character": 0.001
                }
            ]
            
            for voice_data in voices_data:
                voice = audio_pb2.Voice()
                
                # Set metadata
                voice.metadata.resource_id = voice_data["id"]
                voice.metadata.created_at
                voice.metadata.updated_at
                
                # Set voice properties
                voice.name = voice_data["name"]
                voice.display_name = voice_data["display_name"]
                voice.description = voice_data["description"]
                voice.language = voice_data["language"]
                voice.language_code = voice_data["language_code"]
                voice.gender = voice_data["gender"]
                voice.age = voice_data["age"]
                voice.style = voice_data["style"]
                voice.is_available = voice_data["is_available"]
                voice.is_premium = voice_data["is_premium"]
                voice.cost_per_character = voice_data["cost_per_character"]
                
                # Add supported formats
                voice.supported_formats.extend([
                    audio_pb2.AUDIO_FORMAT_MP3,
                    audio_pb2.AUDIO_FORMAT_WAV,
                    audio_pb2.AUDIO_FORMAT_OGG
                ])
                
                # Add supported sample rates
                voice.supported_sample_rates.extend([16000, 22050, 44100])
                
                response.voices.append(voice)
            
            # Set pagination
            response.pagination.has_more = False
            response.pagination.page_size = len(response.voices)
            
            return response
            
        except Exception as e:
            logger.error(f"List voices failed: {e}")
            response = audio_pb2.ListVoicesResponse()
            response.response.success = False
            response.response.message = f"Failed to list voices: {str(e)}"
            set_current_timestamp(response.response.timestamp)
            return response
    
    def GetVoice(self, request: audio_pb2.GetVoiceRequest, context) -> audio_pb2.GetVoiceResponse:
        """Get specific voice by ID"""
        # Implementation would look up specific voice
        # For now, return first voice from list
        list_request = audio_pb2.ListVoicesRequest()
        list_response = self.ListVoices(list_request, context)
        
        response = audio_pb2.GetVoiceResponse()
        if list_response.voices:
            response.voice.CopyFrom(list_response.voices[0])
            response.response.success = True
            response.response.message = "Voice found"
        else:
            response.response.success = False
            response.response.message = "Voice not found"
        
        set_current_timestamp(response.response.timestamp)
        return response
    
    def CreateCustomVoice(self, request: audio_pb2.CreateCustomVoiceRequest, context) -> audio_pb2.CreateCustomVoiceResponse:
        """Create custom voice (not implemented)"""
        response = audio_pb2.CreateCustomVoiceResponse()
        response.response.success = False
        response.response.message = "Custom voice creation not implemented"
        set_current_timestamp(response.response.timestamp)
        return response
    
    def ConvertAudioFormat(self, request: audio_pb2.ConvertAudioRequest, context) -> audio_pb2.ConvertAudioResponse:
        """Convert audio format (not implemented)"""
        response = audio_pb2.ConvertAudioResponse()
        response.response.success = False
        response.response.message = "Audio format conversion not implemented"
        set_current_timestamp(response.response.timestamp)
        return response
    
    def AnalyzeAudio(self, request: audio_pb2.AnalyzeAudioRequest, context) -> audio_pb2.AnalyzeAudioResponse:
        """Analyze audio (not implemented)"""
        response = audio_pb2.AnalyzeAudioResponse()
        response.response.success = False
        response.response.message = "Audio analysis not implemented"
        set_current_timestamp(response.response.timestamp)
        return response
    
    def HealthCheck(self, request: common_pb2.HealthCheckRequest, context) -> common_pb2.HealthCheckResponse:
        """Health check endpoint"""
        try:
            response = common_pb2.HealthCheckResponse()
            response.status = "healthy" if self.whisper_model is not None else "unhealthy"
            set_current_timestamp(response.timestamp)
            response.details.update({
                "whisper_model_loaded": str(self.whisper_model is not None),
                "cuda_available": str(torch.cuda.is_available()),
                "service": "whisper-tts",
                "version": "1.0.0"
            })
            return response
        except Exception as e:
            response = common_pb2.HealthCheckResponse()
            response.status = "unhealthy"
            set_current_timestamp(response.timestamp)
            response.details.update({"error": str(e)})
            return response
    
    def _extract_language_from_voice(self, voice_id: str) -> str:
        """Extract language code from voice ID"""
        if "en-us" in voice_id.lower() or "en-gb" in voice_id.lower():
            return "en"
        elif "es" in voice_id.lower():
            return "es"
        elif "fr" in voice_id.lower():
            return "fr"
        elif "de" in voice_id.lower():
            return "de"
        else:
            return "en"  # Default to English
    
    def _estimate_duration(self, audio_bytes_length: int) -> float:
        """Estimate audio duration from byte length"""
        # Rough estimate: assume 16kHz, 16-bit, mono
        bytes_per_second = 16000 * 2 * 1
        return audio_bytes_length / bytes_per_second


def serve():
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    audio_pb2_grpc.add_AudioServiceServicer_to_server(AudioServiceServicer(), server)
    
    listen_addr = '[::]:9091'
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting gRPC server on {listen_addr}")
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server...")
        server.stop(0)


if __name__ == '__main__':
    serve()
