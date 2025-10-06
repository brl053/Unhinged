import { RecordingState } from './types';
import { VOICE_RECORDER_MESSAGES } from './constants';

export const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const getStatusMessage = (
  recordingState: RecordingState,
  disabled: boolean,
  error?: string | null
): string => {
  if (disabled) {
    return VOICE_RECORDER_MESSAGES.DISABLED;
  }
  
  if (error) {
    if (error.includes('permission')) {
      return VOICE_RECORDER_MESSAGES.PERMISSION_DENIED;
    }
    if (error.includes('microphone') || error.includes('audio')) {
      return VOICE_RECORDER_MESSAGES.NO_MICROPHONE;
    }
    return error;
  }
  
  switch (recordingState) {
    case 'idle':
      return VOICE_RECORDER_MESSAGES.IDLE;
    case 'recording':
      return VOICE_RECORDER_MESSAGES.RECORDING;
    case 'processing':
      return VOICE_RECORDER_MESSAGES.PROCESSING;
    case 'error':
      return VOICE_RECORDER_MESSAGES.ERROR;
    default:
      return VOICE_RECORDER_MESSAGES.IDLE;
  }
};

export const getRecordButtonIcon = (recordingState: RecordingState): string => {
  switch (recordingState) {
    case 'recording':
      return '⏹️'; // Stop icon
    case 'processing':
      return '⏳'; // Processing icon
    case 'error':
      return '❌'; // Error icon
    default:
      return '🎤'; // Microphone icon
  }
};

export const calculateAudioLevel = (audioData: Uint8Array): number => {
  if (!audioData || audioData.length === 0) {
    return 0;
  }
  
  let sum = 0;
  for (let i = 0; i < audioData.length; i++) {
    sum += audioData[i];
  }
  
  const average = sum / audioData.length;
  return Math.min(100, (average / 128) * 100);
};

export const createVoiceEvent = (
  type: string,
  data: any
): { type: string; source: string; data: any } => {
  return {
    type,
    source: 'voice-recorder',
    data: {
      timestamp: new Date().toISOString(),
      ...data,
    },
  };
};
