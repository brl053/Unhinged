// ============================================================================
// Voice Test Page - Simple Voice Recording Test
// ============================================================================
//
// @file VoiceTest.tsx
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Simple page to test voice recording functionality
//
// This page provides a simple interface to test voice recording:
// - Basic voice input component
// - Direct API testing
// - Service health checks
// - Browser compatibility checks
// ============================================================================

import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';

// ============================================================================
// Styled Components
// ============================================================================

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 40px;
`;

const Title = styled.h1`
  color: #212529;
  margin-bottom: 8px;
`;

const Subtitle = styled.p`
  color: #6c757d;
  margin: 0;
`;

const Section = styled.div`
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
`;

const SectionTitle = styled.h2`
  color: #212529;
  margin: 0 0 16px 0;
  font-size: 18px;
`;

const StatusIndicator = styled.div<{ status: 'healthy' | 'unhealthy' | 'loading' }>`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  background: ${props => {
    switch (props.status) {
      case 'healthy': return '#d4edda';
      case 'unhealthy': return '#f8d7da';
      default: return '#fff3cd';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case 'healthy': return '#155724';
      case 'unhealthy': return '#721c24';
      default: return '#856404';
    }
  }};
  border: 1px solid ${props => {
    switch (props.status) {
      case 'healthy': return '#c3e6cb';
      case 'unhealthy': return '#f5c6cb';
      default: return '#ffeaa7';
    }
  }};
`;

const RecordButton = styled.button<{ isRecording: boolean }>`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: none;
  background: ${props => props.isRecording ? '#dc3545' : '#007bff'};
  color: white;
  font-size: 32px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20px auto;
  
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  &:active {
    transform: scale(0.95);
  }
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.6;
    transform: none;
  }
`;

const TestResult = styled.div`
  margin-top: 16px;
  padding: 12px;
  background: #ffffff;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-family: monospace;
  font-size: 14px;
  white-space: pre-wrap;
`;

const CapabilityList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const CapabilityItem = styled.li<{ supported: boolean }>`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  color: ${props => props.supported ? '#28a745' : '#dc3545'};
  
  &::before {
    content: '${props => props.supported ? '✅' : '❌'}';
  }
`;

// ============================================================================
// Voice Test Component
// ============================================================================

export const VoiceTest: React.FC = () => {
  // State
  const [serviceHealth, setServiceHealth] = useState<'loading' | 'healthy' | 'unhealthy'>('loading');
  const [isRecording, setIsRecording] = useState(false);
  const [transcriptionResult, setTranscriptionResult] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [capabilities, setCapabilities] = useState<any>(null);

  // Refs
  const mediaRecorderRef = React.useRef<MediaRecorder | null>(null);
  const audioChunksRef = React.useRef<Blob[]>([]);

  // ============================================================================
  // Service Health Check
  // ============================================================================

  const checkServiceHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        setServiceHealth('healthy');
      } else {
        setServiceHealth('unhealthy');
      }
    } catch (error) {
      setServiceHealth('unhealthy');
    }
  };

  // ============================================================================
  // Browser Capabilities Check
  // ============================================================================

  const checkCapabilities = () => {
    const caps = {
      mediaDevices: typeof navigator !== 'undefined' && !!navigator.mediaDevices,
      getUserMedia: typeof navigator !== 'undefined' && !!navigator.mediaDevices?.getUserMedia,
      mediaRecorder: typeof MediaRecorder !== 'undefined',
      audioContext: typeof AudioContext !== 'undefined' || typeof (window as any).webkitAudioContext !== 'undefined',
    };
    setCapabilities(caps);
  };

  // ============================================================================
  // Voice Recording
  // ============================================================================

  const startRecording = async () => {
    try {
      setError('');
      setTranscriptionResult('');

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
        }
      });

      // Set up media recorder
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm';

      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType });
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        await processRecording(audioBlob);
        
        // Clean up
        stream.getTracks().forEach(track => track.stop());
      };

      // Start recording
      mediaRecorderRef.current.start();
      setIsRecording(true);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to start recording';
      setError(`Recording error: ${errorMessage}`);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processRecording = async (audioBlob: Blob) => {
    try {
      setTranscriptionResult('Processing audio...');

      // Create form data for upload
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      // Send to transcription service
      const response = await fetch('http://localhost:8000/transcribe', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Transcription failed: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      setTranscriptionResult(JSON.stringify(result, null, 2));

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Transcription failed';
      setError(`Transcription error: ${errorMessage}`);
      setTranscriptionResult('');
    }
  };

  // ============================================================================
  // Effects
  // ============================================================================

  useEffect(() => {
    checkServiceHealth();
    checkCapabilities();
  }, []);

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <Container>
      <Header>
        <Title>🎤 Voice Recording Test</Title>
        <Subtitle>Test voice recording and transcription functionality</Subtitle>
      </Header>

      <Section>
        <SectionTitle>Service Status</SectionTitle>
        <StatusIndicator status={serviceHealth}>
          {serviceHealth === 'loading' && '⏳ Checking...'}
          {serviceHealth === 'healthy' && '✅ Whisper Service Healthy'}
          {serviceHealth === 'unhealthy' && '❌ Whisper Service Unavailable'}
        </StatusIndicator>
      </Section>

      <Section>
        <SectionTitle>Browser Capabilities</SectionTitle>
        {capabilities && (
          <CapabilityList>
            <CapabilityItem supported={capabilities.mediaDevices}>
              Media Devices API
            </CapabilityItem>
            <CapabilityItem supported={capabilities.getUserMedia}>
              getUserMedia Support
            </CapabilityItem>
            <CapabilityItem supported={capabilities.mediaRecorder}>
              MediaRecorder API
            </CapabilityItem>
            <CapabilityItem supported={capabilities.audioContext}>
              AudioContext API
            </CapabilityItem>
          </CapabilityList>
        )}
      </Section>

      <Section>
        <SectionTitle>Voice Recording Test</SectionTitle>
        
        <div style={{ textAlign: 'center' }}>
          <RecordButton
            isRecording={isRecording}
            onClick={isRecording ? stopRecording : startRecording}
            disabled={serviceHealth !== 'healthy' || !capabilities?.getUserMedia}
          >
            {isRecording ? '⏹️' : '🎤'}
          </RecordButton>
          
          <div style={{ marginTop: '16px', fontSize: '14px', color: '#6c757d' }}>
            {isRecording ? 'Recording... Click to stop' : 'Click to start recording'}
          </div>
        </div>

        {error && (
          <TestResult style={{ color: '#dc3545', background: '#f8d7da' }}>
            {error}
          </TestResult>
        )}

        {transcriptionResult && (
          <TestResult>
            <strong>Transcription Result:</strong>
            {'\n'}
            {transcriptionResult}
          </TestResult>
        )}
      </Section>

      <Section>
        <SectionTitle>Instructions</SectionTitle>
        <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
          <p><strong>To test voice recording:</strong></p>
          <ol>
            <li>Ensure the Whisper service is healthy (green status above)</li>
            <li>Grant microphone permissions when prompted by your browser</li>
            <li>Click the microphone button to start recording</li>
            <li>Speak clearly into your microphone</li>
            <li>Click the stop button to end recording</li>
            <li>Wait for the transcription result to appear</li>
          </ol>
          
          <p><strong>Troubleshooting:</strong></p>
          <ul>
            <li>If service is unhealthy, ensure Docker containers are running</li>
            <li>If microphone access is denied, check browser permissions</li>
            <li>Try refreshing the page if recording doesn't work</li>
            <li>Use Chrome or Firefox for best compatibility</li>
          </ul>
        </div>
      </Section>
    </Container>
  );
};

export default VoiceTest;
