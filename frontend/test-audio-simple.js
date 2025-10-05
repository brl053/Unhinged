#!/usr/bin/env node
/**
 * Simple Audio Pipeline Test (CommonJS)
 * 
 * Quick test of TTS-to-STT pipeline without TypeScript complications
 */

const fs = require('fs').promises;
const path = require('path');

// Configuration
const CONFIG = {
  serviceBaseUrl: 'http://localhost:8000',
  audioOutputDir: './tests/fixtures/audio',
  similarityThreshold: 0.80,
};

// Test cases
const TEST_CASES = [
  {
    id: 'basic-greeting',
    text: 'Hello, this is a basic audio test.',
    description: 'Basic greeting and introduction',
  },
  {
    id: 'quick-brown-fox',
    text: 'The quick brown fox jumps over the lazy dog.',
    description: 'Classic pangram for comprehensive phoneme testing',
  },
  {
    id: 'doordash-stock',
    text: 'Show me a DoorDash stock chart with weekly candles for the last two months.',
    description: 'DoorDash stock chart request',
  },
  {
    id: 'react-component',
    text: 'Create a React component with TypeScript props and styled components.',
    description: 'React component creation command',
  },
];

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

// Calculate text similarity using Levenshtein distance
function calculateSimilarity(text1, text2) {
  const normalize = (text) => 
    text.toLowerCase()
        .replace(/[^\w\s]/g, '') // Remove punctuation
        .replace(/\s+/g, ' ')    // Normalize whitespace
        .trim();

  const a = normalize(text1);
  const b = normalize(text2);

  if (a === b) return 1.0;
  if (a.length === 0 || b.length === 0) return 0.0;

  // Levenshtein distance calculation
  const matrix = Array(b.length + 1).fill(null).map(() => Array(a.length + 1).fill(null));

  for (let i = 0; i <= a.length; i++) matrix[0][i] = i;
  for (let j = 0; j <= b.length; j++) matrix[j][0] = j;

  for (let j = 1; j <= b.length; j++) {
    for (let i = 1; i <= a.length; i++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      matrix[j][i] = Math.min(
        matrix[j][i - 1] + 1,     // deletion
        matrix[j - 1][i] + 1,     // insertion
        matrix[j - 1][i - 1] + cost // substitution
      );
    }
  }

  const maxLength = Math.max(a.length, b.length);
  const distance = matrix[b.length][a.length];
  return (maxLength - distance) / maxLength;
}

// Generate audio from text using TTS
async function generateAudio(text, outputPath, language = 'en') {
  try {
    const response = await fetch(`${CONFIG.serviceBaseUrl}/synthesize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text, language }),
    });

    if (!response.ok) {
      throw new Error(`TTS request failed: ${response.status}`);
    }

    const audioBuffer = await response.arrayBuffer();
    await fs.writeFile(outputPath, Buffer.from(audioBuffer));
    return outputPath;
  } catch (error) {
    throw new Error(`Failed to generate audio: ${error.message}`);
  }
}

// Transcribe audio using STT
async function transcribeAudio(audioFilePath) {
  try {
    const audioBuffer = await fs.readFile(audioFilePath);
    
    const formData = new FormData();
    const audioBlob = new Blob([audioBuffer], { type: 'audio/mpeg' });
    formData.append('audio', audioBlob, 'test-audio.mp3');

    const response = await fetch(`${CONFIG.serviceBaseUrl}/transcribe`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`STT request failed: ${response.status}`);
    }

    const result = await response.json();
    return result.text || '';
  } catch (error) {
    throw new Error(`Failed to transcribe audio: ${error.message}`);
  }
}

// Run a single audio test
async function runAudioTest(testCase) {
  const startTime = Date.now();
  const audioFileName = `${testCase.id}-${Date.now()}.mp3`;
  const audioFilePath = path.join(CONFIG.audioOutputDir, audioFileName);

  try {
    // Ensure output directory exists
    await fs.mkdir(CONFIG.audioOutputDir, { recursive: true });

    // Step 1: Generate audio from text
    await generateAudio(testCase.text, audioFilePath);

    // Step 2: Transcribe audio back to text
    const transcribedText = await transcribeAudio(audioFilePath);

    // Step 3: Calculate similarity
    const similarityScore = calculateSimilarity(testCase.text, transcribedText);

    // Step 4: Determine if test passed
    const passed = similarityScore >= CONFIG.similarityThreshold;

    return {
      testCase,
      audioFilePath,
      transcribedText,
      similarityScore,
      passed,
      durationMs: Date.now() - startTime,
    };
  } catch (error) {
    return {
      testCase,
      audioFilePath,
      transcribedText: '',
      similarityScore: 0,
      passed: false,
      durationMs: Date.now() - startTime,
      error: error.message,
    };
  }
}

// Print test result
function printTestResult(result) {
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

// Print summary
function printSummary(results) {
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

// Main function
async function main() {
  colorLog('bright', '🎵 SIMPLE AUDIO PIPELINE TEST');
  colorLog('bright', '🔄 Testing TTS → Audio → STT → Text Pipeline');
  console.log('═'.repeat(80));

  try {
    // Verify service is available
    colorLog('blue', '🚀 Checking TTS/STT service...');
    const healthResponse = await fetch(`${CONFIG.serviceBaseUrl}/health`);
    if (!healthResponse.ok) {
      throw new Error(`Service health check failed: ${healthResponse.status}`);
    }
    
    const health = await healthResponse.json();
    if (health.status !== 'healthy') {
      throw new Error('Service is not healthy');
    }
    
    colorLog('green', '✅ Service is healthy and ready');

    // Run tests
    const results = [];
    for (let i = 0; i < TEST_CASES.length; i++) {
      const testCase = TEST_CASES[i];
      colorLog('cyan', `\n[${i + 1}/${TEST_CASES.length}] Running: ${testCase.description}`);
      
      const result = await runAudioTest(testCase);
      results.push(result);
      printTestResult(result);
    }

    // Print summary
    printSummary(results);

    // Cleanup
    colorLog('blue', '\n🧹 Cleaning up generated audio files...');
    try {
      const files = await fs.readdir(CONFIG.audioOutputDir);
      const audioFiles = files.filter(file => file.endsWith('.mp3'));
      
      for (const file of audioFiles) {
        await fs.unlink(path.join(CONFIG.audioOutputDir, file));
      }
      colorLog('green', '✅ Cleanup completed');
    } catch (cleanupError) {
      colorLog('yellow', '⚠️  Cleanup warning: ' + cleanupError.message);
    }

  } catch (error) {
    colorLog('red', `❌ Test failed: ${error.message}`);
    
    if (error.message.includes('health check failed')) {
      colorLog('yellow', '\n💡 Troubleshooting Tips:');
      colorLog('yellow', '   1. Make sure the Whisper-TTS service is running on http://localhost:8000');
      colorLog('yellow', '   2. Check if Docker containers are up: docker ps');
      colorLog('yellow', '   3. Verify service health: curl http://localhost:8000/health');
      colorLog('yellow', '   4. Check service logs: docker logs whisper-tts-service');
    }
    
    process.exit(1);
  }
}

// Run the test
if (require.main === module) {
  main().catch(error => {
    colorLog('red', `❌ Test failed: ${error.message}`);
    process.exit(1);
  });
}

module.exports = { runAudioTest, calculateSimilarity, generateAudio, transcribeAudio };
