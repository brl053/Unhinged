// ============================================================================
// Error Boundary - React Error Boundary for Audio Components
// ============================================================================
//
// @file ErrorBoundary.tsx
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description React Error Boundary with comprehensive error handling
//
// This component provides comprehensive error handling for the audio system:
// - React Error Boundary for component errors
// - Audio-specific error handling and recovery
// - User-friendly error messages and recovery options
// - Error reporting and logging
// - Fallback UI components
// ============================================================================

import React, { Component, ReactNode } from 'react';
import styled from 'styled-components';
import {
  ErrorBoundaryProps,
  ErrorBoundaryState,
  ErrorInfo,
  ErrorReportingConfig
} from './ErrorBoundary/types';
import {
  createErrorInfo,
  generateGitHubIssueUrl,
  shouldReportError,
  sanitizeErrorInfo
} from './ErrorBoundary/utils';
import {
  DEFAULT_CONFIG,
  ERROR_CATEGORY_METADATA,
  RECOVERY_STRATEGY_METADATA
} from './ErrorBoundary/constants';
import {
  errorContainerStyles,
  errorIconStyles,
  errorTitleStyles,
  errorMessageStyles,
  errorDetailsStyles,
  errorActionsStyles,
  errorButtonPrimaryStyles,
  errorButtonSecondaryStyles,
  errorSeverityStyles
} from './ErrorBoundary/styles';

// ============================================================================
// Styled Components
// ============================================================================

const ErrorContainer = styled.div<{ severity?: string; category?: string }>`
  ${errorContainerStyles}
  ${props => props.severity && errorSeverityStyles[props.severity as keyof typeof errorSeverityStyles]}
`;

const ErrorIcon = styled.div`
  ${errorIconStyles}
`;

const ErrorTitle = styled.h3`
  ${errorTitleStyles}
`;

const ErrorMessage = styled.p`
  ${errorMessageStyles}
`;

const ErrorDetails = styled.details`
  ${errorDetailsStyles}
`;

const ErrorActions = styled.div`
  ${errorActionsStyles}
`;

const ErrorButton = styled.button<{ variant?: 'primary' | 'secondary' | 'danger' }>`
  ${props => {
    switch (props.variant) {
      case 'primary':
        return errorButtonPrimaryStyles;
      case 'danger':
        return errorButtonSecondaryStyles; // We'll add danger styles later
      default:
        return errorButtonSecondaryStyles;
    }
  }}
`;

// ============================================================================
// Error Boundary Component
// ============================================================================

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private resetTimeoutId: number | null = null;
  private errorReportingConfig: ErrorReportingConfig;

  constructor(props: ErrorBoundaryProps) {
    super(props);

    this.state = {
      hasError: false,
      errorInfo: null,
      retryCount: 0,
      maxRetries: props.maxRetries || DEFAULT_CONFIG.MAX_RETRIES,
      isRecovering: false,
    };

    this.errorReportingConfig = {
      enabled: DEFAULT_CONFIG.ERROR_REPORTING_ENABLED,
      includeUserAgent: true,
      includeUrl: true,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      isRecovering: false,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    const errorInfoObj = createErrorInfo(error, errorInfo.componentStack || undefined);

    this.setState({
      errorInfo: errorInfoObj,
    });

    // Call error handler if provided
    this.props.onError?.(errorInfoObj);

    // Log error for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // Report error to monitoring service
    this.reportError(errorInfoObj);
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    const { resetOnPropsChange, resetKeys } = this.props;
    const { hasError } = this.state;

    // Reset error state if resetKeys changed
    if (hasError && resetOnPropsChange && resetKeys) {
      const prevResetKeys = prevProps.resetKeys || [];
      const hasResetKeyChanged = resetKeys.some(
        (key, index) => key !== prevResetKeys[index]
      );

      if (hasResetKeyChanged) {
        this.resetErrorBoundary();
      }
    }
  }

  componentWillUnmount() {
    if (this.resetTimeoutId) {
      clearTimeout(this.resetTimeoutId);
    }
  }

  private reportError = (errorInfo: ErrorInfo) => {
    if (!shouldReportError(errorInfo, this.errorReportingConfig)) {
      return;
    }

    const sanitizedErrorInfo = sanitizeErrorInfo(errorInfo);

    // Log error for debugging
    console.warn('Error report generated:', sanitizedErrorInfo);

    // In a real application, you would send this to your error reporting service
    // For example: Sentry, LogRocket, Bugsnag, etc.
    // monitoringService.reportError(sanitizedErrorInfo);
  };

  private resetErrorBoundary = () => {
    this.setState({
      hasError: false,
      errorInfo: null,
      retryCount: 0,
      isRecovering: false,
    });
  };

  private handleRetry = () => {
    if (this.state.retryCount >= this.state.maxRetries) {
      return;
    }

    this.setState(prevState => ({
      retryCount: prevState.retryCount + 1,
      isRecovering: true,
    }));

    // Reset after a delay to trigger retry
    setTimeout(() => {
      this.resetErrorBoundary();
    }, DEFAULT_CONFIG.RETRY_DELAY);
  };

  private handleReload = () => {
    window.location.reload();
  };

  private handleReportIssue = () => {
    const { errorInfo } = this.state;

    if (!errorInfo) return;

    const issueUrl = generateGitHubIssueUrl(errorInfo);
    window.open(issueUrl, '_blank');
  };

  private getErrorIcon = (category: string): string => {
    const metadata = ERROR_CATEGORY_METADATA[category as keyof typeof ERROR_CATEGORY_METADATA];
    return metadata?.icon || '❓';
  };

  private getRecoveryActions = (errorInfo: ErrorInfo) => {
    return errorInfo.recoveryStrategies.map(strategy => {
      const metadata = RECOVERY_STRATEGY_METADATA[strategy];
      return {
        strategy,
        label: metadata.label,
        icon: metadata.icon,
        variant: metadata.buttonVariant,
      };
    });
  };

  render() {
    const { hasError, errorInfo, retryCount, maxRetries, isRecovering } = this.state;
    const { children, fallback, showTechnicalDetails } = this.props;

    if (hasError && errorInfo) {
      // Use custom fallback if provided
      if (fallback) {
        return typeof fallback === 'function' ? fallback(errorInfo) : fallback;
      }

      const recoveryActions = this.getRecoveryActions(errorInfo);
      const canRetry = retryCount < maxRetries;

      // Default error UI
      return (
        <ErrorContainer
          severity={errorInfo.severity}
          category={errorInfo.category}
          data-error-id={errorInfo.id}
          data-error-category={errorInfo.category}
          data-error-severity={errorInfo.severity}
          data-retry-count={retryCount}
          data-has-error="true"
          data-can-retry={canRetry}
        >
          <ErrorIcon>{this.getErrorIcon(errorInfo.category)}</ErrorIcon>

          <ErrorTitle>
            {ERROR_CATEGORY_METADATA[errorInfo.category as keyof typeof ERROR_CATEGORY_METADATA]?.description || 'System Error'}
          </ErrorTitle>

          <ErrorMessage>
            {errorInfo.message}
          </ErrorMessage>

          {isRecovering && (
            <ErrorMessage>
              Attempting to recover... (Attempt {retryCount + 1} of {maxRetries})
            </ErrorMessage>
          )}

          <ErrorActions>
            {recoveryActions.map(action => {
              if (action.strategy === 'retry' && !canRetry) return null;

              return (
                <ErrorButton
                  key={action.strategy}
                  variant={action.variant as 'primary' | 'secondary'}
                  onClick={() => {
                    switch (action.strategy) {
                      case 'retry':
                        this.handleRetry();
                        break;
                      case 'reload':
                        this.handleReload();
                        break;
                      case 'report':
                        this.handleReportIssue();
                        break;
                      default:
                        break;
                    }
                  }}
                  disabled={isRecovering}
                >
                  {action.icon} {action.label}
                </ErrorButton>
              );
            })}
          </ErrorActions>

          {(showTechnicalDetails || process.env.NODE_ENV === 'development') && (
            <ErrorDetails>
              <summary>Technical Details</summary>
              <pre>
                <strong>Error ID:</strong> {errorInfo.id}
                {'\n'}
                <strong>Category:</strong> {errorInfo.category}
                {'\n'}
                <strong>Severity:</strong> {errorInfo.severity}
                {'\n'}
                <strong>Timestamp:</strong> {errorInfo.timestamp}
                {'\n\n'}
                <strong>Message:</strong> {errorInfo.technicalMessage}
                {'\n\n'}
                <strong>Stack Trace:</strong>
                {'\n'}
                {errorInfo.stack}
                {'\n\n'}
                <strong>Component Stack:</strong>
                {'\n'}
                {errorInfo.componentStack}
              </pre>
            </ErrorDetails>
          )}
        </ErrorContainer>
      );
    }

    return children;
  }
}

// ============================================================================
// Higher-Order Component for Audio Error Handling
// ============================================================================

export function withAudioErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<ErrorBoundaryProps, 'children'>
) {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withAudioErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
}

// ============================================================================
// Audio-Specific Error Components
// ============================================================================

export const AudioErrorFallback: React.FC<{ error?: Error; onRetry?: () => void }> = ({
  error,
  onRetry,
}) => (
  <ErrorContainer category="audio" severity="medium">
    <ErrorIcon>🎤❌</ErrorIcon>
    <ErrorTitle>Audio Feature Unavailable</ErrorTitle>
    <ErrorMessage>
      {error?.message || 'Audio features are currently unavailable. This might be due to browser permissions or device limitations.'}
    </ErrorMessage>
    {onRetry && (
      <ErrorActions>
        <ErrorButton variant="primary" onClick={onRetry}>
          🔄 Try Again
        </ErrorButton>
      </ErrorActions>
    )}
  </ErrorContainer>
);

export const MicrophoneErrorFallback: React.FC<{ onRetry?: () => void }> = ({ onRetry }) => (
  <ErrorContainer category="permission" severity="high">
    <ErrorIcon>🎤🚫</ErrorIcon>
    <ErrorTitle>Microphone Access Required</ErrorTitle>
    <ErrorMessage>
      To use voice features, please allow microphone access in your browser settings and refresh the page.
    </ErrorMessage>
    {onRetry && (
      <ErrorActions>
        <ErrorButton variant="primary" onClick={onRetry}>
          🔓 Request Access
        </ErrorButton>
      </ErrorActions>
    )}
  </ErrorContainer>
);

export default ErrorBoundary;
