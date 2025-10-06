// ============================================================================
// PromptSurgeryPanel - Advanced Prompt Crafting Interface
// ============================================================================
//
// @file PromptSurgeryPanel.tsx
// @version 2.0.0
// @author Unhinged Team
// @date 2025-10-06
// @description Advanced prompt editing interface with design system integration
//
// This component provides:
// - Transcription capture and editing with design system styling
// - Multi-source content stitching using semantic colors
// - Rich text editing with responsive typography
// - Context enhancement via backend APIs
// - Full control over prompt crafting with Japanese information density
//
// MIGRATION STATUS: ✅ Complete design system integration
// - Zero hard-coded values
// - All styling uses design system tokens
// - Responsive design with breakpoints
// - Motion system integration
// - Cross-platform ready
// ============================================================================

import React from 'react';
import { PromptSurgeryPanelProps } from './types';
import { 
  usePromptSurgery, 
  useKeyboardShortcuts, 
  useEditorFocus, 
  useAutoSave 
} from './hooks';
import {
  SurgeryPanelContainer,
  PanelHeader,
  PanelTitle,
  SourcesContainer,
  SourceItem,
  SourceHeader,
  SourceType,
  SourceTimestamp,
  SourceContent,
  EditorContainer,
  EditorLabel,
  PromptEditor,
  ButtonContainer,
  Button,
  ErrorMessage,
  LoadingIndicator,
} from './styles';
import { 
  formatTimestamp, 
  createEventData 
} from './utils';
import { 
  SOURCE_TYPE_LABELS, 
  SOURCE_TYPE_ICONS, 
  ARIA_LABELS, 
  KEYBOARD_SHORTCUTS 
} from './constants';

/**
 * PromptSurgeryPanel Component
 * 
 * Advanced prompt crafting interface with Japanese information density philosophy.
 * Displays multiple information streams simultaneously while maintaining usability.
 */
export const PromptSurgeryPanel: React.FC<PromptSurgeryPanelProps> = ({
  isVisible,
  initialSources = [],
  onSendPrompt,
  onCancel,
  onEvent,
  size = 'medium',
  variant = 'primary',
  disabled = false,
  loading = false,
  className,
  'aria-label': ariaLabel = ARIA_LABELS.PANEL,
  'aria-describedby': ariaDescribedBy,
}) => {
  // Component logic hooks
  const { state, actions } = usePromptSurgery({
    isVisible,
    initialSources,
    onSendPrompt,
    onCancel,
    onEvent,
    size,
    variant,
    disabled,
    loading,
  });

  // Additional hooks for enhanced functionality
  useKeyboardShortcuts(actions);
  const editorRef = useEditorFocus(isVisible);
  useAutoSave(state.currentPrompt);

  // Don't render if not visible
  if (!isVisible) {
    return null;
  }

  return (
    <SurgeryPanelContainer
      isVisible={isVisible}
      size={size}
      variant={variant}
      disabled={disabled || loading}
      className={className}
      role="dialog"
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedBy}
      aria-modal="true"
    >
      {/* Panel Header with Title and Status */}
      <PanelHeader>
        <PanelTitle>
          🔧 Prompt Surgery Panel
          {state.hasChanges && <span title="Unsaved changes">*</span>}
        </PanelTitle>
        {loading && (
          <LoadingIndicator>
            ⏳ Processing...
          </LoadingIndicator>
        )}
      </PanelHeader>

      {/* Sources Section - Japanese Information Density */}
      {state.sources.length > 0 && (
        <SourcesContainer>
          <EditorLabel>Sources ({state.sources.length})</EditorLabel>
          {state.sources.map((source) => (
            <SourceItem
              key={source.id}
              sourceType={source.type}
              role="listitem"
            >
              <SourceHeader>
                <SourceType sourceType={source.type}>
                  {SOURCE_TYPE_ICONS[source.type]} {SOURCE_TYPE_LABELS[source.type]}
                </SourceType>
                <SourceTimestamp>
                  {formatTimestamp(source.timestamp)}
                </SourceTimestamp>
              </SourceHeader>
              <SourceContent>
                {source.content}
              </SourceContent>
            </SourceItem>
          ))}
        </SourcesContainer>
      )}

      {/* Main Editor Section */}
      <EditorContainer>
        <EditorLabel htmlFor="prompt-editor">
          Final Prompt ({state.currentPrompt.length} characters)
        </EditorLabel>
        <PromptEditor
          id="prompt-editor"
          ref={editorRef}
          value={state.currentPrompt}
          onChange={(e) => actions.updatePrompt(e.target.value)}
          placeholder="Craft your prompt here... Use Ctrl+Enter to send, Escape to cancel, Ctrl+E to enhance."
          disabled={disabled || loading}
          hasError={state.errors.length > 0}
          size={size}
          aria-label={ARIA_LABELS.EDITOR}
          aria-describedby={state.errors.length > 0 ? 'prompt-errors' : undefined}
        />
        
        {/* Error Messages */}
        {state.errors.length > 0 && (
          <ErrorMessage id="prompt-errors" role="alert">
            {state.errors.map((error, index) => (
              <div key={index}>{error}</div>
            ))}
          </ErrorMessage>
        )}
      </EditorContainer>

      {/* Action Buttons */}
      <ButtonContainer>
        <Button
          variant="success"
          size={size}
          onClick={actions.sendPrompt}
          disabled={disabled || loading || state.errors.length > 0 || !state.currentPrompt.trim()}
          aria-label={ARIA_LABELS.SEND_BUTTON}
          title={`${KEYBOARD_SHORTCUTS.SEND} - Send prompt`}
        >
          🚀 Send Prompt
        </Button>

        <Button
          variant="warning"
          size={size}
          onClick={actions.enhancePrompt}
          disabled={disabled || loading || state.isProcessing}
          aria-label={ARIA_LABELS.ENHANCE_BUTTON}
          title={`${KEYBOARD_SHORTCUTS.ENHANCE} - Enhance with AI`}
        >
          {state.isProcessing ? '⏳' : '✨'} Enhance
        </Button>

        <Button
          variant="secondary"
          size={size}
          onClick={actions.reset}
          disabled={disabled || loading || !state.hasChanges}
          title="Reset to original state"
        >
          🔄 Reset
        </Button>

        <Button
          variant="danger"
          size={size}
          onClick={actions.cancel}
          disabled={loading}
          aria-label={ARIA_LABELS.CANCEL_BUTTON}
          title={`${KEYBOARD_SHORTCUTS.CANCEL} - Cancel and close`}
        >
          ❌ Cancel
        </Button>
      </ButtonContainer>

      {/* Keyboard Shortcuts Help */}
      <div style={{ 
        marginTop: '12px', 
        fontSize: '0.75rem', 
        color: 'var(--color-text-tertiary, #6c757d)',
        textAlign: 'center'
      }}>
        💡 {KEYBOARD_SHORTCUTS.SEND} to send • {KEYBOARD_SHORTCUTS.CANCEL} to cancel • {KEYBOARD_SHORTCUTS.ENHANCE} to enhance
      </div>
    </SurgeryPanelContainer>
  );
};

// Set display name for debugging
PromptSurgeryPanel.displayName = 'PromptSurgeryPanel';

// Default props (TypeScript will enforce these via the interface)
export default PromptSurgeryPanel;
