/**
 * Audio Recording Types
 * 
 * Defines TypeScript interfaces and enums for voice input functionality.
 * Used by audio recording hooks and voice input components.
 * 
 * @author Augment Agent
 * @version 1.0.0
 */

/**
 * Represents the current state of audio recording
 */
export enum RecordingState {
  /** Recording is inactive and ready to start */
  IDLE = 'idle',
  /** Currently recording audio */
  RECORDING = 'recording',
  /** Recording has stopped, processing audio */
  PROCESSING = 'processing',
  /** Recording completed successfully */
  COMPLETED = 'completed',
  /** An error occurred during recording */
  ERROR = 'error',
}

/**
 * Audio recording configuration options
 */
export interface AudioRecordingConfig {
  /** Maximum recording duration in milliseconds */
  maxDuration: number;
  /** Audio sample rate (Hz) */
  sampleRate: number;
  /** Number of audio channels (1 = mono, 2 = stereo) */
  channels: number;
  /** Audio MIME type for recording */
  mimeType: string;
}

/**
 * Audio recording data and metadata
 */
export interface AudioRecording {
  /** The recorded audio as a Blob */
  blob: Blob;
  /** Recording duration in milliseconds */
  duration: number;
  /** File size in bytes */
  size: number;
  /** MIME type of the recorded audio */
  mimeType: string;
  /** Timestamp when recording was created */
  timestamp: Date;
}

/**
 * Audio level data for visualization
 */
export interface AudioLevel {
  /** Current audio level (0-100) */
  level: number;
  /** Peak audio level in current session */
  peak: number;
  /** Whether audio is currently being detected */
  isActive: boolean;
}

/**
 * Voice transcription result from Whisper API
 */
export interface TranscriptionResult {
  /** Transcribed text */
  text: string;
  /** Detected language code (e.g., 'en', 'es') */
  language: string;
  /** Confidence score (0-1) if available */
  confidence?: number;
}

/**
 * Error types that can occur during voice input
 */
export enum VoiceInputError {
  /** Microphone permission denied */
  PERMISSION_DENIED = 'permission_denied',
  /** Microphone not available */
  DEVICE_NOT_FOUND = 'device_not_found',
  /** Recording failed */
  RECORDING_FAILED = 'recording_failed',
  /** Transcription API error */
  TRANSCRIPTION_FAILED = 'transcription_failed',
  /** Network error */
  NETWORK_ERROR = 'network_error',
  /** Browser not supported */
  BROWSER_NOT_SUPPORTED = 'browser_not_supported',
}

/**
 * Voice input error with details
 */
export interface VoiceInputErrorDetails {
  /** Error type */
  type: VoiceInputError;
  /** Human-readable error message */
  message: string;
  /** Original error object if available */
  originalError?: Error;
}
