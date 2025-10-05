/**
 * @fileoverview Unit Tests for useVoiceRecorder Hook
 * 
 * @description
 * Comprehensive tests for the useVoiceRecorder hook including
 * recording functionality, transcription, error handling, and
 * integration with audio services.
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import { renderHook, act } from '@testing-library/react';
import { useVoiceRecorder } from '../../../src/hooks/useVoiceRecorder';

// Mock the API helpers
jest.mock('../../../src/services/api', () => ({
  apiHelpers: {
    transcribeAudio: jest.fn(),
  },
}));

// Mock the database helpers
jest.mock('../../../src/services/db', () => ({
  dbHelpers: {
    audioCache: {
      store: jest.fn(),
      retrieve: jest.fn(),
    },
  },
}));

import { apiHelpers } from '../../../src/services/api';
import { dbHelpers } from '../../../src/services/db';

const mockApiHelpers = apiHelpers as jest.Mocked<typeof apiHelpers>;
const mockDbHelpers = dbHelpers as jest.Mocked<typeof dbHelpers>;

describe('useVoiceRecorder Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Setup default mock responses
    mockApiHelpers.transcribeAudio.mockResolvedValue({
      text: 'Mock transcription result',
      language: 'en',
      confidence: 0.95,
    });
    
    mockDbHelpers.audioCache.store.mockResolvedValue(undefined);
  });

  describe('Initial State', () => {
    it('should initialize with correct default state', () => {
      const { result } = renderHook(() => useVoiceRecorder());
      
      expect(result.current.status).toBe('idle');
      expect(result.current.isRecording).toBe(false);
      expect(result.current.isProcessing).toBe(false);
      expect(result.current.hasError).toBe(false);
      expect(result.current.duration).toBe(0);
      expect(result.current.audioLevel).toBe(0);
      expect(result.current.transcription).toBeNull();
      expect(result.current.error).toBeNull();
    });

    it('should accept custom configuration', () => {
      const config = {
        autoTranscribe: false,
        maxDuration: 30000,
        cacheAudio: false,
      };
      
      const { result } = renderHook(() => useVoiceRecorder(config));
      
      // State should still be initialized correctly
      expect(result.current.status).toBe('idle');
      expect(typeof result.current.startRecording).toBe('function');
      expect(typeof result.current.stopRecording).toBe('function');
    });
  });

  describe('Recording Functionality', () => {
    it('should start recording when startRecording is called', async () => {
      const { result } = renderHook(() => useVoiceRecorder());
      
      await act(async () => {
        await result.current.startRecording();
      });
      
      expect(result.current.isRecording).toBe(true);
      expect(result.current.status).toBe('recording');
    });

    it('should stop recording when stopRecording is called', async () => {
      const { result } = renderHook(() => useVoiceRecorder());
      
      // Start recording first
      await act(async () => {
        await result.current.startRecording();
      });
      
      expect(result.current.isRecording).toBe(true);
      
      // Stop recording
      await act(async () => {
        result.current.stopRecording();
      });
      
      expect(result.current.isRecording).toBe(false);
    });

    it('should handle recording errors gracefully', async () => {
      // Mock getUserMedia to fail
      const mockGetUserMedia = jest.fn().mockRejectedValue(new Error('Permission denied'));
      Object.defineProperty(navigator, 'mediaDevices', {
        value: { getUserMedia: mockGetUserMedia },
        configurable: true,
      });
      
      const { result } = renderHook(() => useVoiceRecorder());
      
      await act(async () => {
        await result.current.startRecording();
      });
      
      expect(result.current.hasError).toBe(true);
      expect(result.current.error).toBeTruthy();
      expect(result.current.status).toBe('error');
    });
  });

  describe('Transcription', () => {
    it('should transcribe audio when autoTranscribe is enabled', async () => {
      const { result } = renderHook(() => useVoiceRecorder({ autoTranscribe: true }));
      
      // Mock successful recording and transcription
      await act(async () => {
        await result.current.startRecording();
      });
      
      await act(async () => {
        result.current.stopRecording();
      });
      
      // Wait for transcription to complete
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
      });
      
      expect(mockApiHelpers.transcribeAudio).toHaveBeenCalled();
    });

    it('should handle transcription errors', async () => {
      mockApiHelpers.transcribeAudio.mockRejectedValue(new Error('Transcription failed'));
      
      const { result } = renderHook(() => useVoiceRecorder({ autoTranscribe: true }));
      
      await act(async () => {
        await result.current.startRecording();
        result.current.stopRecording();
      });
      
      // Wait for transcription attempt
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
      });
      
      expect(result.current.hasError).toBe(true);
      expect(result.current.error).toBeTruthy();
    });

    it('should provide manual transcription method', async () => {
      const { result } = renderHook(() => useVoiceRecorder({ autoTranscribe: false }));
      
      const mockBlob = global.testUtils.createMockAudioBlob();
      
      await act(async () => {
        await result.current.transcribeAudio(mockBlob);
      });
      
      expect(mockApiHelpers.transcribeAudio).toHaveBeenCalledWith(mockBlob);
      expect(result.current.transcription).toEqual({
        text: 'Mock transcription result',
        language: 'en',
        confidence: 0.95,
      });
    });
  });

  describe('Audio Caching', () => {
    it('should cache audio when cacheAudio is enabled', async () => {
      const { result } = renderHook(() => useVoiceRecorder({ 
        cacheAudio: true,
        autoTranscribe: true 
      }));
      
      await act(async () => {
        await result.current.startRecording();
        result.current.stopRecording();
      });
      
      // Wait for processing
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
      });
      
      expect(mockDbHelpers.audioCache.store).toHaveBeenCalled();
    });

    it('should not cache audio when cacheAudio is disabled', async () => {
      const { result } = renderHook(() => useVoiceRecorder({ 
        cacheAudio: false,
        autoTranscribe: true 
      }));
      
      await act(async () => {
        await result.current.startRecording();
        result.current.stopRecording();
      });
      
      // Wait for processing
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
      });
      
      expect(mockDbHelpers.audioCache.store).not.toHaveBeenCalled();
    });
  });

  describe('Duration Tracking', () => {
    it('should track recording duration', async () => {
      const { result } = renderHook(() => useVoiceRecorder());
      
      await act(async () => {
        await result.current.startRecording();
      });
      
      // Wait a bit
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
      });
      
      expect(result.current.duration).toBeGreaterThan(0);
      
      await act(async () => {
        result.current.stopRecording();
      });
    });

    it('should reset duration when recording stops', async () => {
      const { result } = renderHook(() => useVoiceRecorder());
      
      await act(async () => {
        await result.current.startRecording();
      });
      
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
      });
      
      expect(result.current.duration).toBeGreaterThan(0);
      
      await act(async () => {
        result.current.stopRecording();
      });
      
      // Duration should reset after stopping
      expect(result.current.duration).toBe(0);
    });
  });

  describe('Status Management', () => {
    it('should transition through correct status states', async () => {
      const { result } = renderHook(() => useVoiceRecorder({ autoTranscribe: true }));
      
      // Initial state
      expect(result.current.status).toBe('idle');
      
      // Start recording
      await act(async () => {
        await result.current.startRecording();
      });
      expect(result.current.status).toBe('recording');
      
      // Stop recording (should go to processing if autoTranscribe is true)
      await act(async () => {
        result.current.stopRecording();
      });
      
      // Should eventually return to idle
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 200));
      });
      
      expect(['idle', 'processing'].includes(result.current.status)).toBe(true);
    });
  });

  describe('Error Recovery', () => {
    it('should allow recovery from error state', async () => {
      // Mock getUserMedia to fail initially
      const mockGetUserMedia = jest.fn().mockRejectedValueOnce(new Error('Permission denied'));
      Object.defineProperty(navigator, 'mediaDevices', {
        value: { getUserMedia: mockGetUserMedia },
        configurable: true,
      });
      
      const { result } = renderHook(() => useVoiceRecorder());
      
      // First attempt should fail
      await act(async () => {
        await result.current.startRecording();
      });
      
      expect(result.current.hasError).toBe(true);
      
      // Mock getUserMedia to succeed on retry
      mockGetUserMedia.mockResolvedValue({
        getTracks: () => [{ stop: jest.fn() }],
        getAudioTracks: () => [{ stop: jest.fn() }],
      } as any);
      
      // Reset error state and try again
      await act(async () => {
        result.current.clearError();
      });
      
      expect(result.current.hasError).toBe(false);
      expect(result.current.error).toBeNull();
      
      // Should be able to record now
      await act(async () => {
        await result.current.startRecording();
      });
      
      expect(result.current.isRecording).toBe(true);
    });
  });

  describe('Cleanup', () => {
    it('should cleanup resources on unmount', () => {
      const { result, unmount } = renderHook(() => useVoiceRecorder());
      
      // Start recording
      act(() => {
        result.current.startRecording();
      });
      
      // Unmount should not throw
      expect(() => {
        unmount();
      }).not.toThrow();
    });
  });
});
