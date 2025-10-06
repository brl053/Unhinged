// ============================================================================
// Unhinged Event Library - Core Types and Schema
// ============================================================================
//
// @file types.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Centralized event types for the entire monorepo
//
// This library provides:
// - Standardized event schema across all services
// - Type-safe event definitions
// - Event metadata and context
// - Service-specific event types
// - Event aggregation and monitoring types
// ============================================================================

/**
 * Base event interface - all events must implement this
 */
export interface BaseEvent {
  /** Unique event identifier */
  id: string;
  
  /** Event type identifier (e.g., 'voice_recording_started') */
  type: string;
  
  /** ISO timestamp when event occurred */
  timestamp: string;
  
  /** Service that generated the event */
  source: EventSource;
  
  /** Event payload data */
  data: Record<string, any>;
  
  /** Optional metadata */
  metadata?: EventMetadata;
  
  /** Event version for schema evolution */
  version: string;
}

/**
 * Event metadata for context and debugging
 */
export interface EventMetadata {
  /** User ID if applicable */
  userId?: string;
  
  /** Session ID for grouping related events */
  sessionId?: string;
  
  /** Request ID for tracing */
  requestId?: string;
  
  /** User agent for frontend events */
  userAgent?: string;
  
  /** IP address for security events */
  ipAddress?: string;
  
  /** Additional context */
  context?: Record<string, any>;
}

/**
 * Event sources - all services in the monorepo
 */
export enum EventSource {
  // Frontend services
  REACT_FRONTEND = 'react-frontend',
  VOICE_RECORDER = 'voice-recorder-component',
  CHAT_INTERFACE = 'chat-interface',
  
  // Backend services
  KOTLIN_BACKEND = 'kotlin-backend',
  CHAT_SERVICE = 'chat-service',
  USER_SERVICE = 'user-service',
  
  // AI/ML services
  WHISPER_TTS = 'whisper-tts-service',
  LLM_SERVICE = 'llm-service',
  
  // Infrastructure
  DATABASE = 'postgresql-database',
  REDIS_CACHE = 'redis-cache',
  MESSAGE_QUEUE = 'message-queue',
  
  // External integrations
  EXTERNAL_API = 'external-api',
  WEBHOOK = 'webhook',
  
  // System
  SYSTEM = 'system',
  HEALTH_CHECK = 'health-check',
  MONITORING = 'monitoring'
}

/**
 * Event severity levels
 */
export enum EventSeverity {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
  CRITICAL = 'critical'
}

/**
 * Event categories for organization
 */
export enum EventCategory {
  // User interactions
  USER_ACTION = 'user_action',
  USER_SESSION = 'user_session',
  
  // Voice and audio
  VOICE_RECORDING = 'voice_recording',
  AUDIO_PROCESSING = 'audio_processing',
  TRANSCRIPTION = 'transcription',
  
  // Chat and messaging
  CHAT_MESSAGE = 'chat_message',
  CHAT_SESSION = 'chat_session',
  
  // AI and ML
  LLM_REQUEST = 'llm_request',
  LLM_RESPONSE = 'llm_response',
  MODEL_INFERENCE = 'model_inference',
  
  // System events
  SYSTEM_STARTUP = 'system_startup',
  SYSTEM_SHUTDOWN = 'system_shutdown',
  HEALTH_CHECK = 'health_check',
  
  // Errors and debugging
  ERROR = 'error',
  PERFORMANCE = 'performance',
  SECURITY = 'security',
  
  // Business events
  FEATURE_USAGE = 'feature_usage',
  ANALYTICS = 'analytics'
}

// ============================================================================
// Specific Event Types
// ============================================================================

/**
 * Voice recording events
 */
export interface VoiceRecordingEvent extends BaseEvent {
  type: 'voice_recording_started' | 'voice_recording_stopped' | 'voice_recording_error';
  data: {
    sessionId: string;
    duration?: number; // milliseconds
    audioSize?: number; // bytes
    audioFormat?: string;
    error?: string;
  };
}

/**
 * Transcription events
 */
export interface TranscriptionEvent extends BaseEvent {
  type: 'transcription_started' | 'transcription_completed' | 'transcription_error';
  data: {
    sessionId: string;
    audioSize: number;
    transcriptionText?: string;
    language?: string;
    confidence?: number;
    processingTimeMs?: number;
    error?: string;
  };
}

/**
 * Chat events
 */
export interface ChatEvent extends BaseEvent {
  type: 'chat_message_sent' | 'chat_message_received' | 'chat_session_started' | 'chat_session_ended';
  data: {
    sessionId: string;
    messageId?: string;
    messageContent?: string;
    messageRole?: 'user' | 'assistant';
    messageSource?: 'text' | 'voice';
    processingTimeMs?: number;
  };
}

/**
 * LLM events
 */
export interface LLMEvent extends BaseEvent {
  type: 'llm_request_started' | 'llm_response_generated' | 'llm_error';
  data: {
    sessionId: string;
    prompt?: string;
    response?: string;
    model?: string;
    tokenCount?: number;
    processingTimeMs?: number;
    error?: string;
  };
}

/**
 * System events
 */
export interface SystemEvent extends BaseEvent {
  type: 'service_started' | 'service_stopped' | 'health_check' | 'performance_metric';
  data: {
    serviceName: string;
    serviceVersion?: string;
    healthStatus?: 'healthy' | 'unhealthy' | 'degraded';
    metrics?: Record<string, number>;
    error?: string;
  };
}

/**
 * Error events
 */
export interface ErrorEvent extends BaseEvent {
  type: 'error_occurred' | 'exception_thrown' | 'validation_failed';
  data: {
    errorType: string;
    errorMessage: string;
    errorStack?: string;
    errorCode?: string;
    context?: Record<string, any>;
  };
}

/**
 * User action events
 */
export interface UserActionEvent extends BaseEvent {
  type: 'button_clicked' | 'page_viewed' | 'feature_used' | 'setting_changed';
  data: {
    actionType: string;
    elementId?: string;
    pagePath?: string;
    featureName?: string;
    settingName?: string;
    settingValue?: any;
  };
}

// ============================================================================
// Event Union Types
// ============================================================================

/**
 * All possible event types
 */
export type UnhingedEvent = 
  | VoiceRecordingEvent
  | TranscriptionEvent
  | ChatEvent
  | LLMEvent
  | SystemEvent
  | ErrorEvent
  | UserActionEvent;

/**
 * Event type mapping for type safety
 */
export interface EventTypeMap {
  // Voice recording
  'voice_recording_started': VoiceRecordingEvent;
  'voice_recording_stopped': VoiceRecordingEvent;
  'voice_recording_error': VoiceRecordingEvent;
  
  // Transcription
  'transcription_started': TranscriptionEvent;
  'transcription_completed': TranscriptionEvent;
  'transcription_error': TranscriptionEvent;
  
  // Chat
  'chat_message_sent': ChatEvent;
  'chat_message_received': ChatEvent;
  'chat_session_started': ChatEvent;
  'chat_session_ended': ChatEvent;
  
  // LLM
  'llm_request_started': LLMEvent;
  'llm_response_generated': LLMEvent;
  'llm_error': LLMEvent;
  
  // System
  'service_started': SystemEvent;
  'service_stopped': SystemEvent;
  'health_check': SystemEvent;
  'performance_metric': SystemEvent;
  
  // Errors
  'error_occurred': ErrorEvent;
  'exception_thrown': ErrorEvent;
  'validation_failed': ErrorEvent;
  
  // User actions
  'button_clicked': UserActionEvent;
  'page_viewed': UserActionEvent;
  'feature_used': UserActionEvent;
  'setting_changed': UserActionEvent;
}

/**
 * Event handler function type
 */
export type EventHandler<T extends UnhingedEvent = UnhingedEvent> = (event: T) => void | Promise<void>;

/**
 * Event filter function type
 */
export type EventFilter<T extends UnhingedEvent = UnhingedEvent> = (event: T) => boolean;
