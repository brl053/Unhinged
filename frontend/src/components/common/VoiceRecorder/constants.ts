export const VOICE_RECORDER_CONSTANTS = {
  BUTTON_SIZE: 60,
  AUDIO_LEVEL_BAR_WIDTH: 200,
  AUDIO_LEVEL_BAR_HEIGHT: 4,
  ANIMATION_DURATION_FAST: 100,
  ANIMATION_DURATION_STANDARD: 200,
  HOVER_SCALE: 1.05,
  DISABLED_OPACITY: 0.6,
  MIN_STATUS_HEIGHT: 20,
} as const;

export const RECORDING_STATES = {
  IDLE: 'idle',
  RECORDING: 'recording', 
  PROCESSING: 'processing',
  ERROR: 'error',
} as const;

export const VOICE_RECORDER_MESSAGES = {
  IDLE: 'Click to start recording',
  RECORDING: 'Recording... Click to stop',
  PROCESSING: 'Processing audio...',
  ERROR: 'Recording failed',
  DISABLED: 'Recording disabled',
  NO_MICROPHONE: 'Microphone not available',
  PERMISSION_DENIED: 'Microphone permission denied',
} as const;
