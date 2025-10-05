// ============================================================================
// Error Boundary - React Error Boundary for Audio Components
// ============================================================================
//
// @file ErrorBoundary.tsx
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
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

// ============================================================================
// Types
// ============================================================================

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
  errorId: string;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  resetOnPropsChange?: boolean;
  resetKeys?: Array<string | number>;
}

// ============================================================================
// Styled Components
// ============================================================================

const ErrorContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  background: ${props => props.theme?.colors?.surface || '#f8f9fa'};
  border: 1px solid ${props => props.theme?.colors?.danger || '#dc3545'}20;
  border-radius: 8px;
  margin: 20px 0;
`;

const ErrorIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
`;

const ErrorTitle = styled.h3`
  margin: 0 0 12px 0;
  color: ${props => props.theme?.colors?.danger || '#dc3545'};
  font-size: 20px;
  font-weight: 600;
`;

const ErrorMessage = styled.p`
  margin: 0 0 20px 0;
  color: ${props => props.theme?.colors?.text || '#212529'};
  font-size: 16px;
  line-height: 1.5;
  max-width: 500px;
`;

const ErrorDetails = styled.details`
  margin: 16px 0;
  padding: 12px;
  background: ${props => props.theme?.colors?.background || '#ffffff'};
  border: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
  text-align: left;
  max-width: 600px;
  
  summary {
    cursor: pointer;
    font-weight: 600;
    margin-bottom: 8px;
    color: ${props => props.theme?.colors?.muted || '#6c757d'};
  }
  
  pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
  }
`;

const ErrorActions = styled.div`
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
`;

const ErrorButton = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: 10px 20px;
  border-radius: 6px;
  border: 1px solid ${props => 
    props.variant === 'primary' 
      ? props.theme?.colors?.primary || '#007bff'
      : props.theme?.colors?.border || '#dee2e6'
  };
  background: ${props => 
    props.variant === 'primary' 
      ? props.theme?.colors?.primary || '#007bff'
      : props.theme?.colors?.surface || '#f8f9fa'
  };
  color: ${props => 
    props.variant === 'primary' 
      ? '#ffffff'
      : props.theme?.colors?.text || '#212529'
  };
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
  
  &:hover {
    background: ${props => 
      props.variant === 'primary' 
        ? props.theme?.colors?.primaryDark || '#0056b3'
        : props.theme?.colors?.hover || '#e9ecef'
    };
  }
`;

// ============================================================================
// Error Boundary Component
// ============================================================================

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private resetTimeoutId: number | null = null;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: '',
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
      errorId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({
      error,
      errorInfo,
    });

    // Call error handler if provided
    this.props.onError?.(error, errorInfo);

    // Log error for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // Report error to monitoring service (if available)
    this.reportError(error, errorInfo);
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

  private reportError = (error: Error, errorInfo: React.ErrorInfo) => {
    // In a real application, you would send this to your error reporting service
    // For example: Sentry, LogRocket, Bugsnag, etc.
    
    const errorReport = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      errorId: this.state.errorId,
    };

    // Example: Send to monitoring service
    // monitoringService.reportError(errorReport);
    
    console.warn('Error report generated:', errorReport);
  };

  private resetErrorBoundary = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: '',
    });
  };

  private handleRetry = () => {
    this.resetErrorBoundary();
  };

  private handleReload = () => {
    window.location.reload();
  };

  private handleReportIssue = () => {
    const { error, errorInfo, errorId } = this.state;
    
    const issueBody = encodeURIComponent(`
**Error ID:** ${errorId}
**Error Message:** ${error?.message || 'Unknown error'}
**URL:** ${window.location.href}
**Timestamp:** ${new Date().toISOString()}
**User Agent:** ${navigator.userAgent}

**Stack Trace:**
\`\`\`
${error?.stack || 'No stack trace available'}
\`\`\`

**Component Stack:**
\`\`\`
${errorInfo?.componentStack || 'No component stack available'}
\`\`\`

**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Behavior:**


**Actual Behavior:**

    `.trim());

    const issueUrl = `https://github.com/your-org/unhinged/issues/new?title=${encodeURIComponent(`Audio Error: ${error?.message || 'Unknown error'}`)}&body=${issueBody}`;
    
    window.open(issueUrl, '_blank');
  };

  private getErrorMessage = (error: Error): string => {
    // Provide user-friendly messages for common audio errors
    const message = error.message.toLowerCase();
    
    if (message.includes('microphone') || message.includes('getusermedia')) {
      return 'Unable to access your microphone. Please check your browser permissions and try again.';
    }
    
    if (message.includes('audio') && message.includes('not supported')) {
      return 'Audio features are not supported in your current browser. Please try using a modern browser like Chrome, Firefox, or Safari.';
    }
    
    if (message.includes('network') || message.includes('fetch')) {
      return 'Network connection error. Please check your internet connection and try again.';
    }
    
    if (message.includes('grpc') || message.includes('service')) {
      return 'Audio service is temporarily unavailable. Please try again in a few moments.';
    }
    
    return 'An unexpected error occurred while processing audio. Please try again.';
  };

  render() {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback } = this.props;

    if (hasError) {
      // Use custom fallback if provided
      if (fallback) {
        return fallback;
      }

      // Default error UI
      return (
        <ErrorContainer>
          <ErrorIcon>🎵💥</ErrorIcon>
          
          <ErrorTitle>Audio System Error</ErrorTitle>
          
          <ErrorMessage>
            {error ? this.getErrorMessage(error) : 'An unknown error occurred.'}
          </ErrorMessage>

          <ErrorActions>
            <ErrorButton variant="primary" onClick={this.handleRetry}>
              Try Again
            </ErrorButton>
            
            <ErrorButton onClick={this.handleReload}>
              Reload Page
            </ErrorButton>
            
            <ErrorButton onClick={this.handleReportIssue}>
              Report Issue
            </ErrorButton>
          </ErrorActions>

          {process.env.NODE_ENV === 'development' && error && (
            <ErrorDetails>
              <summary>Technical Details (Development)</summary>
              <pre>
                <strong>Error:</strong> {error.message}
                {'\n\n'}
                <strong>Stack Trace:</strong>
                {'\n'}
                {error.stack}
                {'\n\n'}
                <strong>Component Stack:</strong>
                {'\n'}
                {errorInfo?.componentStack}
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
  <ErrorContainer>
    <ErrorIcon>🎤❌</ErrorIcon>
    <ErrorTitle>Audio Feature Unavailable</ErrorTitle>
    <ErrorMessage>
      {error?.message || 'Audio features are currently unavailable. This might be due to browser permissions or device limitations.'}
    </ErrorMessage>
    {onRetry && (
      <ErrorActions>
        <ErrorButton variant="primary" onClick={onRetry}>
          Try Again
        </ErrorButton>
      </ErrorActions>
    )}
  </ErrorContainer>
);

export const MicrophoneErrorFallback: React.FC<{ onRetry?: () => void }> = ({ onRetry }) => (
  <ErrorContainer>
    <ErrorIcon>🎤🚫</ErrorIcon>
    <ErrorTitle>Microphone Access Required</ErrorTitle>
    <ErrorMessage>
      To use voice features, please allow microphone access in your browser settings and refresh the page.
    </ErrorMessage>
    {onRetry && (
      <ErrorActions>
        <ErrorButton variant="primary" onClick={onRetry}>
          Request Access
        </ErrorButton>
      </ErrorActions>
    )}
  </ErrorContainer>
);

export default ErrorBoundary;
