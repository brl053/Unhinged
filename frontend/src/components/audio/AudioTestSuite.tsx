// ============================================================================
// Audio Test Suite - End-to-End Audio Testing Component
// ============================================================================
//
// @file AudioTestSuite.tsx
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Comprehensive testing component for audio functionality
//
// This component provides end-to-end testing for the audio system:
// - Service health checks and connectivity tests
// - Voice recording and transcription tests
// - Text-to-speech synthesis tests
// - Voice management and selection tests
// - Performance and latency measurements
// - Error scenario testing
// - Browser compatibility checks
// ============================================================================

import React, { useState, useCallback, useEffect } from 'react';
import styled from 'styled-components';
import { useAudioHealth, useSynthesizeText, useTranscribeAudio, useVoices } from '../../services/AudioService';
import VoiceInput from './VoiceInput/VoiceInput';
import AudioPlayer from './AudioPlayer/AudioPlayer';
import VoiceSelector from './VoiceSelector/VoiceSelector';
import { Voice, STTResponse } from '../../proto/audio';

// ============================================================================
// Types
// ============================================================================

interface TestResult {
  name: string;
  status: 'pending' | 'running' | 'passed' | 'failed';
  duration?: number;
  error?: string;
  details?: any;
}

interface AudioCapabilities {
  mediaDevices: boolean;
  getUserMedia: boolean;
  mediaRecorder: boolean;
  audioContext: boolean;
  webAudio: boolean;
  speechRecognition: boolean;
}

// ============================================================================
// Styled Components
// ============================================================================

const Container = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 30px;
`;

const Title = styled.h1`
  color: ${props => props.theme?.colors?.text || '#212529'};
  margin-bottom: 8px;
`;

const Subtitle = styled.p`
  color: ${props => props.theme?.colors?.muted || '#6c757d'};
  margin: 0;
`;

const Section = styled.div`
  margin-bottom: 30px;
  padding: 20px;
  background: ${props => props.theme?.colors?.surface || '#f8f9fa'};
  border-radius: 8px;
  border: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
`;

const SectionTitle = styled.h2`
  color: ${props => props.theme?.colors?.text || '#212529'};
  margin: 0 0 16px 0;
  font-size: 18px;
`;

const TestGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
`;

const TestCard = styled.div<{ status: TestResult['status'] }>`
  padding: 16px;
  background: ${props => props.theme?.colors?.background || '#ffffff'};
  border-radius: 6px;
  border: 2px solid ${props => {
    switch (props.status) {
      case 'passed': return props.theme?.colors?.success || '#28a745';
      case 'failed': return props.theme?.colors?.danger || '#dc3545';
      case 'running': return props.theme?.colors?.warning || '#ffc107';
      default: return props.theme?.colors?.border || '#dee2e6';
    }
  }};
`;

const TestName = styled.h3`
  margin: 0 0 8px 0;
  font-size: 16px;
  color: ${props => props.theme?.colors?.text || '#212529'};
`;

const TestStatus = styled.div<{ status: TestResult['status'] }>`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 500;
  color: ${props => {
    switch (props.status) {
      case 'passed': return props.theme?.colors?.success || '#28a745';
      case 'failed': return props.theme?.colors?.danger || '#dc3545';
      case 'running': return props.theme?.colors?.warning || '#ffc107';
      default: return props.theme?.colors?.muted || '#6c757d';
    }
  }};
`;

const TestDetails = styled.div`
  font-size: 14px;
  color: ${props => props.theme?.colors?.muted || '#6c757d'};
  margin-top: 8px;
`;

const TestError = styled.div`
  font-size: 12px;
  color: ${props => props.theme?.colors?.danger || '#dc3545'};
  background: ${props => props.theme?.colors?.danger || '#dc3545'}10;
  padding: 8px;
  border-radius: 4px;
  margin-top: 8px;
  font-family: monospace;
`;

const RunButton = styled.button`
  padding: 12px 24px;
  background: ${props => props.theme?.colors?.primary || '#007bff'};
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.theme?.colors?.primaryDark || '#0056b3'};
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
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
  color: ${props => props.supported 
    ? props.theme?.colors?.success || '#28a745'
    : props.theme?.colors?.danger || '#dc3545'
  };
  
  &::before {
    content: '${props => props.supported ? '✅' : '❌'}';
  }
`;

const InteractiveSection = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
`;

// ============================================================================
// Audio Test Suite Component
// ============================================================================

export const AudioTestSuite: React.FC = () => {
  // State
  const [tests, setTests] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [capabilities, setCapabilities] = useState<AudioCapabilities | null>(null);
  const [testAudio, setTestAudio] = useState<Uint8Array | null>(null);

  // Hooks
  const { data: healthStatus } = useAudioHealth();
  const { data: voices } = useVoices();
  const synthesizeText = useSynthesizeText();
  const transcribeAudio = useTranscribeAudio();

  // ============================================================================
  // Capability Detection
  // ============================================================================

  const detectCapabilities = useCallback((): AudioCapabilities => {
    return {
      mediaDevices: typeof navigator !== 'undefined' && !!navigator.mediaDevices,
      getUserMedia: typeof navigator !== 'undefined' && !!navigator.mediaDevices?.getUserMedia,
      mediaRecorder: typeof MediaRecorder !== 'undefined',
      audioContext: typeof AudioContext !== 'undefined' || typeof (window as any).webkitAudioContext !== 'undefined',
      webAudio: typeof AudioContext !== 'undefined',
      speechRecognition: typeof (window as any).SpeechRecognition !== 'undefined' || typeof (window as any).webkitSpeechRecognition !== 'undefined',
    };
  }, []);

  // ============================================================================
  // Test Implementations
  // ============================================================================

  const runTest = useCallback(async (testName: string, testFn: () => Promise<any>): Promise<TestResult> => {
    const startTime = Date.now();
    
    setTests(prev => prev.map(test => 
      test.name === testName 
        ? { ...test, status: 'running' }
        : test
    ));

    try {
      const result = await testFn();
      const duration = Date.now() - startTime;
      
      const testResult: TestResult = {
        name: testName,
        status: 'passed',
        duration,
        details: result,
      };

      setTests(prev => prev.map(test => 
        test.name === testName ? testResult : test
      ));

      return testResult;
    } catch (error) {
      const duration = Date.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      const testResult: TestResult = {
        name: testName,
        status: 'failed',
        duration,
        error: errorMessage,
      };

      setTests(prev => prev.map(test => 
        test.name === testName ? testResult : test
      ));

      return testResult;
    }
  }, []);

  const testServiceHealth = useCallback(async () => {
    const response = await fetch('/api/v1/audio/health');
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    return await response.json();
  }, []);

  const testVoiceList = useCallback(async () => {
    const response = await fetch('/api/v1/audio/voices');
    if (!response.ok) {
      throw new Error(`Voice list failed: ${response.status}`);
    }
    const data = await response.json();
    if (!data.voices || data.voices.length === 0) {
      throw new Error('No voices available');
    }
    return data;
  }, []);

  const testTextToSpeech = useCallback(async () => {
    const audioData = await synthesizeText.mutateAsync({
      text: 'This is a test of the text-to-speech system.',
      voiceId: 'voice-en-us-female-1',
    });
    
    if (!audioData || audioData.length === 0) {
      throw new Error('No audio data generated');
    }
    
    setTestAudio(audioData);
    return { audioSize: audioData.length };
  }, [synthesizeText]);

  const testMicrophoneAccess = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach(track => track.stop());
    return { tracks: stream.getTracks().length };
  }, []);

  const testAudioRecording = useCallback(async () => {
    return new Promise<any>((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Recording test timed out'));
      }, 10000);

      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          const mediaRecorder = new MediaRecorder(stream);
          const chunks: Blob[] = [];
          
          mediaRecorder.ondataavailable = (event) => {
            chunks.push(event.data);
          };
          
          mediaRecorder.onstop = () => {
            clearTimeout(timeout);
            stream.getTracks().forEach(track => track.stop());
            const audioBlob = new Blob(chunks, { type: 'audio/webm' });
            resolve({ audioSize: audioBlob.size });
          };
          
          mediaRecorder.start();
          setTimeout(() => mediaRecorder.stop(), 2000); // Record for 2 seconds
        })
        .catch(reject);
    });
  }, []);

  // ============================================================================
  // Test Runner
  // ============================================================================

  const runAllTests = useCallback(async () => {
    setIsRunning(true);
    
    const testDefinitions = [
      { name: 'Service Health Check', fn: testServiceHealth },
      { name: 'Voice List Retrieval', fn: testVoiceList },
      { name: 'Text-to-Speech Synthesis', fn: testTextToSpeech },
      { name: 'Microphone Access', fn: testMicrophoneAccess },
      { name: 'Audio Recording', fn: testAudioRecording },
    ];

    // Initialize test results
    setTests(testDefinitions.map(test => ({
      name: test.name,
      status: 'pending' as const,
    })));

    // Run tests sequentially
    for (const test of testDefinitions) {
      await runTest(test.name, test.fn);
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    setIsRunning(false);
  }, [runTest, testServiceHealth, testVoiceList, testTextToSpeech, testMicrophoneAccess, testAudioRecording]);

  // ============================================================================
  // Effects
  // ============================================================================

  useEffect(() => {
    setCapabilities(detectCapabilities());
  }, [detectCapabilities]);

  // ============================================================================
  // Render Helpers
  // ============================================================================

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'passed': return '✅';
      case 'failed': return '❌';
      case 'running': return '⏳';
      default: return '⏸️';
    }
  };

  const renderTestCard = (test: TestResult) => (
    <TestCard key={test.name} status={test.status}>
      <TestName>{test.name}</TestName>
      
      <TestStatus status={test.status}>
        {getStatusIcon(test.status)}
        {test.status.charAt(0).toUpperCase() + test.status.slice(1)}
        {test.duration && ` (${test.duration}ms)`}
      </TestStatus>
      
      {test.details && (
        <TestDetails>
          {JSON.stringify(test.details, null, 2)}
        </TestDetails>
      )}
      
      {test.error && (
        <TestError>{test.error}</TestError>
      )}
    </TestCard>
  );

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <Container>
      <Header>
        <Title>Audio System Test Suite</Title>
        <Subtitle>Comprehensive testing for audio functionality</Subtitle>
      </Header>

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
            <CapabilityItem supported={capabilities.webAudio}>
              Web Audio API
            </CapabilityItem>
            <CapabilityItem supported={capabilities.speechRecognition}>
              Speech Recognition API
            </CapabilityItem>
          </CapabilityList>
        )}
      </Section>

      <Section>
        <SectionTitle>Service Status</SectionTitle>
        <TestDetails>
          Health Status: {healthStatus ? '✅ Healthy' : '❌ Unhealthy'}
          <br />
          Available Voices: {voices?.length || 0}
        </TestDetails>
      </Section>

      <Section>
        <SectionTitle>Automated Tests</SectionTitle>
        
        <div style={{ marginBottom: '20px' }}>
          <RunButton onClick={runAllTests} disabled={isRunning}>
            {isRunning ? 'Running Tests...' : 'Run All Tests'}
          </RunButton>
        </div>

        <TestGrid>
          {tests.map(renderTestCard)}
        </TestGrid>
      </Section>

      <Section>
        <SectionTitle>Interactive Tests</SectionTitle>
        <InteractiveSection>
          <div>
            <h4>Voice Input Test</h4>
            <VoiceInput
              onTranscription={(result: STTResponse) => {
                console.log('Transcription result:', result);
              }}
              onError={(error) => {
                console.error('Voice input error:', error);
              }}
            />
          </div>

          <div>
            <h4>Voice Selection Test</h4>
            <VoiceSelector
              onVoiceSelect={(voice: Voice) => {
                console.log('Selected voice:', voice);
              }}
              showPreview={true}
              showFilters={true}
            />
          </div>

          {testAudio && (
            <div>
              <h4>Audio Playback Test</h4>
              <AudioPlayer
                audioData={testAudio}
                showControls={true}
                showWaveform={true}
              />
            </div>
          )}
        </InteractiveSection>
      </Section>
    </Container>
  );
};

export default AudioTestSuite;
