// ============================================================================
// EventLog Constants - Configuration and Static Values
// ============================================================================
//
// @file constants.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Constants for event log component configuration
//
// Etymology: Latin "constans" = standing firm, unchanging
// Methodology: Centralized configuration with semantic organization
// ============================================================================

import { EventLogConfig, EventTypeMetadata, ConnectionStatus } from './types';

/**
 * Default configuration values for event log
 * Etymology: "default" = standard, typical configuration
 */
export const DEFAULT_CONFIG: EventLogConfig = {
  defaultMaxEvents: 1000,
  
  reconnection: {
    maxAttempts: 5,
    delay: 3000,
    exponentialBackoff: true,
  },
  
  performance: {
    batchSize: 50,
    filterDebounce: 300,
    virtualScrollThreshold: 500,
  },
  
  ui: {
    timestampFormat: 'absolute',
    jsonIndentation: 2,
    showMetadata: true,
  },
} as const;

/**
 * WebSocket configuration
 * Settings for real-time event streaming
 */
export const WEBSOCKET_CONFIG = {
  /** Default WebSocket path */
  DEFAULT_PATH: '/api/events/stream',
  
  /** Heartbeat interval (ms) */
  HEARTBEAT_INTERVAL: 30000,
  
  /** Connection timeout (ms) */
  CONNECTION_TIMEOUT: 10000,
  
  /** Maximum message size (bytes) */
  MAX_MESSAGE_SIZE: 1024 * 1024, // 1MB
  
  /** Reconnection delays (ms) */
  RECONNECTION_DELAYS: [1000, 2000, 4000, 8000, 16000],
} as const;

/**
 * Event type metadata and styling
 * Visual representation for different event types
 */
export const EVENT_TYPE_METADATA: Record<string, EventTypeMetadata> = {
  // System events
  'system.startup': {
    displayName: 'System Startup',
    color: '#10b981', // green
    icon: '🚀',
    description: 'System initialization and startup',
    priority: 'high',
  },
  
  'system.shutdown': {
    displayName: 'System Shutdown',
    color: '#ef4444', // red
    icon: '🛑',
    description: 'System shutdown and cleanup',
    priority: 'high',
  },
  
  'system.error': {
    displayName: 'System Error',
    color: '#dc2626', // red
    icon: '❌',
    description: 'System-level errors and exceptions',
    priority: 'critical',
    highlight: true,
  },
  
  // User events
  'user.login': {
    displayName: 'User Login',
    color: '#3b82f6', // blue
    icon: '🔐',
    description: 'User authentication and login',
    priority: 'medium',
  },
  
  'user.logout': {
    displayName: 'User Logout',
    color: '#6b7280', // gray
    icon: '🚪',
    description: 'User logout and session termination',
    priority: 'medium',
  },
  
  'user.action': {
    displayName: 'User Action',
    color: '#8b5cf6', // purple
    icon: '👤',
    description: 'User-initiated actions and interactions',
    priority: 'low',
  },
  
  // LLM events
  'llm.request': {
    displayName: 'LLM Request',
    color: '#f59e0b', // amber
    icon: '🧠',
    description: 'LLM inference requests',
    priority: 'medium',
  },
  
  'llm.response': {
    displayName: 'LLM Response',
    color: '#10b981', // green
    icon: '💭',
    description: 'LLM inference responses',
    priority: 'medium',
  },
  
  'llm.error': {
    displayName: 'LLM Error',
    color: '#ef4444', // red
    icon: '🚨',
    description: 'LLM processing errors',
    priority: 'high',
    highlight: true,
  },
  
  // Audio events
  'audio.record.start': {
    displayName: 'Recording Started',
    color: '#ec4899', // pink
    icon: '🎤',
    description: 'Audio recording started',
    priority: 'medium',
  },
  
  'audio.record.stop': {
    displayName: 'Recording Stopped',
    color: '#6b7280', // gray
    icon: '⏹️',
    description: 'Audio recording stopped',
    priority: 'medium',
  },
  
  'audio.transcription': {
    displayName: 'Transcription',
    color: '#14b8a6', // teal
    icon: '📝',
    description: 'Audio transcription completed',
    priority: 'medium',
  },
  
  // Chat events
  'chat.message.sent': {
    displayName: 'Message Sent',
    color: '#3b82f6', // blue
    icon: '💬',
    description: 'Chat message sent by user',
    priority: 'low',
  },
  
  'chat.message.received': {
    displayName: 'Message Received',
    color: '#10b981', // green
    icon: '📨',
    description: 'Chat message received from AI',
    priority: 'low',
  },
  
  // Session events
  'session.created': {
    displayName: 'Session Created',
    color: '#8b5cf6', // purple
    icon: '🆕',
    description: 'New session created',
    priority: 'medium',
  },
  
  'session.ended': {
    displayName: 'Session Ended',
    color: '#6b7280', // gray
    icon: '🏁',
    description: 'Session terminated',
    priority: 'medium',
  },
  
  // Default fallback
  'unknown': {
    displayName: 'Unknown Event',
    color: '#6b7280', // gray
    icon: '❓',
    description: 'Unrecognized event type',
    priority: 'low',
  },
} as const;

/**
 * Connection status metadata
 * Visual representation for connection states
 */
export const CONNECTION_STATUS_METADATA: Record<ConnectionStatus, {
  label: string;
  color: string;
  icon: string;
}> = {
  connected: {
    label: 'Connected',
    color: '#10b981', // green
    icon: '🟢',
  },
  
  disconnected: {
    label: 'Disconnected',
    color: '#ef4444', // red
    icon: '🔴',
  },
  
  connecting: {
    label: 'Connecting...',
    color: '#f59e0b', // amber
    icon: '🟡',
  },
  
  error: {
    label: 'Connection Error',
    color: '#dc2626', // red
    icon: '🚨',
  },
} as const;

/**
 * Filter presets for common event filtering scenarios
 * Predefined filters for quick access
 */
export const FILTER_PRESETS = {
  errors: {
    name: 'Errors Only',
    filter: 'error',
    description: 'Show only error events',
  },
  
  llm: {
    name: 'LLM Events',
    filter: 'llm.',
    description: 'Show LLM-related events',
  },
  
  audio: {
    name: 'Audio Events',
    filter: 'audio.',
    description: 'Show audio-related events',
  },
  
  user: {
    name: 'User Actions',
    filter: 'user.',
    description: 'Show user-initiated events',
  },
  
  system: {
    name: 'System Events',
    filter: 'system.',
    description: 'Show system-level events',
  },
  
  recent: {
    name: 'Last 5 Minutes',
    filter: '',
    description: 'Show events from last 5 minutes',
  },
} as const;

/**
 * Event log CSS class names
 * Consistent naming for styling event log components
 */
export const EVENT_LOG_CLASSES = {
  container: 'event-log',
  header: 'event-log__header',
  title: 'event-log__title',
  controls: 'event-log__controls',
  connectionStatus: 'event-log__connection-status',
  filterInput: 'event-log__filter-input',
  autoScrollToggle: 'event-log__auto-scroll-toggle',
  clearButton: 'event-log__clear-button',
  eventCount: 'event-log__event-count',
  eventContainer: 'event-log__event-container',
  noEvents: 'event-log__no-events',
  eventItem: 'event-log__event-item',
  eventHeader: 'event-log__event-header',
  eventType: 'event-log__event-type',
  eventTimestamp: 'event-log__event-timestamp',
  eventId: 'event-log__event-id',
  eventMetadata: 'event-log__event-metadata',
  eventPayload: 'event-log__event-payload',
  jsonPayload: 'event-log__json-payload',
  loadingSpinner: 'event-log__loading-spinner',
  errorMessage: 'event-log__error-message',
} as const;

/**
 * Event log data attributes
 * For testing and debugging purposes
 */
export const EVENT_LOG_DATA_ATTRIBUTES = {
  eventId: 'data-event-id',
  eventType: 'data-event-type',
  connectionStatus: 'data-connection-status',
  filteredCount: 'data-filtered-count',
  totalCount: 'data-total-count',
  autoScroll: 'data-auto-scroll',
  hasFilter: 'data-has-filter',
} as const;

/**
 * Performance thresholds for monitoring
 * Thresholds for performance alerts and optimization
 */
export const PERFORMANCE_THRESHOLDS = {
  /** Maximum events before performance warning */
  maxEventsWarning: 5000,
  
  /** Maximum events before forced cleanup */
  maxEventsLimit: 10000,
  
  /** Maximum WebSocket message processing time (ms) */
  maxProcessingTime: 100,
  
  /** Maximum filter processing time (ms) */
  maxFilterTime: 50,
  
  /** Maximum memory usage (MB) */
  maxMemoryUsage: 100,
  
  /** Events per second threshold for rate limiting */
  maxEventsPerSecond: 100,
} as const;

/**
 * Keyboard shortcuts for event log interactions
 * Accessibility and power user features
 */
export const KEYBOARD_SHORTCUTS = {
  clearEvents: 'Ctrl+K',
  toggleAutoScroll: 'Ctrl+A',
  focusFilter: 'Ctrl+F',
  refresh: 'Ctrl+R',
  togglePayload: 'Space',
  scrollToTop: 'Home',
  scrollToBottom: 'End',
} as const;

/**
 * Local storage keys for persisting user preferences
 * Keys for storing event log settings
 */
export const STORAGE_KEYS = {
  autoScroll: 'unhinged:event-log:auto-scroll',
  filter: 'unhinged:event-log:filter',
  showMetadata: 'unhinged:event-log:show-metadata',
  showPayload: 'unhinged:event-log:show-payload',
  timestampFormat: 'unhinged:event-log:timestamp-format',
  maxEvents: 'unhinged:event-log:max-events',
} as const;
