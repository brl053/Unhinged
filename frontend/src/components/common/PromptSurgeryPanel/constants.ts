// ============================================================================
// PromptSurgeryPanel Constants
// ============================================================================
//
// @file constants.ts
// @version 2.0.0
// @author Unhinged Team
// @date 2025-10-06
// @description Component-specific constants and configuration
// ============================================================================

import { PromptSourceType, PromptSurgerySize, PromptSurgeryVariant } from './types';

/**
 * Prompt source types
 */
export const PROMPT_SOURCE_TYPES = {
  VOICE: 'voice',
  MANUAL: 'manual',
  ENHANCED: 'enhanced',
  TEMPLATE: 'template',
} as const;

/**
 * Component size variants
 */
export const PROMPT_SURGERY_SIZES = {
  SMALL: 'small',
  MEDIUM: 'medium',
  LARGE: 'large',
} as const;

/**
 * Component visual variants
 */
export const PROMPT_SURGERY_VARIANTS = {
  PRIMARY: 'primary',
  SECONDARY: 'secondary',
  SUCCESS: 'success',
  WARNING: 'warning',
  DANGER: 'danger',
} as const;

/**
 * Default component props
 */
export const DEFAULT_PROPS = {
  size: PROMPT_SURGERY_SIZES.MEDIUM,
  variant: PROMPT_SURGERY_VARIANTS.PRIMARY,
  isVisible: false,
  disabled: false,
  loading: false,
} as const;

/**
 * Source type display labels
 */
export const SOURCE_TYPE_LABELS: Record<PromptSourceType, string> = {
  voice: 'Voice Input',
  manual: 'Manual Entry',
  enhanced: 'AI Enhanced',
  template: 'Template',
};

/**
 * Source type icons (using emoji for now, can be replaced with icon system)
 */
export const SOURCE_TYPE_ICONS: Record<PromptSourceType, string> = {
  voice: '🎤',
  manual: '✏️',
  enhanced: '✨',
  template: '📋',
};

/**
 * Animation durations (will be replaced with design system tokens)
 */
export const ANIMATION_DURATIONS = {
  SLIDE_IN: 300,
  FADE: 200,
  BUTTON_HOVER: 150,
} as const;

/**
 * Component dimensions
 */
export const DIMENSIONS = {
  MIN_EDITOR_HEIGHT: 120,
  MAX_EDITOR_HEIGHT: 400,
  PANEL_MAX_WIDTH: 800,
} as const;

/**
 * Validation rules
 */
export const VALIDATION = {
  MIN_PROMPT_LENGTH: 1,
  MAX_PROMPT_LENGTH: 10000,
  MAX_SOURCES: 10,
} as const;

/**
 * Event types for component communication
 */
export const EVENT_TYPES = {
  SOURCE_ADDED: 'source_added',
  SOURCE_REMOVED: 'source_removed',
  PROMPT_UPDATED: 'prompt_updated',
  PROMPT_ENHANCED: 'prompt_enhanced',
  PROMPT_SENT: 'prompt_sent',
  PANEL_CANCELLED: 'panel_cancelled',
} as const;

/**
 * Keyboard shortcuts
 */
export const KEYBOARD_SHORTCUTS = {
  SEND: 'Ctrl+Enter',
  CANCEL: 'Escape',
  ENHANCE: 'Ctrl+E',
  NEW_SOURCE: 'Ctrl+N',
} as const;

/**
 * Accessibility labels
 */
export const ARIA_LABELS = {
  PANEL: 'Prompt Surgery Panel',
  EDITOR: 'Prompt Editor',
  SOURCE_LIST: 'Prompt Sources',
  SEND_BUTTON: 'Send Prompt',
  CANCEL_BUTTON: 'Cancel',
  ENHANCE_BUTTON: 'Enhance Prompt with AI',
  REMOVE_SOURCE: 'Remove Source',
} as const;
