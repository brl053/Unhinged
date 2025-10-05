#!/usr/bin/env node
/**
 * @fileoverview Audio Pipeline Testing Demo
 * 
 * @description
 * Standalone demo script to test the TTS-to-STT pipeline
 * without requiring Playwright. Useful for:
 * - Verifying audio services are working
 * - Testing round-trip accuracy
 * - Generating sample audio files for manual testing
 * - Performance benchmarking
 * 
 * Usage:
 * ```bash
 * cd projects/Unhinged/frontend
 * npx ts-node tests/audio-pipeline-demo.ts
 * ```
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import {
  AudioPipelineTester,
  STANDARD_AUDIO_TEST_CASES,
  AudioTestResult
} from './utils/audio-pipeline-testing';

/**
 * Demo configuration
 */
const DEMO_CONFIG = {
  serviceBaseUrl: 'http://localhost:8000',
  audioOutputDir: './tests/fixtures/audio',
  language: 'en',
  similarityThreshold: 0.80,
  timeoutMs: 30000,
};

/**
 * Colors for console output
 */
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

/**
 * Print colored console output
 */
function colorLog(color: keyof typeof colors, message: string): void {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

/**
 * Print test result summary
 */
function printTestResult(result: AudioTestResult): void {
  const status = result.passed ? '✅ PASS' : '❌ FAIL';
  const statusColor = result.passed ? 'green' : 'red';
  
  colorLog('cyan', `\n📝 Test: ${result.testCase.description}`);
  colorLog('blue', `🔤 Original Text: "${result.testCase.text}"`);
  colorLog('blue', `🎤 Transcribed:   "${result.transcribedText}"`);
  colorLog('yellow', `📊 Similarity:    ${(result.similarityScore * 100).toFixed(1)}%`);
  colorLog('yellow', `⏱️  Duration:      ${result.durationMs}ms`);
  colorLog(statusColor, `${status}`);
  
  if (result.error) {
    colorLog('red', `❌ Error: ${result.error}`);
  }
  
  console.log('─'.repeat(80));
}

/**
 * Print overall summary
 */
function printSummary(results: AudioTestResult[]): void {
  const passed = results.filter(r => r.passed).length;
  const failed = results.filter(r => !r.passed).length;
  const total = results.length;
  
  const avgSimilarity = results.reduce((sum, r) => sum + r.similarityScore, 0) / total;
  const avgDuration = results.reduce((sum, r) => sum + r.durationMs, 0) / total;
  
  colorLog('bright', '\n🎯 AUDIO PIPELINE TEST SUMMARY');
  console.log('═'.repeat(80));
  colorLog('green', `✅ Passed: ${passed}/${total}`);
  colorLog('red', `❌ Failed: ${failed}/${total}`);
  colorLog('yellow', `📊 Average Similarity: ${(avgSimilarity * 100).toFixed(1)}%`);
  colorLog('yellow', `⏱️  Average Duration: ${avgDuration.toFixed(0)}ms`);
  
  if (failed === 0) {
    colorLog('green', '\n🎉 ALL TESTS PASSED! Audio pipeline is working correctly.');
  } else {
    colorLog('red', '\n⚠️  Some tests failed. Check the audio services and network connectivity.');
  }
}

/**
 * Main demo function
 */
async function runAudioPipelineDemo(): Promise<void> {
  colorLog('bright', '🎵 AUDIO PIPELINE TESTING DEMO');
  colorLog('bright', '🔄 Testing TTS → Audio → STT → Text Pipeline');
  console.log('═'.repeat(80));

  try {
    // Initialize the audio pipeline tester
    colorLog('blue', '🚀 Initializing Audio Pipeline Tester...');
    const tester = new AudioPipelineTester(DEMO_CONFIG);
    await tester.initialize();
    colorLog('green', '✅ Audio Pipeline Tester initialized successfully');

    // Run a subset of standard test cases
    const testCases = STANDARD_AUDIO_TEST_CASES.slice(0, 5); // First 5 test cases
    colorLog('yellow', `🧪 Running ${testCases.length} test cases...`);

    const results: AudioTestResult[] = [];

    // Run tests sequentially for better output formatting
    for (let i = 0; i < testCases.length; i++) {
      const testCase = testCases[i];
      colorLog('cyan', `\n[${i + 1}/${testCases.length}] Running: ${testCase.description}`);
      
      try {
        const result = await tester.runAudioTest(testCase);
        results.push(result);
        printTestResult(result);
      } catch (error) {
        colorLog('red', `❌ Test failed with error: ${error}`);
        results.push({
          testCase,
          audioFilePath: '',
          transcribedText: '',
          similarityScore: 0,
          passed: false,
          durationMs: 0,
          error: error instanceof Error ? error.message : String(error),
        });
      }
    }

    // Print summary
    printSummary(results);

    // Cleanup
    colorLog('blue', '\n🧹 Cleaning up generated audio files...');
    await tester.cleanup();
    colorLog('green', '✅ Cleanup completed');

  } catch (error) {
    colorLog('red', `❌ Demo failed: ${error}`);
    
    if (error instanceof Error && error.message.includes('Failed to verify audio services')) {
      colorLog('yellow', '\n💡 Troubleshooting Tips:');
      colorLog('yellow', '   1. Make sure the Whisper-TTS service is running on http://localhost:8000');
      colorLog('yellow', '   2. Check if Docker containers are up: docker ps');
      colorLog('yellow', '   3. Verify service health: curl http://localhost:8000/health');
      colorLog('yellow', '   4. Check service logs: docker logs whisper-tts-service');
    }
    
    process.exit(1);
  }
}

/**
 * Custom test case demo
 */
async function runCustomTestDemo(): Promise<void> {
  colorLog('bright', '\n🎯 CUSTOM TEST CASE DEMO');
  console.log('═'.repeat(80));

  const customTestCases = [
    {
      id: 'doordash-stock',
      text: 'Show me a DoorDash stock chart with weekly candles for the last two months',
      description: 'DoorDash Stock Chart Request',
    },
    {
      id: 'react-component',
      text: 'Create a React component with TypeScript props and styled components',
      description: 'React Component Creation Command',
    },
    {
      id: 'voice-input',
      text: 'Add a voice input button with microphone icon and recording animation',
      description: 'Voice Input UI Command',
    },
  ];

  try {
    const tester = new AudioPipelineTester(DEMO_CONFIG);
    await tester.initialize();

    for (const testCase of customTestCases) {
      colorLog('cyan', `\n🧪 Testing: ${testCase.description}`);
      const result = await tester.runAudioTest(testCase);
      printTestResult(result);
    }

    await tester.cleanup();
    
  } catch (error) {
    colorLog('red', `❌ Custom test demo failed: ${error}`);
  }
}

/**
 * Performance benchmark demo
 */
async function runPerformanceBenchmark(): Promise<void> {
  colorLog('bright', '\n⚡ PERFORMANCE BENCHMARK');
  console.log('═'.repeat(80));

  const benchmarkText = 'This is a performance benchmark test for the audio pipeline system';
  const iterations = 3;

  try {
    const tester = new AudioPipelineTester(DEMO_CONFIG);
    await tester.initialize();

    const times: number[] = [];

    for (let i = 1; i <= iterations; i++) {
      colorLog('yellow', `\n🏃 Benchmark Run ${i}/${iterations}`);
      
      const testCase = {
        id: `benchmark-${i}`,
        text: benchmarkText,
        description: `Performance benchmark run ${i}`,
      };

      const result = await tester.runAudioTest(testCase);
      times.push(result.durationMs);
      
      colorLog('blue', `⏱️  Duration: ${result.durationMs}ms`);
      colorLog('blue', `📊 Similarity: ${(result.similarityScore * 100).toFixed(1)}%`);
    }

    const avgTime = times.reduce((sum, time) => sum + time, 0) / times.length;
    const minTime = Math.min(...times);
    const maxTime = Math.max(...times);

    colorLog('green', `\n📈 BENCHMARK RESULTS:`);
    colorLog('yellow', `   Average: ${avgTime.toFixed(0)}ms`);
    colorLog('yellow', `   Minimum: ${minTime}ms`);
    colorLog('yellow', `   Maximum: ${maxTime}ms`);

    await tester.cleanup();

  } catch (error) {
    colorLog('red', `❌ Performance benchmark failed: ${error}`);
  }
}

/**
 * Main execution
 */
async function main(): Promise<void> {
  const args = process.argv.slice(2);
  
  if (args.includes('--custom')) {
    await runCustomTestDemo();
  } else if (args.includes('--benchmark')) {
    await runPerformanceBenchmark();
  } else if (args.includes('--all')) {
    await runAudioPipelineDemo();
    await runCustomTestDemo();
    await runPerformanceBenchmark();
  } else {
    await runAudioPipelineDemo();
  }
}

// Run the demo
if (require.main === module) {
  main().catch(error => {
    colorLog('red', `❌ Demo failed: ${error}`);
    process.exit(1);
  });
}

export { runAudioPipelineDemo, runCustomTestDemo, runPerformanceBenchmark };
