// ============================================================================
// Global Test Setup - Playwright
// ============================================================================
//
// @file global-setup.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Global setup for Playwright tests
// ============================================================================

import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting Unhinged test setup...');
  
  // Wait for services to be ready
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Check if backend is ready
    console.log('⏳ Waiting for backend to be ready...');
    let backendReady = false;
    let attempts = 0;
    const maxAttempts = 30; // 30 seconds
    
    while (!backendReady && attempts < maxAttempts) {
      try {
        const response = await page.request.get('http://localhost:8080/api/v1/health');
        if (response.ok()) {
          const data = await response.json();
          if (data.status === 'healthy') {
            backendReady = true;
            console.log('✅ Backend is ready');
          }
        }
      } catch (error) {
        // Backend not ready yet
      }
      
      if (!backendReady) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        attempts++;
      }
    }
    
    if (!backendReady) {
      throw new Error('❌ Backend failed to start within 30 seconds');
    }
    
    // Check if frontend is ready
    console.log('⏳ Waiting for frontend to be ready...');
    let frontendReady = false;
    attempts = 0;
    
    while (!frontendReady && attempts < maxAttempts) {
      try {
        const response = await page.request.get('http://localhost:8081');
        if (response.ok()) {
          frontendReady = true;
          console.log('✅ Frontend is ready');
        }
      } catch (error) {
        // Frontend not ready yet
      }
      
      if (!frontendReady) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        attempts++;
      }
    }
    
    if (!frontendReady) {
      throw new Error('❌ Frontend failed to start within 30 seconds');
    }
    
    console.log('🎯 All services are ready for testing!');
    
  } finally {
    await browser.close();
  }
}

export default globalSetup;
