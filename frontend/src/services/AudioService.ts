// ============================================================================
// Audio Service - Clean Service Layer
// ============================================================================
//
// @file AudioService.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Clean service layer for audio operations with React Query integration
//
// This service provides a clean, React-friendly interface for audio operations.
// It wraps the gRPC client and provides proper error handling, caching, and
// state management integration with React Query.
//
// Features:
// - Clean async/await API for React components
// - React Query integration for caching and state management
// - Comprehensive error handling and retry logic
// - TypeScript type safety throughout
// - Audio streaming with proper flow control
// ============================================================================

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import AudioGrpcClient, { AudioServiceError, AudioStreamError } from './grpc/AudioGrpcClient';
import {
  TTSRequest,
  STTResponse,
  ListVoicesRequest,
  ListVoicesResponse,
  Voice,
  AudioFormat,
  AudioQuality,
  VoiceGender,
  VoiceStyle,
} from '../proto/audio';
import { StreamChunk, createStreamChunk } from '../proto/common';

// ============================================================================
// Service Configuration
// ============================================================================

const AUDIO_CLIENT = new AudioGrpcClient({
  baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8080',
  timeout: 30000,
  enableLogging: process.env.NODE_ENV === 'development',
});

// ============================================================================
// Query Keys
// ============================================================================

export const audioQueryKeys = {
  all: ['audio'] as const,
  voices: () => [...audioQueryKeys.all, 'voices'] as const,
  voice: (id: string) => [...audioQueryKeys.voices(), id] as const,
  health: () => [...audioQueryKeys.all, 'health'] as const,
};

// ============================================================================
// Types
// ============================================================================

export interface TTSOptions {
  text: string;
  voiceId?: string;
  format?: AudioFormat;
  quality?: AudioQuality;
  sampleRate?: number;
  channels?: number;
  enableSsml?: boolean;
}

export interface STTOptions {
  audioData: Uint8Array;
  language?: string;
  enableNoiseReduction?: boolean;
}

export interface VoiceFilter {
  language?: string;
  gender?: VoiceGender;
  style?: VoiceStyle;
  premiumOnly?: boolean;
  searchQuery?: string;
}

export interface AudioPlaybackState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
}

export interface AudioRecordingState {
  isRecording: boolean;
  duration: number;
  audioLevel: number;
}

// ============================================================================
// Audio Service Class
// ============================================================================

export class AudioService {
  private client: AudioGrpcClient;
  private queryClient: useQueryClient;

  constructor(client: AudioGrpcClient) {
    this.client = client;
  }

  // ============================================================================
  // Text-to-Speech Operations
  // ============================================================================

  /**
   * Synthesize text to speech with streaming output
   */
  async synthesizeText(options: TTSOptions): Promise<Uint8Array> {
    try {
      const request: TTSRequest = {
        text: options.text,
        voiceId: options.voiceId || 'voice-en-us-female-1',
        outputFormat: options.format || AudioFormat.AUDIO_FORMAT_MP3,
        sampleRate: options.sampleRate || 22050,
        channels: options.channels || 1,
        enableSsml: options.enableSsml || false,
        options: {
          quality: options.quality || AudioQuality.AUDIO_QUALITY_STANDARD,
        },
      };

      // Collect all audio chunks from the stream
      const audioChunks: Uint8Array[] = [];
      for await (const chunk of this.client.textToSpeech(request)) {
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

      return combinedAudio;

    } catch (error) {
      if (error instanceof AudioStreamError) {
        throw new Error(`TTS streaming failed: ${error.message}`);
      }
      throw new Error(`TTS synthesis failed: ${error}`);
    }
  }

  /**
   * Create an audio stream for real-time TTS
   */
  async *synthesizeTextStream(options: TTSOptions): AsyncIterable<Uint8Array> {
    try {
      const request: TTSRequest = {
        text: options.text,
        voiceId: options.voiceId || 'voice-en-us-female-1',
        outputFormat: options.format || AudioFormat.AUDIO_FORMAT_MP3,
        sampleRate: options.sampleRate || 22050,
        channels: options.channels || 1,
        enableSsml: options.enableSsml || false,
      };

      for await (const chunk of this.client.textToSpeech(request)) {
        if (chunk.data && chunk.data.length > 0) {
          yield chunk.data;
        }
      }

    } catch (error) {
      throw new Error(`TTS streaming failed: ${error}`);
    }
  }

  // ============================================================================
  // Speech-to-Text Operations
  // ============================================================================

  /**
   * Transcribe audio data to text
   */
  async transcribeAudio(options: STTOptions): Promise<STTResponse> {
    try {
      // Create audio stream from data
      const audioStream = this.createAudioStream(options.audioData);
      
      // Call STT service
      const response = await this.client.speechToText(audioStream);
      
      return response;

    } catch (error) {
      throw new Error(`STT transcription failed: ${error}`);
    }
  }

  /**
   * Create an audio stream for real-time STT
   */
  async transcribeAudioStream(audioStream: AsyncIterable<Uint8Array>): Promise<STTResponse> {
    try {
      // Convert Uint8Array stream to StreamChunk stream
      const streamChunks = this.createStreamChunkIterator(audioStream);
      
      // Call STT service
      const response = await this.client.speechToText(streamChunks);
      
      return response;

    } catch (error) {
      throw new Error(`STT streaming failed: ${error}`);
    }
  }

  // ============================================================================
  // Voice Management Operations
  // ============================================================================

  /**
   * Get all available voices with filtering
   */
  async getVoices(filter: VoiceFilter = {}): Promise<Voice[]> {
    try {
      const request: ListVoicesRequest = {
        language: filter.language,
        gender: filter.gender,
        style: filter.style,
        premiumOnly: filter.premiumOnly || false,
        pagination: {
          pageSize: 100, // Get all voices for now
        },
      };

      const response = await this.client.listVoices(request);
      let voices = response.voices || [];

      // Apply search filter if provided
      if (filter.searchQuery) {
        const query = filter.searchQuery.toLowerCase();
        voices = voices.filter(voice => 
          voice.name?.toLowerCase().includes(query) ||
          voice.displayName?.toLowerCase().includes(query) ||
          voice.description?.toLowerCase().includes(query)
        );
      }

      return voices;

    } catch (error) {
      throw new Error(`Failed to get voices: ${error}`);
    }
  }

  /**
   * Get a specific voice by ID
   */
  async getVoice(voiceId: string): Promise<Voice> {
    try {
      const response = await this.client.getVoice({ voiceId });
      
      if (!response.voice) {
        throw new Error(`Voice not found: ${voiceId}`);
      }

      return response.voice;

    } catch (error) {
      throw new Error(`Failed to get voice: ${error}`);
    }
  }

  // ============================================================================
  // Health Check
  // ============================================================================

  /**
   * Check audio service health
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.client.healthCheck({});
      return response.status === 'healthy';
    } catch (error) {
      return false;
    }
  }

  // ============================================================================
  // Utility Methods
  // ============================================================================

  /**
   * Create audio stream from Uint8Array
   */
  private async *createAudioStream(audioData: Uint8Array): AsyncIterable<StreamChunk> {
    const chunkSize = 8192; // 8KB chunks
    const totalChunks = Math.ceil(audioData.length / chunkSize);

    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize;
      const end = Math.min(start + chunkSize, audioData.length);
      const chunkData = audioData.slice(start, end);

      yield createStreamChunk({
        streamId: `stt_${Date.now()}`,
        sequenceNumber: i + 1,
        data: chunkData,
        isFinal: i === totalChunks - 1,
      });
    }
  }

  /**
   * Create StreamChunk iterator from Uint8Array stream
   */
  private async *createStreamChunkIterator(audioStream: AsyncIterable<Uint8Array>): AsyncIterable<StreamChunk> {
    let sequenceNumber = 1;
    const streamId = `stt_${Date.now()}`;

    for await (const audioData of audioStream) {
      yield createStreamChunk({
        streamId,
        sequenceNumber: sequenceNumber++,
        data: audioData,
        isFinal: false, // We don't know if it's final in the stream
      });
    }

    // Send final chunk
    yield createStreamChunk({
      streamId,
      sequenceNumber: sequenceNumber,
      data: new Uint8Array(),
      isFinal: true,
    });
  }

  /**
   * Cancel all ongoing operations
   */
  cancel(): void {
    this.client.cancel();
  }
}

// ============================================================================
// Service Instance
// ============================================================================

export const audioService = new AudioService(AUDIO_CLIENT);

// ============================================================================
// React Query Hooks
// ============================================================================

/**
 * Hook for text-to-speech synthesis
 */
export function useSynthesizeText() {
  return useMutation({
    mutationFn: (options: TTSOptions) => audioService.synthesizeText(options),
    onError: (error) => {
      console.error('TTS synthesis failed:', error);
    },
  });
}

/**
 * Hook for speech-to-text transcription
 */
export function useTranscribeAudio() {
  return useMutation({
    mutationFn: (options: STTOptions) => audioService.transcribeAudio(options),
    onError: (error) => {
      console.error('STT transcription failed:', error);
    },
  });
}

/**
 * Hook for getting available voices
 */
export function useVoices(filter: VoiceFilter = {}) {
  return useQuery({
    queryKey: [...audioQueryKeys.voices(), filter],
    queryFn: () => audioService.getVoices(filter),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook for getting a specific voice
 */
export function useVoice(voiceId: string) {
  return useQuery({
    queryKey: audioQueryKeys.voice(voiceId),
    queryFn: () => audioService.getVoice(voiceId),
    enabled: !!voiceId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook for audio service health check
 */
export function useAudioHealth() {
  return useQuery({
    queryKey: audioQueryKeys.health(),
    queryFn: () => audioService.checkHealth(),
    refetchInterval: 30 * 1000, // Check every 30 seconds
    retry: 1,
  });
}

// ============================================================================
// Default Export
// ============================================================================

export default audioService;
