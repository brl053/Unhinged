/**
 * @fileoverview Jest Global Setup
 * 
 * @description
 * Global setup for Jest test suite. Runs once before all tests.
 * Sets up test environment, starts mock servers, and initializes
 * test databases.
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import { execSync } from 'child_process';
import fs from 'fs/promises';
import path from 'path';

export default async function globalSetup(): Promise<void> {
  console.log('🚀 Setting up Jest test environment...');

  try {
    // Create test directories
    await createTestDirectories();
    
    // Setup test database
    await setupTestDatabase();
    
    // Verify services for integration tests
    await verifyTestServices();
    
    // Setup test fixtures
    await setupTestFixtures();
    
    console.log('✅ Jest global setup completed successfully');
  } catch (error) {
    console.error('❌ Jest global setup failed:', error);
    throw error;
  }
}

/**
 * Create necessary test directories
 */
async function createTestDirectories(): Promise<void> {
  const directories = [
    'tests/fixtures/audio',
    'tests/fixtures/images',
    'tests/fixtures/data',
    'test-results',
    'coverage',
    '.jest-cache',
  ];

  for (const dir of directories) {
    try {
      await fs.mkdir(dir, { recursive: true });
    } catch (error) {
      // Directory might already exist, ignore error
    }
  }
}

/**
 * Setup test database
 */
async function setupTestDatabase(): Promise<void> {
  // For now, we'll use IndexedDB mocks
  // In the future, we might want to setup a test database
  console.log('📊 Test database setup completed (using mocks)');
}

/**
 * Verify test services are available for integration tests
 */
async function verifyTestServices(): Promise<void> {
  const services = [
    {
      name: 'TTS/STT Service',
      url: 'http://localhost:8000/health',
      required: false, // Optional for unit tests
    },
    {
      name: 'Backend API',
      url: 'http://localhost:8080/health',
      required: false, // Optional for unit tests
    },
  ];

  for (const service of services) {
    try {
      const response = await fetch(service.url);
      if (response.ok) {
        console.log(`✅ ${service.name} is available for integration tests`);
      } else {
        throw new Error(`Service returned ${response.status}`);
      }
    } catch (error) {
      if (service.required) {
        throw new Error(`Required service ${service.name} is not available: ${error}`);
      } else {
        console.log(`⚠️  ${service.name} is not available (integration tests will be skipped)`);
      }
    }
  }
}

/**
 * Setup test fixtures
 */
async function setupTestFixtures(): Promise<void> {
  // Create sample test data
  const testData = {
    sampleMessages: [
      {
        id: '1',
        type: 'sent',
        message: 'Hello, this is a test message',
        timestamp: Date.now(),
      },
      {
        id: '2',
        type: 'received',
        message: 'This is a response message',
        timestamp: Date.now() + 1000,
      },
    ],
    sampleTranscriptions: [
      {
        text: 'Hello world',
        language: 'en',
        confidence: 0.95,
      },
      {
        text: 'Create a React component',
        language: 'en',
        confidence: 0.88,
      },
    ],
    sampleAudioTestCases: [
      {
        id: 'test-basic',
        text: 'This is a basic test',
        description: 'Basic test case',
      },
      {
        id: 'test-technical',
        text: 'Create a TypeScript interface',
        description: 'Technical terminology test',
      },
    ],
  };

  await fs.writeFile(
    'tests/fixtures/data/testData.json',
    JSON.stringify(testData, null, 2)
  );

  console.log('📁 Test fixtures created');
}

/**
 * Check if running in CI environment
 */
function isCI(): boolean {
  return !!(
    process.env.CI ||
    process.env.CONTINUOUS_INTEGRATION ||
    process.env.BUILD_NUMBER ||
    process.env.GITHUB_ACTIONS ||
    process.env.GITLAB_CI
  );
}

/**
 * Get test environment configuration
 */
function getTestConfig() {
  return {
    isCI: isCI(),
    timeout: isCI() ? 30000 : 10000,
    retries: isCI() ? 2 : 0,
    workers: isCI() ? 2 : '50%',
  };
}
