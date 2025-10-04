/**
 * @fileoverview Image Upload Component Styles
 * @purpose Styled components for drag-and-drop image upload with vision processing
 * @editable true - LLM should update styles when adding new upload features or visual states
 * @deprecated false
 * 
 * @remarks
 * All styles use the enhanced theme system with proper color/spacing/typography tokens.
 * Includes animations for drag states, upload progress, and vision analysis feedback.
 * Uses transient props to prevent DOM warnings.
 * 
 * @example
 * ```typescript
 * // Good - uses theme tokens and transient props
 * background: ${({ theme }) => theme.color.background.secondary};
 * border-radius: ${({ theme }) => theme.borderRadius.lg};
 * 
 * // Component usage with transient props
 * <UploadContainer $isDragging={true} $status="uploading" />
 * ```
 */

import { styled, keyframes } from 'styled-components';
import { UploadStatus, UploadSize } from './types';

// ============================================================================
// Animation Keyframes
// ============================================================================

const pulseAnimation = keyframes`
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
`;

const slideInAnimation = keyframes`
  0% { 
    opacity: 0; 
    transform: translateY(10px); 
  }
  100% { 
    opacity: 1; 
    transform: translateY(0); 
  }
`;

const progressAnimation = keyframes`
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
`;

const spinAnimation = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

// ============================================================================
// Helper Functions
// ============================================================================

const getSizeDimensions = (size: UploadSize) => {
  switch (size) {
    case 'small':
      return { width: '300px', height: '200px' };
    case 'medium':
      return { width: '500px', height: '300px' };
    case 'large':
      return { width: '700px', height: '400px' };
    case 'full':
      return { width: '100%', height: '500px' };
    default:
      return { width: '500px', height: '300px' };
  }
};

// ============================================================================
// Main Container
// ============================================================================

interface UploadContainerProps {
  $size: UploadSize;
  $width?: string | number;
  $height?: string | number;
  $isDragging?: boolean;
  $status?: UploadStatus;
  $disabled?: boolean;
}

export const UploadContainer = styled.div<UploadContainerProps>`
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  
  ${({ $size, $width, $height }) => {
    const dimensions = getSizeDimensions($size);
    return `
      width: ${$width ? (typeof $width === 'number' ? `${$width}px` : $width) : dimensions.width};
      height: ${$height ? (typeof $height === 'number' ? `${$height}px` : $height) : dimensions.height};
    `;
  }}
  
  border: 2px dashed ${({ theme, $isDragging, $status }) => {
    if ($status === 'error') return theme.color.error.main;
    if ($status === 'success') return theme.color.success.main;
    if ($isDragging) return theme.color.primary.main;
    return theme.color.border.primary;
  }};
  
  border-radius: ${({ theme }) => theme.borderRadius.lg};
  background: ${({ theme, $isDragging, $disabled }) => {
    if ($disabled) return theme.color.background.secondary;
    if ($isDragging) return `${theme.color.primary.main}10`;
    return theme.color.background.secondary;
  }};
  
  cursor: ${({ $disabled }) => $disabled ? 'not-allowed' : 'pointer'};
  transition: all 0.3s ease;
  
  &:hover {
    ${({ $disabled, theme }) => !$disabled && `
      border-color: ${theme.color.primary.main};
      background: ${theme.color.primary.main}08;
      transform: translateY(-2px);
      box-shadow: ${theme.shadows.md};
    `}
  }
  
  ${({ $status }) => $status === 'uploading' && `
    animation: ${pulseAnimation} 2s infinite;
  `}
  
  ${({ $disabled, theme }) => $disabled && `
    opacity: 0.6;
    color: ${theme.color.text.disabled};
  `}
`;

// ============================================================================
// Upload Area
// ============================================================================

export const UploadArea = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: ${({ theme }) => theme.spacing.xl};
  width: 100%;
  height: 100%;
`;

export const UploadIcon = styled.div<{ $status?: UploadStatus }>`
  font-size: 3rem;
  margin-bottom: ${({ theme }) => theme.spacing.md};
  color: ${({ theme, $status }) => {
    switch ($status) {
      case 'error': return theme.color.error.main;
      case 'success': return theme.color.success.main;
      case 'uploading': 
      case 'processing': return theme.color.primary.main;
      default: return theme.color.text.secondary;
    }
  }};
  
  ${({ $status }) => ($status === 'uploading' || $status === 'processing') && `
    animation: ${spinAnimation} 2s linear infinite;
  `}
`;

export const UploadTitle = styled.h3`
  color: ${({ theme }) => theme.color.text.primary};
  font-size: ${({ theme }) => theme.typography.fontSize.lg};
  font-weight: ${({ theme }) => theme.typography.fontWeight.semibold};
  margin-bottom: ${({ theme }) => theme.spacing.sm};
  margin-top: 0;
`;

export const UploadDescription = styled.p`
  color: ${({ theme }) => theme.color.text.secondary};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  margin: 0 0 ${({ theme }) => theme.spacing.md} 0;
  line-height: ${({ theme }) => theme.typography.lineHeight.normal};
`;

export const UploadButton = styled.button`
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.lg};
  background: ${({ theme }) => theme.color.primary.main};
  color: ${({ theme }) => theme.color.primary.contrastText};
  border: none;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  font-weight: ${({ theme }) => theme.typography.fontWeight.medium};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${({ theme }) => theme.color.primary.dark};
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:disabled {
    background: ${({ theme }) => theme.color.text.disabled};
    cursor: not-allowed;
    transform: none;
  }
`;

// ============================================================================
// Progress Indicator
// ============================================================================

export const ProgressContainer = styled.div<{ $show: boolean }>`
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: ${({ theme }) => theme.color.background.tertiary};
  border-radius: 0 0 ${({ theme }) => theme.borderRadius.lg} ${({ theme }) => theme.borderRadius.lg};
  overflow: hidden;
  opacity: ${({ $show }) => $show ? 1 : 0};
  transition: opacity 0.3s ease;
`;

export const ProgressBar = styled.div<{ $progress: number }>`
  height: 100%;
  background: linear-gradient(90deg, 
    ${({ theme }) => theme.color.primary.main}, 
    ${({ theme }) => theme.color.primary.light}
  );
  width: ${({ $progress }) => $progress}%;
  transition: width 0.3s ease;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, 
      transparent, 
      rgba(255, 255, 255, 0.3), 
      transparent
    );
    animation: ${progressAnimation} 2s infinite;
  }
`;

// ============================================================================
// File List
// ============================================================================

export const FileList = styled.div`
  margin-top: ${({ theme }) => theme.spacing.lg};
  width: 100%;
  max-height: 200px;
  overflow-y: auto;
`;

export const FileItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${({ theme }) => theme.spacing.sm};
  background: ${({ theme }) => theme.color.background.primary};
  border: 1px solid ${({ theme }) => theme.color.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  margin-bottom: ${({ theme }) => theme.spacing.sm};
  animation: ${slideInAnimation} 0.3s ease;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

export const FileInfo = styled.div`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};
  flex: 1;
`;

export const FilePreview = styled.img`
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  border: 1px solid ${({ theme }) => theme.color.border.primary};
`;

export const FileDetails = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.xs};
`;

export const FileName = styled.span`
  color: ${({ theme }) => theme.color.text.primary};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  font-weight: ${({ theme }) => theme.typography.fontWeight.medium};
`;

export const FileSize = styled.span`
  color: ${({ theme }) => theme.color.text.secondary};
  font-size: ${({ theme }) => theme.typography.fontSize.xs};
`;

export const FileActions = styled.div`
  display: flex;
  gap: ${({ theme }) => theme.spacing.xs};
`;

export const ActionButton = styled.button<{ $variant?: 'danger' | 'primary' }>`
  padding: ${({ theme }) => theme.spacing.xs};
  background: ${({ theme, $variant }) => 
    $variant === 'danger' ? theme.color.error.main : theme.color.primary.main};
  color: ${({ theme, $variant }) => 
    $variant === 'danger' ? theme.color.error.contrastText : theme.color.primary.contrastText};
  border: none;
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  font-size: ${({ theme }) => theme.typography.fontSize.xs};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${({ theme, $variant }) => 
      $variant === 'danger' ? theme.color.error.dark : theme.color.primary.dark};
  }
`;

// ============================================================================
// Analysis Results
// ============================================================================

export const AnalysisContainer = styled.div`
  margin-top: ${({ theme }) => theme.spacing.lg};
  padding: ${({ theme }) => theme.spacing.md};
  background: ${({ theme }) => theme.color.background.primary};
  border: 1px solid ${({ theme }) => theme.color.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  animation: ${slideInAnimation} 0.5s ease;
`;

export const AnalysisTitle = styled.h4`
  color: ${({ theme }) => theme.color.text.primary};
  font-size: ${({ theme }) => theme.typography.fontSize.md};
  font-weight: ${({ theme }) => theme.typography.fontWeight.semibold};
  margin: 0 0 ${({ theme }) => theme.spacing.sm} 0;
`;

export const AnalysisContent = styled.div`
  color: ${({ theme }) => theme.color.text.secondary};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  line-height: ${({ theme }) => theme.typography.lineHeight.normal};
`;

// ============================================================================
// Error States
// ============================================================================

export const ErrorContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  color: ${({ theme }) => theme.color.error.main};
`;

export const ErrorIcon = styled.div`
  font-size: 2rem;
  margin-bottom: ${({ theme }) => theme.spacing.sm};
`;

export const ErrorMessage = styled.p`
  margin: 0;
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
`;

// ============================================================================
// Hidden Input
// ============================================================================

export const HiddenInput = styled.input`
  display: none;
`;
