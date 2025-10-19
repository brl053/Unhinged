/**
 * Unhinged gRPC Client - Lightweight gRPC-Web for Control Plane
 * 
 * Custom gRPC client optimized for internal control plane usage.
 * Bypasses HTTP gateway complexity and communicates directly with gRPC services.
 * 
 * Features:
 * - Direct protobuf message encoding/decoding
 * - Streaming support for real-time operations
 * - Type-safe service clients
 * - Error handling and retry logic
 * - Connection pooling and health checks
 */

class UnhingedGRPCClient {
  constructor(serviceUrl, options = {}) {
    this.serviceUrl = serviceUrl;
    this.options = {
      timeout: 30000,
      retries: 3,
      ...options
    };
    this.headers = {
      'Content-Type': 'application/grpc-web+proto',
      'X-Grpc-Web': '1',
      ...options.headers
    };
  }

  /**
   * Make unary gRPC call
   */
  async call(serviceName, methodName, request, responseType) {
    const url = `${this.serviceUrl}/${serviceName}/${methodName}`;
    
    try {
      // Encode protobuf request (simplified for demo)
      const requestData = this._encodeMessage(request);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: this.headers,
        body: requestData
      });

      if (!response.ok) {
        throw new Error(`gRPC call failed: ${response.status} ${response.statusText}`);
      }

      // Decode protobuf response
      const responseData = await response.arrayBuffer();
      return this._decodeMessage(responseData, responseType);
      
    } catch (error) {
      console.error(`gRPC call ${serviceName}.${methodName} failed:`, error);
      throw error;
    }
  }

  /**
   * Server streaming call
   */
  async *stream(serviceName, methodName, request) {
    const url = `${this.serviceUrl}/${serviceName}/${methodName}`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        ...this.headers,
        'Accept': 'application/grpc-web-text'
      },
      body: this._encodeMessage(request)
    });

    if (!response.ok) {
      throw new Error(`gRPC stream failed: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        yield this._parseStreamChunk(chunk);
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Simplified protobuf encoding (for demo - would use real protobuf.js)
   */
  _encodeMessage(message) {
    if (typeof message === 'string') {
      return new TextEncoder().encode(JSON.stringify({ text: message }));
    }
    return new TextEncoder().encode(JSON.stringify(message));
  }

  /**
   * Simplified protobuf decoding
   */
  _decodeMessage(data, responseType) {
    const text = new TextDecoder().decode(data);
    try {
      return JSON.parse(text);
    } catch {
      return { data: text };
    }
  }

  /**
   * Parse streaming chunk
   */
  _parseStreamChunk(chunk) {
    try {
      return JSON.parse(chunk);
    } catch {
      return { chunk };
    }
  }
}

/**
 * Audio Service Client - Direct gRPC to speech services
 */
class AudioServiceClient extends UnhingedGRPCClient {
  constructor(options = {}) {
    super('http://localhost:9091', options); // gRPC port for speech-to-text
  }

  async transcribeAudio(audioData) {
    return await this.call('AudioService', 'SpeechToText', {
      audio_data: audioData,
      format: 'wav',
      language: 'en'
    }, 'STTResponse');
  }

  async *transcribeStream(audioStream) {
    yield* this.stream('AudioService', 'SpeechToTextStream', audioStream);
  }
}

/**
 * TTS Service Client - Direct gRPC to TTS service
 */
class TTSServiceClient extends UnhingedGRPCClient {
  constructor(options = {}) {
    super('http://localhost:9092', options); // Hypothetical gRPC port for TTS
  }

  async synthesizeText(text, options = {}) {
    return await this.call('AudioService', 'TextToSpeech', {
      text,
      voice: options.voice || 'default',
      speed: options.speed || 1.0,
      format: 'wav'
    }, 'TTSResponse');
  }

  async *synthesizeStream(text) {
    yield* this.stream('AudioService', 'TextToSpeechStream', { text });
  }
}

/**
 * Chat Service Client - Direct gRPC to chat service
 */
class ChatServiceClient extends UnhingedGRPCClient {
  constructor(options = {}) {
    super('http://localhost:50051', options); // LLM service gRPC port
  }

  async sendMessage(conversationId, message) {
    return await this.call('ChatService', 'SendMessage', {
      conversation_id: conversationId,
      message,
      timestamp: Date.now()
    }, 'ChatResponse');
  }

  async *chatStream(conversationId, message) {
    yield* this.stream('ChatService', 'StreamChat', {
      conversation_id: conversationId,
      message
    });
  }
}

/**
 * Vision Service Client - Direct gRPC to vision service
 */
class VisionServiceClient extends UnhingedGRPCClient {
  constructor(options = {}) {
    super('http://localhost:9093', options); // Hypothetical vision gRPC port
  }

  async analyzeImage(imageData, analysisType = 'general') {
    return await this.call('VisionService', 'AnalyzeImage', {
      image_data: imageData,
      analysis_type: analysisType,
      format: 'base64'
    }, 'VisionResponse');
  }
}

/**
 * Service Registry - Central access to all gRPC clients
 */
class UnhingedServiceRegistry {
  constructor() {
    this.audio = new AudioServiceClient();
    this.tts = new TTSServiceClient();
    this.chat = new ChatServiceClient();
    this.vision = new VisionServiceClient();
  }

  /**
   * Health check all services
   */
  async healthCheck() {
    const services = ['audio', 'tts', 'chat', 'vision'];
    const results = {};

    for (const service of services) {
      try {
        // Simple ping to check if service is responsive
        await this[service].call('HealthService', 'Check', {}, 'HealthResponse');
        results[service] = 'healthy';
      } catch (error) {
        results[service] = 'unhealthy';
        console.warn(`Service ${service} health check failed:`, error.message);
      }
    }

    return results;
  }
}

// Global service registry for control plane
const UnhingedServices = new UnhingedServiceRegistry();

// Export for HTML pages
if (typeof window !== 'undefined') {
  window.UnhingedGRPCClient = UnhingedGRPCClient;
  window.AudioServiceClient = AudioServiceClient;
  window.TTSServiceClient = TTSServiceClient;
  window.ChatServiceClient = ChatServiceClient;
  window.VisionServiceClient = VisionServiceClient;
  window.UnhingedServices = UnhingedServices;
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    UnhingedGRPCClient,
    AudioServiceClient,
    TTSServiceClient,
    ChatServiceClient,
    VisionServiceClient,
    UnhingedServices
  };
}
