// ============================================================================
// PromptSurgeryPanel Types - Design System Integrated
// ============================================================================
//
// @file types.ts
// @version 2.0.0
// @author Unhinged Team
// @date 2025-10-06
// @description TypeScript interfaces for PromptSurgeryPanel with design system integration
// ============================================================================

import { ReactNode } from 'react';
import { UnhingedTheme } from '../../../design_system';

/**
 * Prompt source types following our semantic naming
 */
export type PromptSourceType = 'voice' | 'manual' | 'enhanced' | 'template';

/**
 * Component size variants using design system scales
 */
export type PromptSurgerySize = 'small' | 'medium' | 'large';

/**
 * Component visual variants using semantic intent colors
 */
export type PromptSurgeryVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'danger';

/**
 * Prompt source data structure
 */
export interface PromptSource {
  id: string;
  type: PromptSourceType;
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

/**
 * Main component props with design system integration
 */
export interface PromptSurgeryPanelProps {
  // Core functionality
  isVisible: boolean;
  initialSources?: PromptSource[];
  onSendPrompt: (finalPrompt: string, sources: PromptSource[]) => void;
  onCancel: () => void;
  onEvent?: (event: { type: string; source: string; data: any }) => void;
  
  // Design system variants
  size?: PromptSurgerySize;
  variant?: PromptSurgeryVariant;
  
  // State props
  disabled?: boolean;
  loading?: boolean;
  
  // Standard React props
  children?: ReactNode;
  className?: string;
  
  // Accessibility
  'aria-label'?: string;
  'aria-describedby'?: string;
}

/**
 * Styled component props with theme integration
 * Only includes props needed for styling, not event handlers
 */
export interface StyledPromptSurgeryProps {
  isVisible: boolean;
  size?: PromptSurgerySize;
  variant?: PromptSurgeryVariant;
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  theme: UnhingedTheme;
}

/**
 * Source item styled component props
 */
export interface StyledSourceItemProps {
  sourceType: PromptSourceType;
  theme: UnhingedTheme;
}

/**
 * Button styled component props
 */
export interface StyledButtonProps {
  variant?: PromptSurgeryVariant;
  size?: PromptSurgerySize;
  disabled?: boolean;
  theme: UnhingedTheme;
}

/**
 * Editor styled component props
 */
export interface StyledEditorProps {
  size?: PromptSurgerySize;
  hasError?: boolean;
  theme: UnhingedTheme;
}

/**
 * Component state interface for hooks
 */
export interface PromptSurgeryState {
  sources: PromptSource[];
  currentPrompt: string;
  isEditing: boolean;
  hasChanges: boolean;
  isProcessing: boolean;
  errors: string[];
}

/**
 * Hook return interface
 */
export interface UsePromptSurgeryReturn {
  state: PromptSurgeryState;
  actions: {
    addSource: (source: Omit<PromptSource, 'id' | 'timestamp'>) => void;
    removeSource: (id: string) => void;
    updatePrompt: (content: string) => void;
    enhancePrompt: () => Promise<void>;
    sendPrompt: () => void;
    cancel: () => void;
    reset: () => void;
  };
}

/**
 * Event types for component communication
 */
export interface PromptSurgeryEvent {
  type: 'source_added' | 'source_removed' | 'prompt_updated' | 'prompt_enhanced' | 'prompt_sent' | 'panel_cancelled';
  source: string;
  data: {
    sourceId?: string;
    content?: string;
    timestamp: string;
    metadata?: Record<string, any>;
  };
}
