// ============================================================================
// Voice Recorder Component - Pure Functional UI
// ============================================================================
//
// @file VoiceRecorder.tsx
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Pure functional voice recording component
//
// This component provides the same excellent UX as our HTML implementation:
// - Clear visual feedback (recording state, audio levels)
// - Error handling and user guidance
// - Pure functional interface (onTranscription callback)
// - Same button behavior and status indicators
// ============================================================================

import React, { useCallback } from 'react';
import styled from 'styled-components';
import { useVoiceRecording } from '../../hooks/useVoiceRecording';
import { useTranscribeAudio } from '../../queries/api';
import { frontendEventService } from '../../services/EventService';

// ============================================================================
// Styled Components - Same aesthetic as HTML implementation
// ============================================================================

const RecorderContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 16px;
`;

const RecordButton = styled.button<{ isRecording: boolean; disabled: boolean }>`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 3px solid ${({ theme, isRecording }) => 
    isRecording ? '#ff4444' : theme.color.border.primary};
  background: ${({ theme, isRecording }) => 
    isRecording ? '#ff4444' : theme.color.background.secondary};
  color: white;
  font-size: 24px;
  cursor: ${({ disabled }) => disabled ? 'not-allowed' : 'pointer'};
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover:not(:disabled) {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }
  
  &:disabled {
    opacity: 0.6;
  }
`;

const StatusText = styled.div<{ error?: boolean }>`
  font-size: 14px;
  color: ${({ theme, error }) => 
    error ? '#ff4444' : theme.color.text.secondary};
  text-align: center;
  min-height: 20px;
`;

const AudioLevelBar = styled.div<{ level: number }>`
  width: 200px;
  height: 4px;
  background: ${({ theme }) => theme.color.background.primary};
  border-radius: 2px;
  overflow: hidden;
  
  &::after {
    content: '';
    display: block;
    width: ${({ level }) => level}%;
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #FFC107, #FF5722);
    transition: width 0.1s ease;
  }
`;

const DurationDisplay = styled.div`
  font-size: 16px;
  font-weight: bold;
  color: ${({ theme }) => theme.color.text.primary};
  font-family: monospace;
`;

// ============================================================================
// Component Interface
// ============================================================================

interface VoiceRecorderProps {
  onTranscription: (text: string) => void;
  onError?: (error: string) => void;
  disabled?: boolean;
  maxDuration?: number; // seconds
  onEvent?: (event: { type: string; source: string; data: any }) => void;
}

/**
 * Pure functional voice recorder component
 * Same UX patterns as our working HTML implementation
 */
export const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onTranscription,
  onError,
  disabled = false,
  maxDuration = 300, // 5 minutes default
  onEvent
}) => {
  // Voice recording state and actions
  const {
    isRecording,
    isPaused,
    audioLevel,
    duration,
    error: recordingError,
    isSupported,
    startRecording,
    stopRecording,
    cancelRecording,
  } = useVoiceRecording();
  
  // Transcription mutation
  const { 
    mutate: transcribe, 
    isPending: isTranscribing, 
    error: transcriptionError 
  } = useTranscribeAudio();
  
  // Combined error state
  const error = recordingError || (transcriptionError?.message);
  const isDisabled = disabled || !isSupported || isTranscribing;
  
  /**
   * Handle recording button click
   * Same logic flow as HTML implementation + event logging
   */
  const handleRecordClick = useCallback(async () => {
    if (isRecording) {
      // Stop recording and transcribe
      try {
        const startTime = Date.now();
        const audioBlob = await stopRecording();

        if (audioBlob) {
          // Add event to live feed
          onEvent?.({
            type: 'voice_recording_stopped',
            source: 'voice-recorder',
            data: {
              duration: duration * 1000,
              audioSize: audioBlob.size,
              audioFormat: audioBlob.type
            }
          });

          // Log voice recording stopped
          await frontendEventService.logVoiceRecordingStopped(
            duration * 1000, // Convert to milliseconds
            audioBlob.size,
            audioBlob.type
          );

          // Add transcription started event
          onEvent?.({
            type: 'transcription_started',
            source: 'whisper-tts',
            data: {
              audioSize: audioBlob.size
            }
          });

          // Log transcription started
          await frontendEventService.logTranscriptionStarted(audioBlob.size);

          // Transcribe the audio (same API call as HTML)
          transcribe(audioBlob, {
            onSuccess: async (result) => {
              const processingTime = Date.now() - startTime;

              // Add transcription completed event
              onEvent?.({
                type: 'transcription_completed',
                source: 'whisper-tts',
                data: {
                  transcriptionText: result.text,
                  language: result.language,
                  processingTimeMs: processingTime,
                  audioSize: audioBlob.size
                }
              });

              // Log transcription completed
              await frontendEventService.logTranscriptionCompleted(
                audioBlob.size,
                result.text,
                result.language,
                processingTime
              );

              // Log feature usage
              await frontendEventService.logFeatureUsed('voice_transcription');

              onTranscription(result.text);
            },
            onError: async (err) => {
              const errorMessage = err instanceof Error ? err.message : 'Transcription failed';

              // Log transcription error
              await frontendEventService.logTranscriptionError(audioBlob.size, errorMessage);

              onError?.(errorMessage);
            },
          });
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to stop recording';

        // Log voice recording error
        await frontendEventService.logVoiceRecordingError(errorMessage);

        onError?.(errorMessage);
      }
    } else {
      // Start recording
      try {
        // Log button click
        await frontendEventService.logButtonClick('voice-record-button', 'start_recording');

        const success = await startRecording();
        if (success) {
          // Add event to live feed
          onEvent?.({
            type: 'voice_recording_started',
            source: 'voice-recorder',
            data: {
              audioFormat: 'webm'
            }
          });

          // Log voice recording started
          await frontendEventService.logVoiceRecordingStarted('webm');

          // Log feature usage
          await frontendEventService.logFeatureUsed('voice_recording');
        } else {
          const errorMessage = 'Failed to start recording';
          await frontendEventService.logVoiceRecordingError(errorMessage);
          onError?.(errorMessage);
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to start recording';
        await frontendEventService.logVoiceRecordingError(errorMessage);
        onError?.(errorMessage);
      }
    }
  }, [isRecording, startRecording, stopRecording, transcribe, onTranscription, onError, duration]);
  
  /**
   * Auto-stop recording at max duration
   */
  React.useEffect(() => {
    if (isRecording && duration >= maxDuration) {
      handleRecordClick();
    }
  }, [isRecording, duration, maxDuration, handleRecordClick]);
  
  /**
   * Format duration display
   */
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  /**
   * Get status text (same messaging as HTML implementation)
   */
  const getStatusText = (): string => {
    if (!isSupported) {
      return 'Voice recording not supported in this browser';
    }
    if (error) {
      return error;
    }
    if (isTranscribing) {
      return 'Processing recording...';
    }
    if (isRecording) {
      return isPaused ? 'Recording paused - Click to resume' : 'Recording... Click to stop';
    }
    return 'Click to start voice recording';
  };
  
  /**
   * Get button icon (same as HTML implementation)
   */
  const getButtonIcon = (): string => {
    if (isTranscribing) {
      return '⏳';
    }
    if (isRecording) {
      return '⏹️';
    }
    return '🎤';
  };
  
  return (
    <RecorderContainer>
      <RecordButton
        onClick={handleRecordClick}
        disabled={isDisabled}
        isRecording={isRecording}
      >
        {getButtonIcon()}
      </RecordButton>
      
      {isRecording && (
        <>
          <DurationDisplay>
            {formatDuration(duration)}
          </DurationDisplay>
          <AudioLevelBar level={audioLevel} />
        </>
      )}
      
      <StatusText error={!!error}>
        {getStatusText()}
      </StatusText>
    </RecorderContainer>
  );
};
