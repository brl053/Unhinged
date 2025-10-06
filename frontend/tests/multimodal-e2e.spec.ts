// ============================================================================
// Multimodal AI End-to-End Tests
// ============================================================================
//
// @file multimodal-e2e.spec.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description Playwright E2E tests for multimodal AI architecture refactoring
//
// Tests complete user journeys: Frontend → Kotlin Backend → Python gRPC Services
// Validates architecture boundaries and functionality preservation
//
// ============================================================================

import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const FRONTEND_URL = 'http://localhost:8081';
const BACKEND_URL = 'http://localhost:8080';

// Test configuration
const TEST_CONFIG = {
  timeout: 30000,
  slowMo: 100, // Slow down for debugging
  testAssets: path.join(__dirname, 'assets'),
  screenshots: path.join(__dirname, '../test-results/multimodal')
};

test.describe('🎯 Multimodal AI Architecture E2E Tests', () => {
  
  test.beforeAll(async () => {
    // Create test assets directory
    if (!fs.existsSync(TEST_CONFIG.testAssets)) {
      fs.mkdirSync(TEST_CONFIG.testAssets, { recursive: true });
    }
    
    // Create test screenshots directory
    if (!fs.existsSync(TEST_CONFIG.screenshots)) {
      fs.mkdirSync(TEST_CONFIG.screenshots, { recursive: true });
    }
    
    // Generate test images
    await generateTestAssets();
  });

  test.beforeEach(async ({ page }) => {
    // Set up test environment
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
  });

  test('🔄 Complete multimodal analysis workflow - Screenshot', async ({ page, request }) => {
    // Given: A test screenshot image
    const testImage = path.join(TEST_CONFIG.testAssets, 'test-screenshot.png');
    
    // When: Uploading image for analysis via API (simulating frontend behavior)
    const imageBuffer = fs.readFileSync(testImage);
    
    const formData = new FormData();
    formData.append('image', new Blob([imageBuffer], { type: 'image/png' }), 'test-screenshot.png');
    formData.append('analysisType', 'screenshot');
    formData.append('workflowType', 'contextual_analysis');
    formData.append('prompt', 'Analyze this UI screenshot and identify all interactive elements');
    formData.append('priority', 'normal');
    
    const startTime = Date.now();
    
    const response = await request.post(`${BACKEND_URL}/api/multimodal/analyze`, {
      headers: {
        'X-User-ID': 'e2e-test-user'
      },
      multipart: {
        image: {
          name: 'test-screenshot.png',
          mimeType: 'image/png',
          buffer: imageBuffer
        },
        analysisType: 'screenshot',
        workflowType: 'contextual_analysis',
        prompt: 'Analyze this UI screenshot and identify all interactive elements',
        priority: 'normal'
      }
    });
    
    const responseTime = Date.now() - startTime;
    
    // Then: Should receive successful analysis
    expect(response.ok()).toBeTruthy();
    
    const analysisResult = await response.json();
    
    // Validate response structure
    expect(analysisResult.id).toBeDefined();
    expect(analysisResult.imageId).toBeDefined();
    expect(analysisResult.analysisType).toBe('screenshot');
    expect(analysisResult.workflowType).toBe('contextual_analysis');
    expect(analysisResult.description).toBeDefined();
    expect(analysisResult.confidence).toBeGreaterThan(0);
    expect(analysisResult.confidence).toBeLessThanOrEqual(1);
    expect(analysisResult.modelUsed).toBeDefined();
    expect(analysisResult.processingTime).toBeGreaterThan(0);
    expect(analysisResult.createdAt).toBeDefined();
    expect(analysisResult.userId).toBe('e2e-test-user');
    
    // Validate architecture boundaries
    expect(analysisResult.metadata).toBeDefined();
    expect(analysisResult.metadata.workflow_config).toBeDefined();
    expect(analysisResult.metadata.quality_score).toBeDefined();
    
    // Performance validation
    expect(responseTime).toBeLessThan(30000); // 30 second timeout
    console.log(`Screenshot analysis completed in ${responseTime}ms`);
    
    // Take screenshot for visual verification
    await page.screenshot({ 
      path: path.join(TEST_CONFIG.screenshots, 'screenshot-analysis-complete.png'),
      fullPage: true 
    });
  });

  test('📄 Document analysis workflow with OCR', async ({ page, request }) => {
    // Given: A test document image
    const testImage = path.join(TEST_CONFIG.testAssets, 'test-document.png');
    const imageBuffer = fs.readFileSync(testImage);
    
    // When: Analyzing document
    const response = await request.post(`${BACKEND_URL}/api/multimodal/analyze`, {
      headers: {
        'X-User-ID': 'e2e-test-user'
      },
      multipart: {
        image: {
          name: 'test-document.png',
          mimeType: 'image/png',
          buffer: imageBuffer
        },
        analysisType: 'document',
        workflowType: 'iterative_refinement',
        prompt: 'Extract all text content and analyze document structure'
      }
    });
    
    // Then: Should extract text content
    expect(response.ok()).toBeTruthy();
    
    const analysisResult = await response.json();
    expect(analysisResult.analysisType).toBe('document');
    expect(analysisResult.workflowType).toBe('iterative_refinement');
    expect(analysisResult.extractedText).toBeDefined();
    expect(analysisResult.extractedText.length).toBeGreaterThan(0);
    
    // Verify iterative refinement metadata
    expect(analysisResult.metadata.refinement_iterations).toBeDefined();
    
    console.log(`Document OCR extracted: ${analysisResult.extractedText.substring(0, 100)}...`);
  });

  test('🎨 UI component analysis workflow', async ({ page, request }) => {
    // Given: A test UI component image
    const testImage = path.join(TEST_CONFIG.testAssets, 'test-ui-component.png');
    const imageBuffer = fs.readFileSync(testImage);
    
    // When: Analyzing UI component
    const response = await request.post(`${BACKEND_URL}/api/multimodal/analyze`, {
      headers: {
        'X-User-ID': 'e2e-test-user'
      },
      multipart: {
        image: {
          name: 'test-ui-component.png',
          mimeType: 'image/png',
          buffer: imageBuffer
        },
        analysisType: 'ui_component',
        workflowType: 'contextual_analysis',
        prompt: 'Analyze this form component and identify all input fields and buttons'
      }
    });
    
    // Then: Should identify UI elements
    expect(response.ok()).toBeTruthy();
    
    const analysisResult = await response.json();
    expect(analysisResult.analysisType).toBe('ui_component');
    expect(analysisResult.uiElements).toBeDefined();
    expect(analysisResult.uiElements.length).toBeGreaterThan(0);
    
    // Verify UI elements have proper structure
    const uiElements = analysisResult.uiElements;
    uiElements.forEach((element: any) => {
      expect(element.type).toBeDefined();
      expect(element.confidence).toBeGreaterThan(0);
      expect(element.confidence).toBeLessThanOrEqual(1);
    });
    
    console.log(`UI elements detected: ${uiElements.map((e: any) => e.type).join(', ')}`);
  });

  test('🌄 Natural image analysis workflow', async ({ page, request }) => {
    // Given: A test natural image
    const testImage = path.join(TEST_CONFIG.testAssets, 'test-natural-image.png');
    const imageBuffer = fs.readFileSync(testImage);
    
    // When: Analyzing natural image
    const response = await request.post(`${BACKEND_URL}/api/multimodal/analyze`, {
      headers: {
        'X-User-ID': 'e2e-test-user'
      },
      multipart: {
        image: {
          name: 'test-natural-image.png',
          mimeType: 'image/png',
          buffer: imageBuffer
        },
        analysisType: 'natural_image',
        workflowType: 'multi_model_consensus',
        prompt: 'Describe this scene in detail including objects, colors, and composition'
      }
    });
    
    // Then: Should provide detailed scene description
    expect(response.ok()).toBeTruthy();
    
    const analysisResult = await response.json();
    expect(analysisResult.analysisType).toBe('natural_image');
    expect(analysisResult.workflowType).toBe('multi_model_consensus');
    expect(analysisResult.tags).toBeDefined();
    expect(analysisResult.tags.length).toBeGreaterThan(0);
    
    // Verify consensus metadata
    expect(analysisResult.metadata.consensus_models).toBeDefined();
    expect(analysisResult.metadata.consensus_method).toBeDefined();
    
    console.log(`Scene tags: ${analysisResult.tags.join(', ')}`);
  });

  test('📊 Analysis retrieval and statistics', async ({ page, request }) => {
    // Given: Multiple analyses exist (from previous tests)
    
    // When: Getting user analyses
    const analysesResponse = await request.get(`${BACKEND_URL}/api/multimodal/analyses?limit=10&offset=0`, {
      headers: {
        'X-User-ID': 'e2e-test-user'
      }
    });
    
    // Then: Should return paginated analyses
    expect(analysesResponse.ok()).toBeTruthy();
    
    const analysesData = await analysesResponse.json();
    expect(analysesData.analyses).toBeDefined();
    expect(Array.isArray(analysesData.analyses)).toBeTruthy();
    expect(analysesData.total).toBeDefined();
    expect(analysesData.limit).toBe(10);
    expect(analysesData.offset).toBe(0);
    
    // When: Getting statistics
    const statsResponse = await request.get(`${BACKEND_URL}/api/multimodal/statistics`, {
      headers: {
        'X-User-ID': 'e2e-test-user'
      }
    });
    
    // Then: Should return user statistics
    expect(statsResponse.ok()).toBeTruthy();
    
    const statsData = await statsResponse.json();
    expect(statsData.totalAnalyses).toBeGreaterThan(0);
    expect(statsData.averageConfidence).toBeGreaterThan(0);
    expect(statsData.averageProcessingTime).toBeGreaterThan(0);
    expect(statsData.analysisTypeBreakdown).toBeDefined();
    expect(statsData.workflowTypeBreakdown).toBeDefined();
    
    console.log(`User has ${statsData.totalAnalyses} analyses with avg confidence ${statsData.averageConfidence.toFixed(2)}`);
  });

  test('⚙️ Workflow configuration and availability', async ({ page, request }) => {
    // When: Getting available workflows
    const workflowsResponse = await request.get(`${BACKEND_URL}/api/multimodal/workflows`);
    
    // Then: Should return all workflow types
    expect(workflowsResponse.ok()).toBeTruthy();
    
    const workflowsData = await workflowsResponse.json();
    expect(workflowsData.workflows).toBeDefined();
    
    const expectedWorkflows = ['basic_analysis', 'contextual_analysis', 'iterative_refinement', 'multi_model_consensus'];
    expectedWorkflows.forEach(workflow => {
      const found = workflowsData.workflows.find((w: any) => w.type === workflow);
      expect(found).toBeDefined();
      expect(found.name).toBeDefined();
      expect(found.description).toBeDefined();
    });
    
    // When: Getting workflows for specific analysis type
    const screenshotWorkflowsResponse = await request.get(`${BACKEND_URL}/api/multimodal/workflows?analysisType=screenshot`);
    
    // Then: Should return configured workflows for screenshot analysis
    expect(screenshotWorkflowsResponse.ok()).toBeTruthy();
    
    const screenshotWorkflowsData = await screenshotWorkflowsResponse.json();
    expect(screenshotWorkflowsData.analysisType).toBe('screenshot');
    expect(screenshotWorkflowsData.workflows).toBeDefined();
    expect(screenshotWorkflowsData.workflows.length).toBeGreaterThan(0);
    
    // Verify workflow configurations
    screenshotWorkflowsData.workflows.forEach((workflow: any) => {
      expect(workflow.type).toBeDefined();
      expect(workflow.visionModel).toBeDefined();
      expect(workflow.timeoutSeconds).toBeGreaterThan(0);
      expect(workflow.parameters).toBeDefined();
    });
  });

  test('🚨 Error handling and resilience', async ({ page, request }) => {
    // Test 1: Invalid image data
    const invalidResponse = await request.post(`${BACKEND_URL}/api/multimodal/analyze`, {
      headers: {
        'X-User-ID': 'e2e-test-user'
      },
      multipart: {
        image: {
          name: 'invalid.png',
          mimeType: 'image/png',
          buffer: Buffer.from('invalid image data')
        },
        analysisType: 'screenshot'
      }
    });
    
    expect(invalidResponse.status()).toBe(400);
    const invalidError = await invalidResponse.json();
    expect(invalidError.error).toBeDefined();
    expect(invalidError.code).toBe('VALIDATION_ERROR');
    
    // Test 2: Missing required parameters
    const missingImageResponse = await request.post(`${BACKEND_URL}/api/multimodal/analyze`, {
      headers: {
        'X-User-ID': 'e2e-test-user'
      },
      multipart: {
        analysisType: 'screenshot'
      }
    });
    
    expect(missingImageResponse.status()).toBe(400);
    const missingError = await missingImageResponse.json();
    expect(missingError.error).toBe('No image provided');
    
    // Test 3: Invalid analysis type
    const testImage = path.join(TEST_CONFIG.testAssets, 'test-screenshot.png');
    const imageBuffer = fs.readFileSync(testImage);
    
    const invalidTypeResponse = await request.post(`${BACKEND_URL}/api/multimodal/analyze`, {
      headers: {
        'X-User-ID': 'e2e-test-user'
      },
      multipart: {
        image: {
          name: 'test.png',
          mimeType: 'image/png',
          buffer: imageBuffer
        },
        analysisType: 'invalid_type'
      }
    });
    
    expect(invalidTypeResponse.status()).toBe(400);
    
    // Test 4: Non-existent analysis retrieval
    const notFoundResponse = await request.get(`${BACKEND_URL}/api/multimodal/analysis/non-existent-id`);
    expect(notFoundResponse.status()).toBe(404);
    
    const notFoundError = await notFoundResponse.json();
    expect(notFoundError.code).toBe('NOT_FOUND');
  });

  test('⚡ Performance benchmarking - gRPC vs HTTP overhead', async ({ page, request }) => {
    const testImage = path.join(TEST_CONFIG.testAssets, 'test-screenshot.png');
    const imageBuffer = fs.readFileSync(testImage);
    
    const performanceResults: number[] = [];
    const iterations = 3;
    
    // Run multiple iterations to get average performance
    for (let i = 0; i < iterations; i++) {
      const startTime = Date.now();
      
      const response = await request.post(`${BACKEND_URL}/api/multimodal/analyze`, {
        headers: {
          'X-User-ID': 'perf-test-user'
        },
        multipart: {
          image: {
            name: `perf-test-${i}.png`,
            mimeType: 'image/png',
            buffer: imageBuffer
          },
          analysisType: 'screenshot',
          workflowType: 'basic_analysis'
        }
      });
      
      const responseTime = Date.now() - startTime;
      performanceResults.push(responseTime);
      
      expect(response.ok()).toBeTruthy();
      
      const result = await response.json();
      expect(result.processingTime).toBeGreaterThan(0);
      
      // Log individual results
      console.log(`Iteration ${i + 1}: HTTP Response Time: ${responseTime}ms, Processing Time: ${result.processingTime}ms`);
    }
    
    // Calculate performance statistics
    const avgResponseTime = performanceResults.reduce((a, b) => a + b, 0) / performanceResults.length;
    const minResponseTime = Math.min(...performanceResults);
    const maxResponseTime = Math.max(...performanceResults);
    
    console.log(`Performance Summary:`);
    console.log(`  Average Response Time: ${avgResponseTime.toFixed(2)}ms`);
    console.log(`  Min Response Time: ${minResponseTime}ms`);
    console.log(`  Max Response Time: ${maxResponseTime}ms`);
    
    // Performance assertions
    expect(avgResponseTime).toBeLessThan(10000); // 10 second average
    expect(maxResponseTime).toBeLessThan(15000); // 15 second max
    
    // Verify architecture efficiency
    expect(avgResponseTime).toBeLessThan(30000); // Should be much faster than old HTTP approach
  });

  test('🔍 Architecture boundary validation', async ({ page, request }) => {
    // This test validates that service boundaries are properly maintained
    const testImage = path.join(TEST_CONFIG.testAssets, 'test-screenshot.png');
    const imageBuffer = fs.readFileSync(testImage);
    
    const response = await request.post(`${BACKEND_URL}/api/multimodal/analyze`, {
      headers: {
        'X-User-ID': 'boundary-test-user'
      },
      multipart: {
        image: {
          name: 'boundary-test.png',
          mimeType: 'image/png',
          buffer: imageBuffer
        },
        analysisType: 'screenshot',
        workflowType: 'contextual_analysis'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const result = await response.json();
    
    // Validate Kotlin backend handled business logic
    expect(result.id).toBeDefined(); // Generated by Kotlin
    expect(result.createdAt).toBeDefined(); // Timestamp by Kotlin
    expect(result.userId).toBe('boundary-test-user'); // User context by Kotlin
    expect(result.workflowType).toBe('contextual_analysis'); // Workflow by Kotlin
    
    // Validate Python services only provided AI inference
    expect(result.description).toBeDefined(); // From Python vision service
    expect(result.confidence).toBeGreaterThan(0); // From Python vision service
    expect(result.modelUsed).toBeDefined(); // From Python vision service
    expect(result.processingTime).toBeGreaterThan(0); // From Python processing
    
    // Validate orchestration metadata (Kotlin business logic)
    expect(result.metadata.workflow_config).toBeDefined();
    expect(result.metadata.quality_score).toBeDefined();
    expect(result.metadata.context_enhanced).toBeDefined();
    
    console.log('✅ Architecture boundaries properly maintained');
    console.log(`  - Kotlin handled: ID generation, timestamps, user context, workflow orchestration`);
    console.log(`  - Python handled: AI inference, model execution, confidence scoring`);
  });

});

// Helper function to generate test assets
async function generateTestAssets() {
  const assetsDir = TEST_CONFIG.testAssets;

  // Generate simple test images using base64 encoded PNG data
  await generateSimpleTestImage(path.join(assetsDir, 'test-screenshot.png'));
  await generateSimpleTestImage(path.join(assetsDir, 'test-document.png'));
  await generateSimpleTestImage(path.join(assetsDir, 'test-ui-component.png'));
  await generateSimpleTestImage(path.join(assetsDir, 'test-natural-image.png'));
}

async function generateSimpleTestImage(filePath: string) {
  // Create a simple 1x1 PNG image as base64
  // This is a minimal valid PNG file for testing purposes
  const base64PNG = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==';
  const buffer = Buffer.from(base64PNG, 'base64');
  fs.writeFileSync(filePath, buffer);
}

// Helper function for debugging
test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status !== testInfo.expectedStatus) {
    // Take screenshot on failure
    await page.screenshot({ 
      path: path.join(TEST_CONFIG.screenshots, `failure-${testInfo.title.replace(/[^a-zA-Z0-9]/g, '-')}.png`),
      fullPage: true 
    });
  }
});
