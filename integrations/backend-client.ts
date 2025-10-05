/**
 * @fileoverview Unhinged Backend Integration Client - Full-Stack Connection
 * 
 * @description
 * Complete backend integration client that connects the Universal System
 * intelligent frontend with existing Unhinged backend services. Provides
 * context-aware API calls, real-time communication, and seamless integration
 * with LLM, TTS, STT, and tool registry services.
 * 
 * @design_principles
 * - Context-aware: All API calls optimized based on user context
 * - Real-time: WebSocket integration for live updates and interactions
 * - Resilient: Automatic retry, fallback, and error handling
 * - Secure: Proper authentication and data validation
 * - Performance: Context-based optimization and caching strategies
 * 
 * @integration_contract
 * This client serves as the bridge between:
 * 1. Universal System intelligent frontend (DSL, React, Context Adapter)
 * 2. Existing Unhinged backend services (LLM, TTS, STT, Tools)
 * 3. Real-time communication channels (WebSocket, Server-Sent Events)
 * 4. External service integrations (APIs, databases, third-party services)
 * 
 * @production_pipeline
 * Voice Input → Context Analysis → UI Generation → Backend Integration → Live Actions
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import { EventEmitter } from 'events';
import { UserContext, ContextAwareUIAdapter } from '../adapters/context-adapter';
import { DSLInterpreter, ComponentInstance } from '../core/dsl-interpreter';
import { LLMUISchemaGenerator, GeneratedSchemaResult } from '../generators/ui-schema-gen';

/**
 * Backend service configuration
 * 
 * @description
 * Configuration for connecting to various Unhinged backend services
 * with context-aware optimization settings.
 */
export interface BackendServiceConfig {
  /** Service endpoints */
  endpoints: {
    llm: string;
    tts: string;
    stt: string;
    tools: string;
    websocket: string;
    api: string;
  };
  
  /** Authentication configuration */
  auth: {
    apiKey?: string;
    token?: string;
    refreshToken?: string;
    authEndpoint?: string;
  };
  
  /** Performance and optimization settings */
  optimization: {
    enableCaching: boolean;
    cacheTimeout: number;
    enableCompression: boolean;
    maxRetries: number;
    timeoutMs: number;
    batchRequests: boolean;
  };
  
  /** Context-aware settings */
  contextAware: {
    adaptPayloads: boolean;
    optimizeForNetwork: boolean;
    enhanceAccessibility: boolean;
    personalizeResponses: boolean;
  };
}

/**
 * API request with context information
 * 
 * @description
 * Enhanced API request that includes user context for
 * backend optimization and personalization.
 */
export interface ContextAwareAPIRequest {
  /** Standard request data */
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  data?: any;
  headers?: Record<string, string>;
  
  /** Context information for optimization */
  context: UserContext;
  
  /** Request optimization hints */
  optimization?: {
    priority: 'low' | 'normal' | 'high';
    cacheable: boolean;
    realTime: boolean;
    compress: boolean;
  };
  
  /** Accessibility requirements */
  accessibility?: {
    enhanceTextDescriptions: boolean;
    provideAltText: boolean;
    simplifyLanguage: boolean;
  };
}

/**
 * Backend service response
 * 
 * @description
 * Standardized response format from backend services
 * with context-aware enhancements.
 */
export interface BackendServiceResponse<T = any> {
  /** Response data */
  data: T;
  
  /** Response metadata */
  metadata: {
    requestId: string;
    timestamp: number;
    processingTime: number;
    cached: boolean;
    optimized: boolean;
  };
  
  /** Context-aware enhancements */
  enhancements?: {
    accessibilityText?: string;
    simplifiedContent?: string;
    contextualHints?: string[];
  };
  
  /** Error information */
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

/**
 * Real-time event from backend
 * 
 * @description
 * Real-time events received via WebSocket or Server-Sent Events
 * for live updates and interactions.
 */
export interface BackendRealtimeEvent {
  /** Event type */
  type: 'ui_update' | 'context_change' | 'tool_result' | 'llm_response' | 'system_notification';
  
  /** Event data */
  data: any;
  
  /** Event metadata */
  metadata: {
    timestamp: number;
    source: string;
    priority: 'low' | 'normal' | 'high';
    requiresAction: boolean;
  };
  
  /** Target information */
  target?: {
    componentId?: string;
    userId?: string;
    sessionId?: string;
  };
}

/**
 * Tool execution request
 * 
 * @description
 * Request to execute a tool through the backend tool registry
 * with context-aware optimization.
 */
export interface ToolExecutionRequest {
  /** Tool identification */
  toolName: string;
  toolVersion?: string;
  
  /** Tool parameters */
  parameters: Record<string, any>;
  
  /** Execution context */
  context: UserContext;
  
  /** Execution options */
  options: {
    async: boolean;
    timeout: number;
    retries: number;
    priority: 'low' | 'normal' | 'high';
  };
  
  /** Callback information */
  callback?: {
    componentId: string;
    action: string;
  };
}

/**
 * LLM service request
 * 
 * @description
 * Request to LLM service with context-aware prompt enhancement
 * and response optimization.
 */
export interface LLMServiceRequest {
  /** Base prompt */
  prompt: string;
  
  /** LLM configuration */
  config: {
    model: string;
    temperature: number;
    maxTokens: number;
    systemPrompt?: string;
  };
  
  /** Context for prompt enhancement */
  context: UserContext;
  
  /** Response requirements */
  responseFormat: {
    type: 'text' | 'json' | 'structured';
    schema?: any;
    accessibility?: boolean;
  };
}

/**
 * Unhinged Backend Integration Client
 * 
 * @description
 * Main client class that provides seamless integration between the
 * Universal System intelligent frontend and Unhinged backend services.
 * Handles context-aware API calls, real-time communication, and
 * service orchestration.
 * 
 * @example
 * ```typescript
 * const backendClient = new UnhingedBackendClient(config, contextAdapter);
 * 
 * // Context-aware LLM request
 * const response = await backendClient.callLLMService({
 *   prompt: "Generate a voice input component",
 *   context: currentContext
 * });
 * 
 * // Execute tool with context optimization
 * const result = await backendClient.executeTool({
 *   toolName: "file_manager",
 *   parameters: { action: "list" },
 *   context: currentContext
 * });
 * ```
 */
export class UnhingedBackendClient extends EventEmitter {
  private config: BackendServiceConfig;
  private contextAdapter: ContextAwareUIAdapter;
  private interpreter: DSLInterpreter;
  private uiGenerator: LLMUISchemaGenerator;
  
  private websocket: WebSocket | null = null;
  private requestCache: Map<string, { data: any; timestamp: number }> = new Map();
  private activeRequests: Map<string, Promise<any>> = new Map();
  private connectionRetries = 0;
  private maxConnectionRetries = 5;
  
  /**
   * Create Unhinged Backend Integration Client
   * 
   * @param config - Backend service configuration
   * @param contextAdapter - Context-aware UI adapter
   * @param interpreter - DSL interpreter instance
   * @param uiGenerator - LLM UI schema generator
   */
  constructor(
    config: BackendServiceConfig,
    contextAdapter: ContextAwareUIAdapter,
    interpreter: DSLInterpreter,
    uiGenerator: LLMUISchemaGenerator
  ) {
    super();
    
    this.config = config;
    this.contextAdapter = contextAdapter;
    this.interpreter = interpreter;
    this.uiGenerator = uiGenerator;
    
    // Initialize connections
    this.initializeConnections();
    
    // Set up context change listeners
    this.setupContextListeners();
    
    console.log('🔗 Unhinged Backend Integration Client initialized');
    console.log(`🌐 API Endpoint: ${config.endpoints.api}`);
    console.log(`🤖 LLM Service: ${config.endpoints.llm}`);
    console.log(`🎤 Voice Services: ${config.endpoints.stt} / ${config.endpoints.tts}`);
    console.log(`🛠️ Tool Registry: ${config.endpoints.tools}`);
  }
  
  /**
   * Initialize backend connections
   */
  private async initializeConnections(): Promise<void> {
    try {
      // Initialize WebSocket connection for real-time updates
      await this.initializeWebSocket();
      
      // Test API connectivity
      await this.testConnectivity();
      
      // Initialize authentication if required
      if (this.config.auth.authEndpoint) {
        await this.initializeAuthentication();
      }
      
      console.log('✅ Backend connections initialized successfully');
      this.emit('connected');
      
    } catch (error) {
      console.error('❌ Failed to initialize backend connections:', error);
      this.emit('connectionError', error);
      
      // Retry connection
      if (this.connectionRetries < this.maxConnectionRetries) {
        this.connectionRetries++;
        console.log(`🔄 Retrying connection (${this.connectionRetries}/${this.maxConnectionRetries})...`);
        setTimeout(() => this.initializeConnections(), 2000 * this.connectionRetries);
      }
    }
  }
  
  /**
   * Initialize WebSocket connection
   */
  private async initializeWebSocket(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.websocket = new WebSocket(this.config.endpoints.websocket);
        
        this.websocket.onopen = () => {
          console.log('🔌 WebSocket connected');
          this.connectionRetries = 0;
          resolve();
        };
        
        this.websocket.onmessage = (event) => {
          try {
            const realtimeEvent: BackendRealtimeEvent = JSON.parse(event.data);
            this.handleRealtimeEvent(realtimeEvent);
          } catch (error) {
            console.error('❌ Failed to parse WebSocket message:', error);
          }
        };
        
        this.websocket.onclose = () => {
          console.log('🔌 WebSocket disconnected');
          this.websocket = null;
          this.emit('disconnected');
          
          // Attempt to reconnect
          setTimeout(() => this.initializeWebSocket(), 5000);
        };
        
        this.websocket.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          reject(error);
        };
        
        // Set connection timeout
        setTimeout(() => {
          if (this.websocket?.readyState !== WebSocket.OPEN) {
            reject(new Error('WebSocket connection timeout'));
          }
        }, 10000);
        
      } catch (error) {
        reject(error);
      }
    });
  }
  
  /**
   * Test API connectivity
   */
  private async testConnectivity(): Promise<void> {
    const testRequest: ContextAwareAPIRequest = {
      endpoint: '/health',
      method: 'GET',
      context: this.contextAdapter.getCurrentContext(),
      optimization: {
        priority: 'high',
        cacheable: false,
        realTime: false,
        compress: false,
      },
    };
    
    const response = await this.makeAPIRequest(testRequest);
    
    if (response.error) {
      throw new Error(`API connectivity test failed: ${response.error.message}`);
    }
    
    console.log('✅ API connectivity test passed');
  }

  /**
   * Initialize authentication
   */
  private async initializeAuthentication(): Promise<void> {
    if (!this.config.auth.authEndpoint) return;

    const authRequest: ContextAwareAPIRequest = {
      endpoint: this.config.auth.authEndpoint,
      method: 'POST',
      data: {
        apiKey: this.config.auth.apiKey,
        refreshToken: this.config.auth.refreshToken,
      },
      context: this.contextAdapter.getCurrentContext(),
    };

    const response = await this.makeAPIRequest(authRequest);

    if (response.error) {
      throw new Error(`Authentication failed: ${response.error.message}`);
    }

    // Store authentication token
    this.config.auth.token = response.data.token;
    console.log('✅ Authentication successful');
  }

  /**
   * Set up context change listeners
   */
  private setupContextListeners(): void {
    // Listen for context changes from the adapter
    this.contextAdapter.on('contextChanged', (newContext: UserContext) => {
      console.log('🔄 Context changed, optimizing backend connections');
      this.optimizeForContext(newContext);
    });

    console.log('👂 Context change listeners set up');
  }

  /**
   * Optimize backend connections for new context
   *
   * @param context - New user context
   */
  private optimizeForContext(context: UserContext): void {
    // Adjust request timeouts based on network speed
    if (context.environment.network.speed === 'slow') {
      this.config.optimization.timeoutMs = 30000; // 30 seconds
      this.config.optimization.enableCompression = true;
    } else {
      this.config.optimization.timeoutMs = 10000; // 10 seconds
      this.config.optimization.enableCompression = false;
    }

    // Adjust caching based on device type
    if (context.device.type === 'mobile') {
      this.config.optimization.enableCaching = true;
      this.config.optimization.cacheTimeout = 300000; // 5 minutes
    }

    console.log('⚡ Backend optimized for new context');
  }

  /**
   * Make context-aware API request
   *
   * @param request - API request with context
   * @returns Promise resolving to service response
   */
  async makeAPIRequest<T = any>(request: ContextAwareAPIRequest): Promise<BackendServiceResponse<T>> {
    const requestId = this.generateRequestId();
    const startTime = Date.now();

    console.log(`🌐 Making API request: ${request.method} ${request.endpoint} (${requestId})`);

    try {
      // Check cache first if request is cacheable
      if (request.optimization?.cacheable && this.config.optimization.enableCaching) {
        const cached = this.getCachedResponse(request);
        if (cached) {
          console.log(`💾 Returning cached response for ${requestId}`);
          return cached;
        }
      }

      // Optimize request based on context
      const optimizedRequest = this.optimizeRequest(request);

      // Make the actual HTTP request
      const response = await this.executeHTTPRequest(optimizedRequest);

      // Process and enhance response
      const processedResponse = this.processResponse(response, request, requestId, startTime);

      // Cache response if applicable
      if (request.optimization?.cacheable && this.config.optimization.enableCaching) {
        this.cacheResponse(request, processedResponse);
      }

      console.log(`✅ API request completed: ${requestId} (${Date.now() - startTime}ms)`);
      return processedResponse;

    } catch (error) {
      console.error(`❌ API request failed: ${requestId}`, error);

      // Return error response
      return {
        data: null,
        metadata: {
          requestId,
          timestamp: Date.now(),
          processingTime: Date.now() - startTime,
          cached: false,
          optimized: false,
        },
        error: {
          code: 'REQUEST_FAILED',
          message: error instanceof Error ? error.message : 'Unknown error',
          details: error,
        },
      };
    }
  }

  /**
   * Call LLM service with context-aware optimization
   *
   * @param request - LLM service request
   * @returns Promise resolving to LLM response
   */
  async callLLMService(request: LLMServiceRequest): Promise<BackendServiceResponse<string>> {
    console.log(`🤖 Calling LLM service: ${request.config.model}`);

    // Enhance prompt with context information
    const enhancedPrompt = this.enhancePromptWithContext(request.prompt, request.context);

    // Create API request
    const apiRequest: ContextAwareAPIRequest = {
      endpoint: '/llm/generate',
      method: 'POST',
      data: {
        prompt: enhancedPrompt,
        model: request.config.model,
        temperature: request.config.temperature,
        maxTokens: request.config.maxTokens,
        systemPrompt: request.config.systemPrompt,
        responseFormat: request.responseFormat,
      },
      context: request.context,
      optimization: {
        priority: 'high',
        cacheable: true,
        realTime: false,
        compress: true,
      },
      accessibility: request.responseFormat.accessibility ? {
        enhanceTextDescriptions: true,
        provideAltText: true,
        simplifyLanguage: request.context.accessibility.cognitiveSupport,
      } : undefined,
    };

    const response = await this.makeAPIRequest(apiRequest);

    // Post-process LLM response for accessibility if needed
    if (request.responseFormat.accessibility && response.data) {
      response.enhancements = {
        accessibilityText: this.generateAccessibilityText(response.data, request.context),
        simplifiedContent: request.context.accessibility.cognitiveSupport ?
          this.simplifyContent(response.data) : undefined,
      };
    }

    return response;
  }
