// ============================================================================
// Audio gRPC-Web Client - Service Layer
// ============================================================================
//
// @file AudioGrpcClient.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description gRPC-Web client for audio service communication
//
// This client provides a clean interface for communicating with the audio
// service using gRPC-Web. It handles streaming operations, error handling,
// and provides a TypeScript-friendly API for React components.
//
// Features:
// - Streaming TTS and STT operations
// - Voice management operations
// - Comprehensive error handling
// - TypeScript type safety
// - React-friendly async/await API
// ============================================================================

import {
  AudioService,
  TTSRequest,
  STTResponse,
  ListVoicesRequest,
  ListVoicesResponse,
  GetVoiceRequest,
  GetVoiceResponse,
  ProcessAudioRequest,
  ProcessAudioResponse,
  AudioFormat,
  AudioQuality,
  VoiceGender,
  VoiceStyle,
} from '../../proto/audio';

import {
  StreamChunk,
  ChunkType,
  ChunkStatus,
  HealthCheckRequest,
  HealthCheckResponse,
  createStreamChunk,
  generateRequestId,
} from '../../proto/common';

// ============================================================================
// Configuration
// ============================================================================

interface AudioClientConfig {
  baseUrl: string;
  timeout: number;
  enableLogging: boolean;
}

const DEFAULT_CONFIG: AudioClientConfig = {
  baseUrl: 'http://localhost:8080', // Backend proxy endpoint
  timeout: 30000,
  enableLogging: true,
};

// ============================================================================
// Error Types
// ============================================================================

export class AudioServiceError extends Error {
  constructor(
    message: string,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'AudioServiceError';
  }
}

export class AudioStreamError extends AudioServiceError {
  constructor(message: string, public streamId?: string) {
    super(message, 'STREAM_ERROR');
    this.name = 'AudioStreamError';
  }
}

// ============================================================================
// Audio gRPC-Web Client
// ============================================================================

export class AudioGrpcClient implements AudioService {
  private config: AudioClientConfig;
  private abortController: AbortController;

  constructor(config: Partial<AudioClientConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.abortController = new AbortController();
  }

  // ============================================================================
  // Text-to-Speech (Streaming)
  // ============================================================================

  async *textToSpeech(request: TTSRequest): AsyncIterable<StreamChunk> {
    try {
      this.log('TTS Request:', request);

      const response = await fetch(`${this.config.baseUrl}/api/v1/audio/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': generateRequestId(),
        },
        body: JSON.stringify({
          text: request.text,
          voiceId: request.voiceId || 'voice-en-us-female-1',
          sampleRate: request.sampleRate || 22050,
          channels: request.channels || 1,
          enableSsml: request.enableSsml || false,
        }),
        signal: this.abortController.signal,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new AudioServiceError(`TTS request failed: ${response.status} ${errorText}`);
      }

      // For now, we'll simulate streaming by chunking the response
      const audioData = await response.arrayBuffer();
      const audioBytes = new Uint8Array(audioData);
      
      // Chunk the audio data for streaming simulation
      const chunkSize = 8192; // 8KB chunks
      const totalChunks = Math.ceil(audioBytes.length / chunkSize);
      
      for (let i = 0; i < totalChunks; i++) {
        const start = i * chunkSize;
        const end = Math.min(start + chunkSize, audioBytes.length);
        const chunkData = audioBytes.slice(start, end);
        
        const chunk = createStreamChunk({
          streamId: `tts_${Date.now()}`,
          sequenceNumber: i + 1,
          type: ChunkType.CHUNK_TYPE_DATA,
          data: chunkData,
          isFinal: i === totalChunks - 1,
          status: i === totalChunks - 1 ? ChunkStatus.CHUNK_STATUS_COMPLETE : ChunkStatus.CHUNK_STATUS_PROCESSING,
        });

        yield chunk;
        
        // Small delay to simulate streaming
        if (i < totalChunks - 1) {
          await new Promise(resolve => setTimeout(resolve, 50));
        }
      }

    } catch (error) {
      this.log('TTS Error:', error);
      throw new AudioStreamError(`TTS streaming failed: ${error}`);
    }
  }

  // ============================================================================
  // Speech-to-Text (Streaming)
  // ============================================================================

  async speechToText(request: AsyncIterable<StreamChunk>): Promise<STTResponse> {
    try {
      this.log('STT Request started');

      // Collect all audio chunks
      const audioChunks: Uint8Array[] = [];
      for await (const chunk of request) {
        if (chunk.data && chunk.data.length > 0) {
          audioChunks.push(chunk.data);
        }
      }

      // Combine all chunks into a single audio file
      const totalLength = audioChunks.reduce((sum, chunk) => sum + chunk.length, 0);
      const combinedAudio = new Uint8Array(totalLength);
      let offset = 0;
      
      for (const chunk of audioChunks) {
        combinedAudio.set(chunk, offset);
        offset += chunk.length;
      }

      // Create form data for multipart upload
      const formData = new FormData();
      const audioBlob = new Blob([combinedAudio], { type: 'audio/wav' });
      formData.append('audio', audioBlob, 'recording.wav');

      const response = await fetch(`${this.config.baseUrl}/api/v1/audio/transcribe`, {
        method: 'POST',
        headers: {
          'X-Request-ID': generateRequestId(),
        },
        body: formData,
        signal: this.abortController.signal,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new AudioServiceError(`STT request failed: ${response.status} ${errorText}`);
      }

      const result = await response.json();
      this.log('STT Response:', result);

      return {
        response: {
          success: true,
          message: 'Transcription completed',
          timestamp: new Date().toISOString(),
        },
        transcript: result.text || '',
        confidence: result.confidence || 0.9,
        segments: result.segments || [],
        usage: {
          duration: { seconds: Math.floor(combinedAudio.length / 32000), nanos: 0 },
          bytesProcessed: combinedAudio.length,
          sampleRate: 16000,
          channels: 1,
          format: 'wav',
        },
        metadata: {
          model: 'whisper-base',
          language: result.language || 'en',
          processingTimeMs: 0,
          signalToNoiseRatio: 0,
          speechRateWpm: 0,
          detectedLanguages: [result.language || 'en'],
          hasBackgroundNoise: false,
          hasMultipleSpeakers: false,
          detectedQuality: AudioQuality.AUDIO_QUALITY_STANDARD,
        },
      };

    } catch (error) {
      this.log('STT Error:', error);
      throw new AudioServiceError(`STT processing failed: ${error}`);
    }
  }

  // ============================================================================
  // Voice Management
  // ============================================================================

  async listVoices(request: ListVoicesRequest): Promise<ListVoicesResponse> {
    try {
      this.log('List Voices Request:', request);

      const params = new URLSearchParams();
      if (request.language) params.append('language', request.language);
      if (request.gender !== undefined) params.append('gender', VoiceGender[request.gender]);
      if (request.style !== undefined) params.append('style', VoiceStyle[request.style]);
      if (request.premiumOnly) params.append('premium_only', 'true');
      if (request.pagination?.pageSize) params.append('limit', request.pagination.pageSize.toString());

      const response = await fetch(`${this.config.baseUrl}/api/v1/audio/voices?${params}`, {
        method: 'GET',
        headers: {
          'X-Request-ID': generateRequestId(),
        },
        signal: this.abortController.signal,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new AudioServiceError(`List voices failed: ${response.status} ${errorText}`);
      }

      const result = await response.json();
      this.log('List Voices Response:', result);

      return {
        response: {
          success: true,
          message: 'Voices listed successfully',
          timestamp: new Date().toISOString(),
        },
        voices: result.voices || [],
        pagination: {
          hasMore: result.hasMore || false,
          pageSize: result.voices?.length || 0,
        },
      };

    } catch (error) {
      this.log('List Voices Error:', error);
      throw new AudioServiceError(`Failed to list voices: ${error}`);
    }
  }

  async getVoice(request: GetVoiceRequest): Promise<GetVoiceResponse> {
    try {
      this.log('Get Voice Request:', request);

      const response = await fetch(`${this.config.baseUrl}/api/v1/audio/voices/${request.voiceId}`, {
        method: 'GET',
        headers: {
          'X-Request-ID': generateRequestId(),
        },
        signal: this.abortController.signal,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new AudioServiceError(`Get voice failed: ${response.status} ${errorText}`);
      }

      const voice = await response.json();
      this.log('Get Voice Response:', voice);

      return {
        response: {
          success: true,
          message: 'Voice retrieved successfully',
          timestamp: new Date().toISOString(),
        },
        voice,
      };

    } catch (error) {
      this.log('Get Voice Error:', error);
      throw new AudioServiceError(`Failed to get voice: ${error}`);
    }
  }

  // ============================================================================
  // Batch Processing
  // ============================================================================

  async processAudioFile(request: ProcessAudioRequest): Promise<ProcessAudioResponse> {
    try {
      this.log('Process Audio File Request');

      // For now, we'll use the transcribe endpoint for file processing
      const formData = new FormData();
      const audioBlob = new Blob([request.audioFile || new Uint8Array()], { type: 'audio/wav' });
      formData.append('audio', audioBlob, 'audio.wav');

      const response = await fetch(`${this.config.baseUrl}/api/v1/audio/transcribe`, {
        method: 'POST',
        headers: {
          'X-Request-ID': generateRequestId(),
        },
        body: formData,
        signal: this.abortController.signal,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new AudioServiceError(`Process audio file failed: ${response.status} ${errorText}`);
      }

      const result = await response.json();
      this.log('Process Audio File Response:', result);

      return {
        response: {
          success: true,
          message: 'Audio file processed successfully',
          timestamp: new Date().toISOString(),
        },
        transcript: result.text || '',
        usage: {
          duration: { seconds: 0, nanos: 0 },
          bytesProcessed: request.audioFile?.length || 0,
          sampleRate: 16000,
          channels: 1,
          format: 'wav',
        },
      };

    } catch (error) {
      this.log('Process Audio File Error:', error);
      throw new AudioServiceError(`Failed to process audio file: ${error}`);
    }
  }

  // ============================================================================
  // Not Implemented (Placeholder)
  // ============================================================================

  async createCustomVoice(): Promise<any> {
    throw new AudioServiceError('Custom voice creation not implemented');
  }

  async convertAudioFormat(): Promise<any> {
    throw new AudioServiceError('Audio format conversion not implemented');
  }

  async analyzeAudio(): Promise<any> {
    throw new AudioServiceError('Audio analysis not implemented');
  }

  // ============================================================================
  // Health Check
  // ============================================================================

  async healthCheck(request: HealthCheckRequest): Promise<HealthCheckResponse> {
    try {
      const response = await fetch(`${this.config.baseUrl}/api/v1/audio/health`, {
        method: 'GET',
        headers: {
          'X-Request-ID': generateRequestId(),
        },
        signal: this.abortController.signal,
      });

      const result = await response.json();
      
      return {
        status: response.ok ? 'healthy' : 'unhealthy',
        timestamp: new Date().toISOString(),
        details: result,
      };

    } catch (error) {
      return {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        details: { error: error?.toString() || 'Unknown error' },
      };
    }
  }

  // ============================================================================
  // Utility Methods
  // ============================================================================

  /**
   * Cancel all ongoing requests
   */
  cancel(): void {
    this.abortController.abort();
    this.abortController = new AbortController();
  }

  /**
   * Update client configuration
   */
  updateConfig(config: Partial<AudioClientConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Internal logging method
   */
  private log(message: string, data?: any): void {
    if (this.config.enableLogging) {
      console.log(`[AudioGrpcClient] ${message}`, data || '');
    }
  }
}

// ============================================================================
// Default Export
// ============================================================================

export default AudioGrpcClient;
