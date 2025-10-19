#!/usr/bin/env node

/**
 * HTML Client Generator from Protobuf Gateway Annotations
 * 
 * Generates JavaScript clients and query builders for HTML pages
 * from protobuf service definitions with gateway annotations.
 * 
 * This bridges the gap between the sophisticated protobuf+gateway
 * system and simple HTML/JS control plane interfaces.
 */

const fs = require('fs');
const path = require('path');

// Service definitions from our protobuf files
const SERVICES = {
  chat: {
    name: 'ChatService',
    baseUrl: 'http://localhost:8080/api/v1/chat',
    methods: {
      createConversation: { method: 'POST', path: '/conversations' },
      getConversation: { method: 'GET', path: '/conversations/{conversation_id}' },
      listConversations: { method: 'GET', path: '/conversations' },
      sendMessage: { method: 'POST', path: '/conversations/{conversation_id}/messages' }
    }
  },
  audio: {
    name: 'AudioService', 
    baseUrl: 'http://localhost:8000', // STT service
    methods: {
      transcribe: { method: 'POST', path: '/transcribe' }
    }
  },
  tts: {
    name: 'TTSService',
    baseUrl: 'http://localhost:8002', // TTS service
    methods: {
      synthesize: { method: 'POST', path: '/synthesize' },
      getHealth: { method: 'GET', path: '/health' },
      getSpeakers: { method: 'GET', path: '/speakers' }
    }
  },
  vision: {
    name: 'VisionService',
    baseUrl: 'http://localhost:8001',
    methods: {
      analyzeImage: { method: 'POST', path: '/analyze' },
      getHealth: { method: 'GET', path: '/health' }
    }
  }
};

/**
 * Generate a JavaScript client for a service
 */
function generateClient(serviceName, serviceConfig) {
  const className = `${serviceConfig.name}Client`;
  
  let clientCode = `/**
 * ${serviceConfig.name} - Auto-generated from protobuf gateway annotations
 * Generated on: ${new Date().toISOString()}
 */
class ${className} {
  constructor(baseUrl = '${serviceConfig.baseUrl}') {
    this.baseUrl = baseUrl;
  }

  /**
   * Make HTTP request with error handling
   */
  async _request(method, path, data = null, options = {}) {
    const url = \`\${this.baseUrl}\${path}\`;
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
        throw new Error(\`HTTP \${response.status}: \${response.statusText}\`);
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
      console.error(\`\${className} request failed:\`, error);
      throw error;
    }
  }

`;

  // Generate methods for each service endpoint
  Object.entries(serviceConfig.methods).forEach(([methodName, config]) => {
    const pathParams = config.path.match(/\{([^}]+)\}/g) || [];
    const paramNames = pathParams.map(p => p.slice(1, -1));
    
    let methodParams = paramNames.join(', ');
    if (config.method === 'POST' || config.method === 'PUT') {
      methodParams += methodParams ? ', data' : 'data';
    }
    if (methodParams) methodParams += ', ';
    methodParams += 'options = {}';

    let pathBuilder = config.path;
    paramNames.forEach(param => {
      pathBuilder = pathBuilder.replace(`{${param}}`, `\${${param}}`);
    });

    clientCode += `  /**
   * ${methodName} - ${config.method} ${config.path}
   */
  async ${methodName}(${methodParams}) {
    const path = \`${pathBuilder}\`;
    ${config.method === 'POST' || config.method === 'PUT' ? 
      `return await this._request('${config.method}', path, data, options);` :
      `return await this._request('${config.method}', path, null, options);`
    }
  }

`;
  });

  clientCode += `}

// Export for use in HTML pages
if (typeof window !== 'undefined') {
  window.${className} = ${className};
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ${className};
}
`;

  return clientCode;
}

/**
 * Generate query builder helpers
 */
function generateQueries(serviceName, serviceConfig) {
  const queryName = `${serviceName}Queries`;
  
  let queryCode = `/**
 * ${queryName} - Query builders for ${serviceConfig.name}
 * Generated on: ${new Date().toISOString()}
 */
const ${queryName} = {
`;

  Object.entries(serviceConfig.methods).forEach(([methodName, config]) => {
    queryCode += `  /**
   * Build ${methodName} query
   */
  ${methodName}: {
    method: '${config.method}',
    path: '${config.path}',
    buildUrl: (baseUrl, params = {}) => {
      let path = '${config.path}';
      Object.entries(params).forEach(([key, value]) => {
        path = path.replace(\`{\${key}}\`, encodeURIComponent(value));
      });
      return \`\${baseUrl}\${path}\`;
    }
  },

`;
  });

  queryCode += `};

// Export for use in HTML pages
if (typeof window !== 'undefined') {
  window.${queryName} = ${queryName};
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ${queryName};
}
`;

  return queryCode;
}

/**
 * Main generation function
 */
function generateAll() {
  const clientsDir = path.join(__dirname, 'clients');
  const queriesDir = path.join(__dirname, 'queries');

  // Ensure directories exist
  if (!fs.existsSync(clientsDir)) fs.mkdirSync(clientsDir, { recursive: true });
  if (!fs.existsSync(queriesDir)) fs.mkdirSync(queriesDir, { recursive: true });

  console.log('🔧 Generating HTML clients from protobuf gateway annotations...\n');

  Object.entries(SERVICES).forEach(([serviceName, serviceConfig]) => {
    // Generate client
    const clientCode = generateClient(serviceName, serviceConfig);
    const clientPath = path.join(clientsDir, `${serviceName}-client.js`);
    fs.writeFileSync(clientPath, clientCode);
    console.log(`✅ Generated client: ${clientPath}`);

    // Generate queries
    const queryCode = generateQueries(serviceName, serviceConfig);
    const queryPath = path.join(queriesDir, `${serviceName}.js`);
    fs.writeFileSync(queryPath, queryCode);
    console.log(`✅ Generated queries: ${queryPath}`);
  });

  console.log('\n🎉 HTML client generation complete!');
  console.log('\nUsage in HTML:');
  console.log('  <script src="network/clients/chat-client.js"></script>');
  console.log('  <script src="network/queries/chat.js"></script>');
}

// Run if called directly
if (require.main === module) {
  generateAll();
}

module.exports = { generateAll, generateClient, generateQueries };
