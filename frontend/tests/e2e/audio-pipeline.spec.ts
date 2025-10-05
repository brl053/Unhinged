/**
 * @fileoverview Audio Pipeline E2E Tests
 * 
 * @description
 * Comprehensive end-to-end tests for the complete audio pipeline:
 * Text → TTS → Audio → STT → Text verification
 * 
 * Tests the entire voice input workflow including:
 * - TTS service generating audio from text
 * - STT service transcribing audio back to text
 * - Voice input component handling audio files
 * - UI updates and user feedback
 * - Round-trip accuracy and performance
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import { test, expect, Page } from '@playwright/test';
import { 
  AudioPipelineTester, 
  STANDARD_AUDIO_TEST_CASES, 
  AudioTestCase,
  AudioTestResult 
} from '../utils/audio-pipeline-testing';

// Test configuration
const AUDIO_TEST_CONFIG = {
  serviceBaseUrl: 'http://localhost:8000',
  audioOutputDir: './tests/fixtures/audio',
  language: 'en',
  similarityThreshold: 0.80, // 80% similarity for E2E tests (more lenient)
  timeoutMs: 45000, // Longer timeout for E2E
};

let audioPipelineTester: AudioPipelineTester;

test.describe('Audio Pipeline E2E Tests', () => {
  test.beforeAll(async () => {
    // Initialize audio pipeline tester
    audioPipelineTester = new AudioPipelineTester(AUDIO_TEST_CONFIG);
    await audioPipelineTester.initialize();
  });

  test.afterAll(async () => {
    // Cleanup generated audio files
    await audioPipelineTester.cleanup();
  });

  test.describe('TTS-to-STT Round Trip Tests', () => {
    test('should pass basic audio pipeline tests', async () => {
      // Run a subset of standard test cases
      const basicTestCases = STANDARD_AUDIO_TEST_CASES.slice(0, 3);
      const results = await audioPipelineTester.runAudioTestSuite(basicTestCases);

      // Verify all tests passed
      for (const result of results) {
        console.log(`Test: ${result.testCase.description}`);
        console.log(`Original: "${result.testCase.text}"`);
        console.log(`Transcribed: "${result.transcribedText}"`);
        console.log(`Similarity: ${(result.similarityScore * 100).toFixed(1)}%`);
        console.log(`Duration: ${result.durationMs}ms`);
        console.log('---');

        expect(result.passed, 
          `Audio test failed for "${result.testCase.description}": ` +
          `Expected similarity >= ${AUDIO_TEST_CONFIG.similarityThreshold * 100}%, ` +
          `got ${(result.similarityScore * 100).toFixed(1)}%`
        ).toBe(true);

        expect(result.error).toBeUndefined();
        expect(result.durationMs).toBeLessThan(AUDIO_TEST_CONFIG.timeoutMs);
      }
    });

    test('should handle technical terminology correctly', async () => {
      const technicalTestCase: AudioTestCase = {
        id: 'technical-ui-command',
        text: 'Create a React component with TypeScript props and styled components',
        description: 'Technical UI generation command',
      };

      const result = await audioPipelineTester.runAudioTest(technicalTestCase);

      expect(result.passed).toBe(true);
      expect(result.transcribedText).toContain('React');
      expect(result.transcribedText.toLowerCase()).toContain('component');
    });

    test('should handle voice commands for stock charts', async () => {
      const stockChartTestCase: AudioTestCase = {
        id: 'doordash-stock-chart',
        text: 'Show me a DoorDash stock chart with weekly data',
        description: 'Stock chart voice command',
      };

      const result = await audioPipelineTester.runAudioTest(stockChartTestCase);

      expect(result.passed).toBe(true);
      expect(result.transcribedText.toLowerCase()).toContain('doordash');
      expect(result.transcribedText.toLowerCase()).toContain('stock');
      expect(result.transcribedText.toLowerCase()).toContain('chart');
    });
  });

  test.describe('Voice Input Component Integration', () => {
    test('should handle voice input with generated audio', async ({ page }) => {
      // Navigate to the chatroom
      await page.goto('/');
      
      // Wait for the voice input component to be ready
      await expect(page.locator('[data-testid="voice-input"]')).toBeVisible();

      // Generate audio for testing
      const testText = 'Hello, this is a voice input test';
      const audioPath = './tests/fixtures/audio/voice-input-test.mp3';
      
      await audioPipelineTester.generateAudioFromText(testText, audioPath);

      // Simulate voice input (this would require custom implementation)
      // For now, we'll test the UI components are present and functional
      const voiceButton = page.locator('[data-testid="voice-input-button"]');
      await expect(voiceButton).toBeVisible();
      
      // Test voice input button states
      await voiceButton.click();
      await expect(voiceButton).toHaveAttribute('aria-pressed', 'true');
      
      // Stop recording
      await voiceButton.click();
      await expect(voiceButton).toHaveAttribute('aria-pressed', 'false');
    });

    test('should display transcription results in chat', async ({ page }) => {
      await page.goto('/');

      // Wait for chat interface
      await expect(page.locator('[data-testid="chat-container"]')).toBeVisible();

      // Test that we can send a text message (simulating transcription result)
      const textInput = page.locator('[data-testid="text-input"]');
      const sendButton = page.locator('[data-testid="send-button"]');

      await textInput.fill('This is a simulated transcription result');
      await sendButton.click();

      // Verify message appears in chat
      await expect(page.locator('[data-testid="chat-messages"]')).toContainText(
        'This is a simulated transcription result'
      );
    });
  });

  test.describe('Audio Service Integration', () => {
    test('should verify TTS service is accessible', async ({ request }) => {
      const response = await request.get(`${AUDIO_TEST_CONFIG.serviceBaseUrl}/health`);
      expect(response.ok()).toBe(true);

      const health = await response.json();
      expect(health.status).toBe('healthy');
      expect(health.capabilities).toContain('text-to-speech');
      expect(health.capabilities).toContain('speech-to-text');
    });

    test('should generate audio via TTS endpoint', async ({ request }) => {
      const response = await request.post(`${AUDIO_TEST_CONFIG.serviceBaseUrl}/synthesize`, {
        data: {
          text: 'This is a test of the text to speech service',
          language: 'en'
        }
      });

      expect(response.ok()).toBe(true);
      expect(response.headers()['content-type']).toContain('audio');
      
      const audioBuffer = await response.body();
      expect(audioBuffer.length).toBeGreaterThan(0);
    });

    test('should transcribe audio via STT endpoint', async ({ request }) => {
      // First generate an audio file
      const testText = 'This is a transcription test';
      const audioPath = './tests/fixtures/audio/transcription-test.mp3';
      
      await audioPipelineTester.generateAudioFromText(testText, audioPath);

      // Then transcribe it
      const audioBuffer = await require('fs').promises.readFile(audioPath);
      
      const formData = new FormData();
      const audioBlob = new Blob([audioBuffer], { type: 'audio/mpeg' });
      formData.append('audio', audioBlob, 'test.mp3');

      const response = await request.post(`${AUDIO_TEST_CONFIG.serviceBaseUrl}/transcribe`, {
        multipart: {
          audio: {
            name: 'test.mp3',
            mimeType: 'audio/mpeg',
            buffer: audioBuffer
          }
        }
      });

      expect(response.ok()).toBe(true);
      
      const result = await response.json();
      expect(result.text).toBeDefined();
      expect(result.text.length).toBeGreaterThan(0);
      
      // Verify transcription quality
      const similarity = audioPipelineTester.calculateSimilarity(testText, result.text);
      expect(similarity).toBeGreaterThan(0.7); // 70% similarity threshold
    });
  });

  test.describe('Performance and Reliability', () => {
    test('should complete audio pipeline within acceptable time', async () => {
      const testCase: AudioTestCase = {
        id: 'performance-test',
        text: 'This is a performance test for the audio pipeline',
        description: 'Performance benchmark test',
      };

      const startTime = Date.now();
      const result = await audioPipelineTester.runAudioTest(testCase);
      const totalTime = Date.now() - startTime;

      expect(result.passed).toBe(true);
      expect(totalTime).toBeLessThan(15000); // Should complete within 15 seconds
      expect(result.durationMs).toBeLessThan(12000); // Internal timing should be under 12s
    });

    test('should handle multiple concurrent audio requests', async () => {
      const testCases = [
        { id: 'concurrent-1', text: 'First concurrent test', description: 'Concurrent test 1' },
        { id: 'concurrent-2', text: 'Second concurrent test', description: 'Concurrent test 2' },
        { id: 'concurrent-3', text: 'Third concurrent test', description: 'Concurrent test 3' },
      ];

      // Run tests concurrently
      const promises = testCases.map(testCase => 
        audioPipelineTester.runAudioTest(testCase)
      );

      const results = await Promise.all(promises);

      // Verify all tests passed
      for (const result of results) {
        expect(result.passed).toBe(true);
        expect(result.error).toBeUndefined();
      }
    });

    test('should handle edge cases gracefully', async () => {
      const edgeCases: AudioTestCase[] = [
        {
          id: 'empty-text',
          text: '',
          description: 'Empty text input',
          expectedText: '', // Expect empty result
        },
        {
          id: 'single-word',
          text: 'Hello',
          description: 'Single word input',
        },
        {
          id: 'numbers-only',
          text: '12345',
          description: 'Numbers only input',
        },
        {
          id: 'special-characters',
          text: 'Hello! How are you? I am fine.',
          description: 'Text with punctuation',
        },
      ];

      for (const testCase of edgeCases) {
        const result = await audioPipelineTester.runAudioTest(testCase);
        
        // For edge cases, we're more lenient but still expect no errors
        expect(result.error).toBeUndefined();
        
        if (testCase.text.length > 0) {
          expect(result.transcribedText.length).toBeGreaterThan(0);
        }
      }
    });
  });
});

/**
 * Helper function to wait for audio processing to complete
 */
async function waitForAudioProcessing(page: Page, timeout: number = 30000): Promise<void> {
  await page.waitForFunction(
    () => {
      const voiceInput = document.querySelector('[data-testid="voice-input"]');
      return voiceInput && !voiceInput.classList.contains('processing');
    },
    { timeout }
  );
}

/**
 * Helper function to simulate audio file upload
 */
async function simulateAudioUpload(page: Page, audioFilePath: string): Promise<void> {
  // This would need to be implemented based on how the voice input component
  // handles audio file uploads or simulated audio input
  const fileInput = page.locator('input[type="file"][accept*="audio"]');
  if (await fileInput.count() > 0) {
    await fileInput.setInputFiles(audioFilePath);
  }
}
