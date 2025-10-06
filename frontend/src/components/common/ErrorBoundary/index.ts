// ============================================================================
// ErrorBoundary Module - Public API Exports
// ============================================================================
//
// @file index.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Public API for ErrorBoundary module with clean exports
//
// Etymology: Latin "index" = pointer, indicator
// Methodology: Barrel exports with organized public interface
// ============================================================================

// Main ErrorBoundary component and related components
export { 
  ErrorBoundary,
  withAudioErrorBoundary,
  AudioErrorFallback,
  MicrophoneErrorFallback 
} from '../ErrorBoundary';

// Type definitions
export type {
  ErrorBoundaryProps,
  ErrorBoundaryState,
  ErrorInfo,
  ErrorSeverity,
  ErrorCategory,
  ErrorRecoveryStrategy,
  ErrorFallbackProps,
  ErrorReportingConfig,
  AudioErrorInfo,
  NetworkErrorInfo,
  UseErrorBoundaryReturn,
  ErrorBoundaryContextType,
  ErrorMessageTemplate,
  ErrorBoundaryMetrics
} from './types';

// Utility functions
export {
  generateErrorId,
  classifyError,
  determineErrorSeverity,
  getRecoveryStrategies,
  generateErrorMessage,
  createErrorInfo,
  createAudioErrorInfo,
  createNetworkErrorInfo,
  generateErrorReport,
  generateGitHubIssueUrl,
  getBrowserInfo,
  shouldReportError,
  sanitizeErrorInfo
} from './utils';

// React hooks
export {
  useErrorBoundaryState,
  useErrorReporting,
  useErrorBoundaryMetrics,
  useErrorBoundaryPreferences,
  useErrorBoundaryContext,
  useErrorBoundary
} from './hooks';

// Constants and configuration
export {
  DEFAULT_CONFIG,
  ERROR_SEVERITY_WEIGHTS,
  ERROR_CATEGORY_METADATA,
  RECOVERY_STRATEGY_METADATA,
  ERROR_MESSAGE_TEMPLATES,
  ERROR_BOUNDARY_CLASSES,
  ERROR_BOUNDARY_DATA_ATTRIBUTES,
  GITHUB_ISSUE_CONFIG,
  ERROR_BOUNDARY_EVENTS,
  ERROR_BOUNDARY_STORAGE_KEYS,
  PERFORMANCE_THRESHOLDS
} from './constants';

// Styled components and styles
export {
  errorContainerStyles,
  errorIconStyles,
  errorTitleStyles,
  errorMessageStyles,
  errorDetailsStyles,
  errorActionsStyles,
  errorButtonBaseStyles,
  errorButtonPrimaryStyles,
  errorButtonSecondaryStyles,
  errorButtonDangerStyles,
  errorFallbackStyles,
  errorLoadingStyles,
  errorSeverityStyles,
  errorDarkThemeStyles
} from './styles';

// Default export for convenience
export { ErrorBoundary as default } from '../ErrorBoundary';
