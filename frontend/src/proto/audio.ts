// ============================================================================
// Generated TypeScript Proto Definitions - Audio Service
// ============================================================================
//
// @file audio.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description TypeScript definitions for audio.proto messages and services
//
// This file contains TypeScript interfaces and types generated from the
// audio.proto file for use in the frontend React application.
// ============================================================================

import { StreamChunk, HealthCheckRequest, HealthCheckResponse, AudioUsage } from './common';

// ============================================================================
// Enums
// ============================================================================

export enum AudioFormat {
  AUDIO_FORMAT_UNSPECIFIED = 0,
  AUDIO_FORMAT_WAV = 1,
  AUDIO_FORMAT_MP3 = 2,
  AUDIO_FORMAT_OGG = 3,
  AUDIO_FORMAT_FLAC = 4,
  AUDIO_FORMAT_PCM = 5,
  AUDIO_FORMAT_OPUS = 6,
  AUDIO_FORMAT_AAC = 7,
}

export enum AudioQuality {
  AUDIO_QUALITY_UNSPECIFIED = 0,
  AUDIO_QUALITY_LOW = 1,
  AUDIO_QUALITY_STANDARD = 2,
  AUDIO_QUALITY_HIGH = 3,
  AUDIO_QUALITY_PREMIUM = 4,
}

export enum AudioEffectType {
  AUDIO_EFFECT_TYPE_UNSPECIFIED = 0,
  AUDIO_EFFECT_TYPE_REVERB = 1,
  AUDIO_EFFECT_TYPE_ECHO = 2,
  AUDIO_EFFECT_TYPE_CHORUS = 3,
  AUDIO_EFFECT_TYPE_DISTORTION = 4,
  AUDIO_EFFECT_TYPE_NORMALIZE = 5,
  AUDIO_EFFECT_TYPE_COMPRESSOR = 6,
}

export enum VoiceGender {
  VOICE_GENDER_UNSPECIFIED = 0,
  VOICE_GENDER_MALE = 1,
  VOICE_GENDER_FEMALE = 2,
  VOICE_GENDER_NEUTRAL = 3,
  VOICE_GENDER_CHILD = 4,
}

export enum VoiceAge {
  VOICE_AGE_UNSPECIFIED = 0,
  VOICE_AGE_CHILD = 1,
  VOICE_AGE_YOUNG_ADULT = 2,
  VOICE_AGE_ADULT = 3,
  VOICE_AGE_SENIOR = 4,
}

export enum VoiceStyle {
  VOICE_STYLE_UNSPECIFIED = 0,
  VOICE_STYLE_CONVERSATIONAL = 1,
  VOICE_STYLE_PROFESSIONAL = 2,
  VOICE_STYLE_FRIENDLY = 3,
  VOICE_STYLE_AUTHORITATIVE = 4,
  VOICE_STYLE_CALM = 5,
  VOICE_STYLE_ENERGETIC = 6,
  VOICE_STYLE_DRAMATIC = 7,
}

export enum ProcessingType {
  PROCESSING_TYPE_UNSPECIFIED = 0,
  PROCESSING_TYPE_TRANSCRIBE = 1,
  PROCESSING_TYPE_TRANSLATE = 2,
  PROCESSING_TYPE_ENHANCE = 3,
  PROCESSING_TYPE_CONVERT = 4,
}

// ============================================================================
// Message Interfaces
// ============================================================================

export interface AudioOptions {
  speed?: number;
  pitch?: number;
  volume?: number;
  quality?: AudioQuality;
  enableNoiseReduction?: boolean;
  enableEchoCancellation?: boolean;
}

export interface AudioEffect {
  type?: AudioEffectType;
  intensity?: number;
  parameters?: { [key: string]: string };
}

export interface WordTiming {
  word?: string;
  startTime?: number;
  endTime?: number;
  confidence?: number;
}

export interface TranscriptSegment {
  text?: string;
  startTime?: number;
  endTime?: number;
  confidence?: number;
  words?: WordTiming[];
  speakerId?: string;
}

export interface STTMetadata {
  model?: string;
  language?: string;
  processingTimeMs?: number;
  signalToNoiseRatio?: number;
  speechRateWpm?: number;
  detectedLanguages?: string[];
  hasBackgroundNoise?: boolean;
  hasMultipleSpeakers?: boolean;
  detectedQuality?: AudioQuality;
}

export interface AudioMetadata {
  format?: AudioFormat;
  sampleRate?: number;
  channels?: number;
  durationSeconds?: number;
  totalBytes?: number;
}

export interface TTSChunkPayload {
  ttsId?: string;
  chunkIndex?: number;
  progressPercent?: number;
  audioMetadata?: AudioMetadata;
}

export interface Voice {
  metadata?: {
    resourceId?: string;
    createdAt?: string;
    updatedAt?: string;
  };
  name?: string;
  displayName?: string;
  description?: string;
  language?: string;
  languageCode?: string;
  gender?: VoiceGender;
  age?: VoiceAge;
  style?: VoiceStyle;
  supportedFormats?: AudioFormat[];
  supportedSampleRates?: number[];
  isAvailable?: boolean;
  isPremium?: boolean;
  costPerCharacter?: number;
  previewUrl?: string;
  previewText?: string;
}

// ============================================================================
// Request/Response Interfaces
// ============================================================================

export interface TTSRequest {
  text?: string;
  voiceId?: string;
  options?: AudioOptions;
  outputFormat?: AudioFormat;
  sampleRate?: number;
  channels?: number;
  enableSsml?: boolean;
  effects?: AudioEffect[];
}

export interface STTResponse {
  response?: {
    success?: boolean;
    message?: string;
    timestamp?: string;
  };
  transcript?: string;
  confidence?: number;
  segments?: TranscriptSegment[];
  usage?: AudioUsage;
  metadata?: STTMetadata;
}

export interface ProcessAudioRequest {
  processingType?: ProcessingType;
  audioFile?: Uint8Array;
  options?: AudioOptions;
}

export interface ProcessAudioResponse {
  response?: {
    success?: boolean;
    message?: string;
    timestamp?: string;
  };
  transcript?: string;
  usage?: AudioUsage;
}

export interface ListVoicesRequest {
  language?: string;
  gender?: VoiceGender;
  style?: VoiceStyle;
  premiumOnly?: boolean;
  pagination?: {
    pageSize?: number;
    pageToken?: string;
  };
}

export interface ListVoicesResponse {
  response?: {
    success?: boolean;
    message?: string;
    timestamp?: string;
  };
  voices?: Voice[];
  pagination?: {
    hasMore?: boolean;
    nextPageToken?: string;
    pageSize?: number;
  };
}

export interface GetVoiceRequest {
  voiceId?: string;
}

export interface GetVoiceResponse {
  response?: {
    success?: boolean;
    message?: string;
    timestamp?: string;
  };
  voice?: Voice;
}

export interface CreateCustomVoiceRequest {
  name?: string;
  description?: string;
  trainingSamples?: Uint8Array[];
  targetGender?: VoiceGender;
  targetStyle?: VoiceStyle;
}

export interface CreateCustomVoiceResponse {
  response?: {
    success?: boolean;
    message?: string;
    timestamp?: string;
  };
  voice?: Voice;
}

export interface ConvertAudioRequest {
  audioData?: Uint8Array;
  sourceFormat?: AudioFormat;
  targetFormat?: AudioFormat;
  options?: AudioOptions;
}

export interface ConvertAudioResponse {
  response?: {
    success?: boolean;
    message?: string;
    timestamp?: string;
  };
  convertedAudio?: Uint8Array;
}

export interface AnalyzeAudioRequest {
  audioData?: Uint8Array;
  analysisTypes?: string[];
}

export interface AnalyzeAudioResponse {
  response?: {
    success?: boolean;
    message?: string;
    timestamp?: string;
  };
  containsSpeech?: boolean;
  speechPercentage?: number;
  detectedLanguages?: string[];
  speakerCount?: number;
  emotions?: string[];
  qualityScore?: number;
}

// ============================================================================
// Service Interface
// ============================================================================

export interface AudioService {
  /**
   * Text-to-Speech (streaming audio output)
   */
  textToSpeech(request: TTSRequest): AsyncIterable<StreamChunk>;

  /**
   * Speech-to-Text (streaming audio input)
   */
  speechToText(request: AsyncIterable<StreamChunk>): Promise<STTResponse>;

  /**
   * Batch processing
   */
  processAudioFile(request: ProcessAudioRequest): Promise<ProcessAudioResponse>;

  /**
   * Voice management
   */
  listVoices(request: ListVoicesRequest): Promise<ListVoicesResponse>;
  getVoice(request: GetVoiceRequest): Promise<GetVoiceResponse>;
  createCustomVoice(request: CreateCustomVoiceRequest): Promise<CreateCustomVoiceResponse>;

  /**
   * Audio utilities
   */
  convertAudioFormat(request: ConvertAudioRequest): Promise<ConvertAudioResponse>;
  analyzeAudio(request: AnalyzeAudioRequest): Promise<AnalyzeAudioResponse>;

  /**
   * Standard health check
   */
  healthCheck(request: HealthCheckRequest): Promise<HealthCheckResponse>;
}
