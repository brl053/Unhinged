/**
 * @fileoverview Jest Global Teardown
 * 
 * @description
 * Global teardown for Jest test suite. Runs once after all tests.
 * Cleans up test environment, stops mock servers, and removes
 * temporary test files.
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import fs from 'fs/promises';
import path from 'path';

export default async function globalTeardown(): Promise<void> {
  console.log('🧹 Cleaning up Jest test environment...');

  try {
    // Clean up test files
    await cleanupTestFiles();
    
    // Clean up test databases
    await cleanupTestDatabase();
    
    // Generate test summary
    await generateTestSummary();
    
    console.log('✅ Jest global teardown completed successfully');
  } catch (error) {
    console.error('❌ Jest global teardown failed:', error);
    // Don't throw error in teardown to avoid masking test failures
  }
}

/**
 * Clean up temporary test files
 */
async function cleanupTestFiles(): Promise<void> {
  const cleanupPaths = [
    'tests/fixtures/audio',
    '.jest-cache',
  ];

  for (const cleanupPath of cleanupPaths) {
    try {
      const stats = await fs.stat(cleanupPath);
      if (stats.isDirectory()) {
        const files = await fs.readdir(cleanupPath);
        
        // Only clean up generated files, keep fixture templates
        const filesToDelete = files.filter(file => 
          file.includes('test-') || 
          file.includes('mock-') ||
          file.endsWith('.tmp')
        );
        
        for (const file of filesToDelete) {
          await fs.unlink(path.join(cleanupPath, file));
        }
        
        if (filesToDelete.length > 0) {
          console.log(`🗑️  Cleaned up ${filesToDelete.length} temporary files from ${cleanupPath}`);
        }
      }
    } catch (error) {
      // Path might not exist, ignore error
    }
  }
}

/**
 * Clean up test database
 */
async function cleanupTestDatabase(): Promise<void> {
  // For now, we're using mocks, so no cleanup needed
  console.log('📊 Test database cleanup completed (using mocks)');
}

/**
 * Generate test summary
 */
async function generateTestSummary(): Promise<void> {
  try {
    // Check if coverage report exists
    const coveragePath = 'coverage/coverage-summary.json';
    let coverageData = null;
    
    try {
      const coverageContent = await fs.readFile(coveragePath, 'utf-8');
      coverageData = JSON.parse(coverageContent);
    } catch (error) {
      // Coverage file might not exist
    }

    // Check if test results exist
    const testResultsPath = 'test-results/junit.xml';
    let testResultsExist = false;
    
    try {
      await fs.stat(testResultsPath);
      testResultsExist = true;
    } catch (error) {
      // Test results file might not exist
    }

    const summary = {
      timestamp: new Date().toISOString(),
      coverage: coverageData,
      testResultsGenerated: testResultsExist,
      environment: {
        node: process.version,
        platform: process.platform,
        ci: !!(process.env.CI || process.env.GITHUB_ACTIONS),
      },
    };

    await fs.writeFile(
      'test-results/test-summary.json',
      JSON.stringify(summary, null, 2)
    );

    console.log('📋 Test summary generated');
    
    // Print coverage summary if available
    if (coverageData && coverageData.total) {
      const { total } = coverageData;
      console.log('\n📊 Coverage Summary:');
      console.log(`   Lines: ${total.lines.pct}%`);
      console.log(`   Functions: ${total.functions.pct}%`);
      console.log(`   Branches: ${total.branches.pct}%`);
      console.log(`   Statements: ${total.statements.pct}%`);
    }
    
  } catch (error) {
    console.warn('⚠️  Could not generate test summary:', error);
  }
}
