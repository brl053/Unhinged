/**
 * Audio Recording Hook
 * 
 * Custom React hook for managing audio recording state and functionality.
 * Provides a clean interface for components to record, process, and manage audio.
 * 
 * @author Augment Agent
 * @version 1.0.0
 * 
 * @example
 * ```tsx
 * const {
 *   recordingState,
 *   audioLevel,
 *   duration,
 *   startRecording,
 *   stopRecording,
 *   clearRecording,
 *   error
 * } = useAudioRecorder();
 * ```
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import {
  RecordingState,
  AudioRecording,
  AudioLevel,
  VoiceInputErrorDetails,
  AudioRecordingConfig,
} from '../utils/audio/types';
import {
  DEFAULT_AUDIO_CONFIG,
  RECORDING_TIMINGS,
  AUDIO_LEVEL_THRESHOLDS,
} from '../utils/audio/constants';
import {
  requestMicrophoneAccess,
  getSupportedMimeType,
  calculateAudioLevel,
  createVoiceInputError,
  VoiceInputError,
} from '../utils/audio/audioUtils';

/**
 * Return type for the useAudioRecorder hook
 */
interface UseAudioRecorderReturn {
  /** Current recording state */
  recordingState: RecordingState;
  /** Current audio recording data (null if no recording) */
  recording: AudioRecording | null;
  /** Real-time audio level data for visualization */
  audioLevel: AudioLevel;
  /** Current recording duration in milliseconds */
  duration: number;
  /** Any error that occurred during recording */
  error: VoiceInputErrorDetails | null;
  /** Start recording audio */
  startRecording: () => Promise<void>;
  /** Stop recording audio */
  stopRecording: () => void;
  /** Clear current recording and reset state */
  clearRecording: () => void;
  /** Whether recording is currently active */
  isRecording: boolean;
}

/**
 * Custom hook for audio recording functionality
 * 
 * Manages MediaRecorder, audio stream, and recording state.
 * Provides real-time audio level monitoring and error handling.
 * 
 * @param config - Optional audio recording configuration
 * @returns Audio recording interface
 */
export const useAudioRecorder = (
  config: Partial<AudioRecordingConfig> = {}
): UseAudioRecorderReturn => {
  // Merge provided config with defaults
  const audioConfig = { ...DEFAULT_AUDIO_CONFIG, ...config };

  // State management
  const [recordingState, setRecordingState] = useState<RecordingState>(RecordingState.IDLE);
  const [recording, setRecording] = useState<AudioRecording | null>(null);
  const [audioLevel, setAudioLevel] = useState<AudioLevel>({
    level: 0,
    peak: 0,
    isActive: false,
  });
  const [duration, setDuration] = useState<number>(0);
  const [error, setError] = useState<VoiceInputErrorDetails | null>(null);

  // Refs for managing recording resources
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Cleans up all recording resources
   */
  const cleanup = useCallback(() => {
    // Stop media recorder
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }

    // Stop media stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    // Close audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Clear intervals and animation frames
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
      durationIntervalRef.current = null;
    }

    // Reset refs
    mediaRecorderRef.current = null;
    analyserRef.current = null;
    startTimeRef.current = null;
  }, []);

  /**
   * Updates audio level visualization
   */
  const updateAudioLevel = useCallback(() => {
    if (!analyserRef.current) return;

    const dataArray = new Float32Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getFloatTimeDomainData(dataArray);

    const level = calculateAudioLevel(dataArray);
    const isActive = level > AUDIO_LEVEL_THRESHOLDS.ACTIVE_THRESHOLD;

    setAudioLevel(prev => ({
      level,
      peak: Math.max(prev.peak, level),
      isActive,
    }));

    if (recordingState === RecordingState.RECORDING) {
      animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
    }
  }, [recordingState]);

  /**
   * Sets up audio analysis for level monitoring
   */
  const setupAudioAnalysis = useCallback((stream: MediaStream) => {
    try {
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(stream);

      analyser.fftSize = 256;
      source.connect(analyser);

      audioContextRef.current = audioContext;
      analyserRef.current = analyser;

      // Start audio level monitoring
      updateAudioLevel();
    } catch (err) {
      console.warn('Audio analysis setup failed:', err);
      // Continue without audio level monitoring
    }
  }, [updateAudioLevel]);

  /**
   * Starts audio recording
   */
  const startRecording = useCallback(async () => {
    try {
      setError(null);
      setRecordingState(RecordingState.RECORDING);

      // Request microphone access
      const stream = await requestMicrophoneAccess();
      streamRef.current = stream;

      // Setup audio analysis for level monitoring
      setupAudioAnalysis(stream);

      // Create MediaRecorder
      const mimeType = getSupportedMimeType();
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType,
      });

      const audioChunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: mimeType });
        const endTime = Date.now();
        const recordingDuration = startTimeRef.current ? endTime - startTimeRef.current : 0;

        const newRecording: AudioRecording = {
          blob: audioBlob,
          duration: recordingDuration,
          size: audioBlob.size,
          mimeType,
          timestamp: new Date(),
        };

        setRecording(newRecording);
        setRecordingState(RecordingState.COMPLETED);
        cleanup();
      };

      mediaRecorder.onerror = (event) => {
        const errorDetails = createVoiceInputError(
          VoiceInputError.RECORDING_FAILED,
          'Recording failed unexpectedly'
        );
        setError(errorDetails);
        setRecordingState(RecordingState.ERROR);
        cleanup();
      };

      mediaRecorderRef.current = mediaRecorder;
      startTimeRef.current = Date.now();

      // Start recording
      mediaRecorder.start();

      // Setup duration tracking
      durationIntervalRef.current = setInterval(() => {
        if (startTimeRef.current) {
          setDuration(Date.now() - startTimeRef.current);
        }
      }, RECORDING_TIMINGS.LEVEL_UPDATE_INTERVAL);

      // Auto-stop at max duration
      setTimeout(() => {
        if (recordingState === RecordingState.RECORDING) {
          stopRecording();
        }
      }, audioConfig.maxDuration);

    } catch (err) {
      const errorDetails = err as VoiceInputErrorDetails;
      setError(errorDetails);
      setRecordingState(RecordingState.ERROR);
      cleanup();
    }
  }, [audioConfig.maxDuration, setupAudioAnalysis, cleanup, recordingState]);

  /**
   * Stops audio recording
   */
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      setRecordingState(RecordingState.PROCESSING);
      mediaRecorderRef.current.stop();
    }
  }, []);

  /**
   * Clears current recording and resets state
   */
  const clearRecording = useCallback(() => {
    setRecording(null);
    setDuration(0);
    setError(null);
    setAudioLevel({ level: 0, peak: 0, isActive: false });
    setRecordingState(RecordingState.IDLE);
    cleanup();
  }, [cleanup]);

  // Cleanup on unmount
  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  return {
    recordingState,
    recording,
    audioLevel,
    duration,
    error,
    startRecording,
    stopRecording,
    clearRecording,
    isRecording: recordingState === RecordingState.RECORDING,
  };
};
