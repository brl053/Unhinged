/**
 * VoiceInput Component
 * 
 * A comprehensive voice input component that handles audio recording,
 * transcription, and user feedback. Integrates with the Whisper TTS service.
 * 
 * @author Augment Agent
 * @version 1.0.0
 * 
 * @example
 * ```tsx
 * <VoiceInput
 *   onTranscription={(result) => console.log(result.text)}
 *   variant={VoiceInputVariant.PRIMARY}
 *   size={VoiceInputSize.MEDIUM}
 *   showAudioLevel={true}
 * />
 * ```
 */

import React, { useState, useCallback, useEffect } from 'react';
import { Icon } from '../Icon/Icon';
import { IconType, IconSize } from '../Icon/types';
import { useAudioRecorder } from '../../../src/hooks/useAudioRecorder';
import { useTranscribeAudio } from '../../../src/queries/api';
import { RecordingState, TranscriptionResult, VoiceInputErrorDetails } from '../../../src/utils/audio/types';
import { formatDuration, blobToFile, validateAudioFile } from '../../../src/utils/audio/audioUtils';
import { ERROR_MESSAGES } from '../../../src/utils/audio/constants';
import {
  VoiceInputProps,
  VoiceInputVariant,
  VoiceInputSize,
  VoiceInputState,
} from './types';
import {
  VoiceInputContainer,
  VoiceInputButton,
  AudioLevelContainer,
  AudioLevelRipple,
  RecordingDuration,
  StatusText,
  LoadingSpinner,
} from './styles';

/**
 * Maps component size to icon size
 */
const getIconSize = (size: VoiceInputSize): IconSize => {
  switch (size) {
    case VoiceInputSize.SMALL:
      return IconSize.Small;
    case VoiceInputSize.MEDIUM:
      return IconSize.Medium;
    case VoiceInputSize.LARGE:
      return IconSize.Large;
    default:
      return IconSize.Medium;
  }
};

/**
 * VoiceInput Component
 * 
 * Provides a complete voice input interface with recording, transcription,
 * and visual feedback. Handles all states from idle to error gracefully.
 */
export const VoiceInput: React.FC<VoiceInputProps> = ({
  onTranscription,
  onError,
  onRecordingStart,
  onRecordingStop,
  variant = VoiceInputVariant.PRIMARY,
  size = VoiceInputSize.MEDIUM,
  disabled = false,
  placeholder = 'Click to record',
  showAudioLevel = true,
  showDuration = true,
  className,
  maxDuration,
}) => {
  // Component state
  const [state, setState] = useState<VoiceInputState>({
    isTranscribing: false,
    lastTranscription: null,
    hasError: false,
  });

  // Audio recording hook
  const {
    recordingState,
    recording,
    audioLevel,
    duration,
    error: recordingError,
    startRecording,
    stopRecording,
    clearRecording,
    isRecording,
  } = useAudioRecorder({ maxDuration });

  // Transcription API hook
  const transcriptionMutation = useTranscribeAudio();

  /**
   * Handles transcription completion
   */
  const handleTranscriptionSuccess = useCallback((result: TranscriptionResult) => {
    setState(prev => ({
      ...prev,
      isTranscribing: false,
      lastTranscription: result,
      hasError: false,
    }));
    onTranscription(result);
    clearRecording();
  }, [onTranscription, clearRecording]);

  /**
   * Handles transcription errors
   */
  const handleTranscriptionError = useCallback((error: VoiceInputErrorDetails) => {
    setState(prev => ({
      ...prev,
      isTranscribing: false,
      hasError: true,
    }));
    onError?.(error);
  }, [onError]);

  /**
   * Starts transcription process
   */
  const startTranscription = useCallback(async (audioFile: File) => {
    try {
      setState(prev => ({ ...prev, isTranscribing: true, hasError: false }));
      
      const result = await transcriptionMutation.mutateAsync(audioFile);
      handleTranscriptionSuccess(result);
    } catch (error) {
      const errorDetails: VoiceInputErrorDetails = {
        type: 'transcription_failed' as any,
        message: ERROR_MESSAGES.TRANSCRIPTION_FAILED,
        originalError: error as Error,
      };
      handleTranscriptionError(errorDetails);
    }
  }, [transcriptionMutation, handleTranscriptionSuccess, handleTranscriptionError]);

  /**
   * Handles recording button click
   */
  const handleButtonClick = useCallback(async () => {
    if (disabled) return;

    if (isRecording) {
      stopRecording();
      onRecordingStop?.();
    } else {
      try {
        await startRecording();
        onRecordingStart?.();
      } catch (error) {
        const errorDetails = error as VoiceInputErrorDetails;
        setState(prev => ({ ...prev, hasError: true }));
        onError?.(errorDetails);
      }
    }
  }, [disabled, isRecording, startRecording, stopRecording, onRecordingStart, onRecordingStop, onError]);

  /**
   * Effect to handle recording completion
   */
  useEffect(() => {
    if (recordingState === RecordingState.COMPLETED && recording) {
      try {
        validateAudioFile(blobToFile(recording.blob));
        const audioFile = blobToFile(recording.blob);
        startTranscription(audioFile);
      } catch (error) {
        const errorDetails = error as VoiceInputErrorDetails;
        handleTranscriptionError(errorDetails);
      }
    }
  }, [recordingState, recording, startTranscription, handleTranscriptionError]);

  /**
   * Effect to handle recording errors
   */
  useEffect(() => {
    if (recordingError) {
      setState(prev => ({ ...prev, hasError: true }));
      onError?.(recordingError);
    }
  }, [recordingError, onError]);

  /**
   * Gets the appropriate icon based on current state
   */
  const getIcon = (): IconType => {
    if (state.hasError) return IconType.MicrophoneOff;
    if (isRecording) return IconType.Stop;
    return IconType.Microphone;
  };

  /**
   * Gets status text based on current state
   */
  const getStatusText = (): string => {
    if (state.hasError) return 'Error occurred';
    if (state.isTranscribing) return 'Transcribing...';
    if (recordingState === RecordingState.PROCESSING) return 'Processing...';
    if (isRecording) return 'Recording...';
    return placeholder;
  };

  /**
   * Determines if component should show error state
   */
  const hasError = state.hasError || recordingState === RecordingState.ERROR;

  return (
    <VoiceInputContainer
      variant={variant}
      size={size}
      disabled={disabled}
      className={className}
    >
      <VoiceInputButton
        variant={variant}
        size={size}
        isRecording={isRecording}
        hasError={hasError}
        onClick={handleButtonClick}
        disabled={disabled || state.isTranscribing}
        title={getStatusText()}
      >
        {state.isTranscribing ? (
          <LoadingSpinner />
        ) : (
          <Icon type={getIcon()} size={getIconSize(size)} />
        )}

        {/* Audio level visualization */}
        {showAudioLevel && isRecording && (
          <AudioLevelContainer size={size}>
            <AudioLevelRipple
              level={audioLevel.level}
              isActive={audioLevel.isActive}
            />
          </AudioLevelContainer>
        )}
      </VoiceInputButton>

      {/* Recording duration */}
      {showDuration && isRecording && (
        <RecordingDuration variant={variant}>
          {formatDuration(duration)}
        </RecordingDuration>
      )}

      {/* Status text */}
      {variant !== VoiceInputVariant.COMPACT && (
        <StatusText variant={variant} isError={hasError}>
          {getStatusText()}
        </StatusText>
      )}
    </VoiceInputContainer>
  );
};
