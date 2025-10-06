// ============================================================================
// ErrorBoundary Types - Type Definitions for Error Boundary System
// ============================================================================
//
// @file types.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Comprehensive type definitions for error boundary components
//
// Etymology: Greek "typos" = impression, form
// Methodology: TypeScript interface design with semantic naming
// ============================================================================

import { ReactNode } from 'react';

/**
 * Error severity levels for categorizing different types of errors
 * Etymology: Latin "severitas" = strictness, seriousness
 */
export type ErrorSeverity = 'low' | 'medium' | 'high' | 'critical';

/**
 * Error categories for systematic error classification
 * Enables targeted error handling and recovery strategies
 */
export type ErrorCategory = 
  | 'audio'           // Audio system errors (microphone, playback, etc.)
  | 'network'         // Network connectivity and API errors
  | 'permission'      // Browser permission errors
  | 'browser'         // Browser compatibility errors
  | 'service'         // External service errors (gRPC, etc.)
  | 'component'       // React component lifecycle errors
  | 'unknown';        // Unclassified errors

/**
 * Error recovery strategies available to users
 * Defines what actions users can take to resolve errors
 */
export type ErrorRecoveryStrategy = 
  | 'retry'           // Simple retry operation
  | 'reload'          // Full page reload
  | 'permission'      // Request browser permissions
  | 'fallback'        // Use alternative functionality
  | 'report'          // Report issue to support
  | 'none';           // No recovery available

/**
 * Core error information structure
 * Extends native Error with additional metadata for better handling
 */
export interface ErrorInfo {
  /** Unique identifier for error tracking */
  id: string;
  
  /** Error severity level */
  severity: ErrorSeverity;
  
  /** Error category for classification */
  category: ErrorCategory;
  
  /** User-friendly error message */
  message: string;
  
  /** Technical error details (for development) */
  technicalMessage?: string;
  
  /** Error stack trace */
  stack?: string;
  
  /** React component stack trace */
  componentStack?: string;
  
  /** Timestamp when error occurred */
  timestamp: string;
  
  /** Available recovery strategies */
  recoveryStrategies: ErrorRecoveryStrategy[];
  
  /** Additional context data */
  context?: Record<string, unknown>;
}

/**
 * Error boundary state interface
 * Manages the internal state of error boundary components
 */
export interface ErrorBoundaryState {
  /** Whether an error has occurred */
  hasError: boolean;
  
  /** Current error information */
  errorInfo: ErrorInfo | null;
  
  /** Number of retry attempts */
  retryCount: number;
  
  /** Maximum allowed retry attempts */
  maxRetries: number;
  
  /** Whether error boundary is in recovery mode */
  isRecovering: boolean;
}

/**
 * Error boundary configuration props
 * Configures behavior and appearance of error boundaries
 */
export interface ErrorBoundaryProps {
  /** Child components to wrap with error boundary */
  children: ReactNode;
  
  /** Custom fallback component to render on error */
  fallback?: ReactNode | ((errorInfo: ErrorInfo) => ReactNode);
  
  /** Error handler callback */
  onError?: (errorInfo: ErrorInfo) => void;
  
  /** Recovery handler callback */
  onRecover?: () => void;
  
  /** Whether to reset error state when props change */
  resetOnPropsChange?: boolean;
  
  /** Keys to watch for prop changes that trigger reset */
  resetKeys?: Array<string | number>;
  
  /** Maximum number of retry attempts */
  maxRetries?: number;
  
  /** Whether to show technical details in development */
  showTechnicalDetails?: boolean;
  
  /** Custom error categories to handle */
  supportedCategories?: ErrorCategory[];
  
  /** Minimum severity level to display */
  minimumSeverity?: ErrorSeverity;
}

/**
 * Error fallback component props
 * Props passed to custom fallback components
 */
export interface ErrorFallbackProps {
  /** Error information */
  errorInfo: ErrorInfo;
  
  /** Retry function */
  onRetry: () => void;
  
  /** Reset error boundary function */
  onReset: () => void;
  
  /** Report error function */
  onReport?: () => void;
  
  /** Whether retry is available */
  canRetry: boolean;
  
  /** Current retry count */
  retryCount: number;
  
  /** Maximum retry attempts */
  maxRetries: number;
}

/**
 * Error reporting configuration
 * Configures how errors are reported to external services
 */
export interface ErrorReportingConfig {
  /** Whether error reporting is enabled */
  enabled: boolean;
  
  /** External service endpoint for error reporting */
  endpoint?: string;
  
  /** API key for error reporting service */
  apiKey?: string;
  
  /** Additional metadata to include in reports */
  metadata?: Record<string, unknown>;
  
  /** Whether to include user agent information */
  includeUserAgent?: boolean;
  
  /** Whether to include URL information */
  includeUrl?: boolean;
  
  /** Custom error filtering function */
  shouldReport?: (errorInfo: ErrorInfo) => boolean;
}

/**
 * Audio-specific error types
 * Specialized error information for audio system errors
 */
export interface AudioErrorInfo extends ErrorInfo {
  category: 'audio';
  
  /** Audio error subtype */
  audioErrorType: 
    | 'microphone_access'
    | 'microphone_not_found'
    | 'audio_context'
    | 'media_stream'
    | 'audio_processing'
    | 'codec_unsupported'
    | 'sample_rate'
    | 'buffer_underrun';
  
  /** Audio device information */
  deviceInfo?: {
    deviceId?: string;
    label?: string;
    kind?: string;
  };
  
  /** Audio context state */
  audioContextState?: AudioContextState;
  
  /** Browser audio capabilities */
  browserCapabilities?: {
    getUserMedia: boolean;
    audioContext: boolean;
    mediaRecorder: boolean;
  };
}

/**
 * Network error types
 * Specialized error information for network-related errors
 */
export interface NetworkErrorInfo extends ErrorInfo {
  category: 'network';
  
  /** Network error subtype */
  networkErrorType:
    | 'connection_failed'
    | 'timeout'
    | 'server_error'
    | 'rate_limited'
    | 'unauthorized'
    | 'forbidden'
    | 'not_found'
    | 'service_unavailable';
  
  /** HTTP status code (if applicable) */
  statusCode?: number;
  
  /** Request URL */
  url?: string;
  
  /** Request method */
  method?: string;
  
  /** Response headers */
  responseHeaders?: Record<string, string>;
}

/**
 * Error boundary hook return type
 * Type for custom error boundary hooks
 */
export interface UseErrorBoundaryReturn {
  /** Current error state */
  errorState: ErrorBoundaryState;
  
  /** Function to trigger error boundary */
  captureError: (error: Error, context?: Record<string, unknown>) => void;
  
  /** Function to reset error boundary */
  resetError: () => void;
  
  /** Function to retry failed operation */
  retryOperation: () => void;
  
  /** Function to report error */
  reportError: () => void;
}

/**
 * Error boundary context type
 * Context for sharing error boundary state across components
 */
export interface ErrorBoundaryContextType {
  /** Register error handler */
  registerErrorHandler: (handler: (errorInfo: ErrorInfo) => void) => void;
  
  /** Unregister error handler */
  unregisterErrorHandler: (handler: (errorInfo: ErrorInfo) => void) => void;
  
  /** Report error to boundary */
  reportError: (error: Error, context?: Record<string, unknown>) => void;
  
  /** Current error reporting configuration */
  reportingConfig: ErrorReportingConfig;
}

/**
 * Error message template type
 * Template for generating user-friendly error messages
 */
export interface ErrorMessageTemplate {
  /** Error category this template applies to */
  category: ErrorCategory;
  
  /** Error severity this template applies to */
  severity?: ErrorSeverity;
  
  /** Message template with placeholders */
  template: string;
  
  /** Recovery instructions */
  recoveryInstructions?: string;
  
  /** Technical details template */
  technicalTemplate?: string;
}

/**
 * Error boundary metrics type
 * Metrics for monitoring error boundary performance
 */
export interface ErrorBoundaryMetrics {
  /** Total number of errors caught */
  totalErrors: number;
  
  /** Errors by category */
  errorsByCategory: Record<ErrorCategory, number>;
  
  /** Errors by severity */
  errorsBySeverity: Record<ErrorSeverity, number>;
  
  /** Recovery success rate */
  recoverySuccessRate: number;
  
  /** Average time to recovery */
  averageRecoveryTime: number;
  
  /** Most common error types */
  commonErrors: Array<{
    message: string;
    count: number;
    category: ErrorCategory;
  }>;
}
