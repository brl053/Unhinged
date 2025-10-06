// ============================================================================
// Voice Recording Hook - Pure Functional Browser API Wrapper
// ============================================================================
//
// @file useVoiceRecording.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Pure functional hook for voice recording using browser APIs
//
// This hook wraps the MediaRecorder API in a pure functional interface:
// - Input: User actions (start/stop)
// - Output: Recording state and audio data
// - Same logic as our working HTML implementation
// - No external dependencies, just browser APIs + React
// ============================================================================

import { useState, useCallback, useRef, useEffect } from 'react';
import { audioService } from '../services/AudioService';

export interface VoiceRecordingState {
  isRecording: boolean;
  isPaused: boolean;
  audioLevel: number;
  duration: number;
  error: string | null;
  isSupported: boolean;
}

export interface VoiceRecordingActions {
  startRecording: () => Promise<boolean>;
  stopRecording: () => Promise<Blob | null>;
  pauseRecording: () => void;
  resumeRecording: () => void;
  cancelRecording: () => void;
}

/**
 * Pure functional voice recording hook
 * Same approach as our working HTML implementation, wrapped in React state
 */
export const useVoiceRecording = (): VoiceRecordingState & VoiceRecordingActions => {
  // State management
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [duration, setDuration] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  // Refs for browser API objects
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // Check browser capabilities (same as HTML implementation)
  const capabilities = audioService.checkBrowserCapabilities();
  const isSupported = capabilities.mediaRecorder && capabilities.getUserMedia;
  
  /**
   * Pure function: Start recording
   * Same logic as HTML implementation
   */
  const startRecording = useCallback(async (): Promise<boolean> => {
    try {
      setError(null);
      
      // Request microphone access (same as HTML)
      const stream = await audioService.requestMicrophoneAccess();
      streamRef.current = stream;
      
      // Create MediaRecorder (same configuration as HTML)
      const mediaRecorder = audioService.createMediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      // Set up audio level monitoring (same as HTML)
      if (capabilities.audioContext) {
        const audioContext = new (AudioContext || (window as any).webkitAudioContext)();
        const analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);
        
        analyser.fftSize = 256;
        source.connect(analyser);
        
        audioContextRef.current = audioContext;
        analyserRef.current = analyser;
        
        // Start audio level monitoring
        const monitorAudioLevel = () => {
          if (!analyserRef.current || !isRecording) return;
          
          const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
          analyserRef.current.getByteFrequencyData(dataArray);
          
          const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
          setAudioLevel(Math.round((average / 255) * 100));
          
          animationFrameRef.current = requestAnimationFrame(monitorAudioLevel);
        };
        
        monitorAudioLevel();
      }
      
      // Start recording
      mediaRecorder.start();
      setIsRecording(true);
      setIsPaused(false);
      
      // Start duration tracking
      startTimeRef.current = Date.now();
      durationIntervalRef.current = setInterval(() => {
        if (startTimeRef.current) {
          setDuration(Math.floor((Date.now() - startTimeRef.current) / 1000));
        }
      }, 1000);
      
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start recording';
      setError(errorMessage);
      console.error('Recording start error:', err);
      return false;
    }
  }, [isRecording, capabilities.audioContext]);
  
  /**
   * Pure function: Stop recording and return audio blob
   * Same logic as HTML implementation
   */
  const stopRecording = useCallback((): Promise<Blob | null> => {
    return new Promise((resolve) => {
      if (!mediaRecorderRef.current || !isRecording) {
        resolve(null);
        return;
      }
      
      // Set up data handler (same as HTML)
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          resolve(event.data);
        } else {
          resolve(null);
        }
      };
      
      // Stop recording
      mediaRecorderRef.current.stop();
      
      // Cleanup (same as HTML)
      setIsRecording(false);
      setIsPaused(false);
      setAudioLevel(0);
      setDuration(0);
      
      // Stop duration tracking
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
        durationIntervalRef.current = null;
      }
      
      // Stop audio level monitoring
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
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
    });
  }, [isRecording]);
  
  /**
   * Pure function: Pause recording
   */
  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording && !isPaused) {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
    }
  }, [isRecording, isPaused]);
  
  /**
   * Pure function: Resume recording
   */
  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording && isPaused) {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
    }
  }, [isRecording, isPaused]);
  
  /**
   * Pure function: Cancel recording
   */
  const cancelRecording = useCallback(() => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
    
    // Same cleanup as stopRecording but don't return data
    setIsRecording(false);
    setIsPaused(false);
    setAudioLevel(0);
    setDuration(0);
    
    // Cleanup intervals and contexts
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
      durationIntervalRef.current = null;
    }
    
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  }, []);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cancelRecording();
    };
  }, [cancelRecording]);
  
  return {
    // State
    isRecording,
    isPaused,
    audioLevel,
    duration,
    error,
    isSupported,
    
    // Actions
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    cancelRecording,
  };
};
