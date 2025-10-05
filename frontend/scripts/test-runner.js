#!/usr/bin/env node
/**
 * @fileoverview Comprehensive Test Runner
 * 
 * @description
 * Local development test runner that orchestrates all testing phases:
 * - Unit tests with Jest
 * - Integration tests with services
 * - Audio pipeline tests
 * - E2E tests with Playwright
 * - Build verification
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function colorLog(color, message) {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// Test configuration
const TEST_CONFIG = {
  unit: {
    name: 'Unit Tests',
    command: 'npm run test:unit:coverage',
    required: true,
    timeout: 60000,
  },
  integration: {
    name: 'Integration Tests',
    command: 'npm run test:integration',
    required: false, // Optional if services not available
    timeout: 120000,
  },
  audio: {
    name: 'Audio Pipeline Tests',
    command: 'npm run test:audio-demo',
    required: false, // Optional if services not available
    timeout: 180000,
  },
  e2e: {
    name: 'E2E Tests',
    command: 'npm run test:e2e',
    required: false, // Optional for quick runs
    timeout: 300000,
  },
  build: {
    name: 'Build Verification',
    command: 'npm run build',
    required: true,
    timeout: 120000,
  },
};

// Parse command line arguments
const args = process.argv.slice(2);
const options = {
  quick: args.includes('--quick'),
  unit: args.includes('--unit'),
  integration: args.includes('--integration'),
  audio: args.includes('--audio'),
  e2e: args.includes('--e2e'),
  build: args.includes('--build'),
  verbose: args.includes('--verbose'),
  bail: args.includes('--bail'),
  coverage: args.includes('--coverage'),
};

// Determine which tests to run
function getTestsToRun() {
  if (options.quick) {
    return ['unit', 'build'];
  }
  
  if (options.unit || options.integration || options.audio || options.e2e || options.build) {
    const tests = [];
    if (options.unit) tests.push('unit');
    if (options.integration) tests.push('integration');
    if (options.audio) tests.push('audio');
    if (options.e2e) tests.push('e2e');
    if (options.build) tests.push('build');
    return tests;
  }
  
  // Default: run all tests
  return Object.keys(TEST_CONFIG);
}

// Check if services are available
async function checkServices() {
  const services = [
    { name: 'TTS/STT Service', url: 'http://localhost:8000/health' },
    { name: 'Backend API', url: 'http://localhost:8080/health' },
  ];

  const serviceStatus = {};

  for (const service of services) {
    try {
      // Use curl to check service availability
      execSync(`curl -s -f ${service.url} > /dev/null`, { timeout: 5000 });
      serviceStatus[service.name] = true;
      colorLog('green', `✅ ${service.name} is available`);
    } catch (error) {
      serviceStatus[service.name] = false;
      colorLog('yellow', `⚠️  ${service.name} is not available`);
    }
  }

  return serviceStatus;
}

// Run a single test phase
async function runTest(testName, config) {
  colorLog('cyan', `\n🧪 Running ${config.name}...`);
  colorLog('blue', `Command: ${config.command}`);
  
  const startTime = Date.now();
  
  try {
    const result = execSync(config.command, {
      stdio: options.verbose ? 'inherit' : 'pipe',
      timeout: config.timeout,
      encoding: 'utf8',
    });
    
    const duration = Date.now() - startTime;
    colorLog('green', `✅ ${config.name} passed (${duration}ms)`);
    
    return { success: true, duration, output: result };
  } catch (error) {
    const duration = Date.now() - startTime;
    colorLog('red', `❌ ${config.name} failed (${duration}ms)`);
    
    if (options.verbose || config.required) {
      console.error(error.stdout || error.message);
    }
    
    return { success: false, duration, error: error.message };
  }
}

// Generate test report
function generateReport(results) {
  const totalTests = results.length;
  const passedTests = results.filter(r => r.success).length;
  const failedTests = totalTests - passedTests;
  const totalDuration = results.reduce((sum, r) => sum + r.duration, 0);
  
  colorLog('bright', '\n📊 TEST SUMMARY');
  console.log('═'.repeat(60));
  
  results.forEach(result => {
    const status = result.success ? '✅ PASS' : '❌ FAIL';
    const statusColor = result.success ? 'green' : 'red';
    const duration = `${result.duration}ms`;
    
    colorLog(statusColor, `${status} ${result.name.padEnd(20)} ${duration.padStart(10)}`);
  });
  
  console.log('─'.repeat(60));
  colorLog('bright', `Total: ${totalTests} | Passed: ${passedTests} | Failed: ${failedTests}`);
  colorLog('bright', `Duration: ${totalDuration}ms`);
  
  if (failedTests === 0) {
    colorLog('green', '\n🎉 ALL TESTS PASSED!');
  } else {
    colorLog('red', `\n💥 ${failedTests} TEST(S) FAILED`);
  }
  
  // Generate JSON report
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      total: totalTests,
      passed: passedTests,
      failed: failedTests,
      duration: totalDuration,
    },
    results: results.map(r => ({
      name: r.name,
      success: r.success,
      duration: r.duration,
      error: r.error || null,
    })),
  };
  
  try {
    fs.writeFileSync('test-results/test-report.json', JSON.stringify(report, null, 2));
    colorLog('blue', '\n📋 Test report saved to test-results/test-report.json');
  } catch (error) {
    colorLog('yellow', '\n⚠️  Could not save test report');
  }
  
  return failedTests === 0;
}

// Main test runner
async function main() {
  colorLog('bright', '🚀 UNHINGED FRONTEND TEST RUNNER');
  colorLog('bright', '================================');
  
  // Create test results directory
  try {
    fs.mkdirSync('test-results', { recursive: true });
  } catch (error) {
    // Directory might already exist
  }
  
  // Check service availability
  colorLog('blue', '\n🔍 Checking service availability...');
  const serviceStatus = await checkServices();
  
  // Get tests to run
  const testsToRun = getTestsToRun();
  colorLog('cyan', `\n📋 Running tests: ${testsToRun.join(', ')}`);
  
  // Run tests
  const results = [];
  
  for (const testName of testsToRun) {
    const config = TEST_CONFIG[testName];
    
    // Skip integration/audio tests if services not available
    if ((testName === 'integration' || testName === 'audio') && 
        !serviceStatus['TTS/STT Service'] && !serviceStatus['Backend API']) {
      colorLog('yellow', `⏭️  Skipping ${config.name} (services not available)`);
      continue;
    }
    
    const result = await runTest(testName, config);
    result.name = config.name;
    results.push(result);
    
    // Bail on first failure if requested
    if (options.bail && !result.success) {
      colorLog('red', '\n🛑 Bailing on first failure');
      break;
    }
  }
  
  // Generate report
  const allPassed = generateReport(results);
  
  // Exit with appropriate code
  process.exit(allPassed ? 0 : 1);
}

// Handle errors
process.on('unhandledRejection', (error) => {
  colorLog('red', `❌ Unhandled error: ${error.message}`);
  process.exit(1);
});

// Show help
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
🧪 Unhinged Frontend Test Runner

Usage: node scripts/test-runner.js [options]

Options:
  --quick         Run only unit tests and build verification
  --unit          Run unit tests only
  --integration   Run integration tests only
  --audio         Run audio pipeline tests only
  --e2e           Run E2E tests only
  --build         Run build verification only
  --verbose       Show detailed output
  --bail          Stop on first failure
  --coverage      Generate coverage report
  --help, -h      Show this help

Examples:
  node scripts/test-runner.js                    # Run all tests
  node scripts/test-runner.js --quick            # Quick test run
  node scripts/test-runner.js --unit --build     # Unit tests + build
  node scripts/test-runner.js --audio --verbose  # Audio tests with output
`);
  process.exit(0);
}

// Run the test runner
if (require.main === module) {
  main().catch(error => {
    colorLog('red', `❌ Test runner failed: ${error.message}`);
    process.exit(1);
  });
}

module.exports = { runTest, checkServices, generateReport };
