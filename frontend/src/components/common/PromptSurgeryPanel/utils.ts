// ============================================================================
// PromptSurgeryPanel Utilities
// ============================================================================
//
// @file utils.ts
// @version 2.0.0
// @author Unhinged Team
// @date 2025-10-06
// @description Component-specific utility functions with design system integration
// ============================================================================

import { UnhingedTheme } from '../../../design_system';
import { PromptSource, PromptSourceType, PromptSurgeryVariant, PromptSurgerySize } from './types';
import { VALIDATION, SOURCE_TYPE_LABELS } from './constants';

/**
 * Generate unique ID for prompt sources
 */
export const generateSourceId = (): string => {
  return `source_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Format timestamp for display
 */
export const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
  
  return date.toLocaleDateString();
};

/**
 * Get source type color using design system tokens
 */
export const getSourceTypeColor = (sourceType: PromptSourceType, theme: UnhingedTheme): string => {
  switch (sourceType) {
    case 'voice':
      return theme.colors.semantic.intent.success;
    case 'manual':
      return theme.colors.semantic.intent.primary;
    case 'enhanced':
      return theme.colors.semantic.intent.warning;
    case 'template':
      return theme.colors.semantic.intent.secondary;
    default:
      return theme.colors.semantic.context.text.tertiary;
  }
};

/**
 * Get source type background color using design system alpha tokens
 */
export const getSourceTypeBackground = (sourceType: PromptSourceType, theme: UnhingedTheme): string => {
  switch (sourceType) {
    case 'voice':
      return theme.colors.alpha.success.alpha10;
    case 'manual':
      return theme.colors.alpha.primary.alpha10;
    case 'enhanced':
      return theme.colors.alpha.warning.alpha10;
    case 'template':
      return theme.colors.semantic.context.background.secondary;
    default:
      return theme.colors.semantic.context.background.tertiary;
  }
};

/**
 * Get button variant styles using design system tokens
 */
export const getButtonVariantStyles = (variant: PromptSurgeryVariant, theme: UnhingedTheme) => {
  switch (variant) {
    case 'primary':
      return {
        background: theme.colors.semantic.intent.primary,
        color: theme.colors.semantic.context.text.inverse,
        border: theme.colors.semantic.intent.primary,
      };
    case 'secondary':
      return {
        background: 'transparent',
        color: theme.colors.semantic.intent.primary,
        border: theme.colors.semantic.intent.primary,
      };
    case 'success':
      return {
        background: theme.colors.semantic.intent.success,
        color: theme.colors.semantic.context.text.inverse,
        border: theme.colors.semantic.intent.success,
      };
    case 'warning':
      return {
        background: theme.colors.semantic.intent.warning,
        color: theme.colors.semantic.context.text.primary,
        border: theme.colors.semantic.intent.warning,
      };
    case 'danger':
      return {
        background: theme.colors.semantic.intent.danger,
        color: theme.colors.semantic.context.text.inverse,
        border: theme.colors.semantic.intent.danger,
      };
    default:
      return {
        background: theme.colors.semantic.context.background.secondary,
        color: theme.colors.semantic.context.text.primary,
        border: theme.colors.semantic.context.border.primary,
      };
  }
};

/**
 * Get size-based spacing using design system tokens
 */
export const getSizeSpacing = (size: PromptSurgerySize, theme: UnhingedTheme): string => {
  switch (size) {
    case 'small':
      return `${theme.spatial.base.spacing.sm}px`;
    case 'large':
      return `${theme.spatial.base.spacing.lg}px`;
    default:
      return `${theme.spatial.base.spacing.md}px`;
  }
};

/**
 * Get size-based typography using design system tokens
 */
export const getSizeTypography = (size: PromptSurgerySize, theme: UnhingedTheme) => {
  switch (size) {
    case 'small':
      return {
        fontSize: `${theme.typography.scale.small}rem`,
        lineHeight: theme.typography.lineHeights.snug,
      };
    case 'large':
      return {
        fontSize: `${theme.typography.scale.medium}rem`,
        lineHeight: theme.typography.lineHeights.relaxed,
      };
    default:
      return {
        fontSize: `${theme.typography.scale.base}rem`,
        lineHeight: theme.typography.lineHeights.base,
      };
  }
};

/**
 * Validate prompt content
 */
export const validatePrompt = (content: string): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  if (!content || content.trim().length < VALIDATION.MIN_PROMPT_LENGTH) {
    errors.push('Prompt cannot be empty');
  }
  
  if (content.length > VALIDATION.MAX_PROMPT_LENGTH) {
    errors.push(`Prompt cannot exceed ${VALIDATION.MAX_PROMPT_LENGTH} characters`);
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Validate sources array
 */
export const validateSources = (sources: PromptSource[]): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  if (sources.length > VALIDATION.MAX_SOURCES) {
    errors.push(`Cannot have more than ${VALIDATION.MAX_SOURCES} sources`);
  }
  
  // Check for duplicate IDs
  const ids = sources.map(s => s.id);
  const uniqueIds = new Set(ids);
  if (ids.length !== uniqueIds.size) {
    errors.push('Duplicate source IDs detected');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Combine sources into a single prompt
 */
export const combineSources = (sources: PromptSource[]): string => {
  return sources
    .map(source => {
      const label = SOURCE_TYPE_LABELS[source.type];
      return `[${label}]: ${source.content}`;
    })
    .join('\n\n');
};

/**
 * Extract text content from various source formats
 */
export const extractTextContent = (content: string, sourceType: PromptSourceType): string => {
  // For now, just return the content as-is
  // In the future, this could handle different formats based on source type
  switch (sourceType) {
    case 'voice':
      // Could handle transcription formatting
      return content.trim();
    case 'enhanced':
      // Could handle AI-enhanced content formatting
      return content.trim();
    case 'template':
      // Could handle template variable substitution
      return content.trim();
    default:
      return content.trim();
  }
};

/**
 * Calculate responsive editor height based on content
 */
export const calculateEditorHeight = (content: string, minHeight: number = 120): number => {
  const lines = content.split('\n').length;
  const estimatedHeight = Math.max(minHeight, lines * 24); // 24px per line estimate
  return Math.min(estimatedHeight, 400); // Max height cap
};

/**
 * Generate event data for component communication
 */
export const createEventData = (
  type: 'source_added' | 'source_removed' | 'prompt_updated' | 'prompt_enhanced' | 'prompt_sent' | 'panel_cancelled',
  source: string,
  additionalData: Record<string, any> = {}
): { type: typeof type; source: string; data: { timestamp: string; [key: string]: any } } => ({
  type,
  source,
  data: {
    timestamp: new Date().toISOString(),
    ...additionalData,
  },
});
