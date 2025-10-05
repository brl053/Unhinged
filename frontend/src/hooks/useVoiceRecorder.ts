/**
 * Voice Recorder Hook
 * 
 * Headless voice recording hook using @wmik/use-media-recorder.
 * Integrates with Whisper TTS service for speech-to-text transcription.
 * Provides offline caching with Dexie.
 * 
 * @author Augment Agent
 * @version 1.0.0
 */

import { useEffect, useCallback, useState } from 'react';
import useMediaRecorder from '@wmik/use-media-recorder';
import { useMutation } from '@tanstack/react-query';
import { apiHelpers, TranscriptionResponse } from '../services/api';
import { dbHelpers } from '../services/db';

// Hook configuration interface
export interface VoiceRecorderConfig {
  /** Maximum recording duration in milliseconds */
  maxDuration?: number;
  /** Audio constraints for recording */
  audioConstraints?: MediaTrackConstraints;
  /** Auto-transcribe when recording stops */
  autoTranscribe?: boolean;
  /** Cache audio locally */
  cacheAudio?: boolean;
}

// Hook return interface
export interface VoiceRecorderReturn {
  // Recording state
  status: 'idle' | 'recording' | 'stopped' | 'error';
  audioBlob: Blob | null;
  duration: number;
  
  // Transcription state
  transcript: string | null;
  isTranscribing: boolean;
  transcriptionError: Error | null;
  
  // Controls
  startRecording: () => void;
  stopRecording: () => void;
  clearRecording: () => void;
  transcribe: () => void;
  
  // Error state
  error: Error | null;
}

// Default configuration
const DEFAULT_CONFIG: Required<VoiceRecorderConfig> = {
  maxDuration: 5 * 60 * 1000, // 5 minutes
  audioConstraints: {
    echoCancellation: true,
    noiseSuppression: true,
    sampleRate: 16000, // Optimal for Whisper
    channelCount: 1 // Mono audio
  },
  autoTranscribe: true,
  cacheAudio: true
};

/**
 * Voice Recorder Hook
 * 
 * @param config - Configuration options
 * @returns Voice recorder controls and state
 * 
 * @example
 * ```tsx
 * const VoiceButton = () => {
 *   const { status, transcript, startRecording, stopRecording } = useVoiceRecorder({
 *     maxDuration: 60000, // 1 minute
 *     autoTranscribe: true
 *   });
 *   
 *   return (
 *     <button onClick={status === 'recording' ? stopRecording : startRecording}>
 *       {status === 'recording' ? '🛑 Stop' : '🎤 Record'}
 *     </button>
 *   );
 * };
 * ```
 */
export const useVoiceRecorder = (config: VoiceRecorderConfig = {}): VoiceRecorderReturn => {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  
  // Internal state
  const [duration, setDuration] = useState(0);
  const [transcript, setTranscript] = useState<string | null>(null);
  
  // Media recorder hook
  const {
    status,
    mediaBlob,
    startRecording: startMediaRecording,
    stopRecording: stopMediaRecording,
    error: recorderError
  } = useMediaRecorder({
    blobOptions: { type: 'audio/webm' },
    mediaStreamConstraints: {
      audio: finalConfig.audioConstraints
    }
  });

  // Transcription mutation
  const {
    mutate: transcribeAudio,
    data: transcriptionData,
    isPending: isTranscribing,
    error: transcriptionError,
    reset: resetTranscription
  } = useMutation({
    mutationFn: async (blob: Blob): Promise<TranscriptionResponse> => {
      console.log('🎙️ Starting transcription...', { size: blob.size, type: blob.type });
      
      try {
        const result = await apiHelpers.transcribeAudio(blob);
        console.log('✅ Transcription successful:', result);
        
        // Cache audio and transcript if enabled
        if (finalConfig.cacheAudio) {
          await dbHelpers.audioCache.store(blob, result.text);
          console.log('💾 Audio cached locally');
        }
        
        return result;
      } catch (error) {
        console.error('❌ Transcription failed:', error);
        throw error;
      }
    },
    onSuccess: (data) => {
      setTranscript(data.text);
    },
    onError: (error) => {
      console.error('❌ Transcription error:', error);
    }
  });

  // Duration tracking
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (status === 'recording') {
      const startTime = Date.now();
      interval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        setDuration(elapsed);
        
        // Auto-stop at max duration
        if (elapsed >= finalConfig.maxDuration) {
          console.log('⏰ Max duration reached, stopping recording');
          stopMediaRecording();
        }
      }, 100);
    } else {
      setDuration(0);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [status, finalConfig.maxDuration, stopMediaRecording]);

  // Auto-transcribe when recording stops
  useEffect(() => {
    if (status === 'stopped' && mediaBlob && finalConfig.autoTranscribe) {
      console.log('🎯 Auto-transcribing recording...');
      transcribeAudio(mediaBlob);
    }
  }, [status, mediaBlob, finalConfig.autoTranscribe, transcribeAudio]);

  // Enhanced controls
  const startRecording = useCallback(() => {
    console.log('🎤 Starting voice recording...');
    setTranscript(null);
    resetTranscription();
    startMediaRecording();
  }, [startMediaRecording, resetTranscription]);

  const stopRecording = useCallback(() => {
    console.log('🛑 Stopping voice recording...');
    stopMediaRecording();
  }, [stopMediaRecording]);

  const clearRecording = useCallback(() => {
    console.log('🗑️ Clearing recording...');
    // Note: @wmik/use-media-recorder doesn't have clearBlobUrl
    setTranscript(null);
    setDuration(0);
    resetTranscription();
  }, [resetTranscription]);

  const transcribe = useCallback(() => {
    if (mediaBlob) {
      console.log('🎯 Manual transcription triggered...');
      transcribeAudio(mediaBlob);
    } else {
      console.warn('⚠️ No audio blob available for transcription');
    }
  }, [mediaBlob, transcribeAudio]);

  // Update transcript from mutation data
  useEffect(() => {
    if (transcriptionData) {
      setTranscript(transcriptionData.text);
    }
  }, [transcriptionData]);

  return {
    // Recording state
    status: status as 'idle' | 'recording' | 'stopped' | 'error',
    audioBlob: mediaBlob,
    duration,

    // Transcription state
    transcript,
    isTranscribing,
    transcriptionError,

    // Controls
    startRecording,
    stopRecording,
    clearRecording,
    transcribe,

    // Error state
    error: recorderError || transcriptionError
  };
};

// Utility hook for voice recorder status
export const useVoiceRecorderStatus = (recorder: VoiceRecorderReturn) => {
  const isIdle = recorder.status === 'idle';
  const isRecording = recorder.status === 'recording';
  const isStopped = recorder.status === 'stopped';
  const hasError = recorder.status === 'error' || !!recorder.error;
  const hasAudio = !!recorder.audioBlob;
  const hasTranscript = !!recorder.transcript;
  const isProcessing = recorder.isTranscribing;
  
  const statusText = (() => {
    if (hasError) return 'Error occurred';
    if (isProcessing) return 'Transcribing...';
    if (isRecording) return 'Recording...';
    if (isStopped && hasAudio) return 'Recording complete';
    return 'Click to record';
  })();
  
  return {
    isIdle,
    isRecording,
    isStopped,
    hasError,
    hasAudio,
    hasTranscript,
    isProcessing,
    statusText
  };
};
