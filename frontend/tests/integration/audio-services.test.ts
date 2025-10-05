/**
 * @fileoverview Integration Tests for Audio Services
 * 
 * @description
 * Integration tests for TTS and STT services, testing the complete
 * audio pipeline with real service calls (when available).
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import { apiHelpers } from '../../src/services/api';

// Skip integration tests if services are not available
const SERVICES_AVAILABLE = process.env.TEST_INTEGRATION === 'true';
const SERVICE_BASE_URL = process.env.TEST_SERVICE_URL || 'http://localhost:8000';

const describeIntegration = SERVICES_AVAILABLE ? describe : describe.skip;

describeIntegration('Audio Services Integration', () => {
  beforeAll(async () => {
    // Verify services are available
    try {
      const response = await fetch(`${SERVICE_BASE_URL}/health`);
      if (!response.ok) {
        throw new Error(`Service health check failed: ${response.status}`);
      }
    } catch (error) {
      console.warn('Audio services not available for integration tests');
      throw error;
    }
  });

  describe('Text-to-Speech Service', () => {
    it('should generate audio from text', async () => {
      const testText = 'Hello, this is a test of the text to speech service';
      
      const response = await fetch(`${SERVICE_BASE_URL}/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: testText,
          language: 'en',
        }),
      });

      expect(response.ok).toBe(true);
      expect(response.headers.get('content-type')).toContain('audio');
      
      const audioBuffer = await response.arrayBuffer();
      expect(audioBuffer.byteLength).toBeGreaterThan(0);
    }, 30000);

    it('should handle different languages', async () => {
      const testCases = [
        { text: 'Hello world', language: 'en' },
        { text: 'Hola mundo', language: 'es' },
        { text: 'Bonjour le monde', language: 'fr' },
      ];

      for (const testCase of testCases) {
        const response = await fetch(`${SERVICE_BASE_URL}/synthesize`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(testCase),
        });

        expect(response.ok).toBe(true);
        
        const audioBuffer = await response.arrayBuffer();
        expect(audioBuffer.byteLength).toBeGreaterThan(0);
      }
    }, 60000);

    it('should handle empty text gracefully', async () => {
      const response = await fetch(`${SERVICE_BASE_URL}/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: '',
          language: 'en',
        }),
      });

      // Should either succeed with empty audio or return appropriate error
      expect([200, 400].includes(response.status)).toBe(true);
    });
  });

  describe('Speech-to-Text Service', () => {
    let testAudioBlob: Blob;

    beforeAll(async () => {
      // Generate test audio first
      const response = await fetch(`${SERVICE_BASE_URL}/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: 'This is a test transcription',
          language: 'en',
        }),
      });

      expect(response.ok).toBe(true);
      testAudioBlob = await response.blob();
    });

    it('should transcribe audio to text', async () => {
      const formData = new FormData();
      formData.append('audio', testAudioBlob, 'test.mp3');

      const response = await fetch(`${SERVICE_BASE_URL}/transcribe`, {
        method: 'POST',
        body: formData,
      });

      expect(response.ok).toBe(true);
      
      const result = await response.json();
      expect(result).toHaveValidTranscriptionResult();
      expect(result.text).toBeTruthy();
      expect(typeof result.text).toBe('string');
    }, 30000);

    it('should handle different audio formats', async () => {
      // This test would require different audio format samples
      // For now, we'll test with the same blob but different content-type
      const formData = new FormData();
      formData.append('audio', testAudioBlob, 'test.wav');

      const response = await fetch(`${SERVICE_BASE_URL}/transcribe`, {
        method: 'POST',
        body: formData,
      });

      // Should handle gracefully even if format is not optimal
      expect([200, 400, 415].includes(response.status)).toBe(true);
    });

    it('should handle invalid audio data', async () => {
      const invalidBlob = new Blob(['invalid audio data'], { type: 'audio/mp3' });
      const formData = new FormData();
      formData.append('audio', invalidBlob, 'invalid.mp3');

      const response = await fetch(`${SERVICE_BASE_URL}/transcribe`, {
        method: 'POST',
        body: formData,
      });

      // Should return appropriate error for invalid audio
      expect([400, 422].includes(response.status)).toBe(true);
    });
  });

  describe('Round-trip Audio Pipeline', () => {
    const testCases = [
      {
        text: 'Hello world',
        description: 'Basic greeting',
        expectedSimilarity: 0.8,
      },
      {
        text: 'The quick brown fox jumps over the lazy dog',
        description: 'Pangram test',
        expectedSimilarity: 0.7,
      },
      {
        text: 'Create a React component with TypeScript',
        description: 'Technical terminology',
        expectedSimilarity: 0.6,
      },
    ];

    testCases.forEach(testCase => {
      it(`should handle round-trip for: ${testCase.description}`, async () => {
        // Step 1: Generate audio from text
        const ttsResponse = await fetch(`${SERVICE_BASE_URL}/synthesize`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text: testCase.text,
            language: 'en',
          }),
        });

        expect(ttsResponse.ok).toBe(true);
        const audioBlob = await ttsResponse.blob();
        expect(audioBlob.size).toBeGreaterThan(0);

        // Step 2: Transcribe audio back to text
        const formData = new FormData();
        formData.append('audio', audioBlob, 'test.mp3');

        const sttResponse = await fetch(`${SERVICE_BASE_URL}/transcribe`, {
          method: 'POST',
          body: formData,
        });

        expect(sttResponse.ok).toBe(true);
        const transcription = await sttResponse.json();
        expect(transcription).toHaveValidTranscriptionResult();

        // Step 3: Calculate similarity
        const similarity = calculateSimilarity(testCase.text, transcription.text);
        expect(similarity).toBeGreaterThan(testCase.expectedSimilarity);

        console.log(`Round-trip test: "${testCase.text}" -> "${transcription.text}" (${(similarity * 100).toFixed(1)}% similarity)`);
      }, 60000);
    });
  });

  describe('Performance', () => {
    it('should complete TTS within reasonable time', async () => {
      const startTime = Date.now();
      
      const response = await fetch(`${SERVICE_BASE_URL}/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: 'Performance test for text to speech',
          language: 'en',
        }),
      });

      const duration = Date.now() - startTime;
      
      expect(response.ok).toBe(true);
      expect(duration).toBeLessThan(10000); // Should complete within 10 seconds
    });

    it('should complete STT within reasonable time', async () => {
      // Generate test audio first
      const ttsResponse = await fetch(`${SERVICE_BASE_URL}/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: 'Performance test for speech to text',
          language: 'en',
        }),
      });

      const audioBlob = await ttsResponse.blob();
      
      const startTime = Date.now();
      
      const formData = new FormData();
      formData.append('audio', audioBlob, 'test.mp3');

      const sttResponse = await fetch(`${SERVICE_BASE_URL}/transcribe`, {
        method: 'POST',
        body: formData,
      });

      const duration = Date.now() - startTime;
      
      expect(sttResponse.ok).toBe(true);
      expect(duration).toBeLessThan(15000); // Should complete within 15 seconds
    });
  });

  describe('Error Handling', () => {
    it('should handle malformed TTS requests', async () => {
      const response = await fetch(`${SERVICE_BASE_URL}/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: 'invalid json',
      });

      expect(response.status).toBe(400);
    });

    it('should handle missing audio in STT requests', async () => {
      const formData = new FormData();
      // Don't append audio file

      const response = await fetch(`${SERVICE_BASE_URL}/transcribe`, {
        method: 'POST',
        body: formData,
      });

      expect(response.status).toBe(400);
    });

    it('should handle service overload gracefully', async () => {
      // Send multiple concurrent requests
      const promises = Array.from({ length: 5 }, () =>
        fetch(`${SERVICE_BASE_URL}/synthesize`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text: 'Concurrent request test',
            language: 'en',
          }),
        })
      );

      const responses = await Promise.all(promises);
      
      // Most requests should succeed, some might be rate limited
      const successCount = responses.filter(r => r.ok).length;
      expect(successCount).toBeGreaterThan(0);
    }, 30000);
  });
});

/**
 * Calculate text similarity using Levenshtein distance
 */
function calculateSimilarity(text1: string, text2: string): number {
  const normalize = (text: string) => 
    text.toLowerCase()
        .replace(/[^\w\s]/g, '')
        .replace(/\s+/g, ' ')
        .trim();

  const a = normalize(text1);
  const b = normalize(text2);

  if (a === b) return 1.0;
  if (a.length === 0 || b.length === 0) return 0.0;

  const matrix = Array(b.length + 1).fill(null).map(() => Array(a.length + 1).fill(null));

  for (let i = 0; i <= a.length; i++) matrix[0][i] = i;
  for (let j = 0; j <= b.length; j++) matrix[j][0] = j;

  for (let j = 1; j <= b.length; j++) {
    for (let i = 1; i <= a.length; i++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      matrix[j][i] = Math.min(
        matrix[j][i - 1] + 1,
        matrix[j - 1][i] + 1,
        matrix[j - 1][i - 1] + cost
      );
    }
  }

  const maxLength = Math.max(a.length, b.length);
  const distance = matrix[b.length][a.length];
  return (maxLength - distance) / maxLength;
}
