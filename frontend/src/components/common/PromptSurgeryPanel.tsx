// ============================================================================
// Prompt Surgery Panel - Advanced Prompt Crafting Interface
// ============================================================================
//
// @file PromptSurgeryPanel.tsx
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Advanced prompt editing and enhancement interface
//
// This component provides:
// - Transcription capture and editing
// - Multi-source content stitching
// - Rich text editing capabilities
// - Context enhancement via backend APIs
// - Full control over prompt crafting before submission
// ============================================================================

import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';

// Types and interfaces
interface PromptSource {
  id: string;
  type: 'voice' | 'manual' | 'enhanced' | 'template';
  content: string;
  timestamp: string;
  metadata?: any;
}

interface PromptSurgeryPanelProps {
  isVisible: boolean;
  initialSources?: PromptSource[];
  onSendPrompt: (finalPrompt: string, sources: PromptSource[]) => void;
  onCancel: () => void;
  onEvent?: (event: { type: string; source: string; data: any }) => void;
  disabled?: boolean;
}

// Styled components
const SurgeryPanelContainer = styled.div<{ isVisible: boolean }>`
  display: ${props => props.isVisible ? 'block' : 'none'};
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 2px solid #007bff;
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
  box-shadow: 0 8px 32px rgba(0, 123, 255, 0.15);
  animation: slideIn 0.3s ease-out;
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const PanelHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #dee2e6;
`;

const PanelTitle = styled.h3`
  margin: 0;
  color: #007bff;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SourcesContainer = styled.div`
  margin-bottom: 16px;
`;

const SourceItem = styled.div<{ sourceType: string }>`
  background: ${props => {
    switch (props.sourceType) {
      case 'voice': return 'rgba(40, 167, 69, 0.1)';
      case 'manual': return 'rgba(0, 123, 255, 0.1)';
      case 'enhanced': return 'rgba(255, 193, 7, 0.1)';
      default: return 'rgba(108, 117, 125, 0.1)';
    }
  }};
  border-left: 4px solid ${props => {
    switch (props.sourceType) {
      case 'voice': return '#28a745';
      case 'manual': return '#007bff';
      case 'enhanced': return '#ffc107';
      default: return '#6c757d';
    }
  }};
  padding: 12px;
  margin: 8px 0;
  border-radius: 6px;
  font-size: 14px;
`;

const SourceHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

const SourceType = styled.span<{ sourceType: string }>`
  font-weight: bold;
  color: ${props => {
    switch (props.sourceType) {
      case 'voice': return '#28a745';
      case 'manual': return '#007bff';
      case 'enhanced': return '#856404';
      default: return '#6c757d';
    }
  }};
  text-transform: uppercase;
  font-size: 12px;
`;

const SourceTimestamp = styled.span`
  color: #6c757d;
  font-size: 11px;
`;

const SourceContent = styled.div`
  color: #495057;
  line-height: 1.4;
`;

const EditorContainer = styled.div`
  margin-bottom: 16px;
`;

const EditorLabel = styled.label`
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #495057;
`;

const PromptEditor = styled.textarea`
  width: 100%;
  min-height: 120px;
  padding: 12px;
  border: 2px solid #ced4da;
  border-radius: 8px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  transition: border-color 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  }
  
  &::placeholder {
    color: #6c757d;
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' }>`
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  
  background: ${props => {
    switch (props.variant) {
      case 'primary': return '#007bff';
      case 'success': return '#28a745';
      case 'warning': return '#ffc107';
      case 'danger': return '#dc3545';
      default: return '#6c757d';
    }
  }};
  
  color: ${props => props.variant === 'warning' ? '#212529' : 'white'};
  
  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    opacity: 0.9;
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const WordCount = styled.div`
  text-align: right;
  color: #6c757d;
  font-size: 12px;
  margin-top: 4px;
`;

const PreviewContainer = styled.div`
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 12px;
  margin: 12px 0;
  font-size: 13px;
  color: #495057;
  max-height: 100px;
  overflow-y: auto;
`;

/**
 * Prompt Surgery Panel Component
 */
export const PromptSurgeryPanel: React.FC<PromptSurgeryPanelProps> = ({
  isVisible,
  initialSources = [],
  onSendPrompt,
  onCancel,
  onEvent,
  disabled = false
}) => {
  const [sources, setSources] = useState<PromptSource[]>(initialSources);
  const [promptText, setPromptText] = useState('');
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const editorRef = useRef<HTMLTextAreaElement>(null);

  // Initialize prompt text from sources
  useEffect(() => {
    if (initialSources.length > 0) {
      const combinedText = initialSources
        .map(source => source.content)
        .join('\n\n')
        .trim();
      setPromptText(combinedText);
      setSources(initialSources);
      
      // Log prompt surgery started
      onEvent?.({
        type: 'prompt_surgery_started',
        source: 'prompt-surgery-panel',
        data: {
          sourceCount: initialSources.length,
          initialLength: combinedText.length
        }
      });
    }
  }, [initialSources, onEvent]);

  // Focus editor when panel becomes visible
  useEffect(() => {
    if (isVisible && editorRef.current) {
      setTimeout(() => {
        editorRef.current?.focus();
        editorRef.current?.setSelectionRange(promptText.length, promptText.length);
      }, 100);
    }
  }, [isVisible, promptText.length]);

  const handleAddManualSource = () => {
    const newSource: PromptSource = {
      id: `manual_${Date.now()}`,
      type: 'manual',
      content: '',
      timestamp: new Date().toISOString()
    };
    
    setSources(prev => [...prev, newSource]);
    
    onEvent?.({
      type: 'prompt_source_added',
      source: 'prompt-surgery-panel',
      data: {
        sourceType: 'manual',
        sourceCount: sources.length + 1
      }
    });
  };

  const handleEnhancePrompt = async () => {
    if (!promptText.trim()) return;
    
    setIsEnhancing(true);
    
    onEvent?.({
      type: 'prompt_enhancement_started',
      source: 'prompt-surgery-panel',
      data: {
        originalLength: promptText.length,
        sourceCount: sources.length
      }
    });

    try {
      // Simulate context enhancement (replace with actual backend call)
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const enhancedContent = `Context: This appears to be a user query that could benefit from additional background information.\n\nOriginal: ${promptText}\n\nEnhanced with relevant context and clarifications for better AI understanding.`;
      
      const enhancedSource: PromptSource = {
        id: `enhanced_${Date.now()}`,
        type: 'enhanced',
        content: enhancedContent,
        timestamp: new Date().toISOString(),
        metadata: {
          originalLength: promptText.length,
          enhancedLength: enhancedContent.length
        }
      };
      
      setSources(prev => [...prev, enhancedSource]);
      setPromptText(enhancedContent);
      
      onEvent?.({
        type: 'prompt_enhancement_completed',
        source: 'prompt-surgery-panel',
        data: {
          originalLength: promptText.length,
          enhancedLength: enhancedContent.length,
          processingTimeMs: 1500
        }
      });
      
    } catch (error) {
      onEvent?.({
        type: 'prompt_enhancement_error',
        source: 'prompt-surgery-panel',
        data: {
          error: error instanceof Error ? error.message : 'Enhancement failed'
        }
      });
    } finally {
      setIsEnhancing(false);
    }
  };

  const handleSendPrompt = () => {
    if (!promptText.trim()) return;
    
    onEvent?.({
      type: 'prompt_surgery_completed',
      source: 'prompt-surgery-panel',
      data: {
        finalLength: promptText.length,
        sourceCount: sources.length,
        wordCount: promptText.split(/\s+/).length
      }
    });
    
    onSendPrompt(promptText, sources);
  };

  const handleCancel = () => {
    onEvent?.({
      type: 'prompt_surgery_cancelled',
      source: 'prompt-surgery-panel',
      data: {
        draftLength: promptText.length,
        sourceCount: sources.length
      }
    });
    
    onCancel();
  };

  const formatTimestamp = (timestamp: string): string => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getSourceIcon = (type: string): string => {
    switch (type) {
      case 'voice': return '🎤';
      case 'manual': return '✏️';
      case 'enhanced': return '🔍';
      default: return '📄';
    }
  };

  const wordCount = promptText.split(/\s+/).filter(word => word.length > 0).length;

  return (
    <SurgeryPanelContainer isVisible={isVisible}>
      <PanelHeader>
        <PanelTitle>
          🔧 Prompt Surgery Panel
        </PanelTitle>
        <Button variant="secondary" onClick={handleCancel} disabled={disabled}>
          ✕ Close
        </Button>
      </PanelHeader>

      {sources.length > 0 && (
        <SourcesContainer>
          <h4 style={{ margin: '0 0 12px 0', color: '#495057', fontSize: '14px' }}>
            Content Sources ({sources.length})
          </h4>
          {sources.map(source => (
            <SourceItem key={source.id} sourceType={source.type}>
              <SourceHeader>
                <SourceType sourceType={source.type}>
                  {getSourceIcon(source.type)} {source.type}
                </SourceType>
                <SourceTimestamp>
                  {formatTimestamp(source.timestamp)}
                </SourceTimestamp>
              </SourceHeader>
              <SourceContent>
                {source.content.substring(0, 150)}
                {source.content.length > 150 && '...'}
              </SourceContent>
            </SourceItem>
          ))}
        </SourcesContainer>
      )}

      <EditorContainer>
        <EditorLabel htmlFor="prompt-editor">
          Final Prompt
        </EditorLabel>
        <PromptEditor
          id="prompt-editor"
          ref={editorRef}
          value={promptText}
          onChange={(e) => setPromptText(e.target.value)}
          placeholder="Edit your prompt here... Combine voice transcriptions, add context, and refine before sending."
          disabled={disabled}
        />
        <WordCount>
          {wordCount} words, {promptText.length} characters
        </WordCount>
      </EditorContainer>

      {showPreview && promptText.trim() && (
        <PreviewContainer>
          <strong>Preview:</strong> {promptText.substring(0, 200)}
          {promptText.length > 200 && '...'}
        </PreviewContainer>
      )}

      <ButtonContainer>
        <Button
          variant="warning"
          onClick={handleEnhancePrompt}
          disabled={disabled || isEnhancing || !promptText.trim()}
        >
          {isEnhancing ? '🔄 Enhancing...' : '🔍 Enhance'}
        </Button>
        
        <Button
          variant="secondary"
          onClick={handleAddManualSource}
          disabled={disabled}
        >
          ✏️ Add Manual
        </Button>
        
        <Button
          variant="secondary"
          onClick={() => setShowPreview(!showPreview)}
          disabled={disabled}
        >
          👁️ {showPreview ? 'Hide' : 'Preview'}
        </Button>
        
        <Button
          variant="success"
          onClick={handleSendPrompt}
          disabled={disabled || !promptText.trim()}
        >
          🚀 Send Prompt
        </Button>
      </ButtonContainer>
    </SurgeryPanelContainer>
  );
};

export default PromptSurgeryPanel;
