// ============================================================================
// AudioPlayer Component - Audio Playback with Controls and Visualization
// ============================================================================
//
// @file AudioPlayer.tsx
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description React component for audio playback with controls and visualization
//
// This component provides a complete audio playback interface with:
// - Audio playback controls (play, pause, stop, seek)
// - Real-time playback visualization with waveform
// - Volume control and mute functionality
// - Playback speed control
// - Progress tracking and seeking
// - Loading states and error handling
// - Accessibility support
// ============================================================================

import React, { useState, useRef, useEffect, useCallback } from 'react';
import styled from 'styled-components';

// ============================================================================
// Types
// ============================================================================

export interface AudioPlayerProps {
  audioData?: Uint8Array;
  audioUrl?: string;
  autoPlay?: boolean;
  showControls?: boolean;
  showWaveform?: boolean;
  onPlay?: () => void;
  onPause?: () => void;
  onEnded?: () => void;
  onError?: (error: string) => void;
  onTimeUpdate?: (currentTime: number, duration: number) => void;
  className?: string;
}

interface PlaybackState {
  isPlaying: boolean;
  isPaused: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  isMuted: boolean;
  playbackRate: number;
  isLoading: boolean;
}

// ============================================================================
// Styled Components
// ============================================================================

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  background: ${props => props.theme?.colors?.surface || '#f8f9fa'};
  border: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
  max-width: 400px;
`;

const WaveformContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  background: ${props => props.theme?.colors?.background || '#ffffff'};
  border-radius: 6px;
  border: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
  overflow: hidden;
  cursor: pointer;
  position: relative;
`;

const WaveformBar = styled.div<{ height: number; isActive: boolean; progress: number }>`
  width: 3px;
  height: ${props => Math.max(2, props.height)}px;
  background: ${props => {
    if (props.progress > 0) {
      return props.theme?.colors?.primary || '#007bff';
    }
    return props.isActive 
      ? props.theme?.colors?.secondary || '#6c757d'
      : props.theme?.colors?.muted || '#adb5bd';
  }};
  margin: 0 1px;
  border-radius: 1px;
  transition: background-color 0.2s ease;
`;

const ProgressOverlay = styled.div<{ progress: number }>`
  position: absolute;
  top: 0;
  left: 0;
  width: ${props => props.progress}%;
  height: 100%;
  background: linear-gradient(90deg, 
    ${props => props.theme?.colors?.primary || '#007bff'}20 0%,
    transparent 100%
  );
  pointer-events: none;
`;

const ControlsContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const PlayButton = styled.button<{ isPlaying: boolean }>`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background: ${props => props.theme?.colors?.primary || '#007bff'};
  color: white;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
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

const SecondaryButton = styled.button`
  width: 32px;
  height: 32px;
  border-radius: 4px;
  border: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
  background: ${props => props.theme?.colors?.surface || '#f8f9fa'};
  color: ${props => props.theme?.colors?.text || '#212529'};
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  
  &:hover {
    background: ${props => props.theme?.colors?.hover || '#e9ecef'};
  }
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

const TimeDisplay = styled.div`
  font-family: monospace;
  font-size: 14px;
  color: ${props => props.theme?.colors?.text || '#212529'};
  min-width: 80px;
`;

const VolumeContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const VolumeSlider = styled.input`
  width: 80px;
  height: 4px;
  border-radius: 2px;
  background: ${props => props.theme?.colors?.muted || '#adb5bd'};
  outline: none;
  cursor: pointer;
  
  &::-webkit-slider-thumb {
    appearance: none;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: ${props => props.theme?.colors?.primary || '#007bff'};
    cursor: pointer;
  }
  
  &::-moz-range-thumb {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: ${props => props.theme?.colors?.primary || '#007bff'};
    cursor: pointer;
    border: none;
  }
`;

const SpeedSelector = styled.select`
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
  background: ${props => props.theme?.colors?.surface || '#f8f9fa'};
  color: ${props => props.theme?.colors?.text || '#212529'};
  font-size: 12px;
  cursor: pointer;
`;

const LoadingSpinner = styled.div`
  width: 20px;
  height: 20px;
  border: 2px solid ${props => props.theme?.colors?.muted || '#adb5bd'};
  border-top: 2px solid ${props => props.theme?.colors?.primary || '#007bff'};
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  color: ${props => props.theme?.colors?.danger || '#dc3545'};
  font-size: 14px;
  text-align: center;
`;

// ============================================================================
// AudioPlayer Component
// ============================================================================

export const AudioPlayer: React.FC<AudioPlayerProps> = ({
  audioData,
  audioUrl,
  autoPlay = false,
  showControls = true,
  showWaveform = true,
  onPlay,
  onPause,
  onEnded,
  onError,
  onTimeUpdate,
  className,
}) => {
  // State
  const [playbackState, setPlaybackState] = useState<PlaybackState>({
    isPlaying: false,
    isPaused: false,
    currentTime: 0,
    duration: 0,
    volume: 1,
    isMuted: false,
    playbackRate: 1,
    isLoading: false,
  });
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [waveformData, setWaveformData] = useState<number[]>([]);

  // Refs
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const sourceRef = useRef<AudioBufferSourceNode | null>(null);

  // ============================================================================
  // Audio Setup
  // ============================================================================

  const setupAudio = useCallback(async () => {
    try {
      setPlaybackState(prev => ({ ...prev, isLoading: true }));
      setErrorMessage('');

      let audioSrc: string;

      if (audioData) {
        // Create blob URL from audio data
        const audioBlob = new Blob([audioData], { type: 'audio/mpeg' });
        audioSrc = URL.createObjectURL(audioBlob);
      } else if (audioUrl) {
        audioSrc = audioUrl;
      } else {
        throw new Error('No audio source provided');
      }

      // Create audio element
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = '';
      }

      const audio = new Audio(audioSrc);
      audioRef.current = audio;

      // Set up event listeners
      audio.addEventListener('loadedmetadata', () => {
        setPlaybackState(prev => ({
          ...prev,
          duration: audio.duration,
          isLoading: false,
        }));
      });

      audio.addEventListener('timeupdate', () => {
        const currentTime = audio.currentTime;
        const duration = audio.duration;
        
        setPlaybackState(prev => ({ ...prev, currentTime }));
        onTimeUpdate?.(currentTime, duration);
      });

      audio.addEventListener('ended', () => {
        setPlaybackState(prev => ({
          ...prev,
          isPlaying: false,
          isPaused: false,
          currentTime: 0,
        }));
        onEnded?.();
      });

      audio.addEventListener('error', (e) => {
        const error = 'Failed to load audio';
        setErrorMessage(error);
        setPlaybackState(prev => ({ ...prev, isLoading: false }));
        onError?.(error);
      });

      // Generate waveform data (simplified)
      if (showWaveform) {
        generateWaveform(audioSrc);
      }

      // Auto play if requested
      if (autoPlay) {
        await audio.play();
        setPlaybackState(prev => ({ ...prev, isPlaying: true }));
        onPlay?.();
      }

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Audio setup failed';
      setErrorMessage(errorMsg);
      setPlaybackState(prev => ({ ...prev, isLoading: false }));
      onError?.(errorMsg);
    }
  }, [audioData, audioUrl, autoPlay, showWaveform, onPlay, onError, onTimeUpdate, onEnded]);

  // ============================================================================
  // Waveform Generation
  // ============================================================================

  const generateWaveform = useCallback(async (audioSrc: string) => {
    try {
      // This is a simplified waveform generation
      // In a real implementation, you'd analyze the audio buffer
      const bars = Array.from({ length: 50 }, () => Math.random() * 40 + 10);
      setWaveformData(bars);
    } catch (error) {
      // Fallback to random waveform
      const bars = Array.from({ length: 50 }, () => Math.random() * 40 + 10);
      setWaveformData(bars);
    }
  }, []);

  // ============================================================================
  // Playback Controls
  // ============================================================================

  const togglePlayPause = useCallback(async () => {
    if (!audioRef.current) return;

    try {
      if (playbackState.isPlaying) {
        audioRef.current.pause();
        setPlaybackState(prev => ({ ...prev, isPlaying: false, isPaused: true }));
        onPause?.();
      } else {
        await audioRef.current.play();
        setPlaybackState(prev => ({ ...prev, isPlaying: true, isPaused: false }));
        onPlay?.();
      }
    } catch (error) {
      const errorMsg = 'Playback failed';
      setErrorMessage(errorMsg);
      onError?.(errorMsg);
    }
  }, [playbackState.isPlaying, onPlay, onPause, onError]);

  const stopPlayback = useCallback(() => {
    if (!audioRef.current) return;

    audioRef.current.pause();
    audioRef.current.currentTime = 0;
    setPlaybackState(prev => ({
      ...prev,
      isPlaying: false,
      isPaused: false,
      currentTime: 0,
    }));
  }, []);

  const seekTo = useCallback((time: number) => {
    if (!audioRef.current) return;

    audioRef.current.currentTime = time;
    setPlaybackState(prev => ({ ...prev, currentTime: time }));
  }, []);

  const handleWaveformClick = useCallback((event: React.MouseEvent<HTMLDivElement>) => {
    if (!audioRef.current || playbackState.duration === 0) return;

    const rect = event.currentTarget.getBoundingClientRect();
    const clickX = event.clientX - rect.left;
    const percentage = clickX / rect.width;
    const newTime = percentage * playbackState.duration;
    
    seekTo(newTime);
  }, [playbackState.duration, seekTo]);

  const setVolume = useCallback((volume: number) => {
    if (!audioRef.current) return;

    const clampedVolume = Math.max(0, Math.min(1, volume));
    audioRef.current.volume = clampedVolume;
    setPlaybackState(prev => ({ 
      ...prev, 
      volume: clampedVolume,
      isMuted: clampedVolume === 0 
    }));
  }, []);

  const toggleMute = useCallback(() => {
    if (!audioRef.current) return;

    if (playbackState.isMuted) {
      audioRef.current.volume = playbackState.volume;
      setPlaybackState(prev => ({ ...prev, isMuted: false }));
    } else {
      audioRef.current.volume = 0;
      setPlaybackState(prev => ({ ...prev, isMuted: true }));
    }
  }, [playbackState.isMuted, playbackState.volume]);

  const setPlaybackRate = useCallback((rate: number) => {
    if (!audioRef.current) return;

    audioRef.current.playbackRate = rate;
    setPlaybackState(prev => ({ ...prev, playbackRate: rate }));
  }, []);

  // ============================================================================
  // Effects
  // ============================================================================

  useEffect(() => {
    if (audioData || audioUrl) {
      setupAudio();
    }

    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = '';
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [audioData, audioUrl, setupAudio]);

  // ============================================================================
  // Render Helpers
  // ============================================================================

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const renderWaveform = () => {
    if (!showWaveform || waveformData.length === 0) return null;

    const progress = playbackState.duration > 0 
      ? (playbackState.currentTime / playbackState.duration) * 100 
      : 0;

    return (
      <WaveformContainer onClick={handleWaveformClick}>
        <ProgressOverlay progress={progress} />
        {waveformData.map((height, index) => {
          const barProgress = (index / waveformData.length) * 100;
          return (
            <WaveformBar
              key={index}
              height={height}
              isActive={playbackState.isPlaying}
              progress={barProgress <= progress ? 1 : 0}
            />
          );
        })}
      </WaveformContainer>
    );
  };

  // ============================================================================
  // Render
  // ============================================================================

  if (errorMessage) {
    return (
      <Container className={className}>
        <ErrorMessage>{errorMessage}</ErrorMessage>
      </Container>
    );
  }

  return (
    <Container className={className}>
      {renderWaveform()}

      {showControls && (
        <ControlsContainer>
          <PlayButton
            isPlaying={playbackState.isPlaying}
            onClick={togglePlayPause}
            disabled={playbackState.isLoading || !audioRef.current}
            aria-label={playbackState.isPlaying ? 'Pause' : 'Play'}
          >
            {playbackState.isLoading ? (
              <LoadingSpinner />
            ) : playbackState.isPlaying ? (
              '⏸️'
            ) : (
              '▶️'
            )}
          </PlayButton>

          <SecondaryButton
            onClick={stopPlayback}
            disabled={playbackState.isLoading || !audioRef.current}
            aria-label="Stop"
          >
            ⏹️
          </SecondaryButton>

          <TimeDisplay>
            {formatTime(playbackState.currentTime)} / {formatTime(playbackState.duration)}
          </TimeDisplay>

          <VolumeContainer>
            <SecondaryButton
              onClick={toggleMute}
              aria-label={playbackState.isMuted ? 'Unmute' : 'Mute'}
            >
              {playbackState.isMuted ? '🔇' : '🔊'}
            </SecondaryButton>
            <VolumeSlider
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={playbackState.isMuted ? 0 : playbackState.volume}
              onChange={(e) => setVolume(parseFloat(e.target.value))}
              aria-label="Volume"
            />
          </VolumeContainer>

          <SpeedSelector
            value={playbackState.playbackRate}
            onChange={(e) => setPlaybackRate(parseFloat(e.target.value))}
            aria-label="Playback speed"
          >
            <option value="0.5">0.5x</option>
            <option value="0.75">0.75x</option>
            <option value="1">1x</option>
            <option value="1.25">1.25x</option>
            <option value="1.5">1.5x</option>
            <option value="2">2x</option>
          </SpeedSelector>
        </ControlsContainer>
      )}
    </Container>
  );
};

export default AudioPlayer;
