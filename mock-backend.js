#!/usr/bin/env node

// Simple mock backend for testing voice recording integration
// This provides the same API endpoints as the Kotlin backend

const http = require('http');
const url = require('url');

const PORT = 8080;

// Mock responses for testing
const mockResponses = [
  "That's interesting! Let me think about that.",
  "I see what you mean. Here's my perspective on that.",
  "Good point! That reminds me of something related.",
  "Absolutely! I can help you with that.",
  "That's a great question. Let me break it down for you.",
  "I understand your perspective. Here's what I think.",
  "Fascinating! That opens up some interesting possibilities.",
  "You're right to bring that up. It's worth considering.",
  "That's a thoughtful observation. I agree with your approach.",
  "Excellent question! The answer depends on a few factors."
];

function getRandomResponse() {
  return mockResponses[Math.floor(Math.random() * mockResponses.length)];
}

function handleChatRequest(req, res) {
  let body = '';
  
  req.on('data', chunk => {
    body += chunk.toString();
  });
  
  req.on('end', () => {
    try {
      // Parse the request
      let prompt = '';
      try {
        const parsed = JSON.parse(body);
        prompt = parsed.prompt || body;
      } catch (e) {
        prompt = body;
      }
      
      console.log(`[CHAT] Received: ${prompt}`);
      
      // Generate response based on content
      let response;
      if (prompt.toLowerCase().includes('hello') || prompt.toLowerCase().includes('hi')) {
        response = "Hello! I'm a mock AI assistant. How can I help you today?";
      } else if (prompt.toLowerCase().includes('test')) {
        response = "This is a test response from the mock backend. Voice recording integration is working!";
      } else if (prompt.toLowerCase().includes('voice') || prompt.toLowerCase().includes('recording')) {
        response = "Great! I can see that voice recording is working perfectly. The transcription came through clearly.";
      } else {
        response = getRandomResponse();
      }
      
      console.log(`[CHAT] Responding: ${response}`);
      
      // Set CORS headers
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
      
      // Return just the text response (like the Kotlin backend)
      res.writeHead(200, { 'Content-Type': 'text/plain' });
      res.end(response);
      
    } catch (error) {
      console.error('[ERROR]', error);
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end('Error processing request');
    }
  });
}

function handleHealthCheck(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    status: 'healthy',
    service: 'mock-backend',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  }));
}

function handleOptions(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.writeHead(200);
  res.end();
}

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;
  const method = req.method;
  
  console.log(`[${method}] ${path}`);
  
  // Handle CORS preflight
  if (method === 'OPTIONS') {
    handleOptions(req, res);
    return;
  }
  
  // Route handling
  if (path === '/chat' && method === 'POST') {
    handleChatRequest(req, res);
  } else if (path === '/api/v1/health' && method === 'GET') {
    handleHealthCheck(req, res);
  } else if (path === '/' && method === 'GET') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end(`🔥 Mock Backend v1.0.0

📋 Available endpoints:
- POST /chat                - Chat endpoint (compatible with frontend)
- GET  /api/v1/health      - Health check
- GET  /                   - This info

🎤 Voice Recording Integration Test Server
Ready to test voice recording with React frontend!`);
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
  }
});

server.listen(PORT, () => {
  console.log(`🚀 Mock Backend Server running on http://localhost:${PORT}`);
  console.log(`📋 Endpoints:`);
  console.log(`   POST http://localhost:${PORT}/chat`);
  console.log(`   GET  http://localhost:${PORT}/api/v1/health`);
  console.log(`🎤 Ready for voice recording integration testing!`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down mock backend...');
  server.close(() => {
    console.log('✅ Mock backend stopped');
    process.exit(0);
  });
});
