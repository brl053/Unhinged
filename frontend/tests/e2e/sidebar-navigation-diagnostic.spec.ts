/**
 * @fileoverview Comprehensive Sidebar Navigation Diagnostic Test
 * 
 * @description
 * Programmatic diagnostic test to identify why sidebar navigation clicks
 * are not working in the Unhinged frontend application. Uses structured
 * error detection instead of screenshot file size analysis.
 * 
 * @test_objectives
 * 1. Validate React application mounting and health
 * 2. Verify sidebar rendering and interactive elements
 * 3. Test navigation click handlers and URL changes
 * 4. Capture comprehensive error data for LLM analysis
 * 5. Provide actionable debugging recommendations
 * 
 * @debugging_approach
 * - Programmatic state capture instead of visual inspection
 * - Structured error reporting with specific remediation steps
 * - Console log monitoring for React and JavaScript errors
 * - Network request validation for API dependencies
 * - Performance metrics collection for optimization insights
 * 
 * @llm_contract
 * This test provides structured diagnostic data that LLM agents can parse
 * to understand application failures. Output includes:
 * - Specific error types with remediation steps
 * - Confidence scores for different failure modes
 * - Complete application state snapshots
 * - Performance and timing metrics
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import { test, expect } from '@playwright/test';
import { LLMAssertions } from '../utils/llm-assertions';

/**
 * Console error collector for React and JavaScript error detection
 * 
 * @description
 * Captures all console errors, warnings, and uncaught exceptions
 * during test execution for comprehensive error analysis.
 */
interface ErrorCollector {
  errors: string[];
  warnings: string[];
  networkFailures: string[];
  uncaughtExceptions: string[];
}

/**
 * Navigation test result with detailed diagnostic information
 * 
 * @description
 * Structured result object containing navigation success status,
 * error details, performance metrics, and remediation recommendations.
 */
interface NavigationTestResult {
  success: boolean;
  initialUrl: string;
  finalUrl: string;
  navigationTime: number;
  errors: ErrorCollector;
  recommendations: string[];
  applicationState: any;
}

/**
 * Comprehensive sidebar navigation diagnostic test suite
 * 
 * @description
 * Tests sidebar navigation functionality with detailed error capture
 * and programmatic state analysis. Provides actionable debugging
 * information for LLM agents to resolve navigation issues.
 */
test.describe('Sidebar Navigation Diagnostics', () => {
  let llmAssertions: LLMAssertions;
  let errorCollector: ErrorCollector;
  
  /**
   * Test setup with comprehensive error monitoring
   * 
   * @description
   * Initializes error collectors and LLM assertions before each test.
   * Sets up event listeners for console errors, network failures,
   * and uncaught exceptions.
   */
  test.beforeEach(async ({ page }) => {
    // Initialize LLM assertions
    llmAssertions = new LLMAssertions(page);
    
    // Initialize error collector
    errorCollector = {
      errors: [],
      warnings: [],
      networkFailures: [],
      uncaughtExceptions: [],
    };
    
    // Monitor console messages
    page.on('console', msg => {
      const text = msg.text();
      const type = msg.type();
      
      if (type === 'error') {
        errorCollector.errors.push(`[CONSOLE ERROR] ${text}`);
      } else if (type === 'warning') {
        errorCollector.warnings.push(`[CONSOLE WARNING] ${text}`);
      }
    });
    
    // Monitor uncaught exceptions
    page.on('pageerror', exception => {
      errorCollector.uncaughtExceptions.push(`[UNCAUGHT EXCEPTION] ${exception.message}\n${exception.stack}`);
    });
    
    // Monitor network failures
    page.on('requestfailed', request => {
      errorCollector.networkFailures.push(`[NETWORK FAILURE] ${request.method()} ${request.url()} - ${request.failure()?.errorText}`);
    });
    
    // Navigate to application root
    await page.goto('/');
    
    // Wait for initial page load
    await page.waitForLoadState('networkidle');
  });
  
  /**
   * Primary diagnostic test for sidebar navigation functionality
   * 
   * @description
   * Comprehensive test that validates React app health, sidebar rendering,
   * navigation interactions, and captures detailed diagnostic data.
   * Designed to identify the root cause of navigation failures.
   */
  test('diagnose sidebar navigation issues with comprehensive error capture', async ({ page }) => {
    console.log('🔍 Starting comprehensive sidebar navigation diagnostic...');
    
    try {
      // Step 1: Validate React application health
      console.log('📋 Step 1: Validating React application health...');
      await llmAssertions.expectReactAppHealthy();
      console.log('✅ React application is healthy');
      
    } catch (error) {
      console.log('❌ React application health check failed:', error.message);
      
      // Capture application state for debugging
      const appState = await llmAssertions.captureApplicationState();
      console.log('📊 Application State on React Failure:', JSON.stringify(appState, null, 2));
      
      // Don't fail the test yet - continue with diagnostics
    }
    
    try {
      // Step 2: Validate sidebar rendering and interactivity
      console.log('📋 Step 2: Validating sidebar rendering and interactivity...');
      await llmAssertions.expectSidebarInteractive();
      console.log('✅ Sidebar is rendered and interactive');
      
    } catch (error) {
      console.log('❌ Sidebar interactivity check failed:', error.message);
      
      // Check if sidebar element exists at all
      const sidebarExists = await page.locator('[data-testid="sidebar"]').count();
      console.log(`📊 Sidebar element count: ${sidebarExists}`);
      
      if (sidebarExists === 0) {
        console.log('🚨 CRITICAL: Sidebar element not found in DOM');
        console.log('💡 RECOMMENDATION: Check MainLayout rendering and data-testid attributes');
      }
    }
    
    // Step 3: Test navigation functionality
    console.log('📋 Step 3: Testing navigation click functionality...');
    const navigationResult = await testNavigationClicks(page);
    
    // Step 4: Capture comprehensive application state
    console.log('📋 Step 4: Capturing comprehensive application state...');
    const finalAppState = await llmAssertions.captureApplicationState();
    
    // Step 5: Generate diagnostic report
    console.log('📋 Step 5: Generating diagnostic report...');
    const diagnosticReport = generateDiagnosticReport(navigationResult, finalAppState, errorCollector);
    
    // Output comprehensive diagnostic information
    console.log('🎯 COMPREHENSIVE DIAGNOSTIC REPORT');
    console.log('=====================================');
    console.log(JSON.stringify(diagnosticReport, null, 2));
    
    // Provide specific recommendations based on findings
    if (diagnosticReport.recommendations.length > 0) {
      console.log('💡 ACTIONABLE RECOMMENDATIONS:');
      diagnosticReport.recommendations.forEach((rec, index) => {
        console.log(`${index + 1}. ${rec}`);
      });
    }
    
    // Assert based on overall success
    if (!navigationResult.success && errorCollector.errors.length > 0) {
      throw new Error(`Navigation test failed with ${errorCollector.errors.length} errors. See diagnostic report above for details.`);
    }
  });
  
  /**
   * Focused test for individual navigation item click behavior
   * 
   * @description
   * Tests each navigation item individually to identify specific
   * items that may have broken click handlers or routing issues.
   */
  test('test individual navigation items for click responsiveness', async ({ page }) => {
    console.log('🔍 Testing individual navigation items...');
    
    // Wait for sidebar to be present
    const sidebar = page.locator('[data-testid="sidebar"]');
    await expect(sidebar).toBeVisible({ timeout: 10000 });
    
    // Get all navigation items
    const navItems = sidebar.locator('[data-testid="nav-item"]');
    const itemCount = await navItems.count();
    
    console.log(`📊 Found ${itemCount} navigation items to test`);
    
    // Test each navigation item individually
    for (let i = 0; i < itemCount; i++) {
      const item = navItems.nth(i);
      
      // Get item information
      const itemText = await item.locator('[data-testid="nav-label"]').textContent() || `Item ${i}`;
      const itemRoute = await item.getAttribute('data-route') || 'unknown';
      
      console.log(`🧪 Testing navigation item: "${itemText}" (route: ${itemRoute})`);
      
      // Record initial state
      const initialUrl = page.url();
      const startTime = Date.now();
      
      try {
        // Attempt to click the navigation item
        await item.click({ timeout: 5000 });
        
        // Wait for potential navigation
        await page.waitForTimeout(1000);
        
        // Check if URL changed
        const finalUrl = page.url();
        const navigationTime = Date.now() - startTime;
        
        if (initialUrl !== finalUrl) {
          console.log(`✅ Navigation successful: ${initialUrl} → ${finalUrl} (${navigationTime}ms)`);
        } else {
          console.log(`⚠️  Navigation attempted but URL unchanged: ${initialUrl} (${navigationTime}ms)`);
          console.log('💡 RECOMMENDATION: Check click handler attachment and navigation logic');
        }
        
      } catch (error) {
        console.log(`❌ Navigation item click failed: ${error.message}`);
        console.log('💡 RECOMMENDATION: Check element visibility, enabled state, and event handlers');
      }
      
      // Return to home page for next test
      if (page.url() !== 'http://localhost:3000/') {
        await page.goto('/');
        await page.waitForLoadState('networkidle');
      }
    }
  });
});

/**
 * Tests navigation click functionality with detailed result capture
 * 
 * @description
 * Attempts to click navigation items and measures response time,
 * URL changes, and error conditions. Returns structured result
 * object for analysis.
 * 
 * @param page - Playwright page instance
 * @returns Promise resolving to navigation test result
 */
async function testNavigationClicks(page: any): Promise<NavigationTestResult> {
  const initialUrl = page.url();
  const startTime = Date.now();
  
  try {
    // Find first navigation item
    const firstNavItem = page.locator('[data-testid="nav-item"]').first();
    const itemExists = await firstNavItem.count() > 0;
    
    if (!itemExists) {
      return {
        success: false,
        initialUrl,
        finalUrl: initialUrl,
        navigationTime: 0,
        errors: { errors: ['No navigation items found'], warnings: [], networkFailures: [], uncaughtExceptions: [] },
        recommendations: ['Check route configuration and navigation item rendering'],
        applicationState: null,
      };
    }
    
    // Attempt navigation click
    await firstNavItem.click();
    await page.waitForTimeout(1000); // Allow time for navigation
    
    const finalUrl = page.url();
    const navigationTime = Date.now() - startTime;
    
    return {
      success: initialUrl !== finalUrl,
      initialUrl,
      finalUrl,
      navigationTime,
      errors: { errors: [], warnings: [], networkFailures: [], uncaughtExceptions: [] },
      recommendations: initialUrl === finalUrl ? ['Check navigation click handlers and routing logic'] : [],
      applicationState: null,
    };
    
  } catch (error) {
    return {
      success: false,
      initialUrl,
      finalUrl: page.url(),
      navigationTime: Date.now() - startTime,
      errors: { errors: [error.message], warnings: [], networkFailures: [], uncaughtExceptions: [] },
      recommendations: ['Check element selectors and click handler implementation'],
      applicationState: null,
    };
  }
}

/**
 * Generates comprehensive diagnostic report with recommendations
 * 
 * @description
 * Analyzes test results, application state, and error data to generate
 * actionable recommendations for fixing navigation issues.
 * 
 * @param navigationResult - Navigation test results
 * @param appState - Application state snapshot
 * @param errors - Collected error data
 * @returns Structured diagnostic report
 */
function generateDiagnosticReport(
  navigationResult: NavigationTestResult,
  appState: any,
  errors: ErrorCollector
): any {
  const recommendations: string[] = [];
  
  // Analyze navigation results
  if (!navigationResult.success) {
    recommendations.push('Navigation clicks are not working - check click event handlers');
  }
  
  // Analyze application state
  if (appState.confidence.reactHealthy < 0.5) {
    recommendations.push('React application health is poor - check console for React errors');
  }
  
  if (appState.confidence.blankPage > 0.5) {
    recommendations.push('Page appears blank - check component rendering and CSS');
  }
  
  // Analyze error data
  if (errors.errors.length > 0) {
    recommendations.push(`${errors.errors.length} console errors detected - check browser console`);
  }
  
  if (errors.networkFailures.length > 0) {
    recommendations.push(`${errors.networkFailures.length} network failures detected - check API endpoints`);
  }
  
  return {
    summary: {
      navigationWorking: navigationResult.success,
      reactHealthy: appState.confidence.reactHealthy > 0.7,
      errorsDetected: errors.errors.length + errors.uncaughtExceptions.length,
      overallHealth: appState.confidence.fullyRendered,
    },
    navigationResult,
    applicationState: appState,
    errors,
    recommendations,
    timestamp: new Date().toISOString(),
  };
}
