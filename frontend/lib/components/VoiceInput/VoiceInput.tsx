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

import React from 'react';
import { Icon } from '../Icon/Icon';
import { IconType, IconSize } from '../Icon/types';
import { useVoiceRecorder, useVoiceRecorderStatus } from '../../../src/hooks/useVoiceRecorder';
import { TranscriptionResult, VoiceInputErrorDetails } from '../../../src/utils/audio/types';
import { formatDuration } from '../../../src/utils/audio/audioUtils';
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
  // Voice recorder hook
  const recorder = useVoiceRecorder({
    maxDuration,
    autoTranscribe: true,
    cacheAudio: true
  });

  // Voice recorder status helper
  const status = useVoiceRecorderStatus(recorder);

  // Handle transcription completion
  React.useEffect(() => {
    if (recorder.transcript) {
      const result: TranscriptionResult = {
        text: recorder.transcript,
        language: 'en', // TODO: Get from transcription response
        confidence: 1.0 // TODO: Get from transcription response
      };
      onTranscription(result);
    }
  }, [recorder.transcript, onTranscription]);

  // Handle errors
  React.useEffect(() => {
    if (recorder.error) {
      const errorDetails: VoiceInputErrorDetails = {
        type: 'recording_failed' as any,
        message: recorder.error.message,
        originalError: recorder.error
      };
      onError?.(errorDetails);
    }
  }, [recorder.error, onError]);

  // Handle recording start/stop callbacks
  React.useEffect(() => {
    if (recorder.status === 'recording') {
      onRecordingStart?.();
    } else if (recorder.status === 'stopped') {
      onRecordingStop?.();
    }
  }, [recorder.status, onRecordingStart, onRecordingStop]);

  /**
   * Handles recording button click
   */
  const handleButtonClick = () => {
    if (disabled || status.isProcessing) return;

    if (status.isRecording) {
      recorder.stopRecording();
    } else {
      recorder.startRecording();
    }
  };

  /**
   * Gets the appropriate icon based on current state
   */
  const getIcon = (): IconType => {
    if (status.hasError) return IconType.MicrophoneOff;
    if (status.isRecording) return IconType.Stop;
    return IconType.Microphone;
  };

  return (
    <VoiceInputContainer
      $variant={variant}
      $size={size}
      $disabled={disabled}
      className={className}
    >
      <VoiceInputButton
        $variant={variant}
        $size={size}
        $isRecording={status.isRecording}
        $hasError={status.hasError}
        onClick={handleButtonClick}
        disabled={disabled || status.isProcessing}
        title={status.statusText}
      >
        {status.isProcessing ? (
          <LoadingSpinner />
        ) : (
          <Icon type={getIcon()} size={getIconSize(size)} />
        )}

        {/* Audio level visualization */}
        {showAudioLevel && status.isRecording && (
          <AudioLevelContainer size={size}>
            <AudioLevelRipple
              $level={50}
              $isActive={true}
            />
          </AudioLevelContainer>
        )}
      </VoiceInputButton>

      {/* Recording duration */}
      {showDuration && status.isRecording && (
        <RecordingDuration variant={variant}>
          {formatDuration(recorder.duration)}
        </RecordingDuration>
      )}

      {/* Status text */}
      {variant !== VoiceInputVariant.COMPACT && (
        <StatusText variant={variant} $isError={status.hasError}>
          {status.statusText}
        </StatusText>
      )}
    </VoiceInputContainer>
  );
};
