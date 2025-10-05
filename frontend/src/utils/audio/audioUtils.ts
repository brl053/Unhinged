/**
 * Audio Utility Functions
 * 
 * Helper functions for audio processing, format conversion, and browser compatibility.
 * Used by audio recording hooks and components.
 * 
 * @author Augment Agent
 * @version 1.0.0
 */

import { SUPPORTED_MIME_TYPES, DEFAULT_AUDIO_CONFIG } from './constants';
import { VoiceInputError, VoiceInputErrorDetails } from './types';

// Export VoiceInputError for external use
export { VoiceInputError } from './types';

/**
 * Checks if the browser supports audio recording
 * @returns true if MediaRecorder and getUserMedia are available
 */
export const isBrowserSupported = (): boolean => {
  return !!(
    typeof navigator !== 'undefined' &&
    navigator.mediaDevices &&
    typeof navigator.mediaDevices.getUserMedia === 'function' &&
    typeof window !== 'undefined' &&
    window.MediaRecorder
  );
};

/**
 * Gets the best supported MIME type for the current browser
 * @returns The first supported MIME type from our preference list
 */
export const getSupportedMimeType = (): string => {
  if (typeof window === 'undefined' || !window.MediaRecorder) {
    return DEFAULT_AUDIO_CONFIG.mimeType;
  }

  for (const mimeType of SUPPORTED_MIME_TYPES) {
    if (MediaRecorder.isTypeSupported(mimeType)) {
      return mimeType;
    }
  }

  // Fallback to default if none are explicitly supported
  return DEFAULT_AUDIO_CONFIG.mimeType;
};

/**
 * Requests microphone permission and returns the media stream
 * @returns Promise that resolves to MediaStream or rejects with error details
 */
export const requestMicrophoneAccess = async (): Promise<MediaStream> => {
  try {
    if (!isBrowserSupported()) {
      throw createVoiceInputError(
        VoiceInputError.BROWSER_NOT_SUPPORTED,
        'Browser does not support audio recording'
      );
    }

    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        sampleRate: DEFAULT_AUDIO_CONFIG.sampleRate,
        channelCount: DEFAULT_AUDIO_CONFIG.channels,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    });

    return stream;
  } catch (error) {
    if (error instanceof Error) {
      // Handle specific getUserMedia errors
      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        throw createVoiceInputError(VoiceInputError.PERMISSION_DENIED, error.message, error);
      }
      if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        throw createVoiceInputError(VoiceInputError.DEVICE_NOT_FOUND, error.message, error);
      }
    }
    
    throw createVoiceInputError(VoiceInputError.RECORDING_FAILED, 'Failed to access microphone', error as Error);
  }
};

/**
 * Converts audio blob to File object for upload
 * @param blob - The audio blob to convert
 * @param filename - Optional filename (defaults to timestamp-based name)
 * @returns File object ready for upload
 */
export const blobToFile = (blob: Blob, filename?: string): File => {
  const name = filename || `recording-${Date.now()}.webm`;
  return new File([blob], name, { type: blob.type });
};

/**
 * Formats duration in milliseconds to human-readable string
 * @param duration - Duration in milliseconds
 * @returns Formatted string like "1:23" or "0:05"
 */
export const formatDuration = (duration: number): string => {
  const seconds = Math.floor(duration / 1000);
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

/**
 * Calculates audio level from audio data for visualization
 * @param audioData - Float32Array of audio samples
 * @returns Audio level from 0-100
 */
export const calculateAudioLevel = (audioData: Float32Array): number => {
  let sum = 0;
  for (let i = 0; i < audioData.length; i++) {
    sum += Math.abs(audioData[i]);
  }
  const average = sum / audioData.length;
  // Convert to 0-100 scale with some amplification for better UX
  return Math.min(100, Math.floor(average * 200));
};

/**
 * Creates a standardized voice input error object
 * @param type - The error type
 * @param message - Human-readable error message
 * @param originalError - Original error object if available
 * @returns VoiceInputErrorDetails object
 */
export const createVoiceInputError = (
  type: VoiceInputError,
  message: string,
  originalError?: Error
): VoiceInputErrorDetails => {
  return {
    type,
    message,
    originalError,
  };
};

/**
 * Validates audio file before upload
 * @param file - File to validate
 * @returns true if file is valid, throws error if not
 */
export const validateAudioFile = (file: File): boolean => {
  const maxSize = 10 * 1024 * 1024; // 10MB limit
  
  if (file.size > maxSize) {
    throw createVoiceInputError(
      VoiceInputError.RECORDING_FAILED,
      'Audio file is too large. Please record a shorter message.'
    );
  }
  
  if (!file.type.startsWith('audio/')) {
    throw createVoiceInputError(
      VoiceInputError.RECORDING_FAILED,
      'Invalid file type. Please record audio only.'
    );
  }
  
  return true;
};

/**
 * Checks if the browser supports audio playback
 * @returns true if Audio API is available
 */
export const isAudioPlaybackSupported = (): boolean => {
  return !!(
    typeof window !== 'undefined' &&
    window.Audio &&
    typeof window.Audio === 'function'
  );
};

/**
 * Plays an audio blob with error handling
 * @param audioBlob - The audio blob to play
 * @param onEnded - Optional callback when audio finishes playing
 * @param onError - Optional callback when audio playback fails
 * @returns Promise that resolves when audio starts playing
 */
export const playAudioBlob = async (
  audioBlob: Blob,
  onEnded?: () => void,
  onError?: (error: VoiceInputErrorDetails) => void
): Promise<HTMLAudioElement> => {
  try {
    if (!isAudioPlaybackSupported()) {
      throw createVoiceInputError(
        VoiceInputError.BROWSER_NOT_SUPPORTED,
        'Browser does not support audio playback'
      );
    }

    // Create audio URL from blob
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);

    // Set up event listeners
    audio.onended = () => {
      URL.revokeObjectURL(audioUrl); // Clean up memory
      onEnded?.();
    };

    audio.onerror = () => {
      URL.revokeObjectURL(audioUrl); // Clean up memory
      const errorDetails = createVoiceInputError(
        VoiceInputError.PLAYBACK_FAILED,
        'Failed to play audio'
      );
      onError?.(errorDetails);
    };

    // Start playback
    await audio.play();

    return audio;

  } catch (error) {
    if (error instanceof Error) {
      // Handle specific audio errors
      if (error.name === 'NotAllowedError') {
        throw createVoiceInputError(
          VoiceInputError.PLAYBACK_FAILED,
          'Audio playback blocked by browser. Please allow audio autoplay.'
        );
      }
      if (error.name === 'NotSupportedError') {
        throw createVoiceInputError(
          VoiceInputError.PLAYBACK_FAILED,
          'Audio format not supported by browser'
        );
      }
    }

    throw createVoiceInputError(
      VoiceInputError.PLAYBACK_FAILED,
      error instanceof Error ? error.message : 'Failed to play audio'
    );
  }
};

/**
 * Stops and cleans up an audio element
 * @param audio - The audio element to stop
 */
export const stopAudio = (audio: HTMLAudioElement): void => {
  try {
    audio.pause();
    audio.currentTime = 0;
    // Clean up the object URL if it exists
    if (audio.src && audio.src.startsWith('blob:')) {
      URL.revokeObjectURL(audio.src);
    }
  } catch (error) {
    console.warn('Failed to stop audio:', error);
  }
};
