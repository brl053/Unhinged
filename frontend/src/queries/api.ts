import { useMutation } from '@tanstack/react-query';
import { TranscriptionResult, VoiceInputErrorDetails, SynthesisRequest, SynthesisResult } from '../utils/audio/types';
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

/**
 * Hook for synthesizing text to speech using the Whisper TTS service
 *
 * Sends text to the Whisper service and returns synthesized audio.
 * Handles errors gracefully and provides proper TypeScript types.
 *
 * @example
 * ```tsx
 * const synthesizeMutation = useSynthesizeAudio();
 *
 * const handleTextToSpeech = async (text: string) => {
 *   try {
 *     const result = await synthesizeMutation.mutateAsync({ text, language: 'en' });
 *     // Play the audio blob
 *     const audio = new Audio(URL.createObjectURL(result.audioBlob));
 *     audio.play();
 *   } catch (error) {
 *     console.error('Speech synthesis failed:', error);
 *   }
 * };
 * ```
 */
export const useSynthesizeAudio = () => {
  return useMutation<SynthesisResult, VoiceInputErrorDetails, SynthesisRequest>({
    mutationFn: async (request: SynthesisRequest) => {
      try {
        // Send request to Whisper TTS service
        const response = await fetch(`${WHISPER_API_BASE_URL}/synthesize`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text: request.text,
            language: request.language || 'en',
          }),
        });

        if (!response.ok) {
          // Handle HTTP errors
          const errorText = await response.text();
          throw createVoiceInputError(
            VoiceInputError.SYNTHESIS_FAILED,
            `Speech synthesis service error: ${response.status} - ${errorText}`
          );
        }

        // Get the audio blob from response
        const audioBlob = await response.blob();

        // Validate response
        if (!audioBlob || audioBlob.size === 0) {
          throw createVoiceInputError(
            VoiceInputError.SYNTHESIS_FAILED,
            'Invalid response from speech synthesis service'
          );
        }

        return {
          audioBlob,
          language: request.language || 'en',
          text: request.text,
          duration: undefined, // Duration not provided by gTTS
        } as SynthesisResult;

      } catch (error) {
        // Handle network errors
        if (error instanceof TypeError && error.message.includes('fetch')) {
          throw createVoiceInputError(
            VoiceInputError.NETWORK_ERROR,
            'Could not connect to speech synthesis service'
          );
        }

        // Re-throw VoiceInputErrorDetails as-is
        if (error && typeof error === 'object' && 'type' in error) {
          throw error;
        }

        // Handle unexpected errors
        throw createVoiceInputError(
          VoiceInputError.SYNTHESIS_FAILED,
          error instanceof Error ? error.message : 'Unknown speech synthesis error'
        );
      }
    },
  });
};
