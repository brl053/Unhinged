import styled from 'styled-components';
import { 
  StyledVoiceRecorderProps, 
  StyledRecordButtonProps, 
  StyledStatusTextProps, 
  StyledAudioLevelBarProps,
  StyledDurationDisplayProps 
} from './types';
import { VOICE_RECORDER_CONSTANTS } from './constants';

export const StyledRecorderContainer = styled.div<StyledVoiceRecorderProps>`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: ${({ theme }) => theme.spatial.base.spacing.md}px;
  padding: ${({ theme }) => theme.spatial.base.spacing.lg}px;
`;

export const StyledRecordButton = styled.button<StyledRecordButtonProps>`
  width: ${VOICE_RECORDER_CONSTANTS.BUTTON_SIZE}px;
  height: ${VOICE_RECORDER_CONSTANTS.BUTTON_SIZE}px;
  border-radius: 50%;
  border: ${({ theme }) => theme.spatial.base.border.thick}px solid ${({ theme, isRecording }) => 
    isRecording ? theme.colors.semantic.intent.danger : theme.colors.semantic.context.border.primary};
  background: ${({ theme, isRecording }) => 
    isRecording ? theme.colors.semantic.intent.danger : theme.colors.semantic.context.background.secondary};
  color: ${({ theme }) => theme.colors.semantic.context.text.primary};
  font-size: ${({ theme }) => theme.typography.scale.large * 16}px;
  cursor: ${({ disabled }) => disabled ? 'not-allowed' : 'pointer'};
  transition: all ${({ theme }) => theme.motion.duration.moderate}ms ${({ theme }) => theme.motion.easing.easeOut};
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover:not(:disabled) {
    transform: scale(${VOICE_RECORDER_CONSTANTS.HOVER_SCALE});
    box-shadow: 0 ${({ theme }) => theme.spatial.base.spacing.xs}px ${({ theme }) => theme.spatial.base.spacing.md}px ${({ theme }) => theme.colors.semantic.context.background.primary}33;
  }
  
  &:disabled {
    opacity: ${VOICE_RECORDER_CONSTANTS.DISABLED_OPACITY};
  }
`;

export const StyledStatusText = styled.div<StyledStatusTextProps>`
  font-size: ${({ theme }) => theme.typography.scale.small * 16}px;
  color: ${({ theme, error }) => 
    error ? theme.colors.semantic.intent.danger : theme.colors.semantic.context.text.secondary};
  text-align: center;
  min-height: ${VOICE_RECORDER_CONSTANTS.MIN_STATUS_HEIGHT}px;
  font-weight: ${({ theme }) => theme.typography.weights.medium};
`;

export const StyledAudioLevelBar = styled.div<StyledAudioLevelBarProps>`
  width: ${VOICE_RECORDER_CONSTANTS.AUDIO_LEVEL_BAR_WIDTH}px;
  height: ${VOICE_RECORDER_CONSTANTS.AUDIO_LEVEL_BAR_HEIGHT}px;
  background: ${({ theme }) => theme.colors.semantic.context.background.primary};
  border-radius: ${({ theme }) => theme.spatial.base.radius.sm}px;
  overflow: hidden;
  
  &::after {
    content: '';
    display: block;
    width: ${({ level }) => level}%;
    height: 100%;
    background: linear-gradient(90deg, 
      ${({ theme }) => theme.colors.semantic.intent.success}, 
      ${({ theme }) => theme.colors.semantic.intent.warning}, 
      ${({ theme }) => theme.colors.semantic.intent.danger}
    );
    transition: width ${VOICE_RECORDER_CONSTANTS.ANIMATION_DURATION_FAST}ms ${({ theme }) => theme.motion.easing.easeOut};
  }
`;

export const StyledDurationDisplay = styled.div<StyledDurationDisplayProps>`
  font-size: ${({ theme }) => theme.typography.scale.medium * 16}px;
  font-weight: ${({ theme }) => theme.typography.weights.semibold};
  color: ${({ theme }) => theme.colors.semantic.context.text.primary};
  font-family: ${({ theme }) => theme.typography.families.monospace};
`;

export const StyledRecordingIndicator = styled.div<{ isRecording: boolean; theme: any }>`
  width: ${({ theme }) => theme.spatial.base.spacing.sm}px;
  height: ${({ theme }) => theme.spatial.base.spacing.sm}px;
  border-radius: 50%;
  background: ${({ theme, isRecording }) => 
    isRecording ? theme.colors.semantic.intent.danger : 'transparent'};
  animation: ${({ isRecording }) => isRecording ? 'pulse 1s infinite' : 'none'};
  
  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
`;
