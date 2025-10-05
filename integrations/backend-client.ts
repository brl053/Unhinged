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

  /**
   * Execute tool through backend tool registry
   *
   * @param request - Tool execution request
   * @returns Promise resolving to tool execution result
   */
  async executeTool(request: ToolExecutionRequest): Promise<BackendServiceResponse<any>> {
    console.log(`🛠️ Executing tool: ${request.toolName}`);

    const apiRequest: ContextAwareAPIRequest = {
      endpoint: '/tools/execute',
      method: 'POST',
      data: {
        toolName: request.toolName,
        toolVersion: request.toolVersion,
        parameters: request.parameters,
        options: request.options,
        context: request.context,
      },
      context: request.context,
      optimization: {
        priority: request.options.priority,
        cacheable: false,
        realTime: !request.options.async,
        compress: true,
      },
    };

    const response = await this.makeAPIRequest(apiRequest);

    // If tool execution has a callback, update the component
    if (request.callback && response.data && !response.error) {
      this.handleToolCallback(request.callback, response.data);
    }

    return response;
  }

  /**
   * Convert text to speech with context optimization
   *
   * @param text - Text to convert
   * @param context - User context
   * @returns Promise resolving to audio data
   */
  async textToSpeech(text: string, context: UserContext): Promise<BackendServiceResponse<ArrayBuffer>> {
    console.log(`🔊 Converting text to speech: "${text.substring(0, 50)}..."`);

    const apiRequest: ContextAwareAPIRequest = {
      endpoint: '/tts/synthesize',
      method: 'POST',
      data: {
        text,
        voice: this.selectOptimalVoice(context),
        speed: context.accessibility.cognitiveSupport ? 0.8 : 1.0,
        pitch: 1.0,
        format: 'wav',
      },
      context,
      optimization: {
        priority: 'high',
        cacheable: true,
        realTime: true,
        compress: false, // Audio data shouldn't be compressed
      },
    };

    return this.makeAPIRequest(apiRequest);
  }

  /**
   * Convert speech to text with context optimization
   *
   * @param audioData - Audio data to transcribe
   * @param context - User context
   * @returns Promise resolving to transcription
   */
  async speechToText(audioData: ArrayBuffer, context: UserContext): Promise<BackendServiceResponse<string>> {
    console.log(`🎤 Converting speech to text (${audioData.byteLength} bytes)`);

    const apiRequest: ContextAwareAPIRequest = {
      endpoint: '/stt/transcribe',
      method: 'POST',
      data: {
        audio: Array.from(new Uint8Array(audioData)),
        format: 'wav',
        language: context.user.language,
        enhanceForNoise: context.environment.noise === 'noisy',
        model: context.environment.noise === 'noisy' ? 'whisper-large' : 'whisper-base',
      },
      context,
      optimization: {
        priority: 'high',
        cacheable: false,
        realTime: true,
        compress: true,
      },
    };

    return this.makeAPIRequest(apiRequest);
  }

  /**
   * Generate UI from voice command (complete pipeline)
   *
   * @param voiceCommand - Voice command text
   * @param context - User context
   * @returns Promise resolving to generated UI components
   */
  async generateUIFromVoice(voiceCommand: string, context: UserContext): Promise<{
    components: ComponentInstance[];
    confidence: number;
    processingTime: number;
  }> {
    const startTime = Date.now();
    console.log(`🎤→🎨 Generating UI from voice: "${voiceCommand}"`);

    try {
      // Step 1: Generate UI schema using LLM
      const schemaResult = await this.uiGenerator.generateFromPrompt(voiceCommand, {
        existingComponents: [],
        userPreferences: {
          preferredVariants: {},
          commonProps: {},
          stylePreferences: {},
        },
        applicationContext: {
          currentRoute: '/',
          activeFeatures: [],
          userRole: 'user',
        },
        usagePatterns: {
          frequentCombinations: [],
          successfulGenerations: [],
          userFeedback: [],
        },
      });

      // Step 2: Create components in interpreter
      const components: ComponentInstance[] = [];
      for (const componentDef of schemaResult.components) {
        const component = this.interpreter.createComponent(
          componentDef.component,
          componentDef.props || {},
          componentDef.state || {}
        );
        components.push(component);
      }

      // Step 3: Apply context-aware adaptations
      const adaptedComponents: ComponentInstance[] = [];
      for (const component of components) {
        const adaptedComponent = await this.contextAdapter.adaptComponent(component);
        adaptedComponents.push(adaptedComponent);
      }

      const processingTime = Date.now() - startTime;

      console.log(`✅ UI generated from voice in ${processingTime}ms (${adaptedComponents.length} components)`);

      return {
        components: adaptedComponents,
        confidence: schemaResult.confidence,
        processingTime,
      };

    } catch (error) {
      console.error('❌ Failed to generate UI from voice:', error);
      throw error;
    }
  }

  /**
   * Handle real-time events from backend
   *
   * @param event - Real-time event
   */
  private handleRealtimeEvent(event: BackendRealtimeEvent): void {
    console.log(`📡 Received real-time event: ${event.type}`);

    switch (event.type) {
      case 'ui_update':
        this.handleUIUpdateEvent(event);
        break;

      case 'context_change':
        this.handleContextChangeEvent(event);
        break;

      case 'tool_result':
        this.handleToolResultEvent(event);
        break;

      case 'llm_response':
        this.handleLLMResponseEvent(event);
        break;

      case 'system_notification':
        this.handleSystemNotificationEvent(event);
        break;

      default:
        console.warn(`❓ Unknown real-time event type: ${event.type}`);
    }

    // Emit event for external listeners
    this.emit('realtimeEvent', event);
  }

  /**
   * Handle UI update events
   *
   * @param event - UI update event
   */
  private handleUIUpdateEvent(event: BackendRealtimeEvent): void {
    if (event.target?.componentId) {
      const component = this.interpreter.getComponent(event.target.componentId);
      if (component && event.data.props) {
        this.interpreter.updateComponentProps(event.target.componentId, event.data.props);
        console.log(`🔄 Updated component ${event.target.componentId} from real-time event`);
      }
    }
  }

  /**
   * Handle context change events
   *
   * @param event - Context change event
   */
  private handleContextChangeEvent(event: BackendRealtimeEvent): void {
    if (event.data.context) {
      this.contextAdapter.updateContext(event.data.context);
      console.log('🔄 Updated context from real-time event');
    }
  }

  /**
   * Handle tool result events
   *
   * @param event - Tool result event
   */
  private handleToolResultEvent(event: BackendRealtimeEvent): void {
    if (event.target?.componentId && event.data.callback) {
      this.handleToolCallback(event.data.callback, event.data.result);
    }
  }

  /**
   * Handle LLM response events
   *
   * @param event - LLM response event
   */
  private handleLLMResponseEvent(event: BackendRealtimeEvent): void {
    console.log('🤖 Received LLM response via real-time event');
    this.emit('llmResponse', event.data);
  }

  /**
   * Handle system notification events
   *
   * @param event - System notification event
   */
  private handleSystemNotificationEvent(event: BackendRealtimeEvent): void {
    console.log(`📢 System notification: ${event.data.message}`);
    this.emit('systemNotification', event.data);
  }

  /**
   * Handle tool callback execution
   *
   * @param callback - Callback information
   * @param result - Tool execution result
   */
  private handleToolCallback(callback: { componentId: string; action: string }, result: any): void {
    const component = this.interpreter.getComponent(callback.componentId);
    if (!component) {
      console.warn(`⚠️ Tool callback for unknown component: ${callback.componentId}`);
      return;
    }

    // Execute the callback action with the result
    const action = this.interpreter.parseAction(`${callback.action}=${JSON.stringify(result)}`);
    this.interpreter.executeAction(callback.componentId, action).catch(error => {
      console.error('❌ Failed to execute tool callback:', error);
    });

    console.log(`🔗 Tool callback executed for ${callback.componentId}`);
  }

  /**
   * Enhance prompt with context information
   *
   * @param prompt - Base prompt
   * @param context - User context
   * @returns Enhanced prompt
   */
  private enhancePromptWithContext(prompt: string, context: UserContext): string {
    let enhancedPrompt = prompt;

    // Add device context
    enhancedPrompt += `\n\nContext: User is on ${context.device.type} device`;

    // Add accessibility context
    if (context.accessibility.screenReader) {
      enhancedPrompt += ', using screen reader';
    }
    if (context.accessibility.highContrast) {
      enhancedPrompt += ', requires high contrast';
    }

    // Add environment context
    if (context.environment.noise === 'noisy') {
      enhancedPrompt += ', in noisy environment';
    }

    // Add user preference context
    if (context.user.inputPreference === 'voice') {
      enhancedPrompt += ', prefers voice interaction';
    }

    enhancedPrompt += '. Please optimize the response accordingly.';

    return enhancedPrompt;
  }

  /**
   * Generate accessibility text for content
   *
   * @param content - Content to enhance
   * @param context - User context
   * @returns Accessibility text
   */
  private generateAccessibilityText(content: string, context: UserContext): string {
    let accessibilityText = content;

    if (context.accessibility.screenReader) {
      accessibilityText = `Screen reader optimized: ${content}`;
    }

    if (context.accessibility.cognitiveSupport) {
      accessibilityText += ' (Simplified for cognitive accessibility)';
    }

    return accessibilityText;
  }

  /**
   * Simplify content for cognitive accessibility
   *
   * @param content - Content to simplify
   * @returns Simplified content
   */
  private simplifyContent(content: string): string {
    // Basic content simplification
    return content
      .replace(/\b\w{10,}\b/g, (match) => match.substring(0, 8) + '...') // Shorten long words
      .replace(/[;:]/g, '.') // Replace complex punctuation
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim();
  }

  /**
   * Select optimal voice for TTS based on context
   *
   * @param context - User context
   * @returns Voice identifier
   */
  private selectOptimalVoice(context: UserContext): string {
    // Select voice based on user preferences and context
    if (context.accessibility.cognitiveSupport) {
      return 'clear-slow'; // Clear, slower voice for cognitive support
    }

    if (context.environment.noise === 'noisy') {
      return 'enhanced-clarity'; // Enhanced clarity for noisy environments
    }

    return 'default'; // Default voice
  }

  /**
   * Optimize request based on context
   *
   * @param request - Original request
   * @returns Optimized request
   */
  private optimizeRequest(request: ContextAwareAPIRequest): ContextAwareAPIRequest {
    const optimized = { ...request };

    // Add compression if enabled and beneficial
    if (this.config.optimization.enableCompression && request.optimization?.compress) {
      optimized.headers = { ...optimized.headers, 'Accept-Encoding': 'gzip, deflate' };
    }

    // Add authentication if available
    if (this.config.auth.token) {
      optimized.headers = { ...optimized.headers, 'Authorization': `Bearer ${this.config.auth.token}` };
    }

    // Add context information to headers
    optimized.headers = {
      ...optimized.headers,
      'X-Device-Type': request.context.device.type,
      'X-Network-Speed': request.context.environment.network.speed,
      'X-Accessibility': JSON.stringify(request.context.accessibility),
    };

    return optimized;
  }

  /**
   * Execute HTTP request
   *
   * @param request - Optimized request
   * @returns Promise resolving to response
   */
  private async executeHTTPRequest(request: ContextAwareAPIRequest): Promise<any> {
    const url = `${this.config.endpoints.api}${request.endpoint}`;

    const fetchOptions: RequestInit = {
      method: request.method,
      headers: {
        'Content-Type': 'application/json',
        ...request.headers,
      },
      signal: AbortSignal.timeout(this.config.optimization.timeoutMs),
    };

    if (request.data && request.method !== 'GET') {
      fetchOptions.body = JSON.stringify(request.data);
    }

    const response = await fetch(url, fetchOptions);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Process response and add enhancements
   *
   * @param response - Raw response
   * @param request - Original request
   * @param requestId - Request ID
   * @param startTime - Request start time
   * @returns Processed response
   */
  private processResponse(
    response: any,
    request: ContextAwareAPIRequest,
    requestId: string,
    startTime: number
  ): BackendServiceResponse {
    return {
      data: response.data || response,
      metadata: {
        requestId,
        timestamp: Date.now(),
        processingTime: Date.now() - startTime,
        cached: false,
        optimized: true,
      },
      enhancements: request.accessibility ? {
        accessibilityText: this.generateAccessibilityText(response.data || response, request.context),
        simplifiedContent: request.context.accessibility.cognitiveSupport ?
          this.simplifyContent(response.data || response) : undefined,
      } : undefined,
    };
  }

  /**
   * Get cached response if available
   *
   * @param request - API request
   * @returns Cached response or null
   */
  private getCachedResponse(request: ContextAwareAPIRequest): BackendServiceResponse | null {
    const cacheKey = this.generateCacheKey(request);
    const cached = this.requestCache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < this.config.optimization.cacheTimeout) {
      return {
        ...cached.data,
        metadata: {
          ...cached.data.metadata,
          cached: true,
        },
      };
    }

    return null;
  }

  /**
   * Cache response
   *
   * @param request - API request
   * @param response - Response to cache
   */
  private cacheResponse(request: ContextAwareAPIRequest, response: BackendServiceResponse): void {
    const cacheKey = this.generateCacheKey(request);
    this.requestCache.set(cacheKey, {
      data: response,
      timestamp: Date.now(),
    });

    // Clean up old cache entries
    if (this.requestCache.size > 100) {
      const oldestKey = this.requestCache.keys().next().value;
      this.requestCache.delete(oldestKey);
    }
  }

  /**
   * Generate cache key for request
   *
   * @param request - API request
   * @returns Cache key
   */
  private generateCacheKey(request: ContextAwareAPIRequest): string {
    return `${request.method}:${request.endpoint}:${JSON.stringify(request.data)}`;
  }

  /**
   * Generate unique request ID
   *
   * @returns Request ID
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get client statistics
   *
   * @returns Statistics object
   */
  getStats(): {
    connected: boolean;
    cacheSize: number;
    activeRequests: number;
    connectionRetries: number;
    config: BackendServiceConfig;
  } {
    return {
      connected: this.websocket?.readyState === WebSocket.OPEN,
      cacheSize: this.requestCache.size,
      activeRequests: this.activeRequests.size,
      connectionRetries: this.connectionRetries,
      config: this.config,
    };
  }

  /**
   * Disconnect from backend services
   */
  disconnect(): void {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }

    this.requestCache.clear();
    this.activeRequests.clear();

    console.log('🔌 Disconnected from backend services');
    this.emit('disconnected');
  }
}
