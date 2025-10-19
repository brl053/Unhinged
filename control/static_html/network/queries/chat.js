/**
 * chatQueries - Query builders for ChatService
 * Generated on: 2025-10-19T09:16:13.397Z
 */
const chatQueries = {
  /**
   * Build createConversation query
   */
  createConversation: {
    method: 'POST',
    path: '/conversations',
    buildUrl: (baseUrl, params = {}) => {
      let path = '/conversations';
      Object.entries(params).forEach(([key, value]) => {
        path = path.replace(`{${key}}`, encodeURIComponent(value));
      });
      return `${baseUrl}${path}`;
    }
  },

  /**
   * Build getConversation query
   */
  getConversation: {
    method: 'GET',
    path: '/conversations/{conversation_id}',
    buildUrl: (baseUrl, params = {}) => {
      let path = '/conversations/{conversation_id}';
      Object.entries(params).forEach(([key, value]) => {
        path = path.replace(`{${key}}`, encodeURIComponent(value));
      });
      return `${baseUrl}${path}`;
    }
  },

  /**
   * Build listConversations query
   */
  listConversations: {
    method: 'GET',
    path: '/conversations',
    buildUrl: (baseUrl, params = {}) => {
      let path = '/conversations';
      Object.entries(params).forEach(([key, value]) => {
        path = path.replace(`{${key}}`, encodeURIComponent(value));
      });
      return `${baseUrl}${path}`;
    }
  },

  /**
   * Build sendMessage query
   */
  sendMessage: {
    method: 'POST',
    path: '/conversations/{conversation_id}/messages',
    buildUrl: (baseUrl, params = {}) => {
      let path = '/conversations/{conversation_id}/messages';
      Object.entries(params).forEach(([key, value]) => {
        path = path.replace(`{${key}}`, encodeURIComponent(value));
      });
      return `${baseUrl}${path}`;
    }
  },

};

// Export for use in HTML pages
if (typeof window !== 'undefined') {
  window.chatQueries = chatQueries;
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = chatQueries;
}
