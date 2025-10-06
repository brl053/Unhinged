// ============================================================================
// ErrorBoundary Utils - Utility Functions for Error Handling
// ============================================================================
//
// @file utils.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Utility functions for error processing and reporting
//
// Etymology: Latin "utilitas" = usefulness, practical value
// Methodology: Pure functions with clear inputs and outputs
// ============================================================================

import { 
  ErrorInfo, 
  ErrorCategory, 
  ErrorSeverity, 
  ErrorRecoveryStrategy,
  ErrorMessageTemplate,
  AudioErrorInfo,
  NetworkErrorInfo,
  ErrorReportingConfig 
} from './types';
import { 
  ERROR_MESSAGE_TEMPLATES, 
  ERROR_CATEGORY_METADATA, 
  DEFAULT_CONFIG,
  GITHUB_ISSUE_CONFIG 
} from './constants';

/**
 * Generate unique error identifier
 * Creates a unique ID for error tracking and correlation
 * 
 * @returns Unique error identifier string
 */
export const generateErrorId = (): string => {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 9);
  return `error_${timestamp}_${random}`;
};

/**
 * Classify error based on error message and context
 * Analyzes error content to determine appropriate category
 * 
 * @param error - Native Error object
 * @param context - Additional context information
 * @returns Classified error category
 */
export const classifyError = (
  error: Error, 
  context?: Record<string, unknown>
): ErrorCategory => {
  const message = error.message.toLowerCase();
  const stack = error.stack?.toLowerCase() || '';
  
  // Audio-related errors
  if (
    message.includes('microphone') ||
    message.includes('getusermedia') ||
    message.includes('mediastream') ||
    message.includes('audiocontext') ||
    message.includes('audio') ||
    context?.component === 'audio'
  ) {
    return 'audio';
  }
  
  // Network-related errors
  if (
    message.includes('network') ||
    message.includes('fetch') ||
    message.includes('xhr') ||
    message.includes('timeout') ||
    message.includes('connection') ||
    stack.includes('fetch') ||
    context?.type === 'network'
  ) {
    return 'network';
  }
  
  // Permission-related errors
  if (
    message.includes('permission') ||
    message.includes('denied') ||
    message.includes('not allowed') ||
    message.includes('blocked') ||
    context?.type === 'permission'
  ) {
    return 'permission';
  }
  
  // Browser compatibility errors
  if (
    message.includes('not supported') ||
    message.includes('undefined') && message.includes('function') ||
    message.includes('not a function') ||
    context?.type === 'browser'
  ) {
    return 'browser';
  }
  
  // Service-related errors
  if (
    message.includes('grpc') ||
    message.includes('service') ||
    message.includes('api') ||
    message.includes('server') ||
    context?.type === 'service'
  ) {
    return 'service';
  }
  
  // Component-related errors
  if (
    stack.includes('react') ||
    stack.includes('component') ||
    message.includes('render') ||
    context?.type === 'component'
  ) {
    return 'component';
  }
  
  return 'unknown';
};

/**
 * Determine error severity based on error characteristics
 * Analyzes error impact and urgency to assign severity level
 * 
 * @param error - Native Error object
 * @param category - Error category
 * @param context - Additional context information
 * @returns Error severity level
 */
export const determineErrorSeverity = (
  error: Error,
  category: ErrorCategory,
  context?: Record<string, unknown>
): ErrorSeverity => {
  const message = error.message.toLowerCase();
  
  // Critical errors that break core functionality
  if (
    message.includes('fatal') ||
    message.includes('critical') ||
    message.includes('crash') ||
    context?.critical === true
  ) {
    return 'critical';
  }
  
  // High severity errors that significantly impact user experience
  if (
    category === 'audio' && message.includes('microphone') ||
    category === 'network' && message.includes('connection') ||
    category === 'permission' && message.includes('denied') ||
    message.includes('failed') ||
    context?.severity === 'high'
  ) {
    return 'high';
  }
  
  // Medium severity errors that partially impact functionality
  if (
    category === 'browser' ||
    category === 'service' ||
    message.includes('timeout') ||
    message.includes('unavailable') ||
    context?.severity === 'medium'
  ) {
    return 'medium';
  }
  
  // Low severity errors that have minimal impact
  return 'low';
};

/**
 * Get appropriate recovery strategies for error
 * Determines what recovery actions are available based on error type
 * 
 * @param category - Error category
 * @param severity - Error severity
 * @param context - Additional context information
 * @returns Array of available recovery strategies
 */
export const getRecoveryStrategies = (
  category: ErrorCategory,
  severity: ErrorSeverity,
  context?: Record<string, unknown>
): ErrorRecoveryStrategy[] => {
  const categoryMetadata = ERROR_CATEGORY_METADATA[category];
  const baseStrategies = [...categoryMetadata.defaultRecovery];
  
  // Add context-specific strategies
  if (context?.canRetry !== false && !baseStrategies.includes('retry')) {
    baseStrategies.unshift('retry');
  }
  
  if (severity === 'critical' && !baseStrategies.includes('reload')) {
    baseStrategies.push('reload');
  }
  
  if (category === 'unknown' && !baseStrategies.includes('report')) {
    baseStrategies.push('report');
  }
  
  return baseStrategies;
};

/**
 * Generate user-friendly error message
 * Creates appropriate message based on error category and context
 * 
 * @param error - Native Error object
 * @param category - Error category
 * @param severity - Error severity
 * @returns User-friendly error message
 */
export const generateErrorMessage = (
  error: Error,
  category: ErrorCategory,
  severity?: ErrorSeverity
): string => {
  // Find matching template
  const template = ERROR_MESSAGE_TEMPLATES.find(
    t => t.category === category && (!t.severity || t.severity === severity)
  ) || ERROR_MESSAGE_TEMPLATES.find(t => t.category === category);
  
  if (template) {
    return template.template.replace('{technicalMessage}', error.message);
  }
  
  // Fallback to category-specific default messages
  const categoryMetadata = ERROR_CATEGORY_METADATA[category];
  return `${categoryMetadata.description}. Please try again.`;
};

/**
 * Create comprehensive error information object
 * Combines error analysis with metadata for complete error context
 * 
 * @param error - Native Error object
 * @param componentStack - React component stack trace
 * @param context - Additional context information
 * @returns Complete error information object
 */
export const createErrorInfo = (
  error: Error,
  componentStack?: string,
  context?: Record<string, unknown>
): ErrorInfo => {
  const category = classifyError(error, context);
  const severity = determineErrorSeverity(error, category, context);
  const recoveryStrategies = getRecoveryStrategies(category, severity, context);
  const message = generateErrorMessage(error, category, severity);
  
  return {
    id: generateErrorId(),
    severity,
    category,
    message,
    technicalMessage: error.message,
    stack: error.stack,
    componentStack,
    timestamp: new Date().toISOString(),
    recoveryStrategies,
    context,
  };
};

/**
 * Create specialized audio error information
 * Extends base error info with audio-specific metadata
 * 
 * @param error - Native Error object
 * @param componentStack - React component stack trace
 * @param context - Audio-specific context information
 * @returns Audio error information object
 */
export const createAudioErrorInfo = (
  error: Error,
  componentStack?: string,
  context?: Record<string, unknown>
): AudioErrorInfo => {
  const baseInfo = createErrorInfo(error, componentStack, context);
  const message = error.message.toLowerCase();
  
  let audioErrorType: AudioErrorInfo['audioErrorType'] = 'audio_processing';
  
  if (message.includes('permission') || message.includes('denied')) {
    audioErrorType = 'microphone_access';
  } else if (message.includes('not found') || message.includes('no device')) {
    audioErrorType = 'microphone_not_found';
  } else if (message.includes('audiocontext')) {
    audioErrorType = 'audio_context';
  } else if (message.includes('mediastream')) {
    audioErrorType = 'media_stream';
  } else if (message.includes('codec') || message.includes('format')) {
    audioErrorType = 'codec_unsupported';
  } else if (message.includes('sample rate')) {
    audioErrorType = 'sample_rate';
  } else if (message.includes('buffer')) {
    audioErrorType = 'buffer_underrun';
  }
  
  return {
    ...baseInfo,
    category: 'audio',
    audioErrorType,
    deviceInfo: context?.deviceInfo as AudioErrorInfo['deviceInfo'],
    audioContextState: context?.audioContextState as AudioContextState,
    browserCapabilities: context?.browserCapabilities as AudioErrorInfo['browserCapabilities'],
  };
};

/**
 * Create specialized network error information
 * Extends base error info with network-specific metadata
 * 
 * @param error - Native Error object
 * @param componentStack - React component stack trace
 * @param context - Network-specific context information
 * @returns Network error information object
 */
export const createNetworkErrorInfo = (
  error: Error,
  componentStack?: string,
  context?: Record<string, unknown>
): NetworkErrorInfo => {
  const baseInfo = createErrorInfo(error, componentStack, context);
  const message = error.message.toLowerCase();
  
  let networkErrorType: NetworkErrorInfo['networkErrorType'] = 'connection_failed';
  
  if (message.includes('timeout')) {
    networkErrorType = 'timeout';
  } else if (message.includes('server') || message.includes('5')) {
    networkErrorType = 'server_error';
  } else if (message.includes('rate') || message.includes('429')) {
    networkErrorType = 'rate_limited';
  } else if (message.includes('unauthorized') || message.includes('401')) {
    networkErrorType = 'unauthorized';
  } else if (message.includes('forbidden') || message.includes('403')) {
    networkErrorType = 'forbidden';
  } else if (message.includes('not found') || message.includes('404')) {
    networkErrorType = 'not_found';
  } else if (message.includes('unavailable') || message.includes('503')) {
    networkErrorType = 'service_unavailable';
  }
  
  return {
    ...baseInfo,
    category: 'network',
    networkErrorType,
    statusCode: context?.statusCode as number,
    url: context?.url as string,
    method: context?.method as string,
    responseHeaders: context?.responseHeaders as Record<string, string>,
  };
};

/**
 * Generate error report for external services
 * Creates structured error report for monitoring and debugging
 * 
 * @param errorInfo - Error information object
 * @param config - Error reporting configuration
 * @returns Error report object
 */
export const generateErrorReport = (
  errorInfo: ErrorInfo,
  config: ErrorReportingConfig
) => {
  const baseReport: any = {
    errorId: errorInfo.id,
    category: errorInfo.category,
    severity: errorInfo.severity,
    message: errorInfo.message,
    technicalMessage: errorInfo.technicalMessage,
    stack: errorInfo.stack,
    componentStack: errorInfo.componentStack,
    timestamp: errorInfo.timestamp,
    context: errorInfo.context,
    ...config.metadata,
  };

  if (config.includeUserAgent) {
    baseReport.userAgent = navigator.userAgent;
  }

  if (config.includeUrl) {
    baseReport.url = window.location.href;
  }

  return baseReport;
};

/**
 * Generate GitHub issue URL for error reporting
 * Creates pre-filled GitHub issue URL for manual error reporting
 * 
 * @param errorInfo - Error information object
 * @returns GitHub issue URL
 */
export const generateGitHubIssueUrl = (errorInfo: ErrorInfo): string => {
  const title = `${GITHUB_ISSUE_CONFIG.titlePrefix} ${errorInfo.message}`;
  const body = GITHUB_ISSUE_CONFIG.bodyTemplate
    .replace('{errorId}', errorInfo.id)
    .replace('{category}', errorInfo.category)
    .replace('{severity}', errorInfo.severity)
    .replace('{message}', errorInfo.message)
    .replace('{timestamp}', errorInfo.timestamp)
    .replace('{url}', window.location.href)
    .replace('{userAgent}', navigator.userAgent)
    .replace('{browser}', getBrowserInfo())
    .replace('{stack}', errorInfo.stack || 'No stack trace available')
    .replace('{componentStack}', errorInfo.componentStack || 'No component stack available');
  
  const params = new URLSearchParams({
    title: encodeURIComponent(title),
    body: encodeURIComponent(body),
    labels: GITHUB_ISSUE_CONFIG.labels.join(','),
  });
  
  return `https://github.com/${GITHUB_ISSUE_CONFIG.repository}/issues/new?${params.toString()}`;
};

/**
 * Get browser information for error reporting
 * Extracts browser name and version from user agent
 * 
 * @returns Browser information string
 */
export const getBrowserInfo = (): string => {
  const userAgent = navigator.userAgent;
  
  if (userAgent.includes('Chrome')) {
    const match = userAgent.match(/Chrome\/(\d+)/);
    return `Chrome ${match?.[1] || 'Unknown'}`;
  }
  
  if (userAgent.includes('Firefox')) {
    const match = userAgent.match(/Firefox\/(\d+)/);
    return `Firefox ${match?.[1] || 'Unknown'}`;
  }
  
  if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
    const match = userAgent.match(/Version\/(\d+)/);
    return `Safari ${match?.[1] || 'Unknown'}`;
  }
  
  if (userAgent.includes('Edge')) {
    const match = userAgent.match(/Edge\/(\d+)/);
    return `Edge ${match?.[1] || 'Unknown'}`;
  }
  
  return 'Unknown Browser';
};

/**
 * Check if error should be reported based on configuration
 * Determines whether an error meets reporting criteria
 * 
 * @param errorInfo - Error information object
 * @param config - Error reporting configuration
 * @returns Whether error should be reported
 */
export const shouldReportError = (
  errorInfo: ErrorInfo,
  config: ErrorReportingConfig
): boolean => {
  if (!config.enabled) {
    return false;
  }
  
  if (config.shouldReport) {
    return config.shouldReport(errorInfo);
  }
  
  // Default reporting logic
  return errorInfo.severity !== 'low';
};

/**
 * Sanitize error information for safe display
 * Removes sensitive information from error data
 * 
 * @param errorInfo - Error information object
 * @returns Sanitized error information
 */
export const sanitizeErrorInfo = (errorInfo: ErrorInfo): ErrorInfo => {
  const sanitized = { ...errorInfo };
  
  // Remove potentially sensitive context data
  if (sanitized.context) {
    const { password, token, apiKey, ...safeContext } = sanitized.context;
    sanitized.context = safeContext;
  }
  
  // Sanitize stack traces to remove file paths
  if (sanitized.stack) {
    sanitized.stack = sanitized.stack.replace(/file:\/\/[^\s]*/g, '[file path]');
  }
  
  if (sanitized.componentStack) {
    sanitized.componentStack = sanitized.componentStack.replace(/file:\/\/[^\s]*/g, '[file path]');
  }
  
  return sanitized;
};
