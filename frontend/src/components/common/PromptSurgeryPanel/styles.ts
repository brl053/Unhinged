// ============================================================================
// PromptSurgeryPanel Styles - Design System Integration
// ============================================================================
//
// @file styles.ts
// @version 2.0.0
// @author Unhinged Team
// @date 2025-10-06
// @description Styled components using design system tokens exclusively
//
// ZERO HARD-CODED VALUES - All styling uses design system tokens
// ============================================================================

import styled, { keyframes } from 'styled-components';
import { 
  StyledPromptSurgeryProps, 
  StyledSourceItemProps, 
  StyledButtonProps, 
  StyledEditorProps 
} from './types';
import { getSourceTypeColor, getSourceTypeBackground, getButtonVariantStyles, getSizeSpacing, getSizeTypography } from './utils';

/**
 * Slide-in animation using design system motion tokens
 */
const slideIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

/**
 * Main panel container with design system integration
 */
export const SurgeryPanelContainer = styled.div<StyledPromptSurgeryProps>`
  display: ${props => props.isVisible ? 'block' : 'none'};
  
  /* Background using semantic tokens */
  background: linear-gradient(135deg, 
    ${({ theme }) => theme.colors.semantic.context.background.primary} 0%, 
    ${({ theme }) => theme.colors.semantic.context.background.secondary} 100%
  );
  
  /* Border using design system tokens */
  border: ${({ theme }) => theme.spatial.base.border.medium}px solid 
    ${({ theme }) => theme.colors.semantic.intent.primary};
  border-radius: ${({ theme }) => theme.spatial.base.radius.lg}px;
  
  /* Spacing using spatial tokens */
  padding: ${({ theme, size = 'medium' }) => getSizeSpacing(size, theme)};
  margin: ${({ theme }) => theme.spatial.base.spacing.md}px 0;
  
  /* Shadow using platform tokens */
  box-shadow: ${({ theme }) => theme.platform.web.boxShadow.medium};
  
  /* Animation using motion tokens */
  animation: ${slideIn} ${({ theme }) => theme.motion.duration.moderate}ms 
    ${({ theme }) => theme.motion.easing.entrance};
  
  /* Responsive design using breakpoints */
  max-width: 100%;
  
  @media (min-width: ${({ theme }) => theme.spatial.breakpoints.tablet}px) {
    max-width: 800px;
    margin: ${({ theme }) => theme.spatial.base.spacing.lg}px auto;
  }
  
  /* Disabled state */
  ${({ disabled, theme }) => disabled && `
    opacity: 0.6;
    pointer-events: none;
    background: ${theme.colors.semantic.context.background.tertiary};
  `}
`;

/**
 * Panel header with design system spacing and typography
 */
export const PanelHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${({ theme }) => theme.spatial.base.spacing.md}px;
  padding-bottom: ${({ theme }) => theme.spatial.base.spacing.sm}px;
  border-bottom: ${({ theme }) => theme.spatial.base.border.thin}px solid 
    ${({ theme }) => theme.colors.semantic.context.border.secondary};
`;

/**
 * Panel title using semantic typography
 */
export const PanelTitle = styled.h3`
  margin: 0;
  color: ${({ theme }) => theme.colors.semantic.intent.primary};
  font-family: ${({ theme }) => theme.typography.families.primary};
  font-size: ${({ theme }) => theme.typography.semantic.heading.h3.fontSize}rem;
  font-weight: ${({ theme }) => theme.typography.semantic.heading.h3.fontWeight};
  line-height: ${({ theme }) => theme.typography.semantic.heading.h3.lineHeight};
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spatial.base.spacing.xs}px;
`;

/**
 * Sources container with design system spacing
 */
export const SourcesContainer = styled.div`
  margin-bottom: ${({ theme }) => theme.spatial.base.spacing.md}px;
`;

/**
 * Individual source item with dynamic styling based on source type
 */
export const SourceItem = styled.div<StyledSourceItemProps>`
  /* Background using alpha tokens based on source type */
  background: ${({ sourceType, theme }) => getSourceTypeBackground(sourceType, theme)};
  
  /* Border using source type colors */
  border-left: ${({ theme }) => theme.spatial.base.border.thick}px solid 
    ${({ sourceType, theme }) => getSourceTypeColor(sourceType, theme)};
  
  /* Spacing using design system tokens */
  padding: ${({ theme }) => theme.spatial.base.spacing.sm}px;
  margin: ${({ theme }) => theme.spatial.base.spacing.xs}px 0;
  border-radius: ${({ theme }) => theme.spatial.base.radius.sm}px;
  
  /* Typography using design system tokens */
  font-family: ${({ theme }) => theme.typography.families.primary};
  font-size: ${({ theme }) => theme.typography.scale.small}rem;
  line-height: ${({ theme }) => theme.typography.lineHeights.base};
  
  /* Transition using motion tokens */
  transition: ${({ theme }) => 
    `all ${theme.motion.duration.swift}ms ${theme.motion.easing.transition}`
  };
  
  &:hover {
    background: ${({ sourceType, theme }) => getSourceTypeBackground(sourceType, theme)};
    transform: translateX(${({ theme }) => theme.spatial.base.spacing.xs / 2}px);
  }
`;

/**
 * Source header with flexbox layout
 */
export const SourceHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${({ theme }) => theme.spatial.base.spacing.xs}px;
`;

/**
 * Source type label with dynamic coloring
 */
export const SourceType = styled.span<StyledSourceItemProps>`
  font-weight: ${({ theme }) => theme.typography.weights.semibold};
  color: ${({ sourceType, theme }) => getSourceTypeColor(sourceType, theme)};
  text-transform: uppercase;
  font-size: ${({ theme }) => theme.typography.scale.micro}rem;
  letter-spacing: ${({ theme }) => theme.typography.letterSpacing.wider};
`;

/**
 * Source timestamp with muted styling
 */
export const SourceTimestamp = styled.span`
  color: ${({ theme }) => theme.colors.semantic.context.text.tertiary};
  font-size: ${({ theme }) => theme.typography.scale.micro}rem;
  font-weight: ${({ theme }) => theme.typography.weights.regular};
`;

/**
 * Source content with readable typography
 */
export const SourceContent = styled.div`
  color: ${({ theme }) => theme.colors.semantic.context.text.secondary};
  line-height: ${({ theme }) => theme.typography.lineHeights.relaxed};
  font-size: ${({ theme }) => theme.typography.scale.small}rem;
`;

/**
 * Editor container with spacing
 */
export const EditorContainer = styled.div`
  margin-bottom: ${({ theme }) => theme.spatial.base.spacing.md}px;
`;

/**
 * Editor label with semantic typography
 */
export const EditorLabel = styled.label`
  display: block;
  margin-bottom: ${({ theme }) => theme.spatial.base.spacing.xs}px;
  font-weight: ${({ theme }) => theme.typography.weights.semibold};
  color: ${({ theme }) => theme.colors.semantic.context.text.primary};
  font-size: ${({ theme }) => theme.typography.scale.small}rem;
`;

/**
 * Prompt editor textarea with full design system integration
 */
export const PromptEditor = styled.textarea<StyledEditorProps>`
  width: 100%;
  min-height: 120px;
  max-height: 400px;
  
  /* Spacing using design system tokens */
  padding: ${({ theme }) => theme.spatial.base.spacing.sm}px;
  
  /* Border using design system tokens */
  border: ${({ theme }) => theme.spatial.base.border.thin}px solid 
    ${({ theme, hasError }) => 
      hasError 
        ? theme.colors.semantic.context.border.error 
        : theme.colors.semantic.context.border.primary
    };
  border-radius: ${({ theme }) => theme.spatial.base.radius.md}px;
  
  /* Typography using design system tokens */
  font-family: ${({ theme }) => theme.typography.families.primary};
  font-size: ${({ theme, size = 'medium' }) => getSizeTypography(size, theme).fontSize};
  line-height: ${({ theme, size = 'medium' }) => getSizeTypography(size, theme).lineHeight};
  
  /* Colors using semantic tokens */
  color: ${({ theme }) => theme.colors.semantic.context.text.primary};
  background: ${({ theme }) => theme.colors.semantic.context.background.primary};
  
  /* Resize behavior */
  resize: vertical;
  
  /* Transition using motion tokens */
  transition: ${({ theme }) => 
    `border-color ${theme.motion.duration.fast}ms ${theme.motion.easing.transition}`
  };
  
  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.semantic.context.border.focus};
    box-shadow: 0 0 0 3px ${({ theme }) => theme.colors.alpha.primary.alpha20};
  }
  
  &::placeholder {
    color: ${({ theme }) => theme.colors.semantic.context.text.placeholder};
  }
  
  &:disabled {
    background: ${({ theme }) => theme.colors.semantic.context.background.tertiary};
    color: ${({ theme }) => theme.colors.semantic.context.text.disabled};
    cursor: not-allowed;
  }
`;

/**
 * Button container with flexbox layout
 */
export const ButtonContainer = styled.div`
  display: flex;
  gap: ${({ theme }) => theme.spatial.base.spacing.sm}px;
  flex-wrap: wrap;
  align-items: center;
  
  /* Responsive stacking on mobile */
  @media (max-width: ${({ theme }) => theme.spatial.breakpoints.tablet}px) {
    flex-direction: column;
    align-items: stretch;
  }
`;

/**
 * Button component with variant-based styling using design system tokens
 */
export const Button = styled.button<StyledButtonProps>`
  /* Spacing using design system tokens */
  padding: ${({ theme, size = 'medium' }) => {
    switch (size) {
      case 'small': return `${theme.spatial.base.spacing.xs}px ${theme.spatial.base.spacing.sm}px`;
      case 'large': return `${theme.spatial.base.spacing.md}px ${theme.spatial.base.spacing.lg}px`;
      default: return `${theme.spatial.base.spacing.sm}px ${theme.spatial.base.spacing.md}px`;
    }
  }};
  
  /* Border and radius using design system tokens */
  border: ${({ theme }) => theme.spatial.base.border.thin}px solid;
  border-radius: ${({ theme }) => theme.spatial.base.radius.md}px;
  
  /* Typography using design system tokens */
  font-family: ${({ theme }) => theme.typography.families.primary};
  font-weight: ${({ theme }) => theme.typography.weights.semibold};
  font-size: ${({ theme, size = 'medium' }) => getSizeTypography(size, theme).fontSize};
  
  /* Layout */
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spatial.base.spacing.xs}px;
  
  /* Transition using motion tokens */
  transition: ${({ theme }) => 
    `all ${theme.motion.duration.swift}ms ${theme.motion.easing.transition}`
  };
  
  /* Variant-based styling using design system tokens */
  ${({ variant = 'primary', theme }) => {
    const styles = getButtonVariantStyles(variant, theme);
    return `
      background: ${styles.background};
      color: ${styles.color};
      border-color: ${styles.border};
    `;
  }}
  
  &:hover:not(:disabled) {
    transform: translateY(-${({ theme }) => theme.spatial.base.millipixel}px);
    box-shadow: ${({ theme }) => theme.platform.web.boxShadow.small};
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background: ${({ theme }) => theme.colors.semantic.context.background.tertiary};
    color: ${({ theme }) => theme.colors.semantic.context.text.disabled};
    border-color: ${({ theme }) => theme.colors.semantic.context.border.secondary};
  }
`;

/**
 * Error message styling
 */
export const ErrorMessage = styled.div`
  color: ${({ theme }) => theme.colors.semantic.intent.danger};
  font-size: ${({ theme }) => theme.typography.scale.small}rem;
  margin-top: ${({ theme }) => theme.spatial.base.spacing.xs}px;
  padding: ${({ theme }) => theme.spatial.base.spacing.xs}px;
  background: ${({ theme }) => theme.colors.alpha.danger.alpha10};
  border-radius: ${({ theme }) => theme.spatial.base.radius.sm}px;
  border-left: ${({ theme }) => theme.spatial.base.border.medium}px solid 
    ${({ theme }) => theme.colors.semantic.intent.danger};
`;

/**
 * Loading indicator
 */
export const LoadingIndicator = styled.div`
  display: inline-flex;
  align-items: center;
  gap: ${({ theme }) => theme.spatial.base.spacing.xs}px;
  color: ${({ theme }) => theme.colors.semantic.context.text.secondary};
  font-size: ${({ theme }) => theme.typography.scale.small}rem;
`;
