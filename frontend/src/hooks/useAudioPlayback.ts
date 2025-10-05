// ============================================================================
// Audio Playback Hook - React Hook for Audio Playback Management
// ============================================================================
//
// @file useAudioPlayback.ts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description React hook for managing audio playback state and operations
//
// This hook provides a complete interface for audio playback with:
// - HTML5 Audio API integration
// - Playback state management
// - Volume and speed control
// - Progress tracking and seeking
// - Error handling and cleanup
// - TypeScript type safety
// ============================================================================

import { useState, useRef, useCallback, useEffect } from 'react';

// ============================================================================
// Types
// ============================================================================

export interface AudioPlaybackState {
  isPlaying: boolean;
  isPaused: boolean;
  isLoading: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  isMuted: boolean;
  playbackRate: number;
  error: string | null;
  canPlay: boolean;
}

export interface AudioPlaybackOptions {
  autoPlay?: boolean;
  loop?: boolean;
  preload?: 'none' | 'metadata' | 'auto';
  volume?: number;
  playbackRate?: number;
  onPlay?: () => void;
  onPause?: () => void;
  onEnded?: () => void;
  onTimeUpdate?: (currentTime: number, duration: number) => void;
  onVolumeChange?: (volume: number, isMuted: boolean) => void;
  onError?: (error: string) => void;
  onLoadStart?: () => void;
  onLoadEnd?: () => void;
}

export interface AudioPlaybackControls {
  play: () => Promise<void>;
  pause: () => void;
  stop: () => void;
  seek: (time: number) => void;
  setVolume: (volume: number) => void;
  toggleMute: () => void;
  setPlaybackRate: (rate: number) => void;
  load: (source: string | Uint8Array) => void;
  unload: () => void;
}

// ============================================================================
// Audio Playback Hook
// ============================================================================

export function useAudioPlayback(options: AudioPlaybackOptions = {}) {
  const {
    autoPlay = false,
    loop = false,
    preload = 'metadata',
    volume: initialVolume = 1,
    playbackRate: initialPlaybackRate = 1,
    onPlay,
    onPause,
    onEnded,
    onTimeUpdate,
    onVolumeChange,
    onError,
    onLoadStart,
    onLoadEnd,
  } = options;

  // State
  const [state, setState] = useState<AudioPlaybackState>({
    isPlaying: false,
    isPaused: false,
    isLoading: false,
    currentTime: 0,
    duration: 0,
    volume: initialVolume,
    isMuted: false,
    playbackRate: initialPlaybackRate,
    error: null,
    canPlay: false,
  });

  // Refs
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const sourceUrlRef = useRef<string | null>(null);

  // ============================================================================
  // Audio Setup
  // ============================================================================

  const setupAudioElement = useCallback(() => {
    if (audioRef.current) return audioRef.current;

    const audio = new Audio();
    audio.preload = preload;
    audio.loop = loop;
    audio.volume = initialVolume;
    audio.playbackRate = initialPlaybackRate;

    // Event listeners
    audio.addEventListener('loadstart', () => {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      onLoadStart?.();
    });

    audio.addEventListener('loadedmetadata', () => {
      setState(prev => ({
        ...prev,
        duration: audio.duration,
        canPlay: true,
      }));
    });

    audio.addEventListener('canplay', () => {
      setState(prev => ({ ...prev, isLoading: false, canPlay: true }));
      onLoadEnd?.();
    });

    audio.addEventListener('play', () => {
      setState(prev => ({ ...prev, isPlaying: true, isPaused: false }));
      onPlay?.();
    });

    audio.addEventListener('pause', () => {
      setState(prev => ({ ...prev, isPlaying: false, isPaused: true }));
      onPause?.();
    });

    audio.addEventListener('ended', () => {
      setState(prev => ({
        ...prev,
        isPlaying: false,
        isPaused: false,
        currentTime: 0,
      }));
      onEnded?.();
    });

    audio.addEventListener('timeupdate', () => {
      const currentTime = audio.currentTime;
      const duration = audio.duration;
      
      setState(prev => ({ ...prev, currentTime }));
      onTimeUpdate?.(currentTime, duration);
    });

    audio.addEventListener('volumechange', () => {
      setState(prev => ({
        ...prev,
        volume: audio.volume,
        isMuted: audio.muted,
      }));
      onVolumeChange?.(audio.volume, audio.muted);
    });

    audio.addEventListener('ratechange', () => {
      setState(prev => ({ ...prev, playbackRate: audio.playbackRate }));
    });

    audio.addEventListener('error', (e) => {
      const error = audio.error
        ? `Audio error: ${audio.error.message}`
        : 'Unknown audio error';
      
      setState(prev => ({
        ...prev,
        error,
        isLoading: false,
        isPlaying: false,
        canPlay: false,
      }));
      onError?.(error);
    });

    audio.addEventListener('stalled', () => {
      setState(prev => ({ ...prev, isLoading: true }));
    });

    audio.addEventListener('waiting', () => {
      setState(prev => ({ ...prev, isLoading: true }));
    });

    audio.addEventListener('playing', () => {
      setState(prev => ({ ...prev, isLoading: false }));
    });

    audioRef.current = audio;
    return audio;
  }, [
    preload,
    loop,
    initialVolume,
    initialPlaybackRate,
    onLoadStart,
    onLoadEnd,
    onPlay,
    onPause,
    onEnded,
    onTimeUpdate,
    onVolumeChange,
    onError,
  ]);

  // ============================================================================
  // Playback Controls
  // ============================================================================

  const play = useCallback(async () => {
    const audio = audioRef.current;
    if (!audio || !state.canPlay) return;

    try {
      await audio.play();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Playback failed';
      setState(prev => ({ ...prev, error: errorMessage }));
      onError?.(errorMessage);
    }
  }, [state.canPlay, onError]);

  const pause = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;

    audio.pause();
  }, []);

  const stop = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;

    audio.pause();
    audio.currentTime = 0;
  }, []);

  const seek = useCallback((time: number) => {
    const audio = audioRef.current;
    if (!audio || !state.canPlay) return;

    const clampedTime = Math.max(0, Math.min(time, state.duration));
    audio.currentTime = clampedTime;
  }, [state.canPlay, state.duration]);

  const setVolume = useCallback((volume: number) => {
    const audio = audioRef.current;
    if (!audio) return;

    const clampedVolume = Math.max(0, Math.min(1, volume));
    audio.volume = clampedVolume;
  }, []);

  const toggleMute = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;

    audio.muted = !audio.muted;
  }, []);

  const setPlaybackRate = useCallback((rate: number) => {
    const audio = audioRef.current;
    if (!audio) return;

    const clampedRate = Math.max(0.25, Math.min(4, rate));
    audio.playbackRate = clampedRate;
  }, []);

  const load = useCallback((source: string | Uint8Array) => {
    const audio = setupAudioElement();

    // Clean up previous source
    if (sourceUrlRef.current) {
      URL.revokeObjectURL(sourceUrlRef.current);
      sourceUrlRef.current = null;
    }

    setState(prev => ({
      ...prev,
      isPlaying: false,
      isPaused: false,
      currentTime: 0,
      duration: 0,
      error: null,
      canPlay: false,
    }));

    try {
      let audioSrc: string;

      if (typeof source === 'string') {
        audioSrc = source;
      } else {
        // Create blob URL from Uint8Array
        const audioBlob = new Blob([source], { type: 'audio/mpeg' });
        audioSrc = URL.createObjectURL(audioBlob);
        sourceUrlRef.current = audioSrc;
      }

      audio.src = audioSrc;
      audio.load();

      // Auto play if requested
      if (autoPlay) {
        audio.addEventListener('canplay', () => {
          play();
        }, { once: true });
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load audio';
      setState(prev => ({ ...prev, error: errorMessage }));
      onError?.(errorMessage);
    }
  }, [setupAudioElement, autoPlay, play, onError]);

  const unload = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;

    audio.pause();
    audio.src = '';
    audio.load();

    // Clean up blob URL
    if (sourceUrlRef.current) {
      URL.revokeObjectURL(sourceUrlRef.current);
      sourceUrlRef.current = null;
    }

    setState(prev => ({
      ...prev,
      isPlaying: false,
      isPaused: false,
      currentTime: 0,
      duration: 0,
      error: null,
      canPlay: false,
    }));
  }, []);

  // ============================================================================
  // Cleanup
  // ============================================================================

  const cleanup = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = '';
      audioRef.current = null;
    }

    if (sourceUrlRef.current) {
      URL.revokeObjectURL(sourceUrlRef.current);
      sourceUrlRef.current = null;
    }
  }, []);

  // ============================================================================
  // Effects
  // ============================================================================

  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  // ============================================================================
  // Return Hook Interface
  // ============================================================================

  const controls: AudioPlaybackControls = {
    play,
    pause,
    stop,
    seek,
    setVolume,
    toggleMute,
    setPlaybackRate,
    load,
    unload,
  };

  return {
    state,
    controls,
    // Convenience getters
    isPlaying: state.isPlaying,
    isPaused: state.isPaused,
    isLoading: state.isLoading,
    currentTime: state.currentTime,
    duration: state.duration,
    volume: state.volume,
    isMuted: state.isMuted,
    playbackRate: state.playbackRate,
    error: state.error,
    canPlay: state.canPlay,
  };
}

export default useAudioPlayback;
