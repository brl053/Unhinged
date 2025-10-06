// ============================================================================
// ErrorBoundary Hooks - React Hooks for Error Boundary Functionality
// ============================================================================
//
// @file hooks.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Custom React hooks for error boundary state management
//
// Etymology: "Hook" = React pattern for stateful logic
// Methodology: Composable hooks following React patterns
// ============================================================================

import React, { useState, useCallback, useEffect, useRef, useContext } from 'react';
import { 
  ErrorBoundaryState, 
  ErrorInfo, 
  UseErrorBoundaryReturn,
  ErrorReportingConfig,
  ErrorBoundaryContextType 
} from './types';
import { 
  createErrorInfo, 
  generateErrorReport, 
  shouldReportError,
  sanitizeErrorInfo 
} from './utils';
import { DEFAULT_CONFIG } from './constants';

/**
 * Hook for managing error boundary state
 * Provides state management for error boundary components
 * 
 * @param maxRetries - Maximum number of retry attempts
 * @returns Error boundary state and control functions
 */
export const useErrorBoundaryState = (
  maxRetries: number = DEFAULT_CONFIG.MAX_RETRIES
): UseErrorBoundaryReturn => {
  const [errorState, setErrorState] = useState<ErrorBoundaryState>({
    hasError: false,
    errorInfo: null,
    retryCount: 0,
    maxRetries,
    isRecovering: false,
  });
  
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  /**
   * Capture and process an error
   */
  const captureError = useCallback((
    error: Error, 
    context?: Record<string, unknown>
  ) => {
    const errorInfo = createErrorInfo(error, undefined, context);
    
    setErrorState(prevState => ({
      ...prevState,
      hasError: true,
      errorInfo,
      isRecovering: false,
    }));
    
    // Dispatch custom event for monitoring
    window.dispatchEvent(new CustomEvent('error-boundary:error-caught', {
      detail: { errorInfo },
    }));
  }, []);
  
  /**
   * Reset error boundary state
   */
  const resetError = useCallback(() => {
    setErrorState(prevState => ({
      ...prevState,
      hasError: false,
      errorInfo: null,
      retryCount: 0,
      isRecovering: false,
    }));
    
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    
    // Dispatch recovery event
    window.dispatchEvent(new CustomEvent('error-boundary:error-recovered'));
  }, []);
  
  /**
   * Retry failed operation
   */
  const retryOperation = useCallback(() => {
    if (errorState.retryCount >= errorState.maxRetries) {
      window.dispatchEvent(new CustomEvent('error-boundary:max-retries-reached'));
      return;
    }
    
    setErrorState(prevState => ({
      ...prevState,
      retryCount: prevState.retryCount + 1,
      isRecovering: true,
    }));
    
    // Dispatch retry event
    window.dispatchEvent(new CustomEvent('error-boundary:retry-attempted', {
      detail: { retryCount: errorState.retryCount + 1 },
    }));
    
    // Auto-reset after delay to trigger retry
    retryTimeoutRef.current = setTimeout(() => {
      resetError();
    }, DEFAULT_CONFIG.RETRY_DELAY);
  }, [errorState.retryCount, errorState.maxRetries, resetError]);
  
  /**
   * Report error to external service
   */
  const reportError = useCallback(() => {
    if (!errorState.errorInfo) return;
    
    // Dispatch error reporting event
    window.dispatchEvent(new CustomEvent('error-boundary:error-reported', {
      detail: { errorInfo: errorState.errorInfo },
    }));
  }, [errorState.errorInfo]);
  
  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, []);
  
  return {
    errorState,
    captureError,
    resetError,
    retryOperation,
    reportError,
  };
};

/**
 * Hook for error reporting functionality
 * Manages error reporting to external services
 * 
 * @param config - Error reporting configuration
 * @returns Error reporting functions
 */
export const useErrorReporting = (config: ErrorReportingConfig) => {
  const reportedErrorsRef = useRef<Set<string>>(new Set());
  
  /**
   * Report error to external service
   */
  const reportError = useCallback(async (errorInfo: ErrorInfo) => {
    // Prevent duplicate reporting
    if (reportedErrorsRef.current.has(errorInfo.id)) {
      return;
    }
    
    // Check if error should be reported
    if (!shouldReportError(errorInfo, config)) {
      return;
    }
    
    try {
      const sanitizedErrorInfo = sanitizeErrorInfo(errorInfo);
      const errorReport = generateErrorReport(sanitizedErrorInfo, config);
      
      if (config.endpoint && config.apiKey) {
        // Send to external service
        await fetch(config.endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${config.apiKey}`,
          },
          body: JSON.stringify(errorReport),
        });
      }
      
      // Mark as reported
      reportedErrorsRef.current.add(errorInfo.id);
      
      console.info('Error reported successfully:', errorInfo.id);
    } catch (reportingError) {
      console.error('Failed to report error:', reportingError);
    }
  }, [config]);
  
  /**
   * Clear reported errors cache
   */
  const clearReportedErrors = useCallback(() => {
    reportedErrorsRef.current.clear();
  }, []);
  
  return {
    reportError,
    clearReportedErrors,
  };
};

/**
 * Hook for error boundary metrics and monitoring
 * Tracks error boundary performance and statistics
 * 
 * @returns Metrics and monitoring functions
 */
export const useErrorBoundaryMetrics = () => {
  const [metrics, setMetrics] = useState({
    totalErrors: 0,
    errorsByCategory: {} as Record<string, number>,
    errorsBySeverity: {} as Record<string, number>,
    recoveryAttempts: 0,
    successfulRecoveries: 0,
  });
  
  /**
   * Record error occurrence
   */
  const recordError = useCallback((errorInfo: ErrorInfo) => {
    setMetrics(prevMetrics => ({
      ...prevMetrics,
      totalErrors: prevMetrics.totalErrors + 1,
      errorsByCategory: {
        ...prevMetrics.errorsByCategory,
        [errorInfo.category]: (prevMetrics.errorsByCategory[errorInfo.category] || 0) + 1,
      },
      errorsBySeverity: {
        ...prevMetrics.errorsBySeverity,
        [errorInfo.severity]: (prevMetrics.errorsBySeverity[errorInfo.severity] || 0) + 1,
      },
    }));
  }, []);
  
  /**
   * Record recovery attempt
   */
  const recordRecoveryAttempt = useCallback(() => {
    setMetrics(prevMetrics => ({
      ...prevMetrics,
      recoveryAttempts: prevMetrics.recoveryAttempts + 1,
    }));
  }, []);
  
  /**
   * Record successful recovery
   */
  const recordSuccessfulRecovery = useCallback(() => {
    setMetrics(prevMetrics => ({
      ...prevMetrics,
      successfulRecoveries: prevMetrics.successfulRecoveries + 1,
    }));
  }, []);
  
  /**
   * Calculate recovery success rate
   */
  const getRecoverySuccessRate = useCallback(() => {
    if (metrics.recoveryAttempts === 0) return 0;
    return (metrics.successfulRecoveries / metrics.recoveryAttempts) * 100;
  }, [metrics.recoveryAttempts, metrics.successfulRecoveries]);
  
  /**
   * Reset metrics
   */
  const resetMetrics = useCallback(() => {
    setMetrics({
      totalErrors: 0,
      errorsByCategory: {},
      errorsBySeverity: {},
      recoveryAttempts: 0,
      successfulRecoveries: 0,
    });
  }, []);
  
  return {
    metrics,
    recordError,
    recordRecoveryAttempt,
    recordSuccessfulRecovery,
    getRecoverySuccessRate,
    resetMetrics,
  };
};

/**
 * Hook for managing error boundary preferences
 * Handles user preferences for error boundary behavior
 * 
 * @returns Preferences state and management functions
 */
export const useErrorBoundaryPreferences = () => {
  const [preferences, setPreferences] = useState({
    showTechnicalDetails: DEFAULT_CONFIG.SHOW_TECHNICAL_DETAILS,
    autoRetry: true,
    reportingConsent: false,
    dismissedErrorTypes: [] as string[],
  });
  
  /**
   * Load preferences from local storage
   */
  const loadPreferences = useCallback(() => {
    try {
      const stored = localStorage.getItem('unhinged:error-boundary:preferences');
      if (stored) {
        const parsed = JSON.parse(stored);
        setPreferences(prevPrefs => ({ ...prevPrefs, ...parsed }));
      }
    } catch (error) {
      console.warn('Failed to load error boundary preferences:', error);
    }
  }, []);
  
  /**
   * Save preferences to local storage
   */
  const savePreferences = useCallback((newPreferences: Partial<typeof preferences>) => {
    try {
      const updated = { ...preferences, ...newPreferences };
      setPreferences(updated);
      localStorage.setItem('unhinged:error-boundary:preferences', JSON.stringify(updated));
    } catch (error) {
      console.warn('Failed to save error boundary preferences:', error);
    }
  }, [preferences]);
  
  /**
   * Toggle technical details visibility
   */
  const toggleTechnicalDetails = useCallback(() => {
    savePreferences({ showTechnicalDetails: !preferences.showTechnicalDetails });
  }, [preferences.showTechnicalDetails, savePreferences]);
  
  /**
   * Toggle auto-retry behavior
   */
  const toggleAutoRetry = useCallback(() => {
    savePreferences({ autoRetry: !preferences.autoRetry });
  }, [preferences.autoRetry, savePreferences]);
  
  /**
   * Set reporting consent
   */
  const setReportingConsent = useCallback((consent: boolean) => {
    savePreferences({ reportingConsent: consent });
  }, [savePreferences]);
  
  /**
   * Dismiss error type
   */
  const dismissErrorType = useCallback((errorType: string) => {
    const updated = [...preferences.dismissedErrorTypes, errorType];
    savePreferences({ dismissedErrorTypes: updated });
  }, [preferences.dismissedErrorTypes, savePreferences]);
  
  // Load preferences on mount
  useEffect(() => {
    loadPreferences();
  }, [loadPreferences]);
  
  return {
    preferences,
    toggleTechnicalDetails,
    toggleAutoRetry,
    setReportingConsent,
    dismissErrorType,
    savePreferences,
  };
};

/**
 * Hook for accessing error boundary context
 * Provides access to error boundary context for child components
 * 
 * @returns Error boundary context
 */
export const useErrorBoundaryContext = (): ErrorBoundaryContextType | null => {
  const context = useContext(ErrorBoundaryContext);
  return context;
};

/**
 * Hook for imperative error boundary control
 * Allows components to programmatically trigger error boundaries
 *
 * @returns Error boundary control functions
 */
export const useErrorBoundary = () => {
  const context = useErrorBoundaryContext();

  /**
   * Trigger error boundary with custom error
   */
  const triggerError = useCallback((
    error: Error | string,
    errorContext?: Record<string, unknown>
  ) => {
    const errorObj = typeof error === 'string' ? new Error(error) : error;
    if (context) {
      context.reportError(errorObj, errorContext);
    }
  }, [context]);

  return {
    triggerError,
    reportError: context?.reportError || (() => {}),
  };
};

// Create error boundary context (to be defined in main component file)
const ErrorBoundaryContext = React.createContext<ErrorBoundaryContextType | null>(null);
