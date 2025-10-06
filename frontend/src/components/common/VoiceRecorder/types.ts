import { UnhingedTheme } from '../../../design_system';

export interface VoiceRecorderProps {
  onTranscription: (text: string) => void;
  onError?: (error: string) => void;
  onEvent?: (event: { type: string; source: string; data: any }) => void;
  disabled?: boolean;
  className?: string;
}

export interface StyledVoiceRecorderProps {
  theme: UnhingedTheme;
}

export interface StyledRecordButtonProps {
  theme: UnhingedTheme;
  isRecording: boolean;
  disabled: boolean;
}

export interface StyledStatusTextProps {
  theme: UnhingedTheme;
  error?: boolean;
}

export interface StyledAudioLevelBarProps {
  theme: UnhingedTheme;
  level: number;
}

export interface StyledDurationDisplayProps {
  theme: UnhingedTheme;
}

export type RecordingState = 'idle' | 'recording' | 'processing' | 'error';

export interface VoiceRecordingHookResult {
  isRecording: boolean;
  audioLevel: number;
  duration: number;
  error: string | null;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<Blob | null>;
  recordingState: RecordingState;
}
