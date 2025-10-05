// ============================================================================
// VoiceInput Component - Audio Recording with Visualization
// ============================================================================
//
// @file VoiceInput.tsx
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description React component for voice recording with real-time audio visualization
//
// This component provides a complete voice input interface with:
// - Real-time audio recording using MediaRecorder API
// - Audio level visualization with animated waveform
// - Recording controls (start, stop, cancel)
// - Automatic speech-to-text transcription
// - Error handling and loading states
// - Accessibility support
// ============================================================================

import React, { useState, useRef, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { useTranscribeAudio } from '../../../services/AudioService';
import { STTResponse } from '../../../proto/audio';

// ============================================================================
// Types
// ============================================================================

export interface VoiceInputProps {
  onTranscription?: (result: STTResponse) => void;
  onError?: (error: string) => void;
  onRecordingStart?: () => void;
  onRecordingStop?: () => void;
  disabled?: boolean;
  maxDuration?: number; // in seconds
  className?: string;
}

interface RecordingState {
  isRecording: boolean;
  isPaused: boolean;
  duration: number;
  audioLevel: number;
}

// ============================================================================
// Styled Components
// ============================================================================

const Container = styled.div<{ disabled?: boolean }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 12px;
  background: ${props => props.theme?.colors?.surface || '#f8f9fa'};
  border: 2px solid ${props => props.disabled ? '#e9ecef' : 'transparent'};
  opacity: ${props => props.disabled ? 0.6 : 1};
  transition: all 0.2s ease;
`;

const VisualizationContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 200px;
  height: 80px;
  background: ${props => props.theme?.colors?.background || '#ffffff'};
  border-radius: 8px;
  border: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
  overflow: hidden;
`;

const WaveformBar = styled.div<{ height: number; isActive: boolean }>`
  width: 4px;
  height: ${props => Math.max(4, props.height)}px;
  background: ${props => props.isActive 
    ? props.theme?.colors?.primary || '#007bff'
    : props.theme?.colors?.muted || '#6c757d'
  };
  margin: 0 1px;
  border-radius: 2px;
  transition: height 0.1s ease, background-color 0.2s ease;
`;

const ControlsContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const RecordButton = styled.button<{ isRecording: boolean }>`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: none;
  background: ${props => props.isRecording 
    ? props.theme?.colors?.danger || '#dc3545'
    : props.theme?.colors?.primary || '#007bff'
  };
  color: white;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  &:active {
    transform: scale(0.95);
  }
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.6;
    transform: none;
  }
`;

const SecondaryButton = styled.button`
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
  background: ${props => props.theme?.colors?.surface || '#f8f9fa'};
  color: ${props => props.theme?.colors?.text || '#212529'};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.theme?.colors?.hover || '#e9ecef'};
  }
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

const StatusText = styled.div<{ type?: 'info' | 'error' | 'success' }>`
  font-size: 14px;
  color: ${props => {
    switch (props.type) {
      case 'error': return props.theme?.colors?.danger || '#dc3545';
      case 'success': return props.theme?.colors?.success || '#28a745';
      default: return props.theme?.colors?.muted || '#6c757d';
    }
  }};
  text-align: center;
  min-height: 20px;
`;

const DurationDisplay = styled.div`
  font-family: monospace;
  font-size: 16px;
  font-weight: bold;
  color: ${props => props.theme?.colors?.text || '#212529'};
`;

// ============================================================================
// VoiceInput Component
// ============================================================================

export const VoiceInput: React.FC<VoiceInputProps> = ({
  onTranscription,
  onError,
  onRecordingStart,
  onRecordingStop,
  disabled = false,
  maxDuration = 300, // 5 minutes default
  className,
}) => {
  // State
  const [recordingState, setRecordingState] = useState<RecordingState>({
    isRecording: false,
    isPaused: false,
    duration: 0,
    audioLevel: 0,
  });
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [statusType, setStatusType] = useState<'info' | 'error' | 'success'>('info');

  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const animationFrameRef = useRef<number>();
  const durationIntervalRef = useRef<NodeJS.Timeout>();

  // Hooks
  const transcribeAudio = useTranscribeAudio();

  // ============================================================================
  // Audio Level Monitoring
  // ============================================================================

  const updateAudioLevel = useCallback(() => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);

    // Calculate average audio level
    const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
    const normalizedLevel = Math.min(100, (average / 255) * 100);

    setRecordingState(prev => ({ ...prev, audioLevel: normalizedLevel }));

    if (recordingState.isRecording) {
      animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
    }
  }, [recordingState.isRecording]);

  // ============================================================================
  // Recording Controls
  // ============================================================================

  const startRecording = useCallback(async () => {
    try {
      setStatusMessage('Requesting microphone access...');
      setStatusType('info');

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
        }
      });

      // Set up audio context for level monitoring
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 256;

      // Set up media recorder
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
      });

      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await processRecording(audioBlob);
        
        // Clean up
        stream.getTracks().forEach(track => track.stop());
        if (audioContextRef.current) {
          audioContextRef.current.close();
        }
      };

      // Start recording
      mediaRecorderRef.current.start(100); // Collect data every 100ms
      
      setRecordingState(prev => ({ 
        ...prev, 
        isRecording: true, 
        duration: 0,
        audioLevel: 0 
      }));
      
      setStatusMessage('Recording... Speak now');
      setStatusType('info');

      // Start duration timer
      durationIntervalRef.current = setInterval(() => {
        setRecordingState(prev => {
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

      onRecordingStart?.();

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to start recording';
      setStatusMessage(`Error: ${errorMessage}`);
      setStatusType('error');
      onError?.(errorMessage);
    }
  }, [maxDuration, onRecordingStart, onError, updateAudioLevel]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && recordingState.isRecording) {
      mediaRecorderRef.current.stop();
      
      setRecordingState(prev => ({ 
        ...prev, 
        isRecording: false,
        audioLevel: 0 
      }));
      
      setStatusMessage('Processing recording...');
      setStatusType('info');

      // Clear timers
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }

      onRecordingStop?.();
    }
  }, [recordingState.isRecording, onRecordingStop]);

  const cancelRecording = useCallback(() => {
    if (mediaRecorderRef.current && recordingState.isRecording) {
      // Stop recording without processing
      const stream = mediaRecorderRef.current.stream;
      mediaRecorderRef.current.stop();
      stream.getTracks().forEach(track => track.stop());
      
      setRecordingState({
        isRecording: false,
        isPaused: false,
        duration: 0,
        audioLevel: 0,
      });
      
      setStatusMessage('Recording cancelled');
      setStatusType('info');

      // Clear timers
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }

      // Clear audio chunks to prevent processing
      audioChunksRef.current = [];

      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    }
  }, [recordingState.isRecording]);

  // ============================================================================
  // Audio Processing
  // ============================================================================

  const processRecording = useCallback(async (audioBlob: Blob) => {
    try {
      setStatusMessage('Transcribing audio...');
      setStatusType('info');

      // Convert blob to Uint8Array
      const arrayBuffer = await audioBlob.arrayBuffer();
      const audioData = new Uint8Array(arrayBuffer);

      // Transcribe audio
      const result = await transcribeAudio.mutateAsync({ audioData });
      
      setStatusMessage('Transcription complete!');
      setStatusType('success');
      
      onTranscription?.(result);

      // Clear status after 3 seconds
      setTimeout(() => {
        setStatusMessage('');
      }, 3000);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Transcription failed';
      setStatusMessage(`Error: ${errorMessage}`);
      setStatusType('error');
      onError?.(errorMessage);
    }
  }, [transcribeAudio, onTranscription, onError]);

  // ============================================================================
  // Cleanup
  // ============================================================================

  useEffect(() => {
    return () => {
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  // ============================================================================
  // Render Helpers
  // ============================================================================

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const renderWaveform = () => {
    const bars = Array.from({ length: 20 }, (_, i) => {
      const height = recordingState.isRecording 
        ? Math.max(4, (recordingState.audioLevel / 100) * 60 + Math.random() * 10)
        : 4;
      
      return (
        <WaveformBar
          key={i}
          height={height}
          isActive={recordingState.isRecording}
        />
      );
    });

    return bars;
  };

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <Container disabled={disabled} className={className}>
      <VisualizationContainer>
        {renderWaveform()}
      </VisualizationContainer>

      <DurationDisplay>
        {formatDuration(recordingState.duration)}
      </DurationDisplay>

      <ControlsContainer>
        {!recordingState.isRecording ? (
          <RecordButton
            isRecording={false}
            onClick={startRecording}
            disabled={disabled || transcribeAudio.isPending}
            aria-label="Start recording"
          >
            🎤
          </RecordButton>
        ) : (
          <>
            <RecordButton
              isRecording={true}
              onClick={stopRecording}
              disabled={disabled}
              aria-label="Stop recording"
            >
              ⏹️
            </RecordButton>
            <SecondaryButton
              onClick={cancelRecording}
              disabled={disabled}
              aria-label="Cancel recording"
            >
              Cancel
            </SecondaryButton>
          </>
        )}
      </ControlsContainer>

      <StatusText type={statusType}>
        {transcribeAudio.isPending ? 'Transcribing...' : statusMessage}
      </StatusText>
    </Container>
  );
};

export default VoiceInput;

// ============================================================================
// Export Types
// ============================================================================

export type { VoiceInputProps };
