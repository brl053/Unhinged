import { useState } from "react";
import { useSendMessage } from "../../queries/api";
import { Layout } from "../../../lib/components/Layout/Layout";
import { ChatContainer, ChatInputContainer, ChatMessagesContainer, LoadingDots, TerminalInput } from "./styles";
import styled from "styled-components";
import { InlineChildren } from "../../../lib/components/InlineChildren/InlineChildren";
import React from "react";
import { InlineChildrenAlignment, InlineChildrenJustification } from "../../../lib/components/InlineChildren/types";
import { VoiceRecorder } from "../../components/common/VoiceRecorder";
import { EventFeed, useEventFeed } from "../../components/common/EventFeed";
import { PromptSurgeryPanel } from "../../components/common/PromptSurgeryPanel";
import { frontendEventService } from "../../services/EventService";

export const Chatroom: React.FC = () => {
    const [userInput, setUserInput] = useState<string | undefined>();
    const [messageHistroy, setMessageHistory] = useState<ChatMessage[]>([]);
    const { mutate, isPending, isError, data, error } = useSendMessage();
    const { events, addEvent, clearEvents } = useEventFeed();

    // Prompt Surgery Panel state
    const [showSurgeryPanel, setShowSurgeryPanel] = useState(false);
    const [surgeryPanelSources, setSurgeryPanelSources] = useState<any[]>([]);
    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setUserInput(e.target.value);
    };
    const handleSendMessage = async () => {
      if (!userInput) return;
      const newMessage = { type: ChatMessageType.Sent, message: userInput };
      setMessageHistory([...messageHistroy, newMessage])

      // Add event to live feed
      addEvent({
        type: 'chat_message_sent',
        source: 'react-frontend',
        data: {
          messageContent: userInput.substring(0, 50),
          messageRole: 'user',
          messageSource: 'text'
        }
      });

      // Log chat message sent from text
      await frontendEventService.logChatMessageSent(userInput, 'text');

      mutate(userInput);
    };

    React.useEffect(() => {
      if (!data) return;
      const newMessage = { type: ChatMessageType.Received, message: data };
      setMessageHistory([...messageHistroy, newMessage])

      // Add event to live feed
      addEvent({
        type: 'chat_message_received',
        source: 'react-frontend',
        data: {
          messageContent: data.substring(0, 50),
          messageRole: 'assistant'
        }
      });

      // Log chat message received
      frontendEventService.logChatMessageReceived(data).catch(console.error);
    }, [data])

    // Handle voice transcription - route to Prompt Surgery Panel instead of direct chat
    const handleVoiceTranscription = async (text: string) => {
      // Create voice transcription source
      const voiceSource = {
        id: `voice_${Date.now()}`,
        type: 'voice' as const,
        content: text,
        timestamp: new Date().toISOString(),
        metadata: {
          audioProcessed: true,
          transcriptionLength: text.length
        }
      };

      // Add event to live feed
      addEvent({
        type: 'voice_transcription_captured',
        source: 'voice-recorder',
        data: {
          transcriptionText: text.substring(0, 50),
          routedToSurgery: true
        }
      });

      // Route to Prompt Surgery Panel instead of direct chat
      setSurgeryPanelSources([voiceSource]);
      setShowSurgeryPanel(true);

      // Log transcription captured for surgery
      await frontendEventService.logFeatureUsed('voice_transcription_surgery');
    };

    // Handle voice recording errors
    const handleVoiceError = async (error: string) => {
      console.error('Voice recording error:', error);

      // Add error event to live feed
      addEvent({
        type: 'voice_recording_error',
        source: 'voice-recorder',
        data: {
          error: error
        }
      });

      // Log error event
      await frontendEventService.logError('voice_recording_ui_error', error, undefined, {
        component: 'Chatroom',
        action: 'voice_recording'
      });

      // Could add error message to chat or show toast notification
    };

    // Handle prompt surgery panel send
    const handleSurgeryPanelSend = async (finalPrompt: string, sources: any[]) => {
      const newMessage = { type: ChatMessageType.Sent, message: finalPrompt };
      setMessageHistory([...messageHistroy, newMessage]);

      // Add event to live feed
      addEvent({
        type: 'prompt_surgery_sent',
        source: 'prompt-surgery-panel',
        data: {
          finalPromptLength: finalPrompt.length,
          sourceCount: sources.length,
          messageSource: 'surgery'
        }
      });

      // Log crafted prompt sent (use 'text' as closest match)
      await frontendEventService.logChatMessageSent(finalPrompt, 'text');

      // Send to chat
      mutate(finalPrompt);

      // Close surgery panel
      setShowSurgeryPanel(false);
      setSurgeryPanelSources([]);
    };

    // Handle prompt surgery panel cancel
    const handleSurgeryPanelCancel = () => {
      addEvent({
        type: 'prompt_surgery_cancelled',
        source: 'prompt-surgery-panel',
        data: {
          sourceCount: surgeryPanelSources.length
        }
      });

      setShowSurgeryPanel(false);
      setSurgeryPanelSources([]);
    };

    // Handle manual prompt surgery
    const handleManualSurgery = () => {
      const manualSource = {
        id: `manual_${Date.now()}`,
        type: 'manual' as const,
        content: userInput || '',
        timestamp: new Date().toISOString(),
        metadata: {
          manuallyTriggered: true
        }
      };

      setSurgeryPanelSources(userInput ? [manualSource] : []);
      setShowSurgeryPanel(true);
      setUserInput(''); // Clear input since it's now in surgery panel

      addEvent({
        type: 'prompt_surgery_manual_trigger',
        source: 'chat-interface',
        data: {
          hasInitialContent: !!userInput
        }
      });
    };

    console.log(messageHistroy)

    return (
        <Layout title="Ero-Ero Chatroom ~.~">
          <ChatContainer>
            <ChatMessagesContainer>
              {messageHistroy.map((message, index) => <ChatBubble key={index} {...message} />)}
              {isPending &&  <LoadingDots><div></div><div></div><div></div></LoadingDots>}
            </ChatMessagesContainer>
            <ChatInputContainer>
              <InlineChildren>
            <TerminalInput
              type="text"
              value={userInput}
              onChange={handleInputChange}
              placeholder="Enter your message or use voice recording"
            />
            <button onClick={handleSendMessage} disabled={isPending}>
              {isPending ? 'Sending...' : 'Send'}
            </button>
            <button
              onClick={handleManualSurgery}
              disabled={isPending}
              style={{
                background: '#ffc107',
                color: '#212529',
                border: 'none',
                padding: '8px 12px',
                borderRadius: '4px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              🔧 Surgery
            </button>
            <VoiceRecorder
              onTranscription={handleVoiceTranscription}
              onError={handleVoiceError}
              onEvent={addEvent}
              disabled={isPending}
            />
            </InlineChildren>
            </ChatInputContainer>

          {/* Prompt Surgery Panel */}
          <PromptSurgeryPanel
            isVisible={showSurgeryPanel}
            initialSources={surgeryPanelSources}
            onSendPrompt={handleSurgeryPanelSend}
            onCancel={handleSurgeryPanelCancel}
            onEvent={addEvent}
            disabled={isPending}
          />

          {/* Live Event Feed */}
          <EventFeed
            events={events}
            maxEvents={15}
            showTimestamps={true}
            collapsible={true}
          />

          {isError && <p style={{ color: 'red' }}>Error: {error instanceof Error ? error.message : 'Unknown error'}</p>}
          </ChatContainer>
      </Layout>
    );
}

export enum ChatMessageType {
  Sent = 'sent',
  Received = 'received',
}

type ChatMessage = {
  type: ChatMessageType;
  message: string;
}

export const ChatBubbleContainer = styled.div<ChatMessage>`
  background: ${({ theme }) => theme.color.background.secondary};
  padding: 1em;
  border-radius: 10px;
  margin-bottom: 1em;
  max-width: 80%;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;
  align-self: flex-end;
`

const ChatBubble: React.FC<ChatMessage> = ({ type, message }) => {
  const justification = type === ChatMessageType.Sent ? InlineChildrenJustification.End : InlineChildrenJustification.Start;
  return (
    <InlineChildren justification={justification} alignment={InlineChildrenAlignment.Center}>
    <ChatBubbleContainer type={type} message={message}>
      {message}
    </ChatBubbleContainer>
    </InlineChildren>
  );
}