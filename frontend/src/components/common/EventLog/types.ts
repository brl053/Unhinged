// ============================================================================
// EventLog Types - Type Definitions for Event Log Component
// ============================================================================
//
// @file types.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Type definitions for real-time event log viewer
//
// Etymology: Greek "typos" = impression, form
// Methodology: TypeScript interface design with semantic naming
// ============================================================================

/**
 * Core event structure from CDC events
 * Represents a single event in the system
 */
export interface Event {
  /** Unique identifier for the event */
  event_id: string;
  
  /** Type/category of the event */
  event_type: string;
  
  /** Timestamp in milliseconds when event occurred */
  timestamp_ms: number;
  
  /** User ID associated with the event */
  user_id: string;
  
  /** Session ID for grouping related events */
  session_id: string;
  
  /** Event payload data (flexible structure) */
  payload: any;
  
  /** ISO timestamp when event was created */
  created_at: string;
}

/**
 * WebSocket connection states
 * Tracks the real-time connection status
 */
export type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'error';

/**
 * Event log component props
 * Configuration options for the EventLog component
 */
export interface EventLogProps {
  /** Maximum number of events to keep in memory */
  maxEvents?: number;
  
  /** Whether to auto-scroll to new events */
  autoScroll?: boolean;
  
  /** Initial filter value */
  initialFilter?: string;
  
  /** Custom WebSocket URL (defaults to current host) */
  wsUrl?: string;
  
  /** Custom API endpoint for initial events */
  apiEndpoint?: string;
  
  /** Whether to show event metadata */
  showMetadata?: boolean;
  
  /** Whether to show event payload */
  showPayload?: boolean;
  
  /** Custom event type colors */
  eventTypeColors?: Record<string, string>;
  
  /** Callback when events are updated */
  onEventsUpdate?: (events: Event[]) => void;
  
  /** Callback when connection status changes */
  onConnectionChange?: (status: ConnectionStatus) => void;
}

/**
 * Event log state interface
 * Internal state management for the component
 */
export interface EventLogState {
  /** Array of events to display */
  events: Event[];
  
  /** Current WebSocket connection status */
  connectionStatus: ConnectionStatus;
  
  /** Current filter string */
  filter: string;
  
  /** Whether auto-scroll is enabled */
  autoScroll: boolean;
  
  /** Whether the component is loading initial data */
  isLoading: boolean;
  
  /** Any error that occurred */
  error: string | null;
  
  /** Number of filtered events */
  filteredCount: number;
  
  /** Total number of events */
  totalCount: number;
}

/**
 * Event filter options
 * Configuration for filtering events
 */
export interface EventFilter {
  /** Text to search for in event content */
  searchTerm?: string;
  
  /** Specific event types to include */
  eventTypes?: string[];
  
  /** User IDs to filter by */
  userIds?: string[];
  
  /** Session IDs to filter by */
  sessionIds?: string[];
  
  /** Date range for filtering */
  dateRange?: {
    start: Date;
    end: Date;
  };
  
  /** Whether to include payload in search */
  includePayload?: boolean;
}

/**
 * Event formatting options
 * Configuration for how events are displayed
 */
export interface EventFormatOptions {
  /** How to format timestamps */
  timestampFormat?: 'relative' | 'absolute' | 'iso';
  
  /** Whether to show milliseconds in timestamps */
  showMilliseconds?: boolean;
  
  /** How to format JSON payload */
  jsonIndentation?: number;
  
  /** Maximum length for truncated fields */
  maxFieldLength?: number;
  
  /** Whether to syntax highlight JSON */
  syntaxHighlight?: boolean;
}

/**
 * WebSocket message types
 * Different types of messages received via WebSocket
 */
export interface WebSocketMessage {
  /** Type of message */
  type: 'event' | 'heartbeat' | 'error' | 'status';
  
  /** Message payload */
  data: any;
  
  /** Timestamp when message was sent */
  timestamp: number;
}

/**
 * Event log metrics
 * Performance and usage metrics
 */
export interface EventLogMetrics {
  /** Total events received */
  totalEvents: number;

  /** Events per second rate */
  eventsPerSecond: number;

  /** WebSocket connection uptime */
  connectionUptime: number;

  /** Number of reconnection attempts */
  reconnectionAttempts: number;

  /** Average event processing time */
  averageProcessingTime: number;

  /** Memory usage for stored events */
  memoryUsage: number;

  /** Performance warnings */
  warnings?: string[];
}

/**
 * Event log hooks return type
 * Type for custom hooks used by the component
 */
export interface UseEventLogReturn {
  /** Current event log state */
  state: EventLogState;
  
  /** Actions to modify state */
  actions: {
    /** Set filter string */
    setFilter: (filter: string) => void;
    
    /** Toggle auto-scroll */
    toggleAutoScroll: () => void;
    
    /** Clear all events */
    clearEvents: () => void;
    
    /** Refresh events from API */
    refreshEvents: () => Promise<void>;
    
    /** Connect to WebSocket */
    connect: () => void;
    
    /** Disconnect from WebSocket */
    disconnect: () => void;
  };
  
  /** Filtered events based on current filter */
  filteredEvents: Event[];
  
  /** Current metrics */
  metrics: EventLogMetrics;
}

/**
 * Event log context type
 * Context for sharing event log state
 */
export interface EventLogContextType {
  /** Current events */
  events: Event[];
  
  /** Add new event */
  addEvent: (event: Event) => void;
  
  /** Clear all events */
  clearEvents: () => void;
  
  /** Current connection status */
  connectionStatus: ConnectionStatus;
  
  /** Subscribe to event updates */
  subscribe: (callback: (events: Event[]) => void) => () => void;
}

/**
 * Event type metadata
 * Information about different event types
 */
export interface EventTypeMetadata {
  /** Display name for the event type */
  displayName: string;
  
  /** Color for visual representation */
  color: string;
  
  /** Icon or emoji for the event type */
  icon?: string;
  
  /** Description of what this event type represents */
  description?: string;
  
  /** Priority level for sorting/filtering */
  priority?: 'low' | 'medium' | 'high' | 'critical';
  
  /** Whether this event type should be highlighted */
  highlight?: boolean;
}

/**
 * Event log configuration
 * Global configuration for event log behavior
 */
export interface EventLogConfig {
  /** Default maximum events to keep */
  defaultMaxEvents: number;
  
  /** WebSocket reconnection settings */
  reconnection: {
    /** Maximum number of reconnection attempts */
    maxAttempts: number;
    
    /** Delay between reconnection attempts (ms) */
    delay: number;
    
    /** Whether to use exponential backoff */
    exponentialBackoff: boolean;
  };
  
  /** Performance settings */
  performance: {
    /** Batch size for processing events */
    batchSize: number;
    
    /** Debounce delay for filter updates (ms) */
    filterDebounce: number;
    
    /** Virtual scrolling threshold */
    virtualScrollThreshold: number;
  };
  
  /** UI settings */
  ui: {
    /** Default timestamp format */
    timestampFormat: EventFormatOptions['timestampFormat'];
    
    /** Default JSON indentation */
    jsonIndentation: number;
    
    /** Whether to show event metadata by default */
    showMetadata: boolean;
  };
}
