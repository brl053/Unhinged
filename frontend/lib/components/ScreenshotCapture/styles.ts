/**
 * @fileoverview Screenshot Capture Component Styles
 * @purpose Styled components for screenshot capture and vision analysis integration
 * @editable true - LLM should update styles when adding new capture features
 * @deprecated false
 * 
 * @remarks
 * All styles use the enhanced theme system with proper color/spacing/typography tokens.
 * Includes animations for capture states and integration with ImageUpload styling.
 */

import { styled, keyframes, css } from 'styled-components';

// ============================================================================
// Animation Keyframes
// ============================================================================

const captureAnimation = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

const pulseAnimation = keyframes`
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
`;

// ============================================================================
// Main Container
// ============================================================================

export const ScreenshotContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.lg};
  padding: ${({ theme }) => theme.spacing.xl};
  background: ${({ theme }) => theme.color.background.secondary};
  border: 1px solid ${({ theme }) => theme.color.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.lg};

  h3 {
    color: ${({ theme }) => theme.color.text.primary};
    font-size: ${({ theme }) => theme.typography.fontSize.lg};
    font-weight: ${({ theme }) => theme.typography.fontWeight.semibold};
    margin: 0 0 ${({ theme }) => theme.spacing.sm} 0;
  }

  h4 {
    color: ${({ theme }) => theme.color.text.primary};
    font-size: ${({ theme }) => theme.typography.fontSize.md};
    font-weight: ${({ theme }) => theme.typography.fontWeight.medium};
    margin: ${({ theme }) => theme.spacing.lg} 0 ${({ theme }) => theme.spacing.sm} 0;
  }

  p {
    color: ${({ theme }) => theme.color.text.secondary};
    font-size: ${({ theme }) => theme.typography.fontSize.sm};
    line-height: ${({ theme }) => theme.typography.lineHeight.normal};
    margin: 0 0 ${({ theme }) => theme.spacing.md} 0;
  }
`;

// ============================================================================
// Controls Section
// ============================================================================

export const ScreenshotControls = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${({ theme }) => theme.spacing.md};
  padding: ${({ theme }) => theme.spacing.lg};
  background: ${({ theme }) => theme.color.background.primary};
  border: 1px solid ${({ theme }) => theme.color.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};

  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

export const ControlGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.sm};
  min-width: 150px;

  @media (max-width: 768px) {
    min-width: auto;
  }
`;

export const ControlLabel = styled.label`
  color: ${({ theme }) => theme.color.text.primary};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  font-weight: ${({ theme }) => theme.typography.fontWeight.medium};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

export const Input = styled.input`
  padding: ${({ theme }) => theme.spacing.sm};
  background: ${({ theme }) => theme.color.background.secondary};
  color: ${({ theme }) => theme.color.text.primary};
  border: 1px solid ${({ theme }) => theme.color.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.color.border.focus};
    box-shadow: 0 0 0 2px ${({ theme }) => theme.color.primary.main}20;
  }

  &::placeholder {
    color: ${({ theme }) => theme.color.text.tertiary};
  }
`;

export const Select = styled.select`
  padding: ${({ theme }) => theme.spacing.sm};
  background: ${({ theme }) => theme.color.background.secondary};
  color: ${({ theme }) => theme.color.text.primary};
  border: 1px solid ${({ theme }) => theme.color.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.color.border.focus};
    box-shadow: 0 0 0 2px ${({ theme }) => theme.color.primary.main}20;
  }

  option {
    background: ${({ theme }) => theme.color.background.secondary};
    color: ${({ theme }) => theme.color.text.primary};
  }
`;

export const Button = styled.button<{ $variant?: 'primary' | 'secondary' | 'danger' }>`
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.lg};
  background: ${({ theme, $variant }) => {
    switch ($variant) {
      case 'secondary': return theme.color.background.tertiary;
      case 'danger': return theme.color.error.main;
      default: return theme.color.primary.main;
    }
  }};
  color: ${({ theme, $variant }) => {
    switch ($variant) {
      case 'secondary': return theme.color.text.primary;
      case 'danger': return theme.color.error.contrastText;
      default: return theme.color.primary.contrastText;
    }
  }};
  border: ${({ theme, $variant }) => 
    $variant === 'secondary' ? `1px solid ${theme.color.border.primary}` : 'none'
  };
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  font-weight: ${({ theme }) => theme.typography.fontWeight.medium};
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${({ theme, $variant }) => {
      switch ($variant) {
        case 'secondary': return theme.color.background.hovered;
        case 'danger': return theme.color.error.dark;
        default: return theme.color.primary.dark;
      }
    }};
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    background: ${({ theme }) => theme.color.text.disabled};
    color: ${({ theme }) => theme.color.text.tertiary};
    cursor: not-allowed;
    transform: none;
    ${css`animation: ${pulseAnimation} 2s infinite;`}
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px ${({ theme, $variant }) => {
      switch ($variant) {
        case 'secondary': return theme.color.border.focus;
        case 'danger': return theme.color.error.main;
        default: return theme.color.primary.main;
      }
    }}40;
  }
`;

// ============================================================================
// Status Section
// ============================================================================

export const StatusContainer = styled.div`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};
  padding: ${({ theme }) => theme.spacing.md};
  background: ${({ theme }) => theme.color.background.primary};
  border: 1px solid ${({ theme }) => theme.color.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};
`;

export const StatusIcon = styled.div`
  font-size: 1.5rem;
  animation: ${captureAnimation} 2s ease-in-out infinite;
`;

export const StatusMessage = styled.div<{ $status: 'idle' | 'capturing' | 'success' | 'error' }>`
  color: ${({ theme, $status }) => {
    switch ($status) {
      case 'success': return theme.color.success.main;
      case 'error': return theme.color.error.main;
      case 'capturing': return theme.color.primary.main;
      default: return theme.color.text.primary;
    }
  }};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  font-weight: ${({ theme }) => theme.typography.fontWeight.medium};
  flex: 1;

  ${({ $status }) => $status === 'capturing' && css`
    animation: ${pulseAnimation} 1.5s infinite;
  `}
`;

// ============================================================================
// Preview Section
// ============================================================================

export const PreviewContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.md};
  padding: ${({ theme }) => theme.spacing.lg};
  background: ${({ theme }) => theme.color.background.primary};
  border: 1px solid ${({ theme }) => theme.color.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};
`;

export const PreviewImage = styled.img`
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
  border: 1px solid ${({ theme }) => theme.color.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  background: ${({ theme }) => theme.color.background.secondary};
`;

export const ActionButtons = styled.div`
  display: flex;
  gap: ${({ theme }) => theme.spacing.sm};
  flex-wrap: wrap;

  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

// ============================================================================
// Integration Styles
// ============================================================================

export const IntegrationSection = styled.div`
  margin-top: ${({ theme }) => theme.spacing.xl};
  padding-top: ${({ theme }) => theme.spacing.xl};
  border-top: 1px solid ${({ theme }) => theme.color.border.primary};
`;

export const IntegrationTitle = styled.h4`
  color: ${({ theme }) => theme.color.text.primary};
  font-size: ${({ theme }) => theme.typography.fontSize.md};
  font-weight: ${({ theme }) => theme.typography.fontWeight.semibold};
  margin: 0 0 ${({ theme }) => theme.spacing.sm} 0;
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};

  &::before {
    content: '🔗';
    font-size: 1.2em;
  }
`;

export const IntegrationDescription = styled.p`
  color: ${({ theme }) => theme.color.text.secondary};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  line-height: ${({ theme }) => theme.typography.lineHeight.normal};
  margin: 0 0 ${({ theme }) => theme.spacing.lg} 0;
`;
