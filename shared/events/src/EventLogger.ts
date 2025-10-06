// ============================================================================
// Unhinged Event Library - Event Logger
// ============================================================================
//
// @file EventLogger.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Centralized event logging system for the monorepo
//
// This logger provides:
// - Type-safe event logging
// - Multiple output destinations (console, database, file, etc.)
// - Event filtering and transformation
// - Performance monitoring
// - Error handling and retry logic
// ============================================================================

import {
  UnhingedEvent,
  EventSource,
  EventSeverity,
  EventHandler,
  EventFilter,
  EventMetadata
} from './types';

/**
 * Event logger configuration
 */
export interface EventLoggerConfig {
  /** Service name for event source */
  serviceName: EventSource;
  
  /** Default metadata to include in all events */
  defaultMetadata?: Partial<EventMetadata>;
  
  /** Enable console logging */
  enableConsole?: boolean;
  
  /** Enable database logging */
  enableDatabase?: boolean;
  
  /** Database connection config */
  databaseConfig?: {
    host: string;
    port: number;
    database: string;
    user: string;
    password: string;
  };
  
  /** Enable file logging */
  enableFile?: boolean;
  
  /** File logging path */
  filePath?: string;
  
  /** Minimum severity level to log */
  minSeverity?: EventSeverity;
  
  /** Maximum events to buffer before flushing */
  bufferSize?: number;
  
  /** Flush interval in milliseconds */
  flushInterval?: number;
}

/**
 * Event destination interface
 */
export interface EventDestination {
  name: string;
  write(event: UnhingedEvent): Promise<void>;
  flush?(): Promise<void>;
  close?(): Promise<void>;
}

/**
 * Console event destination
 */
export class ConsoleDestination implements EventDestination {
  name = 'console';
  
  async write(event: UnhingedEvent): Promise<void> {
    const timestamp = new Date(event.timestamp).toISOString();
    const severity = this.getSeverity(event);
    
    const logMessage = `[${timestamp}] ${severity} ${event.source}:${event.type}`;
    const logData = {
      id: event.id,
      data: event.data,
      metadata: event.metadata
    };
    
    switch (severity) {
      case EventSeverity.ERROR:
      case EventSeverity.CRITICAL:
        console.error(logMessage, logData);
        break;
      case EventSeverity.WARN:
        console.warn(logMessage, logData);
        break;
      case EventSeverity.DEBUG:
        console.debug(logMessage, logData);
        break;
      default:
        console.log(logMessage, logData);
    }
  }
  
  private getSeverity(event: UnhingedEvent): EventSeverity {
    if (event.type.includes('error') || event.type.includes('exception')) {
      return EventSeverity.ERROR;
    }
    if (event.type.includes('warn') || event.type.includes('failed')) {
      return EventSeverity.WARN;
    }
    if (event.type.includes('debug')) {
      return EventSeverity.DEBUG;
    }
    return EventSeverity.INFO;
  }
}

/**
 * Database event destination
 */
export class DatabaseDestination implements EventDestination {
  name = 'database';
  private client: any = null;
  
  constructor(private config: NonNullable<EventLoggerConfig['databaseConfig']>) {}
  
  async connect(): Promise<void> {
    if (this.client) return;
    
    try {
      // Dynamic import to avoid requiring pg in environments that don't need it
      const pg = await import('pg');
      this.client = new pg.Client(this.config);
      await this.client.connect();
    } catch (error) {
      console.error('Failed to connect to database for event logging:', error);
      throw error;
    }
  }
  
  async write(event: UnhingedEvent): Promise<void> {
    if (!this.client) {
      await this.connect();
    }
    
    try {
      await this.client.query(`
        INSERT INTO events (id, event_type, event_data, source, created_at, metadata)
        VALUES ($1, $2, $3, $4, $5, $6)
      `, [
        event.id,
        event.type,
        JSON.stringify(event.data),
        event.source,
        event.timestamp,
        JSON.stringify(event.metadata || {})
      ]);
    } catch (error) {
      console.error('Failed to write event to database:', error);
      // Don't throw - we don't want event logging to break the application
    }
  }
  
  async close(): Promise<void> {
    if (this.client) {
      await this.client.end();
      this.client = null;
    }
  }
}

/**
 * File event destination
 */
export class FileDestination implements EventDestination {
  name = 'file';
  private writeStream: any = null;
  
  constructor(private filePath: string) {}
  
  async write(event: UnhingedEvent): Promise<void> {
    if (!this.writeStream) {
      const fs = await import('fs');
      this.writeStream = fs.createWriteStream(this.filePath, { flags: 'a' });
    }
    
    const logLine = JSON.stringify(event) + '\n';
    this.writeStream.write(logLine);
  }
  
  async flush(): Promise<void> {
    if (this.writeStream) {
      return new Promise((resolve) => {
        this.writeStream.flush(resolve);
      });
    }
  }
  
  async close(): Promise<void> {
    if (this.writeStream) {
      return new Promise((resolve) => {
        this.writeStream.end(resolve);
      });
    }
  }
}

/**
 * Main event logger class
 */
export class EventLogger {
  private destinations: EventDestination[] = [];
  private handlers: Map<string, EventHandler[]> = new Map();
  private filters: EventFilter[] = [];
  private eventBuffer: UnhingedEvent[] = [];
  private flushTimer: NodeJS.Timeout | null = null;
  
  constructor(private config: EventLoggerConfig) {
    this.setupDestinations();
    this.setupFlushTimer();
  }
  
  private setupDestinations(): void {
    if (this.config.enableConsole !== false) {
      this.destinations.push(new ConsoleDestination());
    }
    
    if (this.config.enableDatabase && this.config.databaseConfig) {
      this.destinations.push(new DatabaseDestination(this.config.databaseConfig));
    }
    
    if (this.config.enableFile && this.config.filePath) {
      this.destinations.push(new FileDestination(this.config.filePath));
    }
  }
  
  private setupFlushTimer(): void {
    const interval = this.config.flushInterval || 5000; // 5 seconds default
    this.flushTimer = setInterval(() => {
      this.flush().catch(console.error);
    }, interval);
  }
  
  /**
   * Log an event
   */
  async logEvent<T extends UnhingedEvent>(
    type: T['type'],
    data: T['data'],
    metadata?: Partial<EventMetadata>
  ): Promise<void> {
    const event: UnhingedEvent = {
      id: this.generateEventId(),
      type,
      timestamp: new Date().toISOString(),
      source: this.config.serviceName,
      data,
      metadata: { ...this.config.defaultMetadata, ...metadata },
      version: '1.0.0'
    } as T;
    
    // Apply filters
    if (!this.shouldLogEvent(event)) {
      return;
    }
    
    // Add to buffer
    this.eventBuffer.push(event);
    
    // Trigger handlers
    await this.triggerHandlers(event);
    
    // Flush if buffer is full
    if (this.eventBuffer.length >= (this.config.bufferSize || 100)) {
      await this.flush();
    }
  }
  
  /**
   * Convenience methods for specific event types
   */
  async logVoiceRecording(
    type: 'voice_recording_started' | 'voice_recording_stopped' | 'voice_recording_error',
    data: { sessionId: string; duration?: number; audioSize?: number; audioFormat?: string; error?: string },
    metadata?: Partial<EventMetadata>
  ): Promise<void> {
    await this.logEvent(type, data, metadata);
  }
  
  async logTranscription(
    type: 'transcription_started' | 'transcription_completed' | 'transcription_error',
    data: { sessionId: string; audioSize: number; transcriptionText?: string; language?: string; confidence?: number; processingTimeMs?: number; error?: string },
    metadata?: Partial<EventMetadata>
  ): Promise<void> {
    await this.logEvent(type, data, metadata);
  }
  
  async logChat(
    type: 'chat_message_sent' | 'chat_message_received' | 'chat_session_started' | 'chat_session_ended',
    data: { sessionId: string; messageId?: string; messageContent?: string; messageRole?: 'user' | 'assistant'; messageSource?: 'text' | 'voice'; processingTimeMs?: number },
    metadata?: Partial<EventMetadata>
  ): Promise<void> {
    await this.logEvent(type, data, metadata);
  }
  
  async logError(
    type: 'error_occurred' | 'exception_thrown' | 'validation_failed',
    data: { errorType: string; errorMessage: string; errorStack?: string; errorCode?: string; context?: Record<string, any> },
    metadata?: Partial<EventMetadata>
  ): Promise<void> {
    await this.logEvent(type, data, metadata);
  }
  
  /**
   * Add event handler
   */
  onEvent<T extends UnhingedEvent>(eventType: T['type'], handler: EventHandler<T>): void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, []);
    }
    this.handlers.get(eventType)!.push(handler as EventHandler);
  }
  
  /**
   * Add event filter
   */
  addFilter(filter: EventFilter): void {
    this.filters.push(filter);
  }
  
  /**
   * Flush buffered events
   */
  async flush(): Promise<void> {
    if (this.eventBuffer.length === 0) return;
    
    const eventsToFlush = [...this.eventBuffer];
    this.eventBuffer = [];
    
    await Promise.all(
      this.destinations.map(async (destination) => {
        try {
          for (const event of eventsToFlush) {
            await destination.write(event);
          }
          if (destination.flush) {
            await destination.flush();
          }
        } catch (error) {
          console.error(`Failed to flush events to ${destination.name}:`, error);
        }
      })
    );
  }
  
  /**
   * Close logger and cleanup resources
   */
  async close(): Promise<void> {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }
    
    await this.flush();
    
    await Promise.all(
      this.destinations.map(async (destination) => {
        if (destination.close) {
          await destination.close();
        }
      })
    );
  }
  
  private generateEventId(): string {
    return `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  private shouldLogEvent(event: UnhingedEvent): boolean {
    return this.filters.every(filter => filter(event));
  }
  
  private async triggerHandlers(event: UnhingedEvent): Promise<void> {
    const handlers = this.handlers.get(event.type) || [];
    await Promise.all(
      handlers.map(async (handler) => {
        try {
          await handler(event);
        } catch (error) {
          console.error(`Event handler failed for ${event.type}:`, error);
        }
      })
    );
  }
}

/**
 * Create a configured event logger instance
 */
export function createEventLogger(config: EventLoggerConfig): EventLogger {
  return new EventLogger(config);
}
