// ============================================================================
// PromptSurgeryPanel Hooks
// ============================================================================
//
// @file hooks.ts
// @version 2.0.0
// @author Unhinged Team
// @date 2025-10-06
// @description Custom React hooks for PromptSurgeryPanel component logic
// ============================================================================

import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  PromptSurgeryPanelProps, 
  PromptSource, 
  PromptSurgeryState, 
  UsePromptSurgeryReturn,
  PromptSurgeryEvent 
} from './types';
import { 
  generateSourceId, 
  validatePrompt, 
  validateSources, 
  combineSources,
  createEventData 
} from './utils';
import { EVENT_TYPES, KEYBOARD_SHORTCUTS } from './constants';

/**
 * Main hook for PromptSurgeryPanel logic
 */
export const usePromptSurgery = (props: PromptSurgeryPanelProps): UsePromptSurgeryReturn => {
  const { initialSources = [], onSendPrompt, onCancel, onEvent } = props;
  
  // Component state
  const [state, setState] = useState<PromptSurgeryState>({
    sources: initialSources,
    currentPrompt: combineSources(initialSources),
    isEditing: false,
    hasChanges: false,
    isProcessing: false,
    errors: [],
  });

  // Refs for managing focus and cleanup
  const editorRef = useRef<HTMLTextAreaElement>(null);
  const initialPromptRef = useRef<string>(combineSources(initialSources));

  /**
   * Emit event to parent component
   */
  const emitEvent = useCallback((event: PromptSurgeryEvent) => {
    onEvent?.(event);
  }, [onEvent]);

  /**
   * Add a new source to the panel
   */
  const addSource = useCallback((sourceData: Omit<PromptSource, 'id' | 'timestamp'>) => {
    const newSource: PromptSource = {
      ...sourceData,
      id: generateSourceId(),
      timestamp: new Date().toISOString(),
    };

    setState(prev => {
      const newSources = [...prev.sources, newSource];
      const validation = validateSources(newSources);
      
      if (!validation.isValid) {
        return {
          ...prev,
          errors: validation.errors,
        };
      }

      const updatedPrompt = combineSources(newSources);
      
      return {
        ...prev,
        sources: newSources,
        currentPrompt: updatedPrompt,
        hasChanges: true,
        errors: [],
      };
    });

    emitEvent(createEventData(EVENT_TYPES.SOURCE_ADDED, 'PromptSurgeryPanel', {
      sourceId: newSource.id,
      sourceType: newSource.type,
      content: newSource.content,
    }));
  }, [emitEvent]);

  /**
   * Remove a source from the panel
   */
  const removeSource = useCallback((id: string) => {
    setState(prev => {
      const newSources = prev.sources.filter(source => source.id !== id);
      const updatedPrompt = combineSources(newSources);
      
      return {
        ...prev,
        sources: newSources,
        currentPrompt: updatedPrompt,
        hasChanges: true,
      };
    });

    emitEvent(createEventData(EVENT_TYPES.SOURCE_REMOVED, 'PromptSurgeryPanel', {
      sourceId: id,
    }));
  }, [emitEvent]);

  /**
   * Update the current prompt content
   */
  const updatePrompt = useCallback((content: string) => {
    setState(prev => {
      const validation = validatePrompt(content);
      
      return {
        ...prev,
        currentPrompt: content,
        hasChanges: content !== initialPromptRef.current,
        isEditing: true,
        errors: validation.isValid ? [] : validation.errors,
      };
    });

    emitEvent(createEventData(EVENT_TYPES.PROMPT_UPDATED, 'PromptSurgeryPanel', {
      content,
      length: content.length,
    }));
  }, [emitEvent]);

  /**
   * Enhance prompt using AI (placeholder for future implementation)
   */
  const enhancePrompt = useCallback(async () => {
    setState(prev => ({ ...prev, isProcessing: true }));

    try {
      // TODO: Implement AI enhancement API call
      // For now, just simulate processing
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Placeholder enhancement - add some context
      const enhancedContent = `${state.currentPrompt}\n\n[AI Enhancement: Please provide a detailed and comprehensive response.]`;
      
      setState(prev => ({
        ...prev,
        currentPrompt: enhancedContent,
        hasChanges: true,
        isProcessing: false,
      }));

      emitEvent(createEventData(EVENT_TYPES.PROMPT_ENHANCED, 'PromptSurgeryPanel', {
        originalLength: state.currentPrompt.length,
        enhancedLength: enhancedContent.length,
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isProcessing: false,
        errors: ['Failed to enhance prompt. Please try again.'],
      }));
    }
  }, [state.currentPrompt, emitEvent]);

  /**
   * Send the final prompt
   */
  const sendPrompt = useCallback(() => {
    const validation = validatePrompt(state.currentPrompt);
    
    if (!validation.isValid) {
      setState(prev => ({ ...prev, errors: validation.errors }));
      return;
    }

    onSendPrompt(state.currentPrompt, state.sources);
    
    emitEvent(createEventData(EVENT_TYPES.PROMPT_SENT, 'PromptSurgeryPanel', {
      content: state.currentPrompt,
      sourceCount: state.sources.length,
      promptLength: state.currentPrompt.length,
    }));
  }, [state.currentPrompt, state.sources, onSendPrompt, emitEvent]);

  /**
   * Cancel and close the panel
   */
  const cancel = useCallback(() => {
    onCancel();
    
    emitEvent(createEventData(EVENT_TYPES.PANEL_CANCELLED, 'PromptSurgeryPanel', {
      hasChanges: state.hasChanges,
    }));
  }, [onCancel, state.hasChanges, emitEvent]);

  /**
   * Reset the panel to initial state
   */
  const reset = useCallback(() => {
    const initialPrompt = combineSources(initialSources);
    initialPromptRef.current = initialPrompt;
    
    setState({
      sources: initialSources,
      currentPrompt: initialPrompt,
      isEditing: false,
      hasChanges: false,
      isProcessing: false,
      errors: [],
    });
  }, [initialSources]);

  // Update initial prompt when initialSources change
  useEffect(() => {
    const newInitialPrompt = combineSources(initialSources);
    initialPromptRef.current = newInitialPrompt;
    
    setState(prev => ({
      ...prev,
      sources: initialSources,
      currentPrompt: newInitialPrompt,
      hasChanges: false,
    }));
  }, [initialSources]);

  return {
    state,
    actions: {
      addSource,
      removeSource,
      updatePrompt,
      enhancePrompt,
      sendPrompt,
      cancel,
      reset,
    },
  };
};

/**
 * Hook for keyboard shortcuts
 */
export const useKeyboardShortcuts = (actions: UsePromptSurgeryReturn['actions']) => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Send prompt: Ctrl+Enter
      if (event.ctrlKey && event.key === 'Enter') {
        event.preventDefault();
        actions.sendPrompt();
        return;
      }

      // Cancel: Escape
      if (event.key === 'Escape') {
        event.preventDefault();
        actions.cancel();
        return;
      }

      // Enhance: Ctrl+E
      if (event.ctrlKey && event.key === 'e') {
        event.preventDefault();
        actions.enhancePrompt();
        return;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [actions]);
};

/**
 * Hook for managing editor focus
 */
export const useEditorFocus = (isVisible: boolean) => {
  const editorRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (isVisible && editorRef.current) {
      // Focus the editor when panel becomes visible
      const timer = setTimeout(() => {
        editorRef.current?.focus();
      }, 100); // Small delay to ensure panel is fully rendered

      return () => clearTimeout(timer);
    }
  }, [isVisible]);

  return editorRef;
};

/**
 * Hook for auto-saving draft content (future enhancement)
 */
export const useAutoSave = (content: string, delay: number = 1000) => {
  const [lastSaved, setLastSaved] = useState<string>('');
  
  useEffect(() => {
    if (content === lastSaved) return;
    
    const timer = setTimeout(() => {
      // TODO: Implement auto-save to localStorage or backend
      console.log('Auto-saving draft:', content.substring(0, 50) + '...');
      setLastSaved(content);
    }, delay);

    return () => clearTimeout(timer);
  }, [content, lastSaved, delay]);

  return lastSaved;
};
