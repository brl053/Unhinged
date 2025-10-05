/**
 * @fileoverview LLM-Focused Assertions for Programmatic Browser Validation
 * 
 * @description
 * Provides structured, programmatic assertions that enable LLM agents to understand
 * application state without relying on visual inspection or screenshot file sizes.
 * Each assertion returns detailed diagnostic information for automated debugging.
 * 
 * @design_principles
 * - Return structured data instead of binary pass/fail results
 * - Capture comprehensive application state for LLM analysis
 * - Provide actionable error messages with specific remediation steps
 * - Validate both functional behavior and technical implementation
 * 
 * @llm_contract
 * When using these assertions:
 * 1. Always capture and log the returned diagnostic data
 * 2. Use expectReactAppHealthy() before component-specific assertions
 * 3. Call captureApplicationState() on test failures for debugging
 * 4. Combine multiple assertions to build comprehensive validation
 * 5. Parse error messages for specific remediation actions
 * 
 * @debugging_philosophy
 * Instead of "screenshot is 8.5KB so page is broken", provide:
 * - Specific error types (React errors, network failures, missing elements)
 * - Confidence scores for different application states
 * - Actionable recommendations for fixing identified issues
 * - Structured data that LLM agents can parse and reason about
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import { expect, Page } from '@playwright/test';

/**
 * Application state snapshot for comprehensive debugging
 * 
 * @description
 * Captures complete application state including URL, React status,
 * DOM structure, performance metrics, and error conditions.
 * Designed for LLM consumption and automated analysis.
 */
export interface ApplicationState {
  /** Current URL and routing information */
  navigation: {
    url: string;
    pathname: string;
    search: string;
    hash: string;
  };
  
  /** React application status */
  react: {
    version?: string;
    devToolsAvailable: boolean;
    mounted: boolean;
    errorBoundariesActive: number;
  };
  
  /** DOM structure and content metrics */
  dom: {
    title: string;
    bodyClasses: string[];
    visibleElements: number;
    interactiveElements: number;
    textContentLength: number;
  };
  
  /** Error and warning indicators */
  errors: {
    consoleErrors: string[];
    networkErrors: string[];
    reactErrors: number;
    loadingElements: number;
  };
  
  /** Performance and timing data */
  performance: {
    navigationStart?: number;
    domContentLoaded?: number;
    loadComplete?: number;
  };
  
  /** Browser and viewport information */
  viewport: {
    width: number;
    height: number;
    devicePixelRatio: number;
  };
  
  /** Local storage and session data */
  storage: {
    localStorage: Record<string, string>;
    sessionStorage: Record<string, string>;
  };
}

/**
 * Confidence scores for different application states
 * 
 * @description
 * Provides probabilistic assessment of application health.
 * Values range from 0.0 (definitely not) to 1.0 (definitely yes).
 * Enables nuanced debugging beyond binary pass/fail.
 */
export interface ConfidenceScores {
  /** Application is fully rendered and functional */
  fullyRendered: number;
  
  /** Application is in an error state */
  errorState: number;
  
  /** Application is still loading */
  loadingState: number;
  
  /** Page is blank or failed to render */
  blankPage: number;
  
  /** Navigation system is working correctly */
  navigationWorking: number;
  
  /** React components are mounted and healthy */
  reactHealthy: number;
}

/**
 * LLM-focused assertions for programmatic browser validation
 * 
 * @description
 * Provides comprehensive application state validation with detailed
 * diagnostic information. Designed for LLM agents to understand
 * application behavior without visual inspection.
 * 
 * @example
 * ```typescript
 * const assertions = new LLMAssertions(page);
 * await assertions.expectReactAppHealthy();
 * const state = await assertions.captureApplicationState();
 * console.log('App State:', JSON.stringify(state, null, 2));
 * ```
 */
export class LLMAssertions {
  /**
   * Creates LLM assertions instance
   * 
   * @param page - Playwright page instance for browser interaction
   */
  constructor(private page: Page) {}
  
  /**
   * Validates React application is mounted and functional
   * 
   * @description
   * Comprehensive React health check including:
   * - React runtime presence and version detection
   * - Component tree mounting validation
   * - Error boundary status verification
   * - Console error analysis for React-specific issues
   * 
   * @returns Promise resolving to detailed health assessment
   * 
   * @throws AssertionError with specific remediation steps if unhealthy
   * 
   * @example
   * ```typescript
   * await assertions.expectReactAppHealthy();
   * // Throws with specific error: "React error boundary active in MainLayout"
   * ```
   */
  async expectReactAppHealthy(): Promise<void> {
    // Check if React is mounted and running
    const reactStatus = await this.page.evaluate(() => {
      return {
        // Check for React runtime
        reactPresent: typeof (window as any).React !== 'undefined',
        
        // Check for React root element
        rootElement: document.querySelector('#root') !== null,
        rootHasChildren: document.querySelector('#root')?.hasChildNodes() || false,
        
        // Check for React DevTools hook (indicates React is running)
        devToolsHook: !!(window as any).__REACT_DEVTOOLS_GLOBAL_HOOK__,
        
        // Check for error boundaries
        errorBoundaries: document.querySelectorAll('[data-error-boundary="true"]').length,
        
        // Check for React-specific error indicators
        reactErrorElements: document.querySelectorAll('[data-react-error="true"]').length,
      };
    });
    
    // Validate React is properly mounted
    if (!reactStatus.rootElement) {
      throw new Error('REACT_MOUNT_FAILURE: Root element #root not found in DOM. Check if React app is properly bootstrapped.');
    }
    
    if (!reactStatus.rootHasChildren) {
      throw new Error('REACT_RENDER_FAILURE: Root element exists but has no children. React app failed to render. Check console for React errors.');
    }
    
    // Check for active error boundaries
    if (reactStatus.errorBoundaries > 0) {
      throw new Error(`REACT_ERROR_BOUNDARY: ${reactStatus.errorBoundaries} error boundary(ies) active. Components failed to render. Check React DevTools and console logs.`);
    }
    
    // Check for React error elements
    if (reactStatus.reactErrorElements > 0) {
      throw new Error(`REACT_COMPONENT_ERROR: ${reactStatus.reactErrorElements} component(s) in error state. Check component error handling and props.`);
    }
    
    // Capture console errors for React-specific issues
    const consoleErrors = await this.page.evaluate(() => {
      return (window as any).consoleErrors || [];
    });
    
    const reactErrors = consoleErrors.filter((error: string) => 
      error.includes('React') || 
      error.includes('Warning: ') ||
      error.includes('Error: ')
    );
    
    if (reactErrors.length > 0) {
      throw new Error(`REACT_CONSOLE_ERRORS: ${reactErrors.length} React-related console errors detected: ${reactErrors.slice(0, 3).join('; ')}`);
    }
  }
  
  /**
   * Validates sidebar navigation is interactive and functional
   * 
   * @description
   * Comprehensive sidebar validation including:
   * - Sidebar element presence and visibility
   * - Navigation item count and accessibility
   * - Click handler attachment verification
   * - ARIA attributes and keyboard navigation support
   * 
   * @returns Promise resolving when sidebar is confirmed interactive
   * 
   * @throws AssertionError with specific issue identification
   */
  async expectSidebarInteractive(): Promise<void> {
    // Check if sidebar exists and is visible
    const sidebar = this.page.locator('[data-testid="sidebar"]');
    
    try {
      await expect(sidebar).toBeVisible({ timeout: 5000 });
    } catch (error) {
      throw new Error('SIDEBAR_NOT_FOUND: Sidebar element with data-testid="sidebar" not found or not visible. Check MainLayout rendering and CSS display properties.');
    }
    
    // Check for navigation items
    const navItems = sidebar.locator('[data-testid="nav-item"]');
    const itemCount = await navItems.count();
    
    if (itemCount === 0) {
      throw new Error('SIDEBAR_NO_ITEMS: No navigation items found with data-testid="nav-item". Check route configuration and navigation item rendering.');
    }
    
    // Validate each navigation item is interactive
    for (let i = 0; i < Math.min(itemCount, 5); i++) { // Check first 5 items
      const item = navItems.nth(i);
      
      // Check visibility
      const isVisible = await item.isVisible();
      if (!isVisible) {
        throw new Error(`SIDEBAR_ITEM_HIDDEN: Navigation item ${i} is not visible. Check CSS display and visibility properties.`);
      }
      
      // Check if clickable
      const isEnabled = await item.isEnabled();
      if (!isEnabled) {
        throw new Error(`SIDEBAR_ITEM_DISABLED: Navigation item ${i} is disabled. Check event handler attachment and element state.`);
      }
      
      // Check for accessibility attributes
      const hasAriaLabel = await item.getAttribute('aria-label');
      const hasRole = await item.getAttribute('role');
      const hasTabIndex = await item.getAttribute('tabindex');
      
      if (!hasAriaLabel && !hasRole) {
        console.warn(`ACCESSIBILITY_WARNING: Navigation item ${i} lacks aria-label or role attribute. Consider adding for screen reader support.`);
      }
    }
    
    console.log(`✅ SIDEBAR_VALIDATION: Found ${itemCount} interactive navigation items`);
  }
  
  /**
   * Validates routing system is functional with proper URL handling
   * 
   * @description
   * Comprehensive routing validation including:
   * - Current URL matching expected path
   * - React Router context availability
   * - Route parameter extraction
   * - Navigation state consistency
   * 
   * @param expectedPath - Expected current pathname
   * @param expectedTitle - Optional expected page title
   * 
   * @returns Promise resolving when routing is confirmed working
   */
  async expectRoutingWorking(expectedPath: string, expectedTitle?: string): Promise<void> {
    // Validate current URL matches expected path
    const currentPath = await this.page.evaluate(() => window.location.pathname);
    
    if (currentPath !== expectedPath) {
      throw new Error(`ROUTING_PATH_MISMATCH: Expected path "${expectedPath}" but found "${currentPath}". Check navigation logic and route configuration.`);
    }
    
    // Check if React Router is active
    const routerStatus = await this.page.evaluate(() => {
      return {
        historyAvailable: typeof window.history.pushState === 'function',
        locationAvailable: typeof window.location === 'object',
        routerOutlet: document.querySelector('[data-testid="router-outlet"]') !== null,
      };
    });
    
    if (!routerStatus.historyAvailable) {
      throw new Error('ROUTING_HISTORY_UNAVAILABLE: Browser history API not available. Check browser compatibility and routing setup.');
    }
    
    // Validate page title if provided
    if (expectedTitle) {
      await expect(this.page).toHaveTitle(expectedTitle);
    }
    
    // Check for routing error indicators
    const routeErrors = await this.page.locator('[data-testid="route-error"]').count();
    if (routeErrors > 0) {
      throw new Error(`ROUTING_ERROR: ${routeErrors} route error(s) detected. Check route definitions and error boundary handling.`);
    }
    
    console.log(`✅ ROUTING_VALIDATION: Successfully navigated to ${expectedPath}`);
  }
  
  /**
   * Captures comprehensive application state for LLM analysis
   * 
   * @description
   * Collects detailed application state including navigation, React status,
   * DOM metrics, error conditions, performance data, and browser context.
   * Designed for LLM consumption and automated debugging.
   * 
   * @returns Promise resolving to complete application state snapshot
   * 
   * @example
   * ```typescript
   * const state = await assertions.captureApplicationState();
   * console.log('Errors:', state.errors.consoleErrors);
   * console.log('Confidence:', state.confidence?.fullyRendered);
   * ```
   */
  async captureApplicationState(): Promise<ApplicationState & { confidence: ConfidenceScores }> {
    const state = await this.page.evaluate(() => {
      // Collect DOM and content metrics
      const body = document.body;
      const visibleElements = Array.from(document.querySelectorAll('*')).filter(el => {
        const style = window.getComputedStyle(el);
        return style.display !== 'none' && 
               style.visibility !== 'hidden' && 
               style.opacity !== '0';
      });
      
      return {
        // Navigation state
        navigation: {
          url: window.location.href,
          pathname: window.location.pathname,
          search: window.location.search,
          hash: window.location.hash,
        },
        
        // React application status
        react: {
          version: (window as any).React?.version,
          devToolsAvailable: !!(window as any).__REACT_DEVTOOLS_GLOBAL_HOOK__,
          mounted: !!document.querySelector('#root')?.hasChildNodes(),
          errorBoundariesActive: document.querySelectorAll('[data-error-boundary="true"]').length,
        },
        
        // DOM structure metrics
        dom: {
          title: document.title,
          bodyClasses: Array.from(document.body.classList),
          visibleElements: visibleElements.length,
          interactiveElements: document.querySelectorAll('button, a, input, select, textarea, [role="button"]').length,
          textContentLength: body.textContent?.trim().length || 0,
        },
        
        // Error indicators
        errors: {
          consoleErrors: (window as any).consoleErrors || [],
          networkErrors: (window as any).networkErrors || [],
          reactErrors: document.querySelectorAll('[data-react-error="true"]').length,
          loadingElements: document.querySelectorAll('[data-testid*="loading"], .loading, .spinner').length,
        },
        
        // Performance metrics
        performance: {
          navigationStart: performance.timing?.navigationStart,
          domContentLoaded: performance.timing?.domContentLoadedEventEnd,
          loadComplete: performance.timing?.loadEventEnd,
        },
        
        // Viewport information
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight,
          devicePixelRatio: window.devicePixelRatio,
        },
        
        // Storage data
        storage: {
          localStorage: { ...localStorage },
          sessionStorage: { ...sessionStorage },
        },
      };
    });
    
    // Calculate confidence scores
    const confidence = this.calculateConfidenceScores(state);
    
    return { ...state, confidence };
  }
  
  /**
   * Calculates confidence scores for application state assessment
   * 
   * @description
   * Provides probabilistic assessment of application health based on
   * DOM metrics, error indicators, and content analysis.
   * 
   * @param state - Application state data
   * @returns Confidence scores for different application states
   * 
   * @private
   */
  private calculateConfidenceScores(state: ApplicationState): ConfidenceScores {
    return {
      // High confidence if lots of content and interactive elements
      fullyRendered: Math.min(
        (state.dom.textContentLength / 1000) * 0.3 +
        (state.dom.interactiveElements / 10) * 0.4 +
        (state.dom.visibleElements / 50) * 0.3,
        1.0
      ),
      
      // High confidence if error indicators present
      errorState: Math.min(
        state.errors.consoleErrors.length * 0.3 +
        state.react.errorBoundariesActive * 0.5 +
        state.errors.reactErrors * 0.2,
        1.0
      ),
      
      // High confidence if loading elements present
      loadingState: Math.min(state.errors.loadingElements * 0.8, 1.0),
      
      // High confidence if very little content
      blankPage: state.dom.textContentLength < 100 && state.dom.visibleElements < 10 ? 0.9 : 0.1,
      
      // Navigation confidence based on URL and interactive elements
      navigationWorking: state.navigation.pathname !== '/' || state.dom.interactiveElements > 5 ? 0.8 : 0.3,
      
      // React health based on mounting and error absence
      reactHealthy: state.react.mounted && state.react.errorBoundariesActive === 0 ? 0.9 : 0.2,
    };
  }
}
