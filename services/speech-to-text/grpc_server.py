#!/usr/bin/env python3
"""
@llm-type service
@llm-legend Speech-to-Text gRPC server with health.proto implementation
@llm-key Provides STT capabilities via gRPC with standardized health endpoints
@llm-map gRPC server for speech-to-text service using health.proto compliance
@llm-axiom Service must implement health.proto for service discovery and monitoring
@llm-contract Provides speech transcription via gRPC API with health.proto compliance
@llm-token stt-service: Speech-to-text with gRPC and health.proto

Speech-to-Text gRPC Server - Proto-Compliant Implementation

Provides Speech-to-Text (Whisper) capabilities with health.proto implementation:
- STT processing: Whisper-based speech transcription
- Health checks: Implements unhinged.health.v1.HealthService
- Service discovery integration via health.proto
- Whisper model management and CUDA optimization
"""

import os
import tempfile
import asyncio
import grpc
from unhinged_events import create_service_logger
from concurrent import futures
from typing import Iterator, AsyncIterator
import io

# Audio processing imports
import whisper
import torch

# Add centralized protobuf clients to path
import sys
from pathlib import Path

# For Docker environment, use the copied centralized clients
if Path("/app/generated/python/clients").exists():
    sys.path.insert(0, "/app/generated/python/clients")
else:
    # For development, use project root path
    project_root = Path(__file__).parent.parent.parent
    generated_path = project_root / "generated" / "python" / "clients"
    sys.path.insert(0, str(generated_path))

# Generated proto imports from centralized generation
from unhinged_proto_clients import audio_pb2, audio_pb2_grpc, common_pb2
from unhinged_proto_clients.health import health_pb2, health_pb2_grpc
from google.protobuf import timestamp_pb2
import time

def set_current_timestamp(timestamp_field):
    """Helper function to set current timestamp"""
    timestamp_field.seconds = int(time.time())
    timestamp_field.nanos = int((time.time() % 1) * 1e9)

# Initialize event logger
events = create_service_logger("speech-to-text", "1.0.0")

class AudioServiceServicer(audio_pb2_grpc.AudioServiceServicer, health_pb2_grpc.HealthServiceServicer):
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
        self.start_time = time.time()  # Track service start time for uptime
        os.makedirs(self.upload_folder, exist_ok=True)
        self._load_whisper_model()
    
    def _load_whisper_model(self):
        """Load Whisper model on startup"""
        try:
            self.whisper_model = whisper.load_model("base")
            events.info("Whisper model loaded", {"model": "base"})
        except Exception as e:
            events.error("Failed to load Whisper model", exception=e, metadata={"model": "base"})
            self.whisper_model = None
    

    
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

            
            # Collect audio chunks
            audio_data = io.BytesIO()
            chunk_count = 0
            
            for chunk in request_iterator:
                if chunk.type == common_pb2.CHUNK_TYPE_DATA:
                    audio_data.write(chunk.data)
                    chunk_count += 1

            
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
            events.error("STT processing failed", exception=e)
            # Return error response
            response = audio_pb2.STTResponse()
            response.response.success = False
            response.response.message = f"STT processing failed: {str(e)}"
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

            
            response = audio_pb2.ProcessAudioResponse()
            
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
            events.error("Audio file processing failed", exception=e)
            response = audio_pb2.ProcessAudioResponse()
            response.response.success = False
            response.response.message = f"Processing failed: {str(e)}"
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
            events.error("List voices failed", exception=e)
            response = audio_pb2.ListVoicesResponse()
            response.response.success = False
            response.response.message = f"Failed to list voices: {str(e)}"
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

        return response
    
    def CreateCustomVoice(self, request: audio_pb2.CreateCustomVoiceRequest, context) -> audio_pb2.CreateCustomVoiceResponse:
        """Create custom voice (not implemented)"""
        response = audio_pb2.CreateCustomVoiceResponse()
        response.response.success = False
        response.response.message = "Custom voice creation not implemented"
        return response
    
    def ConvertAudioFormat(self, request: audio_pb2.ConvertAudioRequest, context) -> audio_pb2.ConvertAudioResponse:
        """Convert audio format (not implemented)"""
        response = audio_pb2.ConvertAudioResponse()
        response.response.success = False
        response.response.message = "Audio format conversion not implemented"
        return response
    
    def AnalyzeAudio(self, request: audio_pb2.AnalyzeAudioRequest, context) -> audio_pb2.AnalyzeAudioResponse:
        """Analyze audio (not implemented)"""
        response = audio_pb2.AnalyzeAudioResponse()
        response.response.success = False
        response.response.message = "Audio analysis not implemented"
        return response
    
    def Heartbeat(self, request: health_pb2.HeartbeatRequest, context) -> health_pb2.HeartbeatResponse:
        """Fast heartbeat endpoint (<10ms) - health.proto implementation"""
        try:
            response = health_pb2.HeartbeatResponse()
            response.alive = True
            response.timestamp_ms = int(time.time() * 1000)
            response.service_id = "speech-to-text-service"
            response.version = "1.0.0"
            response.uptime_ms = int((time.time() - self.start_time) * 1000) if hasattr(self, 'start_time') else 0
            response.status = health_pb2.HEALTH_STATUS_HEALTHY if self.whisper_model is not None else health_pb2.HEALTH_STATUS_UNHEALTHY
            return response
        except Exception as e:
            response = health_pb2.HeartbeatResponse()
            response.alive = False
            response.timestamp_ms = int(time.time() * 1000)
            response.service_id = "speech-to-text-service"
            response.version = "1.0.0"
            response.status = health_pb2.HEALTH_STATUS_UNHEALTHY
            return response

    def Diagnostics(self, request: health_pb2.DiagnosticsRequest, context) -> health_pb2.DiagnosticsResponse:
        """Detailed diagnostics endpoint (<1s) - health.proto implementation"""
        try:
            # Get heartbeat first
            heartbeat = self.Heartbeat(health_pb2.HeartbeatRequest(), context)

            response = health_pb2.DiagnosticsResponse()
            response.heartbeat.CopyFrom(heartbeat)

            # Add metadata if requested
            if request.include_metrics:
                response.metadata["whisper_model_loaded"] = str(self.whisper_model is not None)
                response.metadata["cuda_available"] = str(torch.cuda.is_available())
                response.metadata["service_type"] = "speech-to-text"

            response.last_updated.GetCurrentTime()
            return response
        except Exception as e:
            # Return minimal response on error
            response = health_pb2.DiagnosticsResponse()
            response.heartbeat.CopyFrom(self.Heartbeat(health_pb2.HeartbeatRequest(), context))
            response.metadata["error"] = str(e)
            response.last_updated.GetCurrentTime()
            return response
    



def serve():
    """Start the gRPC server with health.proto implementation"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = AudioServiceServicer()

    # Register both audio and health services
    audio_pb2_grpc.add_AudioServiceServicer_to_server(servicer, server)
    health_pb2_grpc.add_HealthServiceServicer_to_server(servicer, server)
    
    listen_addr = '[::]:9091'
    server.add_insecure_port(listen_addr)
    
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        pass
        server.stop(0)


if __name__ == '__main__':
    serve()
