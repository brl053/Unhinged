// ============================================================================
// ErrorBoundary Styles - Design Token-Based Styling
// ============================================================================
//
// @file styles.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Styles for error boundary components using design tokens
//
// Etymology: Latin "stylus" = writing instrument, manner of expression
// Methodology: Design token-based styling with semantic naming
// ============================================================================

import { css } from 'styled-components';
import { 
  semanticColors, 
  alphaColors, 
  primitiveColors 
} from '../../../design_system/tokens/colors';
import { 
  spatial, 
  spacing, 
  radius, 
  border 
} from '../../../design_system/tokens/spatial';
import {
  semanticTypography,
  fontSize,
  fontWeights,
  lineHeights
} from '../../../design_system/tokens/typography';

/**
 * Base error container styles
 * Foundation styling for all error boundary containers
 */
export const errorContainerStyles = css`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${spacing('xl')} ${spacing('lg')};
  text-align: center;
  background: ${semanticColors.context.background.primary};
  border: ${border('thin')} solid ${alphaColors.danger.alpha20};
  border-radius: ${radius('md')};
  margin: ${spacing('lg')} 0;
  min-height: ${spatial.hectopixel * 2}px; /* 200px */
  max-width: 600px;
  width: 100%;
  box-shadow: 0 ${spatial.spacing.xs}px ${spatial.spacing.lg}px ${alphaColors.primary.alpha10};
  
  /* Responsive adjustments */
  @media (max-width: 768px) {
    padding: ${spacing('lg')} ${spacing('md')};
    margin: ${spacing('md')} 0;
    border-radius: ${radius('sm')};
  }
`;

/**
 * Error icon styles
 * Styling for error state icons and visual indicators
 */
export const errorIconStyles = css`
  font-size: ${fontSize('xxxlarge')};
  margin-bottom: ${spacing('md')};
  opacity: 0.7;
  line-height: 1;
  user-select: none;
  
  /* Animation for attention */
  animation: errorPulse 2s ease-in-out infinite;
  
  @keyframes errorPulse {
    0%, 100% { opacity: 0.7; }
    50% { opacity: 0.9; }
  }
`;

/**
 * Error title styles
 * Styling for error headings and titles
 */
export const errorTitleStyles = css`
  margin: 0 0 ${spacing('sm')} 0;
  color: ${semanticColors.intent.danger};
  font-size: ${fontSize('xlarge')};
  font-weight: ${fontWeights.semibold};
  line-height: ${lineHeights.tight};
  letter-spacing: -0.025em;

  /* Responsive typography */
  @media (max-width: 768px) {
    font-size: ${fontSize('large')};
  }
`;

/**
 * Error message styles
 * Styling for user-friendly error messages
 */
export const errorMessageStyles = css`
  margin: 0 0 ${spacing('lg')} 0;
  color: ${semanticColors.context.text.primary};
  font-size: ${fontSize('medium')};
  font-weight: ${fontWeights.regular};
  line-height: ${lineHeights.relaxed};
  max-width: 500px;

  /* Responsive typography */
  @media (max-width: 768px) {
    font-size: ${fontSize('small')};
    margin-bottom: ${spacing('md')};
  }
`;

/**
 * Error details styles
 * Styling for collapsible technical error details
 */
export const errorDetailsStyles = css`
  margin: ${spacing('md')} 0;
  padding: ${spacing('md')};
  background: ${semanticColors.context.background.secondary};
  border: ${border('thin')} solid ${semanticColors.context.border.primary};
  border-radius: ${radius('sm')};
  font-family: ${semanticTypography.code.inline.fontFamily};
  font-size: ${fontSize('micro')};
  text-align: left;
  max-width: 600px;
  width: 100%;

  summary {
    cursor: pointer;
    font-weight: ${fontWeights.medium};
    margin-bottom: ${spacing('xs')};
    color: ${semanticColors.context.text.secondary};
    padding: ${spacing('xs')};
    border-radius: ${radius('xs')};
    transition: background-color 0.2s ease;

    &:hover {
      background: ${alphaColors.primary.alpha10};
    }

    &:focus {
      outline: 2px solid ${alphaColors.primary.alpha30};
      outline-offset: 2px;
    }
  }

  pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
    color: ${semanticColors.context.text.primary};
    line-height: ${lineHeights.relaxed};
    overflow-x: auto;
    max-height: 300px;
    overflow-y: auto;
    padding: ${spacing('xs')};
    background: ${primitiveColors.achromatic.white};
    border-radius: ${radius('xs')};
    border: ${border('hairline')} solid ${semanticColors.context.border.secondary};
  }

  /* Responsive adjustments */
  @media (max-width: 768px) {
    font-size: ${fontSize('micro')};
    padding: ${spacing('sm')};

    pre {
      max-height: 200px;
    }
  }
`;

/**
 * Error actions container styles
 * Styling for error action buttons container
 */
export const errorActionsStyles = css`
  display: flex;
  gap: ${spacing('sm')};
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  margin-top: ${spacing('md')};
  
  /* Responsive stacking */
  @media (max-width: 480px) {
    flex-direction: column;
    width: 100%;
    
    > * {
      width: 100%;
      max-width: 280px;
    }
  }
`;

/**
 * Error button base styles
 * Foundation styling for error action buttons
 */
export const errorButtonBaseStyles = css`
  padding: ${spacing('sm')} ${spacing('lg')};
  border-radius: ${radius('md')};
  border: ${border('thin')} solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: ${fontSize('small')};
  font-weight: ${fontWeights.medium};
  line-height: ${lineHeights.tight};
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: ${spacing('xs')};
  min-width: 120px;
  
  &:focus {
    outline: 2px solid ${alphaColors.primary.alpha50};
    outline-offset: 2px;
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
  }
  
  /* Loading state */
  &[data-loading="true"] {
    position: relative;
    color: transparent;
    
    &::after {
      content: '';
      position: absolute;
      width: 16px;
      height: 16px;
      border: 2px solid currentColor;
      border-radius: 50%;
      border-top-color: transparent;
      animation: buttonSpin 1s linear infinite;
    }
  }
  
  @keyframes buttonSpin {
    to { transform: rotate(360deg); }
  }
`;

/**
 * Primary error button styles
 * Styling for primary action buttons (retry, etc.)
 */
export const errorButtonPrimaryStyles = css`
  ${errorButtonBaseStyles}
  
  background: ${semanticColors.intent.primary};
  color: ${primitiveColors.achromatic.white};
  border-color: ${semanticColors.intent.primary};
  
  &:hover:not(:disabled) {
    background: ${semanticColors.intent.primary};
    transform: translateY(-1px);
    box-shadow: 0 ${spatial.spacing.xs}px ${spatial.spacing.md}px ${alphaColors.primary.alpha30};
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
    box-shadow: 0 ${spatial.spacing.xs}px ${spatial.spacing.sm}px ${alphaColors.primary.alpha20};
  }
`;

/**
 * Secondary error button styles
 * Styling for secondary action buttons (reload, report, etc.)
 */
export const errorButtonSecondaryStyles = css`
  ${errorButtonBaseStyles}
  
  background: ${semanticColors.context.background.primary};
  color: ${semanticColors.context.text.primary};
  border-color: ${semanticColors.context.border.primary};
  
  &:hover:not(:disabled) {
    background: ${semanticColors.context.background.secondary};
    border-color: ${semanticColors.context.border.secondary};
    transform: translateY(-1px);
    box-shadow: 0 ${spatial.spacing.xs}px ${spatial.spacing.md}px ${alphaColors.primary.alpha10};
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
    background: ${semanticColors.context.background.tertiary};
  }
`;

/**
 * Danger error button styles
 * Styling for destructive action buttons
 */
export const errorButtonDangerStyles = css`
  ${errorButtonBaseStyles}
  
  background: ${semanticColors.intent.danger};
  color: ${primitiveColors.achromatic.white};
  border-color: ${semanticColors.intent.danger};
  
  &:hover:not(:disabled) {
    background: ${semanticColors.intent.danger};
    transform: translateY(-1px);
    box-shadow: 0 ${spatial.spacing.xs}px ${spatial.spacing.md}px ${alphaColors.danger.alpha30};
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
    box-shadow: 0 ${spatial.spacing.xs}px ${spatial.spacing.sm}px ${alphaColors.danger.alpha20};
  }
`;

/**
 * Error fallback container styles
 * Styling for specialized error fallback components
 */
export const errorFallbackStyles = css`
  ${errorContainerStyles}
  
  /* Specialized styling for fallback components */
  background: ${alphaColors.warning.alpha10};
  border-color: ${alphaColors.warning.alpha30};
  
  /* Audio-specific styling */
  &[data-error-category="audio"] {
    background: ${alphaColors.warning.alpha10};
    border-color: ${semanticColors.intent.warning};
    
    ${errorIconStyles} {
      color: ${semanticColors.intent.warning};
    }
  }
  
  /* Network-specific styling */
  &[data-error-category="network"] {
    background: ${alphaColors.danger.alpha10};
    border-color: ${semanticColors.intent.danger};
    
    ${errorIconStyles} {
      color: ${semanticColors.intent.danger};
    }
  }
  
  /* Permission-specific styling */
  &[data-error-category="permission"] {
    background: ${alphaColors.warning.alpha10};
    border-color: ${semanticColors.intent.warning};
    
    ${errorIconStyles} {
      color: ${semanticColors.intent.warning};
    }
  }
`;

/**
 * Error boundary loading styles
 * Styling for loading states during error recovery
 */
export const errorLoadingStyles = css`
  display: inline-flex;
  align-items: center;
  gap: ${spacing('xs')};
  color: ${semanticColors.context.text.secondary};
  font-size: ${fontSize('small')};

  &::before {
    content: '';
    width: 16px;
    height: 16px;
    border: 2px solid ${semanticColors.context.border.primary};
    border-radius: 50%;
    border-top-color: ${semanticColors.intent.primary};
    animation: loadingSpin 1s linear infinite;
  }
  
  @keyframes loadingSpin {
    to { transform: rotate(360deg); }
  }
`;

/**
 * Error severity indicator styles
 * Visual indicators for different error severity levels
 */
export const errorSeverityStyles = {
  low: css`
    border-left: 4px solid ${semanticColors.intent.info};
    background: ${alphaColors.primary.alpha10};
  `,
  
  medium: css`
    border-left: 4px solid ${semanticColors.intent.warning};
    background: ${alphaColors.warning.alpha10};
  `,
  
  high: css`
    border-left: 4px solid ${semanticColors.intent.danger};
    background: ${alphaColors.danger.alpha10};
  `,
  
  critical: css`
    border-left: 4px solid ${semanticColors.intent.danger};
    background: ${alphaColors.danger.alpha20};
    border-color: ${semanticColors.intent.danger};
    
    ${errorTitleStyles} {
      color: ${semanticColors.intent.danger};
      font-weight: ${fontWeights.bold};
    }
    
    ${errorIconStyles} {
      animation: criticalPulse 1s ease-in-out infinite;
    }
    
    @keyframes criticalPulse {
      0%, 100% { opacity: 0.8; transform: scale(1); }
      50% { opacity: 1; transform: scale(1.05); }
    }
  `,
};

/**
 * Dark theme overrides
 * Styling adjustments for dark theme support
 */
export const errorDarkThemeStyles = css`
  @media (prefers-color-scheme: dark) {
    ${errorContainerStyles} {
      background: ${primitiveColors.achromatic.gray800};
      border-color: ${primitiveColors.achromatic.gray600};
      color: ${primitiveColors.achromatic.gray100};
    }
    
    ${errorDetailsStyles} {
      background: ${primitiveColors.achromatic.gray900};
      border-color: ${primitiveColors.achromatic.gray700};
      
      pre {
        background: ${primitiveColors.achromatic.black};
        border-color: ${primitiveColors.achromatic.gray700};
        color: ${primitiveColors.achromatic.gray200};
      }
    }
    
    ${errorButtonSecondaryStyles} {
      background: ${primitiveColors.achromatic.gray700};
      color: ${primitiveColors.achromatic.gray100};
      border-color: ${primitiveColors.achromatic.gray600};
      
      &:hover:not(:disabled) {
        background: ${primitiveColors.achromatic.gray600};
      }
    }
  }
`;
