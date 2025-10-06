import React, { useCallback } from 'react';
import { VoiceRecorderProps } from './types';
import { useVoiceRecording } from './hooks';
import { useTranscribeAudio } from '../../../queries/api';
import { frontendEventService } from '../../../services/EventService';
import { formatDuration, getStatusMessage, getRecordButtonIcon, createVoiceEvent } from './utils';
import {
  StyledRecorderContainer,
  StyledRecordButton,
  StyledStatusText,
  StyledAudioLevelBar,
  StyledDurationDisplay,
  StyledRecordingIndicator,
} from './styles';

export const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onTranscription,
  onError,
  onEvent,
  disabled = false,
  className,
}) => {
  const { mutate: transcribeAudio, isPending: isTranscribing } = useTranscribeAudio();
  
  const {
    isRecording,
    audioLevel,
    duration,
    error,
    startRecording,
    stopRecording,
    recordingState,
  } = useVoiceRecording(onEvent);

  const handleRecordClick = useCallback(async () => {
    if (disabled) return;
    
    if (isRecording) {
      // Stop recording
      const audioBlob = await stopRecording();
      
      if (audioBlob) {
        onEvent?.(createVoiceEvent('transcription_started', { 
          audioSize: audioBlob.size,
          duration 
        }));
        
        // Convert blob to file for transcription
        const audioFile = new File([audioBlob], 'recording.wav', { type: 'audio/wav' });
        
        transcribeAudio(audioFile, {
          onSuccess: (response) => {
            const transcriptionText = typeof response === 'string' ? response : response.text || '';
            onTranscription(transcriptionText);
            onEvent?.(createVoiceEvent('transcription_completed', {
              transcription: transcriptionText.substring(0, 100),
              fullLength: transcriptionText.length
            }));

            // Log to event service (remove if method doesn't exist)
            // frontendEventService.logVoiceTranscriptionCaptured(transcriptionText).catch(console.error);
          },
          onError: (err) => {
            const errorMessage = err instanceof Error ? err.message : 'Transcription failed';
            onError?.(errorMessage);
            onEvent?.(createVoiceEvent('transcription_error', { error: errorMessage }));
          },
        });
      }
    } else {
      // Start recording
      await startRecording();
    }
  }, [
    disabled,
    isRecording,
    stopRecording,
    startRecording,
    transcribeAudio,
    onTranscription,
    onError,
    onEvent,
    duration,
  ]);

  const isProcessing = isTranscribing || recordingState === 'processing';
  const hasError = !!error || recordingState === 'error';
  const statusMessage = getStatusMessage(recordingState, disabled, error);
  const buttonIcon = getRecordButtonIcon(recordingState);

  return (
    <StyledRecorderContainer className={className}>
      <StyledRecordButton
        isRecording={isRecording}
        disabled={disabled || isProcessing}
        onClick={handleRecordClick}
        type="button"
        aria-label={statusMessage}
      >
        {buttonIcon}
      </StyledRecordButton>
      
      {isRecording && (
        <>
          <StyledRecordingIndicator isRecording={isRecording} />
          <StyledDurationDisplay>
            {formatDuration(duration)}
          </StyledDurationDisplay>
          <StyledAudioLevelBar level={audioLevel} />
        </>
      )}
      
      <StyledStatusText error={hasError}>
        {isTranscribing ? 'Transcribing audio...' : statusMessage}
      </StyledStatusText>
    </StyledRecorderContainer>
  );
};
