// ============================================================================
// EventLog Styles - Design Token-Based Styling
// ============================================================================
//
// @file styles.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Styles for event log components using design tokens
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
 * Base event log container styles
 * Foundation styling for the main event log component
 */
export const eventLogContainerStyles = css`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: ${primitiveColors.achromatic.gray900};
  color: ${primitiveColors.achromatic.gray100};
  font-family: ${semanticTypography.code.inline.fontFamily};
  border-radius: ${radius('md')};
  overflow: hidden;
  box-shadow: 0 ${spatial.spacing.sm}px ${spatial.spacing.lg}px ${alphaColors.primary.alpha20};
`;

/**
 * Event log header styles
 * Styling for the header section with controls
 */
export const eventLogHeaderStyles = css`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${spacing('lg')};
  background: ${primitiveColors.achromatic.gray800};
  border-bottom: ${border('thin')} solid ${primitiveColors.achromatic.gray700};
  flex-shrink: 0;
  
  /* Responsive layout */
  @media (max-width: 768px) {
    flex-direction: column;
    gap: ${spacing('md')};
    align-items: stretch;
  }
`;

/**
 * Event log title styles
 * Styling for the main title
 */
export const eventLogTitleStyles = css`
  margin: 0;
  color: ${primitiveColors.achromatic.white};
  font-size: ${fontSize('large')};
  font-weight: ${fontWeights.semibold};
  line-height: ${lineHeights.tight};
  display: flex;
  align-items: center;
  gap: ${spacing('sm')};
`;

/**
 * Event log controls container styles
 * Styling for the controls section
 */
export const eventLogControlsStyles = css`
  display: flex;
  align-items: center;
  gap: ${spacing('md')};
  
  /* Responsive layout */
  @media (max-width: 768px) {
    flex-wrap: wrap;
    justify-content: space-between;
  }
`;

/**
 * Connection status indicator styles
 * Styling for WebSocket connection status
 */
export const connectionStatusStyles = css`
  font-size: ${fontSize('small')};
  font-weight: ${fontWeights.medium};
  display: flex;
  align-items: center;
  gap: ${spacing('xs')};
  
  &[data-status="connected"] {
    color: ${semanticColors.intent.success};
  }
  
  &[data-status="disconnected"] {
    color: ${semanticColors.intent.danger};
  }
  
  &[data-status="connecting"] {
    color: ${semanticColors.intent.warning};
  }
  
  &[data-status="error"] {
    color: ${semanticColors.intent.danger};
  }
`;

/**
 * Filter input styles
 * Styling for the event filter input
 */
export const filterInputStyles = css`
  padding: ${spacing('sm')};
  background: ${primitiveColors.achromatic.gray700};
  border: ${border('thin')} solid ${primitiveColors.achromatic.gray600};
  border-radius: ${radius('sm')};
  color: ${primitiveColors.achromatic.gray100};
  font-size: ${fontSize('small')};
  font-family: ${semanticTypography.code.inline.fontFamily};
  width: 200px;
  transition: border-color 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: ${semanticColors.intent.primary};
    box-shadow: 0 0 0 2px ${alphaColors.primary.alpha30};
  }
  
  &::placeholder {
    color: ${primitiveColors.achromatic.gray500};
  }
  
  /* Responsive width */
  @media (max-width: 768px) {
    width: 100%;
    max-width: 200px;
  }
`;

/**
 * Auto-scroll toggle styles
 * Styling for the auto-scroll checkbox
 */
export const autoScrollToggleStyles = css`
  display: flex;
  align-items: center;
  gap: ${spacing('xs')};
  font-size: ${fontSize('small')};
  cursor: pointer;
  user-select: none;
  
  input[type="checkbox"] {
    accent-color: ${semanticColors.intent.primary};
    width: 16px;
    height: 16px;
  }
  
  &:hover {
    color: ${primitiveColors.achromatic.white};
  }
`;

/**
 * Clear button styles
 * Styling for the clear events button
 */
export const clearButtonStyles = css`
  padding: ${spacing('sm')} ${spacing('md')};
  background: ${semanticColors.intent.danger};
  border: none;
  border-radius: ${radius('sm')};
  color: ${primitiveColors.achromatic.white};
  cursor: pointer;
  font-size: ${fontSize('small')};
  font-weight: ${fontWeights.medium};
  transition: all 0.2s ease;
  
  &:hover:not(:disabled) {
    background: ${semanticColors.intent.danger};
    transform: translateY(-1px);
    box-shadow: 0 ${spatial.spacing.xs}px ${spatial.spacing.sm}px ${alphaColors.danger.alpha30};
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

/**
 * Event count display styles
 * Styling for the event count information
 */
export const eventCountStyles = css`
  padding: ${spacing('sm')} ${spacing('lg')};
  background: ${primitiveColors.achromatic.gray800};
  border-bottom: ${border('thin')} solid ${primitiveColors.achromatic.gray700};
  font-size: ${fontSize('micro')};
  color: ${primitiveColors.achromatic.gray400};
  flex-shrink: 0;
`;

/**
 * Event list container styles
 * Styling for the scrollable event list
 */
export const eventListContainerStyles = css`
  flex: 1;
  overflow-y: auto;
  padding: 0;
  
  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: ${primitiveColors.achromatic.gray800};
  }
  
  &::-webkit-scrollbar-thumb {
    background: ${primitiveColors.achromatic.gray600};
    border-radius: ${radius('sm')};
  }
  
  &::-webkit-scrollbar-thumb:hover {
    background: ${primitiveColors.achromatic.gray500};
  }
`;

/**
 * No events message styles
 * Styling for empty state
 */
export const noEventsStyles = css`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: ${primitiveColors.achromatic.gray500};
  font-style: italic;
  font-size: ${fontSize('medium')};
  text-align: center;
  padding: ${spacing('xl')};
`;

/**
 * Event item styles
 * Styling for individual event entries
 */
export const eventItemStyles = css`
  border-bottom: ${border('thin')} solid ${primitiveColors.achromatic.gray800};
  padding: ${spacing('lg')};
  transition: background-color 0.2s ease;
  
  &:hover {
    background: ${primitiveColors.achromatic.gray800};
  }
  
  &:last-child {
    border-bottom: none;
  }
  
  /* Animation for new events */
  &:first-child {
    animation: slideIn 0.3s ease-out;
  }
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

/**
 * Event header styles
 * Styling for event header information
 */
export const eventHeaderStyles = css`
  display: flex;
  align-items: center;
  gap: ${spacing('md')};
  margin-bottom: ${spacing('sm')};
  
  /* Responsive layout */
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: ${spacing('xs')};
  }
`;

/**
 * Event type badge styles
 * Styling for event type indicators
 */
export const eventTypeStyles = css`
  background: ${semanticColors.intent.primary};
  color: ${primitiveColors.achromatic.white};
  padding: ${spacing('xs')} ${spacing('sm')};
  border-radius: ${radius('sm')};
  font-size: ${fontSize('micro')};
  font-weight: ${fontWeights.bold};
  text-transform: uppercase;
  letter-spacing: 0.5px;
  
  /* Dynamic colors based on event type */
  &[data-event-type*="error"] {
    background: ${semanticColors.intent.danger};
  }
  
  &[data-event-type*="warning"] {
    background: ${semanticColors.intent.warning};
    color: ${primitiveColors.achromatic.gray900};
  }
  
  &[data-event-type*="success"] {
    background: ${semanticColors.intent.success};
  }
  
  &[data-event-type*="llm"] {
    background: ${alphaColors.warning.alpha50};
    color: ${primitiveColors.achromatic.gray900};
  }
  
  &[data-event-type*="audio"] {
    background: ${semanticColors.intent.info};
  }
`;

/**
 * Event timestamp styles
 * Styling for timestamp display
 */
export const eventTimestampStyles = css`
  color: ${primitiveColors.achromatic.gray400};
  font-size: ${fontSize('micro')};
  font-family: ${semanticTypography.code.inline.fontFamily};
  white-space: nowrap;
`;

/**
 * Event ID styles
 * Styling for event ID display
 */
export const eventIdStyles = css`
  color: ${primitiveColors.achromatic.gray500};
  font-size: ${fontSize('micro')};
  font-family: ${semanticTypography.code.inline.fontFamily};
  opacity: 0.7;
`;

/**
 * Event metadata styles
 * Styling for user and session information
 */
export const eventMetadataStyles = css`
  display: flex;
  gap: ${spacing('md')};
  margin-bottom: ${spacing('sm')};
  font-size: ${fontSize('micro')};
  
  span {
    background: ${primitiveColors.achromatic.gray700};
    padding: ${spacing('xs')} ${spacing('sm')};
    border-radius: ${radius('xs')};
    color: ${primitiveColors.achromatic.gray300};
  }
  
  /* Responsive layout */
  @media (max-width: 768px) {
    flex-direction: column;
    gap: ${spacing('xs')};
  }
`;

/**
 * Event payload styles
 * Styling for collapsible payload section
 */
export const eventPayloadStyles = css`
  margin-top: ${spacing('sm')};
  
  details {
    cursor: pointer;
  }
  
  summary {
    color: ${semanticColors.intent.warning};
    font-weight: ${fontWeights.bold};
    padding: ${spacing('xs')} 0;
    user-select: none;
    transition: color 0.2s ease;
    
    &:hover {
      color: ${alphaColors.warning.alpha50};
    }
    
    &:focus {
      outline: 2px solid ${alphaColors.primary.alpha30};
      outline-offset: 2px;
      border-radius: ${radius('xs')};
    }
  }
`;

/**
 * JSON payload styles
 * Styling for JSON code display
 */
export const jsonPayloadStyles = css`
  background: ${primitiveColors.achromatic.black};
  border: ${border('thin')} solid ${primitiveColors.achromatic.gray700};
  border-radius: ${radius('sm')};
  padding: ${spacing('md')};
  margin-top: ${spacing('sm')};
  overflow-x: auto;
  font-size: ${fontSize('micro')};
  line-height: ${lineHeights.relaxed};
  color: ${primitiveColors.achromatic.gray200};
  font-family: ${semanticTypography.code.inline.fontFamily};
  
  /* Syntax highlighting would go here */
  .string { color: ${semanticColors.intent.success}; }
  .number { color: ${semanticColors.intent.info}; }
  .boolean { color: ${semanticColors.intent.warning}; }
  .null { color: ${primitiveColors.achromatic.gray500}; }
  .key { color: ${semanticColors.intent.primary}; }
`;

/**
 * Loading spinner styles
 * Styling for loading states
 */
export const loadingSpinnerStyles = css`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${spacing('xl')};
  color: ${primitiveColors.achromatic.gray400};
  
  &::before {
    content: '';
    width: 20px;
    height: 20px;
    border: 2px solid ${primitiveColors.achromatic.gray600};
    border-radius: 50%;
    border-top-color: ${semanticColors.intent.primary};
    animation: spin 1s linear infinite;
    margin-right: ${spacing('sm')};
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

/**
 * Error message styles
 * Styling for error states
 */
export const errorMessageStyles = css`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${spacing('xl')};
  color: ${semanticColors.intent.danger};
  background: ${alphaColors.danger.alpha10};
  border: ${border('thin')} solid ${alphaColors.danger.alpha30};
  border-radius: ${radius('sm')};
  margin: ${spacing('md')};
  text-align: center;
  
  &::before {
    content: '⚠️';
    margin-right: ${spacing('sm')};
    font-size: ${fontSize('large')};
  }
`;

/**
 * Dark theme overrides
 * Additional styling for dark theme support
 */
export const eventLogDarkThemeStyles = css`
  @media (prefers-color-scheme: dark) {
    /* Already using dark colors by default */
  }
`;
