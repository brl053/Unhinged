import { useState } from "react";
import { useSendMessage } from "../../queries/api";
import { Layout } from "../../../lib/components/Layout/Layout";
import { ChatContainer, ChatInputContainer, ChatMessagesContainer, LoadingDots, TerminalInput } from "./styles";
import styled from "styled-components";
import { InlineChildren } from "../../../lib/components/InlineChildren/InlineChildren";
import React from "react";
import { InlineChildrenAlignment, InlineChildrenJustification } from "../../../lib/components/InlineChildren/types";
import { VoiceInput } from "../../../lib/components/VoiceInput/VoiceInput";
import { VoiceInputVariant, VoiceInputSize } from "../../../lib/components/VoiceInput/types";
import { TranscriptionResult, VoiceInputErrorDetails } from "../../utils/audio/types";

export const Chatroom: React.FC = () => {
    const [userInput, setUserInput] = useState<string | undefined>();
    const [messageHistroy, setMessageHistory] = useState<ChatMessage[]>([]);
    const { mutate, isPending, isError, data, error } = useSendMessage();

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setUserInput(e.target.value);
    };

    const handleSendMessage = () => {
      if (!userInput) return;
      const newMessage = { type: ChatMessageType.Sent, message: userInput };
      setMessageHistory([...messageHistroy, newMessage])
      mutate(userInput);
      setUserInput(''); // Clear input after sending
    };

    /**
     * Handles voice transcription completion
     * Automatically sends the transcribed text as a message
     */
    const handleVoiceTranscription = (result: TranscriptionResult) => {
      const transcribedText = result.text.trim();
      if (transcribedText) {
        const newMessage = { type: ChatMessageType.Sent, message: transcribedText };
        setMessageHistory([...messageHistroy, newMessage]);
        mutate(transcribedText);
      }
    };

    /**
     * Handles voice input errors
     * Shows error feedback to the user
     */
    const handleVoiceError = (error: VoiceInputErrorDetails) => {
      console.error('Voice input error:', error);
      // TODO: Add toast notification or error display
      // For now, just log the error
    };

    React.useEffect(() => {
      if (!data) return;
      const newMessage = { type: ChatMessageType.Received, message: data };
      setMessageHistory([...messageHistroy, newMessage])
    }, [data])

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
                  value={userInput || ''}
                  onChange={handleInputChange}
                  placeholder="Enter your message or use voice input"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !isPending) {
                      handleSendMessage();
                    }
                  }}
                />
                <VoiceInput
                  onTranscription={handleVoiceTranscription}
                  onError={handleVoiceError}
                  variant={VoiceInputVariant.PRIMARY}
                  size={VoiceInputSize.MEDIUM}
                  showAudioLevel={true}
                  showDuration={true}
                  disabled={isPending}
                  placeholder="Click to record"
                />
                <button onClick={handleSendMessage} disabled={isPending || !userInput}>
                  {isPending ? 'Sending...' : 'Send Message'}
                </button>
              </InlineChildren>
            </ChatInputContainer>

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