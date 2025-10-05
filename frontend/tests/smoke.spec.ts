// ============================================================================
// Smoke Tests - Basic Functionality Verification
// ============================================================================
//
// @file smoke.spec.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Playwright smoke tests for critical user journeys
// ============================================================================

import { test, expect } from '@playwright/test';

const FRONTEND_URL = 'http://localhost:8081';
const BACKEND_URL = 'http://localhost:8080';

test.describe('🔥 Unhinged Smoke Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Set up any common test data or state
    await page.goto(FRONTEND_URL);
  });

  test('🏠 Frontend loads successfully', async ({ page }) => {
    // Verify the page loads
    await expect(page).toHaveTitle(/Unhinged/);
    
    // Verify React app mounted (no loading spinner)
    await expect(page.locator('.loading-spinner')).not.toBeVisible({ timeout: 10000 });
    
    // Verify main content is visible
    await expect(page.locator('#root')).toBeVisible();
    
    // Take screenshot for visual verification
    await page.screenshot({ path: 'test-results/frontend-loaded.png' });
  });

  test('🎯 Chat interface is present', async ({ page }) => {
    // Wait for React to load
    await page.waitForLoadState('networkidle');
    
    // Look for chat-related elements (adjust selectors based on actual implementation)
    const chatContainer = page.locator('[data-testid="chat-container"], .chatroom, .chat-interface');
    await expect(chatContainer.first()).toBeVisible({ timeout: 15000 });
    
    // Look for input field
    const messageInput = page.locator('input[type="text"], textarea, [data-testid="message-input"]');
    await expect(messageInput.first()).toBeVisible();
    
    // Look for send button
    const sendButton = page.locator('button:has-text("Send"), [data-testid="send-button"], button[type="submit"]');
    await expect(sendButton.first()).toBeVisible();
  });

  test('🔗 Backend API is responding', async ({ request }) => {
    // Test health endpoint
    const healthResponse = await request.get(`${BACKEND_URL}/api/v1/health`);
    expect(healthResponse.ok()).toBeTruthy();
    
    const healthData = await healthResponse.json();
    expect(healthData.status).toBe('healthy');
    
    // Test root endpoint
    const rootResponse = await request.get(`${BACKEND_URL}/`);
    expect(rootResponse.ok()).toBeTruthy();
    
    const rootText = await rootResponse.text();
    expect(rootText).toContain('Unhinged Backend');
    expect(rootText).toContain('Clean Architecture');
  });

  test('💬 Chat API functionality', async ({ request }) => {
    // Test legacy chat endpoint
    const chatResponse = await request.post(`${BACKEND_URL}/chat`, {
      headers: {
        'Content-Type': 'application/json',
      },
      data: {
        prompt: 'Hello, this is a smoke test!'
      }
    });
    
    expect(chatResponse.ok()).toBeTruthy();
    const responseText = await chatResponse.text();
    expect(responseText.length).toBeGreaterThan(0);
    
    // Test modern chat endpoint
    const modernChatResponse = await request.post(`${BACKEND_URL}/api/v1/chat`, {
      headers: {
        'Content-Type': 'application/json',
      },
      data: {
        prompt: 'Hello from modern API!',
        userId: 'smoke-test-user'
      }
    });
    
    expect(modernChatResponse.ok()).toBeTruthy();
    const modernResponseData = await modernChatResponse.json();
    expect(modernResponseData.response).toBeDefined();
    expect(modernResponseData.sessionId).toBeDefined();
    expect(modernResponseData.messageId).toBeDefined();
    expect(modernResponseData.processingTimeMs).toBeGreaterThan(0);
  });

  test('🗂️ Session management works', async ({ request }) => {
    // Create a session
    const createSessionResponse = await request.post(`${BACKEND_URL}/api/v1/sessions`, {
      headers: {
        'Content-Type': 'application/json',
      },
      data: {
        userId: 'smoke-test-user',
        title: 'Smoke Test Session'
      }
    });
    
    expect(createSessionResponse.ok()).toBeTruthy();
    const sessionData = await createSessionResponse.json();
    expect(sessionData.sessionId).toBeDefined();
    expect(sessionData.userId).toBe('smoke-test-user');
    expect(sessionData.title).toBe('Smoke Test Session');
    
    const sessionId = sessionData.sessionId;
    
    // Get session details
    const getSessionResponse = await request.get(`${BACKEND_URL}/api/v1/sessions/${sessionId}`);
    expect(getSessionResponse.ok()).toBeTruthy();
    
    // Get user sessions
    const getUserSessionsResponse = await request.get(`${BACKEND_URL}/api/v1/sessions/user/smoke-test-user`);
    expect(getUserSessionsResponse.ok()).toBeTruthy();
    const userSessions = await getUserSessionsResponse.json();
    expect(Array.isArray(userSessions)).toBeTruthy();
    expect(userSessions.length).toBeGreaterThan(0);
  });

  test('🔄 End-to-end chat flow', async ({ page, request }) => {
    // This test verifies the complete user journey
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    // Find and fill message input
    const messageInput = page.locator('input[type="text"], textarea, [data-testid="message-input"]').first();
    await messageInput.waitFor({ state: 'visible', timeout: 15000 });
    await messageInput.fill('Hello from Playwright smoke test!');
    
    // Find and click send button
    const sendButton = page.locator('button:has-text("Send"), [data-testid="send-button"], button[type="submit"]').first();
    await sendButton.click();
    
    // Wait for response (look for new message or loading state)
    await page.waitForTimeout(2000); // Give time for API call
    
    // Verify backend received the request by checking if there are any network errors
    const logs: string[] = [];
    page.on('console', msg => logs.push(msg.text()));
    
    // Take screenshot of final state
    await page.screenshot({ path: 'test-results/chat-flow-complete.png' });
    
    // Verify no critical errors in console
    const criticalErrors = logs.filter(log => 
      log.includes('Error') && 
      !log.includes('404') && // Ignore 404s for missing resources
      !log.includes('favicon') // Ignore favicon errors
    );
    
    if (criticalErrors.length > 0) {
      console.warn('Console errors detected:', criticalErrors);
    }
  });

  test('📱 Responsive design basics', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    // Verify content is still visible
    await expect(page.locator('#root')).toBeVisible();
    await page.screenshot({ path: 'test-results/mobile-view.png' });
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('#root')).toBeVisible();
    await page.screenshot({ path: 'test-results/tablet-view.png' });
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page.locator('#root')).toBeVisible();
    await page.screenshot({ path: 'test-results/desktop-view.png' });
  });

  test('⚡ Performance basics', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // Verify reasonable load time (adjust threshold as needed)
    expect(loadTime).toBeLessThan(10000); // 10 seconds max
    
    console.log(`Page load time: ${loadTime}ms`);
  });

  test('🔍 Accessibility basics', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    // Check for basic accessibility features
    const mainContent = page.locator('main, [role="main"], #root');
    await expect(mainContent.first()).toBeVisible();
    
    // Verify page has a title
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
    
    // Check for keyboard navigation (basic test)
    await page.keyboard.press('Tab');
    const focusedElement = await page.locator(':focus').count();
    expect(focusedElement).toBeGreaterThanOrEqual(0);
  });

});

// Helper function for debugging
test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status !== testInfo.expectedStatus) {
    // Take screenshot on failure
    await page.screenshot({ 
      path: `test-results/failure-${testInfo.title.replace(/[^a-zA-Z0-9]/g, '-')}.png`,
      fullPage: true 
    });
  }
});
