/**
 * @fileoverview Audio Pipeline E2E Testing Utilities
 * 
 * @description
 * Comprehensive testing utilities for the complete audio pipeline:
 * Text → TTS → Audio File → STT → Text comparison
 * 
 * This enables end-to-end testing of the voice input system by:
 * 1. Generating audio files from test text using our TTS service
 * 2. Using those audio files to test STT transcription
 * 3. Comparing the round-trip accuracy
 * 4. Testing the complete voice UI workflow in Playwright
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import { Page, expect } from '@playwright/test';
import fs from 'fs/promises';
import path from 'path';

/**
 * Configuration for audio pipeline testing
 */
export interface AudioTestConfig {
  /** Base URL for TTS/STT services */
  serviceBaseUrl: string;
  /** Directory to store generated audio files */
  audioOutputDir: string;
  /** Language for TTS generation */
  language: string;
  /** Similarity threshold for text comparison (0-1) */
  similarityThreshold: number;
  /** Timeout for audio generation/transcription */
  timeoutMs: number;
}

/**
 * Default configuration for audio testing
 */
const DEFAULT_CONFIG: AudioTestConfig = {
  serviceBaseUrl: 'http://localhost:8000',
  audioOutputDir: './tests/fixtures/audio',
  language: 'en',
  similarityThreshold: 0.85, // 85% similarity threshold
  timeoutMs: 30000,
};

/**
 * Test case for audio pipeline testing
 */
export interface AudioTestCase {
  /** Unique identifier for the test case */
  id: string;
  /** Original text to convert to speech */
  text: string;
  /** Expected transcription (may differ slightly from original) */
  expectedText?: string;
  /** Language for TTS/STT */
  language?: string;
  /** Description of the test case */
  description: string;
}

/**
 * Result of audio pipeline test
 */
export interface AudioTestResult {
  /** Test case that was executed */
  testCase: AudioTestCase;
  /** Generated audio file path */
  audioFilePath: string;
  /** Transcribed text from STT */
  transcribedText: string;
  /** Similarity score (0-1) */
  similarityScore: number;
  /** Whether the test passed */
  passed: boolean;
  /** Duration of the test in milliseconds */
  durationMs: number;
  /** Any errors encountered */
  error?: string;
}

/**
 * Pre-defined test cases for common scenarios
 */
export const STANDARD_AUDIO_TEST_CASES: AudioTestCase[] = [
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
    id: 'numbers-and-dates',
    text: 'Today is January 4th, 2025, and the temperature is 72 degrees.',
    description: 'Numbers, dates, and measurements',
  },
  {
    id: 'voice-commands',
    text: 'Create a voice input with submit button and placeholder text.',
    description: 'Typical voice command for UI generation',
  },
  {
    id: 'stock-chart-request',
    text: 'Show me a DoorDash stock chart with weekly candles for the last two months.',
    description: 'Complex financial data request',
  },
  {
    id: 'technical-terms',
    text: 'Initialize the React component with TypeScript interfaces and styled components.',
    description: 'Technical programming terminology',
  },
  {
    id: 'punctuation-test',
    text: 'Hello! How are you? I am fine, thank you. What about you?',
    description: 'Punctuation and conversational flow',
  },
  {
    id: 'long-sentence',
    text: 'This is a longer sentence designed to test the audio pipeline with multiple clauses, complex grammar, and various phonetic combinations that might challenge the speech recognition system.',
    description: 'Long complex sentence with multiple clauses',
  },
];

/**
 * Audio Pipeline Testing Utility Class
 */
export class AudioPipelineTester {
  private config: AudioTestConfig;

  constructor(config: Partial<AudioTestConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Initialize the testing environment
   */
  async initialize(): Promise<void> {
    // Ensure audio output directory exists
    await fs.mkdir(this.config.audioOutputDir, { recursive: true });

    // Verify TTS/STT service is available
    await this.verifyServices();
  }

  /**
   * Verify that TTS and STT services are available
   */
  private async verifyServices(): Promise<void> {
    try {
      const response = await fetch(`${this.config.serviceBaseUrl}/health`);
      if (!response.ok) {
        throw new Error(`Service health check failed: ${response.status}`);
      }

      const health = await response.json();
      if (!health.capabilities?.includes('text-to-speech') || 
          !health.capabilities?.includes('speech-to-text')) {
        throw new Error('Required TTS/STT capabilities not available');
      }
    } catch (error) {
      throw new Error(`Failed to verify audio services: ${error}`);
    }
  }

  /**
   * Generate audio file from text using TTS service
   */
  async generateAudioFromText(
    text: string, 
    outputPath: string, 
    language: string = this.config.language
  ): Promise<string> {
    try {
      const response = await fetch(`${this.config.serviceBaseUrl}/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          language,
        }),
      });

      if (!response.ok) {
        throw new Error(`TTS request failed: ${response.status}`);
      }

      // Save the audio file
      const audioBuffer = await response.arrayBuffer();
      await fs.writeFile(outputPath, Buffer.from(audioBuffer));

      return outputPath;
    } catch (error) {
      throw new Error(`Failed to generate audio: ${error}`);
    }
  }

  /**
   * Transcribe audio file using STT service
   */
  async transcribeAudioFile(audioFilePath: string): Promise<string> {
    try {
      const audioBuffer = await fs.readFile(audioFilePath);
      
      const formData = new FormData();
      const audioBlob = new Blob([audioBuffer], { type: 'audio/mpeg' });
      formData.append('audio', audioBlob, 'test-audio.mp3');

      const response = await fetch(`${this.config.serviceBaseUrl}/transcribe`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`STT request failed: ${response.status}`);
      }

      const result = await response.json();
      return result.text || '';
    } catch (error) {
      throw new Error(`Failed to transcribe audio: ${error}`);
    }
  }

  /**
   * Calculate text similarity using Levenshtein distance
   */
  calculateSimilarity(text1: string, text2: string): number {
    const normalize = (text: string) => 
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

  /**
   * Run a complete audio pipeline test
   */
  async runAudioTest(testCase: AudioTestCase): Promise<AudioTestResult> {
    const startTime = Date.now();
    const audioFileName = `${testCase.id}-${Date.now()}.mp3`;
    const audioFilePath = path.join(this.config.audioOutputDir, audioFileName);

    try {
      // Step 1: Generate audio from text
      await this.generateAudioFromText(
        testCase.text, 
        audioFilePath, 
        testCase.language || this.config.language
      );

      // Step 2: Transcribe audio back to text
      const transcribedText = await this.transcribeAudioFile(audioFilePath);

      // Step 3: Calculate similarity
      const expectedText = testCase.expectedText || testCase.text;
      const similarityScore = this.calculateSimilarity(expectedText, transcribedText);

      // Step 4: Determine if test passed
      const passed = similarityScore >= this.config.similarityThreshold;

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
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }

  /**
   * Run multiple audio tests
   */
  async runAudioTestSuite(testCases: AudioTestCase[]): Promise<AudioTestResult[]> {
    const results: AudioTestResult[] = [];

    for (const testCase of testCases) {
      const result = await this.runAudioTest(testCase);
      results.push(result);
    }

    return results;
  }

  /**
   * Clean up generated audio files
   */
  async cleanup(): Promise<void> {
    try {
      const files = await fs.readdir(this.config.audioOutputDir);
      const audioFiles = files.filter(file => file.endsWith('.mp3'));
      
      for (const file of audioFiles) {
        await fs.unlink(path.join(this.config.audioOutputDir, file));
      }
    } catch (error) {
      console.warn('Failed to cleanup audio files:', error);
    }
  }
}

/**
 * Playwright helper for testing voice input with generated audio
 */
export async function testVoiceInputWithAudio(
  page: Page,
  testText: string,
  voiceInputSelector: string = '[data-testid="voice-input"]'
): Promise<void> {
  const tester = new AudioPipelineTester();
  await tester.initialize();

  // Generate audio file
  const audioPath = path.join(tester['config'].audioOutputDir, `playwright-test-${Date.now()}.mp3`);
  await tester.generateAudioFromText(testText, audioPath);

  // Simulate file upload to voice input
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(audioPath);

  // Wait for transcription to complete
  await expect(page.locator('[data-testid="transcription-result"]')).toContainText(testText, {
    timeout: 30000,
  });

  // Cleanup
  await tester.cleanup();
}

export { AudioPipelineTester, DEFAULT_CONFIG };
