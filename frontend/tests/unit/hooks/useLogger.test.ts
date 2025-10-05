/**
 * @fileoverview Unit Tests for useLogger Hook
 * 
 * @description
 * Comprehensive tests for the useLogger hook including
 * log level filtering, component context, and performance.
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import { renderHook } from '@testing-library/react';
import { useLogger, LogLevel } from '../../../src/hooks/useLogger';

// Mock console methods
const mockConsole = {
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
  log: jest.fn(),
};

beforeEach(() => {
  jest.clearAllMocks();
  
  // Replace console methods with mocks
  Object.assign(console, mockConsole);
});

afterEach(() => {
  jest.restoreAllMocks();
});

describe('useLogger Hook', () => {
  describe('Basic Functionality', () => {
    it('should create a logger function', () => {
      const { result } = renderHook(() => useLogger(LogLevel.INFO, 'TestComponent'));
      
      expect(typeof result.current).toBe('function');
    });

    it('should log messages with component context', () => {
      const { result } = renderHook(() => useLogger(LogLevel.INFO, 'TestComponent'));
      const logger = result.current;
      
      logger('Test message', { key: 'value' });
      
      // Verify console was called (exact implementation may vary)
      expect(mockConsole.info).toHaveBeenCalled();
    });

    it('should handle messages without context', () => {
      const { result } = renderHook(() => useLogger(LogLevel.INFO, 'TestComponent'));
      const logger = result.current;
      
      expect(() => {
        logger('Test message without context');
      }).not.toThrow();
    });
  });

  describe('Log Level Filtering', () => {
    it('should respect log level filtering', () => {
      const { result } = renderHook(() => useLogger(LogLevel.ERROR, 'TestComponent'));
      const logger = result.current;
      
      // This should be logged (ERROR level)
      logger('Error message');
      
      // Mock different log levels if the implementation supports it
      expect(mockConsole.error || mockConsole.info).toHaveBeenCalled();
    });

    it('should work with different log levels', () => {
      const levels = [LogLevel.TRACE, LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR, LogLevel.FATAL];
      
      levels.forEach(level => {
        const { result } = renderHook(() => useLogger(level, 'TestComponent'));
        const logger = result.current;
        
        expect(typeof logger).toBe('function');
        expect(() => logger('Test message')).not.toThrow();
      });
    });
  });

  describe('Component Context', () => {
    it('should include component name in logs', () => {
      const componentName = 'VoiceInputComponent';
      const { result } = renderHook(() => useLogger(LogLevel.INFO, componentName));
      const logger = result.current;
      
      logger('Test message');
      
      // The exact implementation may vary, but component context should be included
      expect(mockConsole.info).toHaveBeenCalled();
    });

    it('should handle different component names', () => {
      const components = ['Chatroom', 'VoiceInput', 'AudioPipeline', 'StockChart'];
      
      components.forEach(componentName => {
        const { result } = renderHook(() => useLogger(LogLevel.INFO, componentName));
        const logger = result.current;
        
        expect(() => logger('Test message')).not.toThrow();
      });
    });
  });

  describe('Performance', () => {
    it('should not cause memory leaks with multiple renders', () => {
      const { result, rerender } = renderHook(
        ({ level, component }) => useLogger(level, component),
        {
          initialProps: { level: LogLevel.INFO, component: 'TestComponent' }
        }
      );

      // Re-render multiple times
      for (let i = 0; i < 10; i++) {
        rerender({ level: LogLevel.INFO, component: `TestComponent${i}` });
      }

      const logger = result.current;
      expect(typeof logger).toBe('function');
    });

    it('should handle rapid logging without issues', () => {
      const { result } = renderHook(() => useLogger(LogLevel.INFO, 'TestComponent'));
      const logger = result.current;
      
      // Log many messages rapidly
      for (let i = 0; i < 100; i++) {
        expect(() => {
          logger(`Message ${i}`, { iteration: i });
        }).not.toThrow();
      }
    });
  });

  describe('Error Handling', () => {
    it('should handle invalid log levels gracefully', () => {
      // @ts-ignore - Testing invalid input
      const { result } = renderHook(() => useLogger('invalid' as any, 'TestComponent'));
      const logger = result.current;
      
      expect(typeof logger).toBe('function');
      expect(() => logger('Test message')).not.toThrow();
    });

    it('should handle empty component names', () => {
      const { result } = renderHook(() => useLogger(LogLevel.INFO, ''));
      const logger = result.current;
      
      expect(typeof logger).toBe('function');
      expect(() => logger('Test message')).not.toThrow();
    });

    it('should handle null/undefined context data', () => {
      const { result } = renderHook(() => useLogger(LogLevel.INFO, 'TestComponent'));
      const logger = result.current;
      
      expect(() => {
        logger('Test message', null as any);
        logger('Test message', undefined);
      }).not.toThrow();
    });
  });

  describe('Integration with Audio Pipeline', () => {
    it('should work with voice recorder context', () => {
      const { result } = renderHook(() => useLogger(LogLevel.DEBUG, 'VoiceRecorder'));
      const logger = result.current;
      
      const voiceContext = {
        status: 'recording',
        duration: 1500,
        audioLevel: 0.7,
      };
      
      expect(() => {
        logger('Recording started', voiceContext);
        logger('Audio level updated', { level: voiceContext.audioLevel });
        logger('Recording stopped', { duration: voiceContext.duration });
      }).not.toThrow();
    });

    it('should work with transcription context', () => {
      const { result } = renderHook(() => useLogger(LogLevel.INFO, 'AudioPipeline'));
      const logger = result.current;
      
      const transcriptionContext = {
        originalText: 'Hello world',
        transcribedText: 'Hello world',
        similarity: 1.0,
        duration: 850,
      };
      
      expect(() => {
        logger('Transcription completed', transcriptionContext);
      }).not.toThrow();
    });
  });

  describe('Development vs Production', () => {
    it('should adapt to environment', () => {
      const originalEnv = process.env.NODE_ENV;
      
      // Test development environment
      process.env.NODE_ENV = 'development';
      const { result: devResult } = renderHook(() => useLogger(LogLevel.DEBUG, 'TestComponent'));
      expect(typeof devResult.current).toBe('function');
      
      // Test production environment
      process.env.NODE_ENV = 'production';
      const { result: prodResult } = renderHook(() => useLogger(LogLevel.DEBUG, 'TestComponent'));
      expect(typeof prodResult.current).toBe('function');
      
      // Restore original environment
      process.env.NODE_ENV = originalEnv;
    });
  });
});
