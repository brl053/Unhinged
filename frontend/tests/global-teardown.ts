// ============================================================================
// Global Test Teardown - Playwright
// ============================================================================
//
// @file global-teardown.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Global teardown for Playwright tests
// ============================================================================

import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Cleaning up after tests...');
  
  // Add any cleanup logic here
  // For example:
  // - Clear test data from database
  // - Reset application state
  // - Clean up temporary files
  
  console.log('✅ Test cleanup complete');
}

export default globalTeardown;
