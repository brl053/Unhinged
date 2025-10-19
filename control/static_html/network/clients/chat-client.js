/**
 * ChatService - Auto-generated from protobuf gateway annotations
 * Generated on: 2025-10-19T09:16:13.397Z
 */
class ChatServiceClient {
  constructor(baseUrl = 'http://localhost:8080/api/v1/chat') {
    this.baseUrl = baseUrl;
  }

  /**
   * Make HTTP request with error handling
   */
  async _request(method, path, data = null, options = {}) {
    const url = `${this.baseUrl}${path}`;
    const config = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      config.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // Handle different response types
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else if (contentType && contentType.includes('audio/')) {
        return await response.blob();
      } else {
        return await response.text();
      }
    } catch (error) {
      console.error(`${className} request failed:`, error);
      throw error;
    }
  }

  /**
   * createConversation - POST /conversations
   */
  async createConversation(data, options = {}) {
    const path = `/conversations`;
    return await this._request('POST', path, data, options);
  }

  /**
   * getConversation - GET /conversations/{conversation_id}
   */
  async getConversation(conversation_id, options = {}) {
    const path = `/conversations/${conversation_id}`;
    return await this._request('GET', path, null, options);
  }

  /**
   * listConversations - GET /conversations
   */
  async listConversations(options = {}) {
    const path = `/conversations`;
    return await this._request('GET', path, null, options);
  }

  /**
   * sendMessage - POST /conversations/{conversation_id}/messages
   */
  async sendMessage(conversation_id, data, options = {}) {
    const path = `/conversations/${conversation_id}/messages`;
    return await this._request('POST', path, data, options);
  }

}

// Export for use in HTML pages
if (typeof window !== 'undefined') {
  window.ChatServiceClient = ChatServiceClient;
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ChatServiceClient;
}
