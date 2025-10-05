import { useMutation, useQuery } from '@tanstack/react-query';
import { chatService, ChatRequest, ChatResponse, ChatSession, ConversationResponse } from '../services/ChatService';

/**
 * React Query hooks for chat functionality - Clean Architecture
 */

// Legacy hook for backward compatibility
export const useSendMessage = () => {
  return useMutation<string, Error, string>({
    mutationFn: async (message: string) => {
      return await chatService.sendMessageLegacy(message);
    }
  });
};

// Modern chat hooks
export const useChatMutation = () => {
  return useMutation({
    mutationFn: async (request: ChatRequest): Promise<ChatResponse> => {
      return await chatService.sendMessage(request);
    },
  });
};

export const useCreateSessionMutation = () => {
  return useMutation({
    mutationFn: async ({ userId, title }: { userId: string; title?: string }): Promise<ChatSession> => {
      return await chatService.createSession(userId, title);
    },
  });
};

export const useUserSessions = (userId: string) => {
  return useQuery({
    queryKey: ['sessions', userId],
    queryFn: () => chatService.getUserSessions(userId),
    enabled: !!userId,
  });
};

export const useConversation = (sessionId: string, limit?: number) => {
  return useQuery({
    queryKey: ['conversation', sessionId, limit],
    queryFn: () => chatService.getConversation(sessionId, limit),
    enabled: !!sessionId,
  });
};

export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => chatService.healthCheck(),
    refetchInterval: 30000, // Check every 30 seconds
  });
};
