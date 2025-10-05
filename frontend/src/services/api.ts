/**
 * API Service Layer
 * 
 * Centralized HTTP client configuration for Unhinged application.
 * Handles communication with Ktor backend and Whisper TTS service.
 * 
 * @author Augment Agent
 * @version 1.0.0
 */

import axios from 'axios';

// Environment variable fallbacks
const getApiUrl = () => {
  try {
    return process.env.REACT_APP_API_URL || 'http://localhost:8080';
  } catch {
    return 'http://localhost:8080';
  }
};

const getWhisperUrl = () => {
  try {
    return process.env.REACT_APP_WHISPER_URL || 'http://localhost:8000';
  } catch {
    return 'http://localhost:8000';
  }
};

// Ktor Backend API
export const api = axios.create({
  baseURL: getApiUrl(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Whisper TTS Service API
export const whisperApi = axios.create({
  baseURL: getWhisperUrl(),
  timeout: 30000 // Longer timeout for audio processing
});

// Request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for global error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Response Error:', error);
    
    if (error.response?.status === 401) {
      // Handle unauthorized - clear token and redirect
      localStorage.removeItem('auth_token');
      // TODO: Redirect to login when auth is implemented
      console.warn('Unauthorized access - token cleared');
    }
    
    if (error.response?.status >= 500) {
      // Handle server errors
      console.error('Server error:', error.response.data);
    }
    
    return Promise.reject(error);
  }
);

// Whisper API error handling
whisperApi.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('Whisper API Error:', error);
    
    if (error.code === 'ECONNREFUSED') {
      console.error('Whisper service is not running on port 8000');
    }
    
    return Promise.reject(error);
  }
);

// API endpoint helpers
export const endpoints = {
  // Chat endpoints
  chat: '/chat',
  
  // Message endpoints (to be implemented in backend)
  messages: '/messages',
  messagesBulk: '/messages/bulk',
  
  // File upload endpoints (to be implemented in backend)
  files: '/files',
  
  // TTS endpoints
  tts: {
    synthesize: '/tts/synthesize',
    health: '/tts/health'
  },
  
  // Whisper service endpoints
  whisper: {
    transcribe: '/transcribe',
    synthesize: '/synthesize',
    health: '/health',
    info: '/info'
  }
};

// Type definitions for API responses
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

export interface TranscriptionResponse {
  text: string;
  language: string;
}

export interface MessageResponse {
  id: number;
  content: string;
  userId: string;
  timestamp: number;
  createdAt: string;
}

export interface FileUploadResponse {
  id: number;
  filename: string;
  contentType: string;
  sizeBytes: number;
  filePath: string;
  uploadedAt: string;
}

// Helper functions for common API calls
export const apiHelpers = {
  // Transcribe audio file
  transcribeAudio: async (audioBlob: Blob): Promise<TranscriptionResponse> => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    
    const response = await whisperApi.post(endpoints.whisper.transcribe, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    return response.data;
  },
  
  // Send chat message
  sendChatMessage: async (message: string): Promise<string> => {
    const response = await api.post(endpoints.chat, message, {
      headers: {
        'Content-Type': 'text/plain'
      }
    });
    
    return response.data;
  },
  
  // Upload file
  uploadFile: async (file: File): Promise<FileUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(endpoints.files, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / (progressEvent.total || 1)
        );
        console.log(`Upload progress: ${percentCompleted}%`);
      }
    });
    
    return response.data;
  }
};
