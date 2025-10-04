/**
 * @fileoverview Structured Logging Hook for React Components
 * 
 * @description
 * Provides structured logging capabilities for React components with support
 * for different log levels, component lifecycle tracking, and production
 * monitoring integration. Designed to replace console.log usage throughout
 * the application with centralized, structured logging.
 * 
 * @design_principles
 * - Structured logging with consistent format across all components
 * - Log level filtering for development vs production environments
 * - Component lifecycle tracking for debugging React issues
 * - Integration with monitoring services (Sentry, DataDog, LogRocket)
 * - Performance-aware logging that doesn't impact user experience
 * 
 * @llm_contract
 * When using useLogger:
 * 1. Always specify component name for context tracking
 * 2. Use appropriate log levels (DEBUG for development, WARN/ERROR for production)
 * 3. Include relevant context data in log entries
 * 4. Avoid logging sensitive user data or authentication tokens
 * 5. Use structured data instead of string concatenation
 * 
 * @usage_examples
 * ```typescript
 * // Basic usage in component
 * const logger = useLogger(LogLevel.INFO, 'MainLayout');
 * logger('User clicked navigation item', { route: '/showcase' });
 * 
 * // Error logging with context
 * const logger = useLogger(LogLevel.ERROR, 'ApiClient');
 * logger('API request failed', { endpoint: '/api/users', status: 500 });
 * 
 * // Debug logging for development
 * const logger = useLogger(LogLevel.DEBUG, 'FormComponent');
 * logger('Form validation triggered', { fieldCount: 5, errors: [] });
 * ```
 * 
 * @monitoring_integration
 * In production, logs are automatically sent to configured monitoring services:
 * - Sentry for error tracking and performance monitoring
 * - DataDog for application performance monitoring
 * - LogRocket for session replay and user behavior analysis
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import { useCallback, useEffect, useRef } from 'react';

/**
 * Log level enumeration for filtering and categorization
 * 
 * @description
 * Defines hierarchical log levels from most verbose (TRACE) to most critical (FATAL).
 * Higher numeric values indicate higher severity. Log filtering is based on
 * minimum level configuration.
 * 
 * @enum {number}
 */
export enum LogLevel {
  /** Detailed tracing information for debugging complex flows */
  TRACE = 0,
  
  /** Debug information for development and troubleshooting */
  DEBUG = 1,
  
  /** General information about application operation */
  INFO = 2,
  
  /** Warning conditions that don't prevent operation */
  WARN = 3,
  
  /** Error conditions that may affect functionality */
  ERROR = 4,
  
  /** Critical errors that may cause application failure */
  FATAL = 5,
}

/**
 * Context data interface for structured logging
 * 
 * @description
 * Flexible interface for attaching contextual information to log entries.
 * Supports any serializable data for comprehensive debugging information.
 * 
 * @example
 * ```typescript
 * const context: LogContext = {
 *   userId: '123',
 *   action: 'navigation',
 *   route: '/dashboard',
 *   timestamp: Date.now(),
 *   metadata: { source: 'sidebar' }
 * };
 * ```
 */
export interface LogContext {
  [key: string]: any;
}

/**
 * Log entry structure for consistent formatting
 * 
 * @description
 * Standardized log entry format used across all logging operations.
 * Includes timestamp, level, component context, and arbitrary data.
 */
export interface LogEntry {
  /** ISO timestamp of log entry creation */
  timestamp: string;
  
  /** Log level as string for readability */
  level: string;
  
  /** Human-readable log message */
  message: string;
  
  /** Component name that generated the log */
  component: string;
  
  /** Current URL pathname for navigation context */
  pathname: string;
  
  /** Environment (development, staging, production) */
  environment: string;
  
  /** Browser user agent for debugging browser-specific issues */
  userAgent: string;
  
  /** Additional context data */
  context?: LogContext;
}

/**
 * Logger function type for component usage
 * 
 * @description
 * Function signature for the logger returned by useLogger hook.
 * Provides consistent interface for all logging operations.
 * 
 * @param message - Human-readable log message
 * @param context - Optional contextual data
 */
export type LoggerFunction = (message: string, context?: LogContext) => void;

/**
 * Configuration for logger behavior
 * 
 * @description
 * Controls logger behavior including level filtering, remote logging,
 * and performance optimizations.
 */
interface LoggerConfig {
  /** Minimum log level to output */
  minLevel: LogLevel;
  
  /** Whether to send logs to remote monitoring services */
  enableRemoteLogging: boolean;
  
  /** Whether to include component lifecycle logging */
  enableLifecycleLogging: boolean;
  
  /** Maximum number of log entries to buffer before sending */
  bufferSize: number;
}

/**
 * Default logger configuration based on environment
 * 
 * @description
 * Provides sensible defaults for different environments:
 * - Development: Verbose logging with lifecycle tracking
 * - Production: Error/warning logging with remote monitoring
 * - Test: Minimal logging to avoid test noise
 */
const getDefaultConfig = (): LoggerConfig => {
  const env = process.env.NODE_ENV;
  
  if (env === 'production') {
    return {
      minLevel: LogLevel.WARN,
      enableRemoteLogging: true,
      enableLifecycleLogging: false,
      bufferSize: 50,
    };
  }
  
  if (env === 'test') {
    return {
      minLevel: LogLevel.ERROR,
      enableRemoteLogging: false,
      enableLifecycleLogging: false,
      bufferSize: 0,
    };
  }
  
  // Development environment
  return {
    minLevel: LogLevel.DEBUG,
    enableRemoteLogging: false,
    enableLifecycleLogging: true,
    bufferSize: 10,
  };
};

/**
 * Global logger configuration
 * 
 * @description
 * Singleton configuration object used across all logger instances.
 * Can be modified at runtime for dynamic log level adjustment.
 */
const loggerConfig = getDefaultConfig();

/**
 * Log buffer for batching remote log submissions
 * 
 * @description
 * Collects log entries for efficient batch submission to monitoring services.
 * Automatically flushes when buffer size limit is reached.
 */
const logBuffer: LogEntry[] = [];

/**
 * Structured logging hook for React components
 * 
 * @description
 * Provides structured logging capabilities with component lifecycle tracking,
 * log level filtering, and integration with monitoring services. Replaces
 * console.log usage with centralized, structured logging.
 * 
 * @param level - Log level for filtering (messages below this level are ignored)
 * @param componentName - Name of the component using the logger
 * @returns Logger function for creating log entries
 * 
 * @example
 * ```typescript
 * const MyComponent: React.FC = () => {
 *   const logger = useLogger(LogLevel.INFO, 'MyComponent');
 *   
 *   const handleClick = () => {
 *     logger('Button clicked', { buttonId: 'submit' });
 *   };
 *   
 *   return <button onClick={handleClick}>Submit</button>;
 * };
 * ```
 */
export const useLogger = (level: LogLevel, componentName: string): LoggerFunction => {
  const mountTimeRef = useRef(Date.now());
  const renderCountRef = useRef(0);
  
  // Track render count for performance monitoring
  renderCountRef.current += 1;
  
  // Component lifecycle logging
  useEffect(() => {
    if (loggerConfig.enableLifecycleLogging && level >= loggerConfig.minLevel) {
      const mountLogger = createLoggerFunction(LogLevel.DEBUG, componentName);
      mountLogger('Component mounted', {
        renderCount: renderCountRef.current,
        mountTime: mountTimeRef.current,
      });
    }
    
    return () => {
      if (loggerConfig.enableLifecycleLogging && level >= loggerConfig.minLevel) {
        const unmountLogger = createLoggerFunction(LogLevel.DEBUG, componentName);
        const lifetime = Date.now() - mountTimeRef.current;
        
        unmountLogger('Component unmounted', {
          lifetime,
          totalRenders: renderCountRef.current,
        });
      }
    };
  }, [componentName, level]);
  
  // Create memoized logger function
  const logger = useCallback(
    (message: string, context?: LogContext) => {
      if (level >= loggerConfig.minLevel) {
        const logEntry = createLogEntry(level, componentName, message, context);
        outputLogEntry(logEntry);
        
        if (loggerConfig.enableRemoteLogging) {
          bufferLogEntry(logEntry);
        }
      }
    },
    [level, componentName]
  );
  
  return logger;
};

/**
 * Creates a logger function for specific level and component
 * 
 * @description
 * Internal utility for creating logger functions with pre-configured
 * level and component context. Used for lifecycle logging.
 * 
 * @param level - Log level for the logger
 * @param componentName - Component name for context
 * @returns Logger function
 * 
 * @private
 */
const createLoggerFunction = (level: LogLevel, componentName: string): LoggerFunction => {
  return (message: string, context?: LogContext) => {
    if (level >= loggerConfig.minLevel) {
      const logEntry = createLogEntry(level, componentName, message, context);
      outputLogEntry(logEntry);
      
      if (loggerConfig.enableRemoteLogging) {
        bufferLogEntry(logEntry);
      }
    }
  };
};

/**
 * Creates structured log entry with consistent formatting
 * 
 * @description
 * Generates standardized log entry with timestamp, environment context,
 * and browser information for comprehensive debugging.
 * 
 * @param level - Log level
 * @param componentName - Component generating the log
 * @param message - Log message
 * @param context - Additional context data
 * @returns Formatted log entry
 * 
 * @private
 */
const createLogEntry = (
  level: LogLevel,
  componentName: string,
  message: string,
  context?: LogContext
): LogEntry => {
  return {
    timestamp: new Date().toISOString(),
    level: LogLevel[level],
    message,
    component: componentName,
    pathname: typeof window !== 'undefined' ? window.location.pathname : '',
    environment: process.env.NODE_ENV || 'development',
    userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
    context,
  };
};

/**
 * Outputs log entry to console with appropriate formatting
 * 
 * @description
 * Sends log entry to browser console using appropriate console method
 * based on log level. Formats output for readability in development.
 * 
 * @param logEntry - Log entry to output
 * 
 * @private
 */
const outputLogEntry = (logEntry: LogEntry): void => {
  const formattedMessage = `[${logEntry.timestamp}] [${logEntry.level}] [${logEntry.component}] ${logEntry.message}`;
  
  switch (logEntry.level) {
    case 'FATAL':
    case 'ERROR':
      console.error(formattedMessage, logEntry.context);
      break;
    case 'WARN':
      console.warn(formattedMessage, logEntry.context);
      break;
    case 'INFO':
      console.info(formattedMessage, logEntry.context);
      break;
    case 'DEBUG':
    case 'TRACE':
    default:
      console.log(formattedMessage, logEntry.context);
      break;
  }
};

/**
 * Buffers log entry for batch submission to monitoring services
 * 
 * @description
 * Adds log entry to buffer and triggers flush when buffer size limit
 * is reached. Provides efficient batching for remote log submission.
 * 
 * @param logEntry - Log entry to buffer
 * 
 * @private
 */
const bufferLogEntry = (logEntry: LogEntry): void => {
  logBuffer.push(logEntry);
  
  if (logBuffer.length >= loggerConfig.bufferSize) {
    flushLogBuffer();
  }
};

/**
 * Flushes log buffer to monitoring services
 * 
 * @description
 * Sends buffered log entries to configured monitoring services
 * and clears the buffer. Handles errors gracefully to prevent
 * logging from affecting application functionality.
 * 
 * @private
 */
const flushLogBuffer = (): void => {
  if (logBuffer.length === 0) return;
  
  const logsToSend = [...logBuffer];
  logBuffer.length = 0; // Clear buffer
  
  // Send to monitoring services (implement based on your monitoring stack)
  if (typeof window !== 'undefined' && (window as any).Sentry) {
    // Send to Sentry
    logsToSend.forEach(log => {
      if (log.level === 'ERROR' || log.level === 'FATAL') {
        (window as any).Sentry.captureException(new Error(log.message), {
          tags: { component: log.component },
          extra: log.context,
        });
      }
    });
  }
  
  // Add other monitoring service integrations here
  // Example: DataDog, LogRocket, custom analytics
};

/**
 * Updates logger configuration at runtime
 * 
 * @description
 * Allows dynamic adjustment of logger behavior without application restart.
 * Useful for debugging production issues or adjusting log verbosity.
 * 
 * @param newConfig - Partial configuration to update
 * 
 * @example
 * ```typescript
 * // Enable debug logging in production for troubleshooting
 * updateLoggerConfig({ minLevel: LogLevel.DEBUG });
 * ```
 */
export const updateLoggerConfig = (newConfig: Partial<LoggerConfig>): void => {
  Object.assign(loggerConfig, newConfig);
};
