/**
 * VoiceInput Component Types
 * 
 * TypeScript interfaces and enums for the VoiceInput component.
 * Defines props, state, and configuration options.
 * 
 * @author Augment Agent
 * @version 1.0.0
 */

import { TranscriptionResult, VoiceInputErrorDetails } from '../../../src/utils/audio/types';

/**
 * Visual style variants for the voice input button
 */
export enum VoiceInputVariant {
  /** Primary style - main action button */
  PRIMARY = 'primary',
  /** Secondary style - subtle button */
  SECONDARY = 'secondary',
  /** Compact style - smaller button for inline use */
  COMPACT = 'compact',
}

/**
 * Size options for the voice input component
 */
export enum VoiceInputSize {
  /** Small size - 32px */
  SMALL = 'small',
  /** Medium size - 40px */
  MEDIUM = 'medium',
  /** Large size - 48px */
  LARGE = 'large',
}

/**
 * Props for the VoiceInput component
 */
export interface VoiceInputProps {
  /** Callback when transcription is completed */
  onTranscription: (result: TranscriptionResult) => void;
  /** Callback when an error occurs */
  onError?: (error: VoiceInputErrorDetails) => void;
  /** Callback when recording starts */
  onRecordingStart?: () => void;
  /** Callback when recording stops */
  onRecordingStop?: () => void;
  /** Visual variant of the component */
  variant?: VoiceInputVariant;
  /** Size of the component */
  size?: VoiceInputSize;
  /** Whether the component is disabled */
  disabled?: boolean;
  /** Custom placeholder text when not recording */
  placeholder?: string;
  /** Whether to show audio level visualization */
  showAudioLevel?: boolean;
  /** Whether to show recording duration */
  showDuration?: boolean;
  /** Custom CSS class name */
  className?: string;
  /** Maximum recording duration in milliseconds */
  maxDuration?: number;
}

/**
 * Internal state for the VoiceInput component
 */
export interface VoiceInputState {
  /** Whether transcription is in progress */
  isTranscribing: boolean;
  /** Last transcription result */
  lastTranscription: TranscriptionResult | null;
  /** Whether the component is in an error state */
  hasError: boolean;
}
