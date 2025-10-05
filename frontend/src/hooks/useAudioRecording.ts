// ============================================================================
// Audio Recording Hook - React Hook for Voice Recording
// ============================================================================
//
// @file useAudioRecording.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description React hook for managing audio recording state and operations
//
// This hook provides a complete interface for audio recording with:
// - MediaRecorder API integration
// - Real-time audio level monitoring
// - Recording state management
// - Error handling and cleanup
// - TypeScript type safety
// ============================================================================

import { useState, useRef, useCallback, useEffect } from 'react';

// ============================================================================
// Types
// ============================================================================

export interface AudioRecordingState {
  isRecording: boolean;
  isPaused: boolean;
  duration: number;
  audioLevel: number;
  error: string | null;
  isSupported: boolean;
}

export interface AudioRecordingOptions {
  maxDuration?: number; // in seconds
  sampleRate?: number;
  echoCancellation?: boolean;
  noiseSuppression?: boolean;
  onDataAvailable?: (chunk: Blob) => void;
  onRecordingComplete?: (audioBlob: Blob) => void;
  onError?: (error: string) => void;
}

export interface AudioRecordingControls {
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  pauseRecording: () => void;
  resumeRecording: () => void;
  cancelRecording: () => void;
  resetRecording: () => void;
}

// ============================================================================
// Audio Recording Hook
// ============================================================================

export function useAudioRecording(options: AudioRecordingOptions = {}) {
  const {
    maxDuration = 300, // 5 minutes default
    sampleRate = 16000,
    echoCancellation = true,
    noiseSuppression = true,
    onDataAvailable,
    onRecordingComplete,
    onError,
  } = options;

  // State
  const [state, setState] = useState<AudioRecordingState>({
    isRecording: false,
    isPaused: false,
    duration: 0,
    audioLevel: 0,
    error: null,
    isSupported: typeof navigator !== 'undefined' && !!navigator.mediaDevices?.getUserMedia,
  });

  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const durationIntervalRef = useRef<NodeJS.Timeout>();
  const animationFrameRef = useRef<number>();

  // ============================================================================
  // Audio Level Monitoring
  // ============================================================================

  const updateAudioLevel = useCallback(() => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);

    // Calculate RMS (Root Mean Square) for more accurate level
    const rms = Math.sqrt(
      dataArray.reduce((sum, value) => sum + value * value, 0) / dataArray.length
    );
    
    const normalizedLevel = Math.min(100, (rms / 255) * 100);

    setState(prev => ({ ...prev, audioLevel: normalizedLevel }));

    if (state.isRecording && !state.isPaused) {
      animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
    }
  }, [state.isRecording, state.isPaused]);

  // ============================================================================
  // Recording Controls
  // ============================================================================

  const startRecording = useCallback(async () => {
    if (!state.isSupported) {
      const error = 'Audio recording is not supported in this browser';
      setState(prev => ({ ...prev, error }));
      onError?.(error);
      return;
    }

    try {
      setState(prev => ({ ...prev, error: null }));

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation,
          noiseSuppression,
          sampleRate,
        },
      });

      streamRef.current = stream;

      // Set up audio context for level monitoring
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 256;

      // Set up media recorder
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/mp4')
        ? 'audio/mp4'
        : '';

      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType,
      });

      audioChunksRef.current = [];

      // Event listeners
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          onDataAvailable?.(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        onRecordingComplete?.(audioBlob);
        cleanup();
      };

      mediaRecorderRef.current.onerror = (event) => {
        const error = `Recording error: ${event.error?.message || 'Unknown error'}`;
        setState(prev => ({ ...prev, error, isRecording: false }));
        onError?.(error);
        cleanup();
      };

      // Start recording
      mediaRecorderRef.current.start(100); // Collect data every 100ms

      setState(prev => ({
        ...prev,
        isRecording: true,
        isPaused: false,
        duration: 0,
        audioLevel: 0,
        error: null,
      }));

      // Start duration timer
      durationIntervalRef.current = setInterval(() => {
        setState(prev => {
          const newDuration = prev.duration + 1;
          
          // Auto-stop at max duration
          if (newDuration >= maxDuration) {
            stopRecording();
            return prev;
          }
          
          return { ...prev, duration: newDuration };
        });
      }, 1000);

      // Start audio level monitoring
      updateAudioLevel();

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to start recording';
      setState(prev => ({ ...prev, error: errorMessage, isRecording: false }));
      onError?.(errorMessage);
    }
  }, [
    state.isSupported,
    echoCancellation,
    noiseSuppression,
    sampleRate,
    maxDuration,
    onDataAvailable,
    onRecordingComplete,
    onError,
    updateAudioLevel,
  ]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && state.isRecording) {
      mediaRecorderRef.current.stop();
      setState(prev => ({ ...prev, isRecording: false, isPaused: false, audioLevel: 0 }));
      
      // Clear timers
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    }
  }, [state.isRecording]);

  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current && state.isRecording && !state.isPaused) {
      mediaRecorderRef.current.pause();
      setState(prev => ({ ...prev, isPaused: true, audioLevel: 0 }));
      
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    }
  }, [state.isRecording, state.isPaused]);

  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current && state.isRecording && state.isPaused) {
      mediaRecorderRef.current.resume();
      setState(prev => ({ ...prev, isPaused: false }));
      updateAudioLevel();
    }
  }, [state.isRecording, state.isPaused, updateAudioLevel]);

  const cancelRecording = useCallback(() => {
    if (mediaRecorderRef.current && state.isRecording) {
      // Stop without triggering onstop event
      mediaRecorderRef.current.ondataavailable = null;
      mediaRecorderRef.current.onstop = null;
      mediaRecorderRef.current.stop();
      
      setState(prev => ({
        ...prev,
        isRecording: false,
        isPaused: false,
        duration: 0,
        audioLevel: 0,
      }));
      
      // Clear audio chunks
      audioChunksRef.current = [];
      
      cleanup();
    }
  }, [state.isRecording]);

  const resetRecording = useCallback(() => {
    setState(prev => ({
      ...prev,
      isRecording: false,
      isPaused: false,
      duration: 0,
      audioLevel: 0,
      error: null,
    }));
    
    audioChunksRef.current = [];
    cleanup();
  }, []);

  // ============================================================================
  // Cleanup
  // ============================================================================

  const cleanup = useCallback(() => {
    // Clear timers
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
      durationIntervalRef.current = undefined;
    }
    
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = undefined;
    }

    // Close audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Stop media stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    // Clear refs
    mediaRecorderRef.current = null;
    analyserRef.current = null;
  }, []);

  // ============================================================================
  // Effects
  // ============================================================================

  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  // ============================================================================
  // Return Hook Interface
  // ============================================================================

  const controls: AudioRecordingControls = {
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    cancelRecording,
    resetRecording,
  };

  return {
    state,
    controls,
    // Convenience getters
    isRecording: state.isRecording,
    isPaused: state.isPaused,
    duration: state.duration,
    audioLevel: state.audioLevel,
    error: state.error,
    isSupported: state.isSupported,
  };
}

export default useAudioRecording;
