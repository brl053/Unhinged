/**
 * Audio Recording Constants
 * 
 * Configuration constants for voice input functionality.
 * Centralized settings that can be easily adjusted for different environments.
 * 
 * @author Augment Agent
 * @version 1.0.0
 */

import { AudioRecordingConfig } from './types';

/**
 * Default audio recording configuration
 * Optimized for speech recognition with Whisper
 */
export const DEFAULT_AUDIO_CONFIG: AudioRecordingConfig = {
  /** 5 minutes max recording time */
  maxDuration: 5 * 60 * 1000,
  /** 16kHz sample rate - good balance of quality and file size for speech */
  sampleRate: 16000,
  /** Mono audio - sufficient for speech and reduces file size */
  channels: 1,
  /** WebM with Opus codec - widely supported and efficient */
  mimeType: 'audio/webm;codecs=opus',
};

/**
 * Fallback MIME types for browser compatibility
 * Ordered by preference (best quality/compatibility first)
 */
export const SUPPORTED_MIME_TYPES = [
  'audio/webm;codecs=opus',
  'audio/webm',
  'audio/mp4',
  'audio/wav',
] as const;

/**
 * Audio level thresholds for UI feedback
 */
export const AUDIO_LEVEL_THRESHOLDS = {
  /** Minimum level to consider as "active" speech */
  ACTIVE_THRESHOLD: 10,
  /** Level considered "loud" for visual feedback */
  LOUD_THRESHOLD: 70,
  /** Maximum level for normalization */
  MAX_LEVEL: 100,
} as const;

/**
 * Recording UI timing constants
 */
export const RECORDING_TIMINGS = {
  /** How often to update audio level visualization (ms) */
  LEVEL_UPDATE_INTERVAL: 100,
  /** Minimum recording duration to prevent accidental taps (ms) */
  MIN_RECORDING_DURATION: 500,
  /** Debounce time for stop recording button (ms) */
  STOP_DEBOUNCE: 200,
} as const;

/**
 * API endpoints for voice services
 */
export const VOICE_API_ENDPOINTS = {
  /** Whisper transcription endpoint */
  TRANSCRIBE: '/transcribe',
  /** Health check endpoint */
  HEALTH: '/health',
} as const;

/**
 * Error messages for user feedback
 * Friendly, actionable messages for common issues
 */
export const ERROR_MESSAGES = {
  PERMISSION_DENIED: 'Microphone access is required. Please allow microphone permissions and try again.',
  DEVICE_NOT_FOUND: 'No microphone found. Please check your audio devices and try again.',
  RECORDING_FAILED: 'Recording failed. Please try again.',
  TRANSCRIPTION_FAILED: 'Could not transcribe audio. Please try speaking more clearly.',
  NETWORK_ERROR: 'Network error. Please check your connection and try again.',
  BROWSER_NOT_SUPPORTED: 'Your browser does not support audio recording. Please use a modern browser.',
} as const;
