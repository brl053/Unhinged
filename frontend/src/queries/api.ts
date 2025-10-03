import { useMutation } from '@tanstack/react-query';
import { TranscriptionResult, VoiceInputErrorDetails } from '../utils/audio/types';
import { createVoiceInputError, VoiceInputError } from '../utils/audio/audioUtils';

const API_BASE_URL = "http://localhost:8080";
const WHISPER_API_BASE_URL = "http://localhost:8000";

// Define response type for clarity
interface ResponseData {
  response: string;
}

export const useSendMessage = () => {
  return useMutation<string, Error, string>({
    mutationFn: async (message: string) => {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: message }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      console.log('response', response);
      return await response.text(); // This will return ResponseData
    }
  });
};

/**
 * Hook for transcribing audio using the Whisper TTS service
 *
 * Uploads audio file to the Whisper service and returns transcribed text.
 * Handles errors gracefully and provides proper TypeScript types.
 *
 * @example
 * ```tsx
 * const transcribeMutation = useTranscribeAudio();
 *
 * const handleAudioFile = async (file: File) => {
 *   try {
 *     const result = await transcribeMutation.mutateAsync(file);
 *     console.log('Transcribed text:', result.text);
 *   } catch (error) {
 *     console.error('Transcription failed:', error);
 *   }
 * };
 * ```
 */
export const useTranscribeAudio = () => {
  return useMutation<TranscriptionResult, VoiceInputErrorDetails, File>({
    mutationFn: async (audioFile: File) => {
      try {
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('audio', audioFile);

        // Send request to Whisper service
        const response = await fetch(`${WHISPER_API_BASE_URL}/transcribe`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          // Handle HTTP errors
          const errorText = await response.text();
          throw createVoiceInputError(
            VoiceInputError.TRANSCRIPTION_FAILED,
            `Transcription service error: ${response.status} - ${errorText}`
          );
        }

        // Parse response
        const result = await response.json();

        // Validate response structure
        if (!result.text) {
          throw createVoiceInputError(
            VoiceInputError.TRANSCRIPTION_FAILED,
            'Invalid response from transcription service'
          );
        }

        return {
          text: result.text,
          language: result.language || 'unknown',
          confidence: result.confidence,
        } as TranscriptionResult;

      } catch (error) {
        // Handle network errors
        if (error instanceof TypeError && error.message.includes('fetch')) {
          throw createVoiceInputError(
            VoiceInputError.NETWORK_ERROR,
            'Could not connect to transcription service'
          );
        }

        // Re-throw VoiceInputErrorDetails as-is
        if (error && typeof error === 'object' && 'type' in error) {
          throw error;
        }

        // Handle unexpected errors
        throw createVoiceInputError(
          VoiceInputError.TRANSCRIPTION_FAILED,
          error instanceof Error ? error.message : 'Unknown transcription error'
        );
      }
    },
  });
};
