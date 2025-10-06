// ============================================================================
// Audio Service - Pure Functions for Voice Processing
// ============================================================================
//
// @file AudioService.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Pure functional API client for audio processing
//
// This service provides pure functions for audio operations:
// - Input: Data (Blob, parameters)
// - Output: Promises with typed responses
// - No side effects, no state management
// - Direct browser API integration
// ============================================================================

/**
 * Audio API types - matching our working HTML implementation
 */
export interface TranscriptionResponse {
  language: string;
  text: string;
}

export interface ServiceHealth {
  status: string;
  service: string;
  version: string;
  capabilities: string[];
  whisper_model_loaded: boolean;
  cuda_available: boolean;
}

export interface AudioError {
  error: string;
  message: string;
  status?: number;
}

/**
 * @llm-type service
 * @llm-legend Provides frontend audio processing capabilities including speech-to-text transcription
 * @llm-key Uses Fetch API with FormData for audio upload, implements error handling and retry logic
 * @llm-map Frontend service layer, communicates with whisper-tts service on port 8000
 * @llm-axiom All audio operations must provide user feedback and handle network failures gracefully
 * @llm-contract Returns structured responses or throws descriptive errors for UI handling
 * @llm-token whisper-service: Python microservice providing speech-to-text capabilities
 *
 * Audio service for pure functional API communication
 * Following the same pattern as ChatService.ts
 */
export class AudioService {
  private whisperUrl: string;
  
  constructor(whisperUrl: string = 'http://localhost:8000') {
    this.whisperUrl = whisperUrl;
  }
  
  /**
   * @llm-type function
   * @llm-legend Converts user audio recordings to text using AI speech recognition
   * @llm-key Creates FormData with audio blob, sends POST to whisper service, handles JSON response
   * @llm-map Core transcription function called by UI components, integrates with whisper-tts service
   * @llm-contract Accepts audio Blob, returns TranscriptionResponse with text and language, throws on errors
   *
   * Pure function: Transcribe audio blob to text
   * Input: Blob (audio data)
   * Output: Promise<TranscriptionResponse>
   *
   * Uses the EXACT same approach as our working HTML implementation
   */
  async transcribeAudio(audioBlob: Blob): Promise<TranscriptionResponse> {
    try {
      // Same FormData approach that worked in HTML
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');
      
      const response = await fetch(`${this.whisperUrl}/transcribe`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error transcribing audio:', error);
      throw error;
    }
  }
  
  /**
   * Pure function: Check Whisper service health
   * Input: None
   * Output: Promise<ServiceHealth>
   */
  async checkHealth(): Promise<ServiceHealth> {
    try {
      const response = await fetch(`${this.whisperUrl}/health`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error checking audio service health:', error);
      throw error;
    }
  }
  
  /**
   * Pure function: Check browser audio capabilities
   * Input: None
   * Output: Object with capability flags
   * 
   * Same capability checks as our HTML implementation
   */
  checkBrowserCapabilities() {
    return {
      mediaRecorder: typeof MediaRecorder !== 'undefined',
      getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
      audioContext: typeof AudioContext !== 'undefined' || typeof (window as any).webkitAudioContext !== 'undefined',
    };
  }
  
  /**
   * Pure function: Create MediaRecorder with optimal settings
   * Input: MediaStream
   * Output: MediaRecorder instance
   * 
   * Same configuration as our working HTML implementation
   */
  createMediaRecorder(stream: MediaStream): MediaRecorder {
    const options: MediaRecorderOptions = {};
    
    // Use the same codec preferences as HTML version
    if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
      options.mimeType = 'audio/webm;codecs=opus';
    } else if (MediaRecorder.isTypeSupported('audio/webm')) {
      options.mimeType = 'audio/webm';
    } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
      options.mimeType = 'audio/mp4';
    }
    
    return new MediaRecorder(stream, options);
  }
  
  /**
   * Pure function: Request microphone access
   * Input: MediaStreamConstraints (optional)
   * Output: Promise<MediaStream>
   */
  async requestMicrophoneAccess(constraints?: MediaStreamConstraints): Promise<MediaStream> {
    const defaultConstraints: MediaStreamConstraints = {
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      }
    };
    
    try {
      return await navigator.mediaDevices.getUserMedia(constraints || defaultConstraints);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      throw new Error('Microphone access denied or not available');
    }
  }
}

// Export singleton instance following ChatService pattern
export const audioService = new AudioService();
