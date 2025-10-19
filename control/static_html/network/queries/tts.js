/**
 * ttsQueries - Query builders for TTSService
 * Generated on: 2025-10-19T09:16:13.398Z
 */
const ttsQueries = {
  /**
   * Build synthesize query
   */
  synthesize: {
    method: 'POST',
    path: '/synthesize',
    buildUrl: (baseUrl, params = {}) => {
      let path = '/synthesize';
      Object.entries(params).forEach(([key, value]) => {
        path = path.replace(`{${key}}`, encodeURIComponent(value));
      });
      return `${baseUrl}${path}`;
    }
  },

  /**
   * Build getHealth query
   */
  getHealth: {
    method: 'GET',
    path: '/health',
    buildUrl: (baseUrl, params = {}) => {
      let path = '/health';
      Object.entries(params).forEach(([key, value]) => {
        path = path.replace(`{${key}}`, encodeURIComponent(value));
      });
      return `${baseUrl}${path}`;
    }
  },

  /**
   * Build getSpeakers query
   */
  getSpeakers: {
    method: 'GET',
    path: '/speakers',
    buildUrl: (baseUrl, params = {}) => {
      let path = '/speakers';
      Object.entries(params).forEach(([key, value]) => {
        path = path.replace(`{${key}}`, encodeURIComponent(value));
      });
      return `${baseUrl}${path}`;
    }
  },

};

// Export for use in HTML pages
if (typeof window !== 'undefined') {
  window.ttsQueries = ttsQueries;
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ttsQueries;
}
