/**
 * @fileoverview Jest Setup Configuration
 * 
 * @description
 * Global Jest setup for React Testing Library, custom matchers,
 * and test environment configuration.
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';
import { TextEncoder, TextDecoder } from 'util';

// Configure React Testing Library
configure({
  testIdAttribute: 'data-testid',
  asyncUtilTimeout: 5000,
  computedStyleSupportsPseudoElements: true,
});

// Global polyfills for Node.js environment
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock window.ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock fetch for API testing
global.fetch = jest.fn();

// Mock console methods to reduce noise in tests
const originalError = console.error;
const originalWarn = console.warn;

beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOM.render is deprecated') ||
       args[0].includes('Warning: componentWillReceiveProps') ||
       args[0].includes('Warning: componentWillMount'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };

  console.warn = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('styled-components')
    ) {
      return;
    }
    originalWarn.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
  console.warn = originalWarn;
});

// Mock audio context for voice recorder tests
const mockAudioContext = {
  createMediaStreamSource: jest.fn(() => ({
    connect: jest.fn(),
    disconnect: jest.fn(),
  })),
  createAnalyser: jest.fn(() => ({
    connect: jest.fn(),
    disconnect: jest.fn(),
    fftSize: 256,
    frequencyBinCount: 128,
    getByteFrequencyData: jest.fn(),
    getByteTimeDomainData: jest.fn(),
  })),
  createGain: jest.fn(() => ({
    connect: jest.fn(),
    disconnect: jest.fn(),
    gain: { value: 1 },
  })),
  destination: {},
  sampleRate: 44100,
  currentTime: 0,
  state: 'running',
  suspend: jest.fn(),
  resume: jest.fn(),
  close: jest.fn(),
};

// @ts-ignore
global.AudioContext = jest.fn(() => mockAudioContext);
// @ts-ignore
global.webkitAudioContext = jest.fn(() => mockAudioContext);

// Mock MediaRecorder for voice input tests
const mockMediaRecorder = {
  start: jest.fn(),
  stop: jest.fn(),
  pause: jest.fn(),
  resume: jest.fn(),
  requestData: jest.fn(),
  state: 'inactive',
  mimeType: 'audio/webm',
  ondataavailable: null,
  onstart: null,
  onstop: null,
  onerror: null,
  onpause: null,
  onresume: null,
};

global.MediaRecorder = jest.fn(() => mockMediaRecorder) as any;
global.MediaRecorder.isTypeSupported = jest.fn(() => true);

// Mock getUserMedia
const mockGetUserMedia = jest.fn(() =>
  Promise.resolve({
    getTracks: () => [
      {
        stop: jest.fn(),
        kind: 'audio',
        enabled: true,
        readyState: 'live',
      },
    ],
    getAudioTracks: () => [
      {
        stop: jest.fn(),
        kind: 'audio',
        enabled: true,
        readyState: 'live',
      },
    ],
    getVideoTracks: () => [],
  })
);

Object.defineProperty(navigator, 'mediaDevices', {
  writable: true,
  value: {
    getUserMedia: mockGetUserMedia,
    enumerateDevices: jest.fn(() => Promise.resolve([])),
  },
});

// Mock URL.createObjectURL and revokeObjectURL
global.URL.createObjectURL = jest.fn(() => 'mock-object-url');
global.URL.revokeObjectURL = jest.fn();

// Mock Blob constructor
global.Blob = jest.fn().mockImplementation((content, options) => ({
  size: content ? content.reduce((acc: number, chunk: any) => acc + chunk.length, 0) : 0,
  type: options?.type || '',
  arrayBuffer: jest.fn(() => Promise.resolve(new ArrayBuffer(0))),
  text: jest.fn(() => Promise.resolve('')),
  stream: jest.fn(),
  slice: jest.fn(),
})) as any;

// Mock File constructor
global.File = jest.fn().mockImplementation((content, name, options) => ({
  ...new (global.Blob as any)(content, options),
  name,
  lastModified: Date.now(),
  webkitRelativePath: '',
})) as any;

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  length: 0,
  key: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock sessionStorage
Object.defineProperty(window, 'sessionStorage', {
  value: localStorageMock,
});

// Mock IndexedDB for database tests
const mockIDBRequest = {
  result: null,
  error: null,
  onsuccess: null,
  onerror: null,
  readyState: 'done',
};

const mockIDBDatabase = {
  close: jest.fn(),
  createObjectStore: jest.fn(),
  deleteObjectStore: jest.fn(),
  transaction: jest.fn(() => ({
    objectStore: jest.fn(() => ({
      add: jest.fn(() => mockIDBRequest),
      put: jest.fn(() => mockIDBRequest),
      get: jest.fn(() => mockIDBRequest),
      delete: jest.fn(() => mockIDBRequest),
      clear: jest.fn(() => mockIDBRequest),
      getAll: jest.fn(() => mockIDBRequest),
    })),
    oncomplete: null,
    onerror: null,
    onabort: null,
  })),
  version: 1,
  name: 'test-db',
  objectStoreNames: [],
};

global.indexedDB = {
  open: jest.fn(() => ({
    ...mockIDBRequest,
    result: mockIDBDatabase,
    onsuccess: null,
    onerror: null,
    onupgradeneeded: null,
  })),
  deleteDatabase: jest.fn(() => mockIDBRequest),
  databases: jest.fn(() => Promise.resolve([])),
} as any;

// Custom Jest matchers
expect.extend({
  toHaveBeenCalledWithAudioBlob(received: jest.Mock, expectedSize?: number) {
    const calls = received.mock.calls;
    const pass = calls.some(call => {
      const arg = call[0];
      return arg instanceof Blob && 
             arg.type.startsWith('audio/') &&
             (expectedSize === undefined || arg.size === expectedSize);
    });

    return {
      message: () => 
        pass 
          ? `Expected function not to have been called with audio blob`
          : `Expected function to have been called with audio blob${expectedSize ? ` of size ${expectedSize}` : ''}`,
      pass,
    };
  },

  toHaveValidTranscriptionResult(received: any) {
    const pass = received && 
                 typeof received === 'object' &&
                 typeof received.text === 'string' &&
                 received.text.length > 0;

    return {
      message: () =>
        pass
          ? `Expected not to have valid transcription result`
          : `Expected to have valid transcription result with text property`,
      pass,
    };
  },
});

// Global test utilities
global.testUtils = {
  // Create mock audio blob
  createMockAudioBlob: (size = 1024) => new Blob(['x'.repeat(size)], { type: 'audio/wav' }),
  
  // Create mock transcription result
  createMockTranscriptionResult: (text = 'Mock transcription') => ({
    text,
    language: 'en',
    confidence: 0.95,
  }),
  
  // Wait for async operations
  waitFor: (ms: number) => new Promise(resolve => setTimeout(resolve, ms)),
  
  // Mock fetch response
  mockFetchResponse: (data: any, status = 200) => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: status >= 200 && status < 300,
      status,
      json: () => Promise.resolve(data),
      text: () => Promise.resolve(JSON.stringify(data)),
      blob: () => Promise.resolve(new Blob([JSON.stringify(data)])),
    });
  },
};

// Declare global types for TypeScript
declare global {
  namespace jest {
    interface Matchers<R> {
      toHaveBeenCalledWithAudioBlob(expectedSize?: number): R;
      toHaveValidTranscriptionResult(): R;
    }
  }

  var testUtils: {
    createMockAudioBlob: (size?: number) => Blob;
    createMockTranscriptionResult: (text?: string) => any;
    waitFor: (ms: number) => Promise<void>;
    mockFetchResponse: (data: any, status?: number) => void;
  };
}
