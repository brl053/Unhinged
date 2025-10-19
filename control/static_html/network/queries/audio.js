/**
 * audioQueries - Query builders for AudioService
 * Generated on: 2025-10-19T09:16:13.398Z
 */
const audioQueries = {
  /**
   * Build transcribe query
   */
  transcribe: {
    method: 'POST',
    path: '/transcribe',
    buildUrl: (baseUrl, params = {}) => {
      let path = '/transcribe';
      Object.entries(params).forEach(([key, value]) => {
        path = path.replace(`{${key}}`, encodeURIComponent(value));
      });
      return `${baseUrl}${path}`;
    }
  },

};

// Export for use in HTML pages
if (typeof window !== 'undefined') {
  window.audioQueries = audioQueries;
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = audioQueries;
}
