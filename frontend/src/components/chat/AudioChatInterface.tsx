// ============================================================================
// Audio Chat Interface - Complete End-to-End Audio Workflow
// ============================================================================
//
// @file AudioChatInterface.tsx
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Complete chat interface with integrated audio capabilities
//
// This component provides the complete end-to-end audio workflow:
// - Voice input with real-time transcription
// - Text-to-speech for AI responses
// - Voice selection and management
// - Chat history with audio messages
// - Seamless integration with existing chat system
// - Error handling and loading states
// ============================================================================

import React, { useState, useCallback, useRef, useEffect } from 'react';
import styled from 'styled-components';
import VoiceInput from '../audio/VoiceInput/VoiceInput';
import AudioPlayer from '../audio/AudioPlayer/AudioPlayer';
import VoiceSelector from '../audio/VoiceSelector/VoiceSelector';
import { useSynthesizeText, useTranscribeAudio } from '../../services/AudioService';
import { Voice, STTResponse } from '../../proto/audio';
import useAudioRecording from '../../hooks/useAudioRecording';
import useAudioPlayback from '../../hooks/useAudioPlayback';

// ============================================================================
// Types
// ============================================================================

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  audioData?: Uint8Array;
  isAudioMessage?: boolean;
  transcription?: string;
}

export interface AudioChatInterfaceProps {
  messages?: ChatMessage[];
  onSendMessage?: (message: string) => void;
  onSendAudioMessage?: (audioData: Uint8Array, transcription: string) => void;
  isLoading?: boolean;
  className?: string;
}

// ============================================================================
// Styled Components
// ============================================================================

const Container = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  background: ${props => props.theme?.colors?.background || '#ffffff'};
`;

const Header = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
  background: ${props => props.theme?.colors?.surface || '#f8f9fa'};
`;

const Title = styled.h1`
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: ${props => props.theme?.colors?.text || '#212529'};
`;

const AudioToggle = styled.button<{ isActive: boolean }>`
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
  background: ${props => props.isActive 
    ? props.theme?.colors?.primary || '#007bff'
    : props.theme?.colors?.surface || '#f8f9fa'
  };
  color: ${props => props.isActive 
    ? '#ffffff'
    : props.theme?.colors?.text || '#212529'
  };
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  
  &:hover {
    background: ${props => props.isActive 
      ? props.theme?.colors?.primaryDark || '#0056b3'
      : props.theme?.colors?.hover || '#e9ecef'
    };
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const MessageBubble = styled.div<{ isUser: boolean }>`
  max-width: 70%;
  align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  padding: 12px 16px;
  border-radius: 18px;
  background: ${props => props.isUser 
    ? props.theme?.colors?.primary || '#007bff'
    : props.theme?.colors?.surface || '#f8f9fa'
  };
  color: ${props => props.isUser 
    ? '#ffffff'
    : props.theme?.colors?.text || '#212529'
  };
  border: 1px solid ${props => props.isUser 
    ? 'transparent'
    : props.theme?.colors?.border || '#dee2e6'
  };
`;

const MessageContent = styled.div`
  margin-bottom: 8px;
  line-height: 1.4;
`;

const MessageMeta = styled.div`
  font-size: 12px;
  opacity: 0.7;
  display: flex;
  justify-content: between;
  align-items: center;
  gap: 8px;
`;

const AudioMessageIndicator = styled.span`
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  
  &::before {
    content: '🎤';
  }
`;

const InputContainer = styled.div`
  padding: 20px;
  border-top: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
  background: ${props => props.theme?.colors?.surface || '#f8f9fa'};
`;

const TextInputContainer = styled.div`
  display: flex;
  gap: 12px;
  align-items: flex-end;
  margin-bottom: 16px;
`;

const TextInput = styled.textarea`
  flex: 1;
  min-height: 40px;
  max-height: 120px;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
  background: ${props => props.theme?.colors?.background || '#ffffff'};
  color: ${props => props.theme?.colors?.text || '#212529'};
  font-size: 14px;
  resize: none;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme?.colors?.primary || '#007bff'};
    box-shadow: 0 0 0 2px ${props => props.theme?.colors?.primary || '#007bff'}20;
  }
  
  &::placeholder {
    color: ${props => props.theme?.colors?.muted || '#6c757d'};
  }
`;

const SendButton = styled.button`
  padding: 10px 16px;
  border-radius: 6px;
  border: none;
  background: ${props => props.theme?.colors?.primary || '#007bff'};
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
  
  &:hover {
    background: ${props => props.theme?.colors?.primaryDark || '#0056b3'};
  }
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

const VoiceSelectorContainer = styled.div<{ isVisible: boolean }>`
  max-height: ${props => props.isVisible ? '400px' : '0'};
  overflow: hidden;
  transition: max-height 0.3s ease;
  margin-bottom: ${props => props.isVisible ? '16px' : '0'};
`;

const LoadingIndicator = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  color: ${props => props.theme?.colors?.muted || '#6c757d'};
  font-size: 14px;
`;

// ============================================================================
// Audio Chat Interface Component
// ============================================================================

export const AudioChatInterface: React.FC<AudioChatInterfaceProps> = ({
  messages = [],
  onSendMessage,
  onSendAudioMessage,
  isLoading = false,
  className,
}) => {
  // State
  const [textInput, setTextInput] = useState('');
  const [isAudioMode, setIsAudioMode] = useState(false);
  const [showVoiceSelector, setShowVoiceSelector] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState<Voice | null>(null);
  const [currentPlayingMessage, setCurrentPlayingMessage] = useState<string | null>(null);

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Hooks
  const synthesizeText = useSynthesizeText();
  const transcribeAudio = useTranscribeAudio();

  // ============================================================================
  // Message Handling
  // ============================================================================

  const handleSendTextMessage = useCallback(() => {
    if (!textInput.trim() || isLoading) return;

    onSendMessage?.(textInput.trim());
    setTextInput('');
  }, [textInput, isLoading, onSendMessage]);

  const handleVoiceTranscription = useCallback((result: STTResponse) => {
    if (result.transcript) {
      // If in audio mode, send as audio message
      if (isAudioMode) {
        // We would need the original audio data here
        // For now, just send as text with transcription flag
        onSendMessage?.(result.transcript);
      } else {
        // Fill text input with transcription
        setTextInput(result.transcript);
      }
    }
  }, [isAudioMode, onSendMessage]);

  const handleVoiceSelect = useCallback((voice: Voice) => {
    setSelectedVoice(voice);
    setShowVoiceSelector(false);
  }, []);

  // ============================================================================
  // Audio Playback
  // ============================================================================

  const handlePlayMessage = useCallback(async (message: ChatMessage) => {
    if (message.audioData) {
      // Play existing audio
      setCurrentPlayingMessage(message.id);
      // Audio player component will handle playback
    } else if (message.type === 'assistant' && message.content) {
      // Synthesize and play AI response
      try {
        setCurrentPlayingMessage(message.id);
        
        const audioData = await synthesizeText.mutateAsync({
          text: message.content,
          voiceId: selectedVoice?.metadata?.resourceId || 'voice-en-us-female-1',
        });

        // Create temporary audio player
        const audioBlob = new Blob([audioData], { type: 'audio/mpeg' });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        audio.onended = () => {
          setCurrentPlayingMessage(null);
          URL.revokeObjectURL(audioUrl);
        };
        
        audio.onerror = () => {
          setCurrentPlayingMessage(null);
          URL.revokeObjectURL(audioUrl);
        };
        
        await audio.play();
        
      } catch (error) {
        console.error('Failed to synthesize message:', error);
        setCurrentPlayingMessage(null);
      }
    }
  }, [selectedVoice, synthesizeText]);

  // ============================================================================
  // Effects
  // ============================================================================

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    // Auto-play AI responses if audio mode is enabled
    if (isAudioMode && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.type === 'assistant' && !lastMessage.audioData) {
        // Small delay to allow message to render
        setTimeout(() => {
          handlePlayMessage(lastMessage);
        }, 500);
      }
    }
  }, [messages, isAudioMode, handlePlayMessage]);

  // ============================================================================
  // Render Helpers
  // ============================================================================

  const renderMessage = (message: ChatMessage) => {
    const isCurrentlyPlaying = currentPlayingMessage === message.id;

    return (
      <MessageBubble key={message.id} isUser={message.type === 'user'}>
        <MessageContent>{message.content}</MessageContent>
        
        {message.audioData && (
          <AudioPlayer
            audioData={message.audioData}
            showControls={true}
            showWaveform={true}
            onPlay={() => setCurrentPlayingMessage(message.id)}
            onEnded={() => setCurrentPlayingMessage(null)}
          />
        )}
        
        <MessageMeta>
          <span>{message.timestamp.toLocaleTimeString()}</span>
          
          {message.isAudioMessage && <AudioMessageIndicator />}
          
          {message.type === 'assistant' && !message.audioData && (
            <button
              onClick={() => handlePlayMessage(message)}
              disabled={isCurrentlyPlaying || synthesizeText.isPending}
              style={{
                background: 'none',
                border: 'none',
                color: 'inherit',
                cursor: 'pointer',
                fontSize: '12px',
                opacity: 0.7,
              }}
            >
              {isCurrentlyPlaying ? '🔊' : '🔈'}
            </button>
          )}
        </MessageMeta>
      </MessageBubble>
    );
  };

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <Container className={className}>
      <Header>
        <Title>Unhinged Chat</Title>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <AudioToggle
            isActive={isAudioMode}
            onClick={() => setIsAudioMode(!isAudioMode)}
          >
            {isAudioMode ? '🎤 Audio Mode' : '💬 Text Mode'}
          </AudioToggle>
          
          <AudioToggle
            isActive={showVoiceSelector}
            onClick={() => setShowVoiceSelector(!showVoiceSelector)}
          >
            🎭 Voices
          </AudioToggle>
        </div>
      </Header>

      <MessagesContainer>
        {messages.map(renderMessage)}
        
        {isLoading && (
          <LoadingIndicator>
            AI is thinking...
          </LoadingIndicator>
        )}
        
        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputContainer>
        <VoiceSelectorContainer isVisible={showVoiceSelector}>
          <VoiceSelector
            selectedVoiceId={selectedVoice?.metadata?.resourceId}
            onVoiceSelect={handleVoiceSelect}
            showPreview={true}
            showFilters={true}
          />
        </VoiceSelectorContainer>

        {isAudioMode ? (
          <VoiceInput
            onTranscription={handleVoiceTranscription}
            onError={(error) => console.error('Voice input error:', error)}
            maxDuration={60} // 1 minute for chat messages
          />
        ) : (
          <TextInputContainer>
            <TextInput
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendTextMessage();
                }
              }}
              placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
              disabled={isLoading}
            />
            
            <SendButton
              onClick={handleSendTextMessage}
              disabled={!textInput.trim() || isLoading}
            >
              Send
            </SendButton>
          </TextInputContainer>
        )}

        {!isAudioMode && (
          <VoiceInput
            onTranscription={handleVoiceTranscription}
            onError={(error) => console.error('Voice input error:', error)}
            maxDuration={60}
            disabled={isLoading}
          />
        )}
      </InputContainer>
    </Container>
  );
};

export default AudioChatInterface;
