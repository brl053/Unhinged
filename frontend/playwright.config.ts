/**
 * @fileoverview Playwright Configuration for Unhinged Frontend Testing
 * 
 * @description
 * Production-ready Playwright configuration optimized for React TypeScript applications.
 * Provides comprehensive browser testing with error capture, performance monitoring,
 * and visual regression testing capabilities.
 * 
 * @design_principles
 * - Fail fast in development (retries: 0) to catch flaky tests early
 * - Comprehensive error capture (traces, screenshots, videos) for debugging
 * - Cross-browser testing for compatibility validation
 * - Automatic dev server management for seamless testing workflow
 * 
 * @llm_contract
 * When modifying this configuration:
 * 1. Maintain baseURL consistency with development server
 * 2. Keep trace capture on first retry only (performance optimization)
 * 3. Preserve webServer configuration for automatic server management
 * 4. Update timeout values based on application complexity
 * 5. Add new projects for additional browser/device testing
 * 
 * @performance_considerations
 * - fullyParallel: true enables concurrent test execution
 * - workers: 1 in CI prevents resource contention
 * - retries: 2 in CI handles transient failures
 * - trace: 'on-first-retry' balances debugging with performance
 * 
 * @debugging_features
 * - HTML reporter with detailed test results and screenshots
 * - JSON reporter for programmatic analysis by LLM agents
 * - JUnit reporter for CI/CD integration
 * - Video capture on failure for visual debugging
 * - Network request logging for API validation
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration object
 * 
 * @description
 * Configures Playwright for comprehensive testing of the Unhinged React application.
 * Includes cross-browser testing, mobile emulation, and automatic dev server management.
 * 
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  /**
   * Test directory containing all test files
   * 
   * @description
   * All test files should be placed in the ./tests directory.
   * Supports nested directories for organization (e2e/, component/, unit/).
   */
  testDir: './tests',
  
  /**
   * Output directory for test results and artifacts
   * 
   * @description
   * Contains test reports, screenshots, videos, and traces.
   * Automatically cleaned before each test run.
   */
  outputDir: './test-results',
  
  /**
   * Global test timeout in milliseconds
   * 
   * @description
   * Maximum time allowed for each individual test.
   * Increase for complex user flows or slow network conditions.
   * 
   * @default 30000 (30 seconds)
   */
  timeout: 30 * 1000,
  
  /**
   * Assertion timeout configuration
   * 
   * @description
   * Controls how long Playwright waits for assertions to pass.
   * Separate timeout for screenshot comparisons to handle rendering delays.
   */
  expect: {
    /**
     * Default assertion timeout
     * 
     * @description
     * Time to wait for expect() assertions to pass.
     * Applies to element visibility, text content, etc.
     */
    timeout: 5 * 1000,
    
    /**
     * Screenshot comparison configuration
     * 
     * @description
     * Controls visual regression testing behavior.
     * maxDiffPixels allows minor rendering differences.
     * animations: 'disabled' ensures consistent screenshots.
     */
    toHaveScreenshot: {
      maxDiffPixels: 100,
      animations: 'disabled',
      mode: 'pixel',
    },
  },
  
  /**
   * Parallel execution configuration
   * 
   * @description
   * Enables concurrent test execution for faster feedback.
   * Tests within the same file run sequentially for predictable state.
   */
  fullyParallel: true,
  
  /**
   * CI/CD environment detection
   * 
   * @description
   * Prevents .only() tests from running in CI to avoid incomplete test suites.
   * Ensures all tests run in production environments.
   */
  forbidOnly: !!process.env.CI,
  
  /**
   * Retry configuration
   * 
   * @description
   * Retries failed tests to handle transient failures.
   * 0 retries locally to catch flaky tests during development.
   * 2 retries in CI to handle infrastructure instability.
   */
  retries: process.env.CI ? 2 : 0,
  
  /**
   * Worker process configuration
   * 
   * @description
   * Controls parallel test execution.
   * Single worker in CI prevents resource contention.
   * Automatic worker count locally based on CPU cores.
   */
  workers: process.env.CI ? 1 : undefined,
  
  /**
   * Test reporting configuration
   * 
   * @description
   * Multiple reporters provide different views of test results:
   * - HTML: Interactive report with screenshots and traces
   * - JSON: Machine-readable results for LLM analysis
   * - JUnit: CI/CD integration format
   */
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],
  
  /**
   * Global test configuration
   * 
   * @description
   * Default settings applied to all tests unless overridden.
   * Includes base URL, debugging artifacts, and browser context options.
   */
  use: {
    /**
     * Base URL for all page.goto() calls
     * 
     * @description
     * Automatically prepended to relative URLs in tests.
     * Should match the development server URL.
     */
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    
    /**
     * Trace capture configuration
     * 
     * @description
     * Records detailed execution traces for debugging.
     * 'on-first-retry' balances debugging capability with performance.
     * Traces include DOM snapshots, network requests, and console logs.
     */
    trace: 'on-first-retry',
    
    /**
     * Screenshot capture configuration
     * 
     * @description
     * Captures screenshots on test failure for visual debugging.
     * 'only-on-failure' minimizes storage while preserving debug info.
     */
    screenshot: 'only-on-failure',
    
    /**
     * Video recording configuration
     * 
     * @description
     * Records video of test execution for complex failure analysis.
     * 'retain-on-failure' saves storage while preserving debug capability.
     */
    video: 'retain-on-failure',
    
    /**
     * Action timeout configuration
     * 
     * @description
     * Maximum time to wait for actions like click(), fill(), etc.
     * Increase for slow-loading applications or complex interactions.
     */
    actionTimeout: 10 * 1000,
    
    /**
     * Navigation timeout configuration
     * 
     * @description
     * Maximum time to wait for page navigation and loading.
     * Includes network requests and DOM ready state.
     */
    navigationTimeout: 30 * 1000,
  },
  
  /**
   * Browser project configurations
   * 
   * @description
   * Defines different browser/device combinations for testing.
   * Each project runs the full test suite in its environment.
   * Enables cross-browser compatibility validation.
   */
  projects: [
    /**
     * Desktop Chromium testing
     * 
     * @description
     * Primary testing environment using Chromium browser.
     * Matches most common user environment (Chrome/Edge).
     */
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    
    /**
     * Desktop Firefox testing
     * 
     * @description
     * Firefox compatibility testing for cross-browser validation.
     * Catches browser-specific rendering and JavaScript issues.
     */
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    
    /**
     * Desktop Safari testing
     * 
     * @description
     * WebKit engine testing for Safari compatibility.
     * Important for macOS and iOS user coverage.
     */
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    
    /**
     * Mobile Chrome testing
     * 
     * @description
     * Mobile viewport and touch interaction testing.
     * Validates responsive design and mobile UX patterns.
     */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  
  /**
   * Development server configuration
   * 
   * @description
   * Automatically starts and stops the development server for testing.
   * Ensures consistent test environment and eliminates manual server management.
   */
  webServer: {
    /**
     * Command to start the development server
     * 
     * @description
     * Should match the command used for local development.
     * Playwright waits for server to be ready before running tests.
     */
    command: 'npm run dev',
    
    /**
     * Port number for server health checks
     * 
     * @description
     * Playwright polls this port to determine when server is ready.
     * Must match the port used by the development server.
     */
    port: 3000,
    
    /**
     * Server reuse configuration
     * 
     * @description
     * Reuses existing server in development to avoid restart delays.
     * Always starts fresh server in CI for consistent environment.
     */
    reuseExistingServer: !process.env.CI,
    
    /**
     * Server startup timeout
     * 
     * @description
     * Maximum time to wait for server to become ready.
     * Increase for applications with slow startup times.
     */
    timeout: 120 * 1000,
  },
});
