/**
 * VoiceInput Component Styles
 * 
 * Styled components for the VoiceInput component.
 * Follows the established design system patterns and theme structure.
 * 
 * @author Augment Agent
 * @version 1.0.0
 */

import styled, { css, keyframes } from 'styled-components';
import { VoiceInputVariant, VoiceInputSize } from './types';

/**
 * Pulse animation for recording state
 */
const pulseAnimation = keyframes`
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
`;

/**
 * Ripple animation for audio level visualization
 */
const rippleAnimation = keyframes`
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.4);
    opacity: 0;
  }
`;

/**
 * Main container for the voice input component
 */
export const VoiceInputContainer = styled.div<{
  $variant: VoiceInputVariant;
  $size: VoiceInputSize;
  $disabled: boolean;
}>`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  position: relative;

  ${({ $disabled }) => $disabled && css`
    opacity: 0.5;
    pointer-events: none;
  `}
`;

/**
 * Size variants for buttons and containers
 */
const sizeVariants = {
  [VoiceInputSize.SMALL]: css`
    width: 32px;
    height: 32px;
    font-size: 14px;
  `,
  [VoiceInputSize.MEDIUM]: css`
    width: 40px;
    height: 40px;
    font-size: 16px;
  `,
  [VoiceInputSize.LARGE]: css`
    width: 48px;
    height: 48px;
    font-size: 18px;
  `,
};

/**
 * Color variants for different button styles
 */
const colorVariants = {
  [VoiceInputVariant.PRIMARY]: css`
    background: ${({ theme }) => theme.color.background.secondary};
    color: ${({ theme }) => theme.color.text.primary};
    border: 2px solid ${({ theme }) => theme.color.border.primary};
    
    &:hover:not(:disabled) {
      background: ${({ theme }) => theme.color.background.hovered};
    }
  `,
  [VoiceInputVariant.SECONDARY]: css`
    background: transparent;
    color: ${({ theme }) => theme.color.text.primary};
    border: 2px solid ${({ theme }) => theme.color.border.secondary};
    
    &:hover:not(:disabled) {
      background: ${({ theme }) => theme.color.background.secondary};
    }
  `,
  [VoiceInputVariant.COMPACT]: css`
    background: ${({ theme }) => theme.color.background.primary};
    color: ${({ theme }) => theme.color.text.primary};
    border: 1px solid ${({ theme }) => theme.color.border.primary};
    
    &:hover:not(:disabled) {
      background: ${({ theme }) => theme.color.background.secondary};
    }
  `,
};

/**
 * Main voice input button
 */
export const VoiceInputButton = styled.button<{
  $variant: VoiceInputVariant;
  $size: VoiceInputSize;
  $isRecording: boolean;
  $hasError: boolean;
}>`
  ${({ $size }) => sizeVariants[$size]}
  ${({ $variant }) => colorVariants[$variant]}
  
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px ${({ theme }) => theme.color.border.secondary}40;
  }
  
  &:disabled {
    cursor: not-allowed;
  }
  
  ${({ $isRecording }) => $isRecording && css`
    animation: ${pulseAnimation} 1.5s ease-in-out infinite;
    background: #ff4444 !important;
    color: white;
  `}

  ${({ $hasError }) => $hasError && css`
    background: #ff6b6b !important;
    color: white;
  `}
`;

/**
 * Audio level visualization container
 */
export const AudioLevelContainer = styled.div<{
  size: VoiceInputSize;
}>`
  position: absolute;
  ${({ size }) => sizeVariants[size]}
  border-radius: 50%;
  pointer-events: none;
  z-index: -1;
`;

/**
 * Audio level ripple effect
 */
export const AudioLevelRipple = styled.div<{
  $level: number;
  $isActive: boolean;
}>`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  border: 2px solid ${({ theme }) => theme.color.border.secondary};
  opacity: 0;
  
  ${({ $isActive, $level }) => $isActive && css`
    animation: ${rippleAnimation} 1s ease-out infinite;
    border-color: ${$level > 70 ? '#ff4444' : $level > 40 ? '#ffaa00' : '#44ff44'};
  `}
`;

/**
 * Recording duration display
 */
export const RecordingDuration = styled.span<{
  variant: VoiceInputVariant;
}>`
  font-family: ${({ theme }) => theme.typography.fontFamily.main};
  font-size: 14px;
  color: ${({ theme }) => theme.color.text.primary};
  font-weight: 500;
  min-width: 40px;
  text-align: center;
  
  ${({ variant }) => variant === VoiceInputVariant.COMPACT && css`
    font-size: 12px;
    min-width: 35px;
  `}
`;

/**
 * Status text display
 */
export const StatusText = styled.span<{
  variant: VoiceInputVariant;
  $isError: boolean;
}>`
  font-family: ${({ theme }) => theme.typography.fontFamily.main};
  font-size: 12px;
  color: ${({ theme, $isError }) =>
    $isError ? '#ff6b6b' : theme.color.text.primary};
  opacity: 0.8;
  
  ${({ variant }) => variant === VoiceInputVariant.COMPACT && css`
    font-size: 11px;
  `}
`;

/**
 * Loading spinner for transcription
 */
export const LoadingSpinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid ${({ theme }) => theme.color.border.primary};
  border-top: 2px solid ${({ theme }) => theme.color.text.primary};
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;
