// ============================================================================
// Chat Service - Clean Frontend API Client
// ============================================================================
//
// @file ChatService.ts
// @version 2.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Clean API client for chat functionality
// ============================================================================

/**
 * Chat API types
 */
export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: string;
}

export interface ChatSession {
  sessionId: string;
  userId: string;
  title?: string;
  createdAt: string;
  isActive: boolean;
}

export interface ChatRequest {
  prompt: string;
  sessionId?: string;
  userId?: string;
}

export interface ChatResponse {
  response: string;
  sessionId: string;
  messageId: string;
  processingTimeMs: number;
}

export interface ConversationResponse {
  sessionId: string;
  messages: ChatMessage[];
  totalCount: number;
}

/**
 * Chat service for API communication
 */
export class ChatService {
  private baseUrl: string;
  
  constructor(baseUrl: string = 'http://localhost:8080') {
    this.baseUrl = baseUrl;
  }
  
  /**
   * Send a chat message and get response
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: request.prompt,
          sessionId: request.sessionId,
          userId: request.userId || 'default-user'
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }
  
  /**
   * Send message using legacy endpoint (for backward compatibility)
   */
  async sendMessageLegacy(prompt: string): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.text();
    } catch (error) {
      console.error('Error sending legacy message:', error);
      throw error;
    }
  }
  
  /**
   * Create a new chat session
   */
  async createSession(userId: string, title?: string): Promise<ChatSession> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId,
          title,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error creating session:', error);
      throw error;
    }
  }
  
  /**
   * Get user's chat sessions
   */
  async getUserSessions(userId: string): Promise<ChatSession[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/sessions/user/${userId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting user sessions:', error);
      throw error;
    }
  }
  
  /**
   * Get conversation history
   */
  async getConversation(sessionId: string, limit?: number): Promise<ConversationResponse> {
    try {
      const url = new URL(`${this.baseUrl}/api/v1/sessions/${sessionId}/messages`);
      if (limit) {
        url.searchParams.set('limit', limit.toString());
      }
      
      const response = await fetch(url.toString());
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting conversation:', error);
      throw error;
    }
  }
  
  /**
   * Delete a session
   */
  async deleteSession(sessionId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/sessions/${sessionId}`, {
        method: 'DELETE',
      });
      
      return response.ok;
    } catch (error) {
      console.error('Error deleting session:', error);
      return false;
    }
  }
  
  /**
   * Health check
   */
  async healthCheck(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/health`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const chatService = new ChatService();
