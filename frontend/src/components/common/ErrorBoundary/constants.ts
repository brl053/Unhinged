// ============================================================================
// ErrorBoundary Constants - Configuration and Static Values
// ============================================================================
//
// @file constants.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Constants for error boundary system configuration
//
// Etymology: Latin "constans" = standing firm, unchanging
// Methodology: Centralized configuration with semantic organization
// ============================================================================

import { 
  ErrorCategory, 
  ErrorSeverity, 
  ErrorRecoveryStrategy, 
  ErrorMessageTemplate 
} from './types';

/**
 * Default configuration values for error boundaries
 * Etymology: "default" = standard, typical configuration
 */
export const DEFAULT_CONFIG = {
  /** Maximum number of retry attempts before giving up */
  MAX_RETRIES: 3,
  
  /** Timeout for retry operations (milliseconds) */
  RETRY_TIMEOUT: 5000,
  
  /** Delay between retry attempts (milliseconds) */
  RETRY_DELAY: 1000,
  
  /** Whether to show technical details in development */
  SHOW_TECHNICAL_DETAILS: process.env.NODE_ENV === 'development',
  
  /** Whether error reporting is enabled by default */
  ERROR_REPORTING_ENABLED: true,
  
  /** Minimum severity level to display errors */
  MINIMUM_SEVERITY: 'low' as ErrorSeverity,
  
  /** Default error category for unclassified errors */
  DEFAULT_CATEGORY: 'unknown' as ErrorCategory,
} as const;

/**
 * Error severity hierarchy and weights
 * Used for prioritizing and filtering errors
 */
export const ERROR_SEVERITY_WEIGHTS = {
  low: 1,
  medium: 2,
  high: 3,
  critical: 4,
} as const;

/**
 * Error category metadata
 * Provides additional information about each error category
 */
export const ERROR_CATEGORY_METADATA = {
  audio: {
    icon: '🎤',
    color: 'warning',
    description: 'Audio system and microphone related errors',
    commonCauses: ['Permission denied', 'Device not found', 'Browser compatibility'],
    defaultRecovery: ['permission', 'retry'] as ErrorRecoveryStrategy[],
  },
  network: {
    icon: '🌐',
    color: 'danger',
    description: 'Network connectivity and API errors',
    commonCauses: ['Connection timeout', 'Server error', 'Rate limiting'],
    defaultRecovery: ['retry', 'reload'] as ErrorRecoveryStrategy[],
  },
  permission: {
    icon: '🔒',
    color: 'warning',
    description: 'Browser permission and security errors',
    commonCauses: ['Permission denied', 'Insecure context', 'User rejection'],
    defaultRecovery: ['permission', 'reload'] as ErrorRecoveryStrategy[],
  },
  browser: {
    icon: '🌍',
    color: 'info',
    description: 'Browser compatibility and feature support errors',
    commonCauses: ['Unsupported feature', 'Old browser version', 'Missing API'],
    defaultRecovery: ['fallback', 'report'] as ErrorRecoveryStrategy[],
  },
  service: {
    icon: '⚙️',
    color: 'danger',
    description: 'External service and API errors',
    commonCauses: ['Service unavailable', 'API error', 'Authentication failure'],
    defaultRecovery: ['retry', 'report'] as ErrorRecoveryStrategy[],
  },
  component: {
    icon: '⚛️',
    color: 'danger',
    description: 'React component lifecycle and rendering errors',
    commonCauses: ['Render error', 'State corruption', 'Props mismatch'],
    defaultRecovery: ['retry', 'reload'] as ErrorRecoveryStrategy[],
  },
  unknown: {
    icon: '❓',
    color: 'secondary',
    description: 'Unclassified or unexpected errors',
    commonCauses: ['Unexpected condition', 'Third-party library', 'Runtime error'],
    defaultRecovery: ['retry', 'report'] as ErrorRecoveryStrategy[],
  },
} as const;

/**
 * Recovery strategy metadata
 * Provides information about each recovery strategy
 */
export const RECOVERY_STRATEGY_METADATA = {
  retry: {
    label: 'Try Again',
    icon: '🔄',
    description: 'Retry the failed operation',
    buttonVariant: 'primary',
  },
  reload: {
    label: 'Reload Page',
    icon: '↻',
    description: 'Reload the entire page',
    buttonVariant: 'secondary',
  },
  permission: {
    label: 'Grant Permission',
    icon: '🔓',
    description: 'Request necessary browser permissions',
    buttonVariant: 'primary',
  },
  fallback: {
    label: 'Use Alternative',
    icon: '🔀',
    description: 'Switch to alternative functionality',
    buttonVariant: 'secondary',
  },
  report: {
    label: 'Report Issue',
    icon: '📝',
    description: 'Report this issue to support',
    buttonVariant: 'secondary',
  },
  none: {
    label: 'No Action Available',
    icon: '🚫',
    description: 'No recovery action available',
    buttonVariant: 'secondary',
  },
} as const;

/**
 * Pre-defined error message templates
 * User-friendly messages for common error scenarios
 */
export const ERROR_MESSAGE_TEMPLATES: ErrorMessageTemplate[] = [
  // Audio errors
  {
    category: 'audio',
    severity: 'high',
    template: 'Unable to access your microphone. Please check your browser permissions and try again.',
    recoveryInstructions: 'Click the microphone icon in your browser\'s address bar and allow access.',
    technicalTemplate: 'getUserMedia() failed: {technicalMessage}',
  },
  {
    category: 'audio',
    severity: 'medium',
    template: 'Audio features are not supported in your current browser.',
    recoveryInstructions: 'Please try using a modern browser like Chrome, Firefox, or Safari.',
    technicalTemplate: 'Audio API not available: {technicalMessage}',
  },
  
  // Network errors
  {
    category: 'network',
    severity: 'high',
    template: 'Network connection error. Please check your internet connection and try again.',
    recoveryInstructions: 'Verify your internet connection and refresh the page.',
    technicalTemplate: 'Network request failed: {technicalMessage}',
  },
  {
    category: 'network',
    severity: 'medium',
    template: 'The service is temporarily unavailable. Please try again in a few moments.',
    recoveryInstructions: 'Wait a moment and try your request again.',
    technicalTemplate: 'Service error: {technicalMessage}',
  },
  
  // Permission errors
  {
    category: 'permission',
    severity: 'high',
    template: 'Permission required to access this feature.',
    recoveryInstructions: 'Please grant the necessary permissions and try again.',
    technicalTemplate: 'Permission denied: {technicalMessage}',
  },
  
  // Browser compatibility errors
  {
    category: 'browser',
    severity: 'medium',
    template: 'This feature is not supported in your current browser.',
    recoveryInstructions: 'Please update your browser or try a different one.',
    technicalTemplate: 'Browser compatibility issue: {technicalMessage}',
  },
  
  // Service errors
  {
    category: 'service',
    severity: 'high',
    template: 'External service is temporarily unavailable.',
    recoveryInstructions: 'Please try again later or contact support if the issue persists.',
    technicalTemplate: 'Service error: {technicalMessage}',
  },
  
  // Component errors
  {
    category: 'component',
    severity: 'high',
    template: 'A component error occurred. Please try refreshing the page.',
    recoveryInstructions: 'Refresh the page or try navigating to a different section.',
    technicalTemplate: 'Component error: {technicalMessage}',
  },
  
  // Unknown errors
  {
    category: 'unknown',
    template: 'An unexpected error occurred. Please try again.',
    recoveryInstructions: 'Try refreshing the page or contact support if the issue persists.',
    technicalTemplate: 'Unknown error: {technicalMessage}',
  },
];

/**
 * Error boundary CSS class names
 * Consistent naming for styling error boundary components
 */
export const ERROR_BOUNDARY_CLASSES = {
  container: 'error-boundary',
  errorContainer: 'error-boundary__error',
  errorIcon: 'error-boundary__icon',
  errorTitle: 'error-boundary__title',
  errorMessage: 'error-boundary__message',
  errorDetails: 'error-boundary__details',
  errorActions: 'error-boundary__actions',
  errorButton: 'error-boundary__button',
  retryButton: 'error-boundary__button--retry',
  reloadButton: 'error-boundary__button--reload',
  reportButton: 'error-boundary__button--report',
  technicalDetails: 'error-boundary__technical',
  fallbackContainer: 'error-boundary__fallback',
} as const;

/**
 * Error boundary data attributes
 * For testing and debugging purposes
 */
export const ERROR_BOUNDARY_DATA_ATTRIBUTES = {
  errorId: 'data-error-id',
  errorCategory: 'data-error-category',
  errorSeverity: 'data-error-severity',
  retryCount: 'data-retry-count',
  hasError: 'data-has-error',
  canRetry: 'data-can-retry',
} as const;

/**
 * GitHub issue template configuration
 * For automated error reporting to GitHub issues
 */
export const GITHUB_ISSUE_CONFIG = {
  repository: 'your-org/unhinged',
  labels: ['bug', 'error-boundary'],
  assignees: [],
  titlePrefix: 'Error Boundary:',
  bodyTemplate: `
**Error Information**
- **Error ID:** {errorId}
- **Category:** {category}
- **Severity:** {severity}
- **Message:** {message}
- **Timestamp:** {timestamp}

**Environment**
- **URL:** {url}
- **User Agent:** {userAgent}
- **Browser:** {browser}

**Technical Details**
\`\`\`
{stack}
\`\`\`

**Component Stack**
\`\`\`
{componentStack}
\`\`\`

**Steps to Reproduce**
1. 
2. 
3. 

**Expected Behavior**


**Actual Behavior**


**Additional Context**

  `.trim(),
} as const;

/**
 * Error boundary event names
 * For custom event dispatching and monitoring
 */
export const ERROR_BOUNDARY_EVENTS = {
  errorCaught: 'error-boundary:error-caught',
  errorRecovered: 'error-boundary:error-recovered',
  retryAttempted: 'error-boundary:retry-attempted',
  maxRetriesReached: 'error-boundary:max-retries-reached',
  errorReported: 'error-boundary:error-reported',
  fallbackRendered: 'error-boundary:fallback-rendered',
} as const;

/**
 * Local storage keys for error boundary persistence
 * For storing error state and user preferences
 */
export const ERROR_BOUNDARY_STORAGE_KEYS = {
  errorHistory: 'unhinged:error-boundary:history',
  userPreferences: 'unhinged:error-boundary:preferences',
  reportingConsent: 'unhinged:error-boundary:reporting-consent',
  dismissedErrors: 'unhinged:error-boundary:dismissed',
} as const;

/**
 * Error boundary performance thresholds
 * For monitoring and alerting on error boundary performance
 */
export const PERFORMANCE_THRESHOLDS = {
  /** Maximum time for error boundary to render (milliseconds) */
  maxRenderTime: 100,
  
  /** Maximum time for error recovery (milliseconds) */
  maxRecoveryTime: 5000,
  
  /** Maximum number of errors per session before alerting */
  maxErrorsPerSession: 10,
  
  /** Maximum error rate (errors per minute) before alerting */
  maxErrorRate: 5,
} as const;
