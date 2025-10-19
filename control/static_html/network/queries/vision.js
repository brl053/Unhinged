/**
 * visionQueries - Query builders for VisionService
 * Generated on: 2025-10-19T09:16:13.398Z
 */
const visionQueries = {
  /**
   * Build analyzeImage query
   */
  analyzeImage: {
    method: 'POST',
    path: '/analyze',
    buildUrl: (baseUrl, params = {}) => {
      let path = '/analyze';
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

};

// Export for use in HTML pages
if (typeof window !== 'undefined') {
  window.visionQueries = visionQueries;
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = visionQueries;
}
