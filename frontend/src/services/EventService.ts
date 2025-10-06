// ============================================================================
// Frontend Event Service - Centralized Event Logging
// ============================================================================
//
// @file EventService.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Frontend event logging service using the centralized event library
//
// This service provides:
// - Centralized event logging for the React frontend
// - Voice recording event tracking
// - User interaction analytics
// - Error tracking and debugging
// - Performance monitoring
// ============================================================================

// Browser-compatible event types (subset of @unhinged/events)
enum EventSource {
  REACT_FRONTEND = 'react-frontend',
  VOICE_RECORDER = 'voice-recorder-component'
}

/**
 * Browser event logger with PostgreSQL persistence
 * Sends ALL events to Event API Server for OLTP persistence
 */
class BrowserEventLogger {
  private eventBuffer: any[] = [];
  private flushTimer: NodeJS.Timeout | null = null;
  private eventApiUrl = 'http://localhost:8084/events';

  constructor() {
    this.setupFlushTimer();
  }

  private setupFlushTimer(): void {
    this.flushTimer = setInterval(() => {
      this.flush().catch(console.error);
    }, 2000); // Flush every 2 seconds for better OLTP
  }

  async logEvent(type: string, data: any, metadata?: any): Promise<void> {
    const event = {
      id: this.generateEventId(),
      type,
      timestamp: new Date().toISOString(),
      source: EventSource.REACT_FRONTEND,
      data,
      metadata: {
        userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
        pathname: typeof window !== 'undefined' ? window.location.pathname : 'unknown',
        url: typeof window !== 'undefined' ? window.location.href : 'unknown',
        timestamp: new Date().toISOString(),
        ...metadata
      },
      version: '1.0.0'
    };

    // Log to console for immediate debugging
    console.log(`[EVENT] ${event.type}:`, event);

    // Add to buffer for PostgreSQL persistence
    this.eventBuffer.push(event);

    // Immediate flush for critical events
    if (type.includes('error') || type.includes('exception')) {
      await this.flush();
    }

    // Auto-flush when buffer gets large
    if (this.eventBuffer.length >= 10) {
      await this.flush();
    }
  }

  async flush(): Promise<void> {
    if (this.eventBuffer.length === 0) return;

    const eventsToSend = [...this.eventBuffer];
    this.eventBuffer = [];

    try {
      console.log(`[EVENT FLUSH] Persisting ${eventsToSend.length} events to PostgreSQL...`);

      const response = await fetch(this.eventApiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(eventsToSend)
      });

      if (response.ok) {
        const result = await response.json();
        console.log(`✅ [EVENT FLUSH] Persisted ${result.persisted}/${result.processed} events to PostgreSQL`);
      } else {
        console.error(`❌ [EVENT FLUSH] Failed to persist events:`, response.status, response.statusText);
        // Re-add events to buffer for retry
        this.eventBuffer.unshift(...eventsToSend);
      }
    } catch (error) {
      console.error('❌ [EVENT FLUSH] Network error persisting events:', error);
      // Re-add events to buffer for retry
      this.eventBuffer.unshift(...eventsToSend);
    }
  }

  async close(): Promise<void> {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }
    await this.flush();
  }

  private generateEventId(): string {
    return `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

const eventLogger = new BrowserEventLogger();

/**
 * Frontend Event Service Class
 * Provides convenient methods for logging frontend-specific events
 */
export class FrontendEventService {
  private static instance: FrontendEventService;
  private sessionId: string;
  
  private constructor() {
    this.sessionId = this.generateSessionId();
    this.setupEventHandlers();
  }
  
  public static getInstance(): FrontendEventService {
    if (!FrontendEventService.instance) {
      FrontendEventService.instance = new FrontendEventService();
    }
    return FrontendEventService.instance;
  }
  
  /**
   * Voice Recording Events
   */
  async logVoiceRecordingStarted(audioFormat?: string): Promise<void> {
    await eventLogger.logEvent('voice_recording_started', {
      sessionId: this.sessionId,
      audioFormat: audioFormat || 'unknown'
    }, {
      sessionId: this.sessionId
    });
  }
  
  async logVoiceRecordingStopped(duration: number, audioSize: number, audioFormat?: string): Promise<void> {
    await eventLogger.logEvent('voice_recording_stopped', {
      sessionId: this.sessionId,
      duration,
      audioSize,
      audioFormat: audioFormat || 'unknown'
    }, {
      sessionId: this.sessionId
    });
  }

  async logVoiceRecordingError(error: string): Promise<void> {
    await eventLogger.logEvent('voice_recording_error', {
      sessionId: this.sessionId,
      error
    }, {
      sessionId: this.sessionId
    });
  }
  
  /**
   * Transcription Events
   */
  async logTranscriptionStarted(audioSize: number): Promise<void> {
    await eventLogger.logEvent('transcription_started', {
      sessionId: this.sessionId,
      audioSize
    }, {
      sessionId: this.sessionId
    });
  }

  async logTranscriptionCompleted(
    audioSize: number,
    transcriptionText: string,
    language: string,
    processingTimeMs: number,
    confidence?: number
  ): Promise<void> {
    await eventLogger.logEvent('transcription_completed', {
      sessionId: this.sessionId,
      audioSize,
      transcriptionText,
      language,
      confidence,
      processingTimeMs
    }, {
      sessionId: this.sessionId
    });
  }

  async logTranscriptionError(audioSize: number, error: string): Promise<void> {
    await eventLogger.logEvent('transcription_error', {
      sessionId: this.sessionId,
      audioSize,
      error
    }, {
      sessionId: this.sessionId
    });
  }
  
  /**
   * Chat Events
   */
  async logChatMessageSent(messageContent: string, messageSource: 'text' | 'voice'): Promise<void> {
    await eventLogger.logEvent('chat_message_sent', {
      sessionId: this.sessionId,
      messageId: this.generateMessageId(),
      messageContent: messageContent.substring(0, 100), // Truncate for privacy
      messageRole: 'user',
      messageSource
    }, {
      sessionId: this.sessionId
    });
  }

  async logChatMessageReceived(messageContent: string, processingTimeMs?: number): Promise<void> {
    await eventLogger.logEvent('chat_message_received', {
      sessionId: this.sessionId,
      messageId: this.generateMessageId(),
      messageContent: messageContent.substring(0, 100), // Truncate for privacy
      messageRole: 'assistant',
      processingTimeMs
    }, {
      sessionId: this.sessionId
    });
  }

  async logChatSessionStarted(): Promise<void> {
    await eventLogger.logEvent('chat_session_started', {
      sessionId: this.sessionId
    }, {
      sessionId: this.sessionId
    });
  }
  
  /**
   * User Action Events
   */
  async logButtonClick(elementId: string, actionType: string): Promise<void> {
    await eventLogger.logEvent('button_clicked', {
      actionType,
      elementId
    }, {
      sessionId: this.sessionId
    });
  }

  async logPageView(pagePath: string): Promise<void> {
    await eventLogger.logEvent('page_viewed', {
      actionType: 'page_view',
      pagePath
    }, {
      sessionId: this.sessionId
    });
  }

  async logFeatureUsed(featureName: string): Promise<void> {
    await eventLogger.logEvent('feature_used', {
      actionType: 'feature_usage',
      featureName
    }, {
      sessionId: this.sessionId
    });
  }

  /**
   * Prompt Surgery Events
   */
  async logPromptSurgeryStarted(sourceCount: number, initialLength: number): Promise<void> {
    await eventLogger.logEvent('prompt_surgery_started', {
      sourceCount,
      initialLength
    }, {
      sessionId: this.sessionId
    });
  }

  async logPromptSurgeryCompleted(finalLength: number, sourceCount: number, wordCount: number): Promise<void> {
    await eventLogger.logEvent('prompt_surgery_completed', {
      finalLength,
      sourceCount,
      wordCount
    }, {
      sessionId: this.sessionId
    });
  }

  async logPromptEnhancement(originalLength: number, enhancedLength: number, processingTimeMs: number): Promise<void> {
    await eventLogger.logEvent('prompt_enhancement_completed', {
      originalLength,
      enhancedLength,
      processingTimeMs
    }, {
      sessionId: this.sessionId
    });
  }

  /**
   * Error Events
   */
  async logError(errorType: string, errorMessage: string, errorStack?: string, context?: Record<string, any>): Promise<void> {
    await eventLogger.logEvent('error_occurred', {
      errorType,
      errorMessage,
      errorStack,
      context
    }, {
      sessionId: this.sessionId
    });
  }

  async logException(error: Error, context?: Record<string, any>): Promise<void> {
    await eventLogger.logEvent('exception_thrown', {
      errorType: error.name,
      errorMessage: error.message,
      errorStack: error.stack,
      context
    }, {
      sessionId: this.sessionId
    });
  }
  
  /**
   * Performance Events
   */
  async logPerformanceMetric(metricName: string, value: number, unit: string): Promise<void> {
    await eventLogger.logEvent('performance_metric', {
      serviceName: 'react-frontend',
      metrics: {
        [metricName]: value
      }
    }, {
      sessionId: this.sessionId,
      context: { unit }
    });
  }
  
  /**
   * Utility Methods
   */
  getSessionId(): string {
    return this.sessionId;
  }
  
  async flush(): Promise<void> {
    await eventLogger.flush();
  }
  
  async close(): Promise<void> {
    await eventLogger.close();
  }
  
  /**
   * Private Methods
   */
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  private setupEventHandlers(): void {
    // Log session start
    this.logChatSessionStarted().catch(console.error);
    
    // Log page view
    if (typeof window !== 'undefined') {
      this.logPageView(window.location.pathname).catch(console.error);
    }
    
    // Setup error handlers
    if (typeof window !== 'undefined') {
      window.addEventListener('error', (event) => {
        this.logError(
          'javascript_error',
          event.message,
          event.error?.stack,
          {
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno
          }
        ).catch(console.error);
      });
      
      window.addEventListener('unhandledrejection', (event) => {
        this.logError(
          'unhandled_promise_rejection',
          event.reason?.message || 'Unhandled promise rejection',
          event.reason?.stack,
          {
            reason: event.reason
          }
        ).catch(console.error);
      });
      
      // Flush events before page unload
      window.addEventListener('beforeunload', () => {
        this.flush().catch(console.error);
      });
    }
  }
}

// Export singleton instance
export const frontendEventService = FrontendEventService.getInstance();

// Export for convenience
export default frontendEventService;
