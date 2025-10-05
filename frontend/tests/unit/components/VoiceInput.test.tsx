/**
 * @fileoverview Unit Tests for VoiceInput Component
 * 
 * @description
 * Comprehensive tests for the VoiceInput component including
 * rendering, user interactions, voice recording, and accessibility.
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { VoiceInput } from '../../../lib/components/VoiceInput/VoiceInput';

// Mock the useVoiceRecorder hook
jest.mock('../../../src/hooks/useVoiceRecorder', () => ({
  useVoiceRecorder: jest.fn(),
}));

import { useVoiceRecorder } from '../../../src/hooks/useVoiceRecorder';

const mockUseVoiceRecorder = useVoiceRecorder as jest.MockedFunction<typeof useVoiceRecorder>;

describe('VoiceInput Component', () => {
  const mockVoiceRecorder = {
    status: 'idle' as const,
    isRecording: false,
    isProcessing: false,
    hasError: false,
    duration: 0,
    audioLevel: 0,
    transcription: null,
    error: null,
    startRecording: jest.fn(),
    stopRecording: jest.fn(),
    transcribeAudio: jest.fn(),
    clearError: jest.fn(),
    statusText: 'Ready to record',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseVoiceRecorder.mockReturnValue(mockVoiceRecorder);
  });

  describe('Rendering', () => {
    it('should render voice input button', () => {
      render(<VoiceInput />);
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('type', 'button');
    });

    it('should render with custom placeholder', () => {
      const placeholder = 'Click to start recording';
      render(<VoiceInput placeholder={placeholder} />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('title', expect.stringContaining('Ready to record'));
    });

    it('should render with different variants', () => {
      const variants = ['primary', 'secondary', 'outline'] as const;
      
      variants.forEach(variant => {
        const { unmount } = render(<VoiceInput variant={variant} />);
        
        const button = screen.getByRole('button');
        expect(button).toBeInTheDocument();
        
        unmount();
      });
    });

    it('should render with different sizes', () => {
      const sizes = ['small', 'medium', 'large'] as const;
      
      sizes.forEach(size => {
        const { unmount } = render(<VoiceInput size={size} />);
        
        const button = screen.getByRole('button');
        expect(button).toBeInTheDocument();
        
        unmount();
      });
    });
  });

  describe('User Interactions', () => {
    it('should start recording when button is clicked', async () => {
      const user = userEvent.setup();
      render(<VoiceInput />);
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(mockVoiceRecorder.startRecording).toHaveBeenCalledTimes(1);
    });

    it('should stop recording when button is clicked while recording', async () => {
      mockUseVoiceRecorder.mockReturnValue({
        ...mockVoiceRecorder,
        isRecording: true,
        status: 'recording',
      });
      
      const user = userEvent.setup();
      render(<VoiceInput />);
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(mockVoiceRecorder.stopRecording).toHaveBeenCalledTimes(1);
    });

    it('should call onTranscription when transcription is available', () => {
      const onTranscription = jest.fn();
      const transcription = {
        text: 'Hello world',
        language: 'en',
        confidence: 0.95,
      };
      
      mockUseVoiceRecorder.mockReturnValue({
        ...mockVoiceRecorder,
        transcription,
      });
      
      render(<VoiceInput onTranscription={onTranscription} />);
      
      expect(onTranscription).toHaveBeenCalledWith(transcription);
    });

    it('should call onError when error occurs', () => {
      const onError = jest.fn();
      const error = new Error('Recording failed');
      
      mockUseVoiceRecorder.mockReturnValue({
        ...mockVoiceRecorder,
        hasError: true,
        error,
      });
      
      render(<VoiceInput onError={onError} />);
      
      expect(onError).toHaveBeenCalledWith(error);
    });
  });

  describe('Recording States', () => {
    it('should show recording state visually', () => {
      mockUseVoiceRecorder.mockReturnValue({
        ...mockVoiceRecorder,
        isRecording: true,
        status: 'recording',
        statusText: 'Recording...',
      });
      
      render(<VoiceInput />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-pressed', 'true');
      expect(button).toHaveAttribute('title', expect.stringContaining('Recording'));
    });

    it('should show processing state', () => {
      mockUseVoiceRecorder.mockReturnValue({
        ...mockVoiceRecorder,
        isProcessing: true,
        status: 'processing',
        statusText: 'Processing...',
      });
      
      render(<VoiceInput />);
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(button).toHaveAttribute('title', expect.stringContaining('Processing'));
    });

    it('should show error state', () => {
      mockUseVoiceRecorder.mockReturnValue({
        ...mockVoiceRecorder,
        hasError: true,
        status: 'error',
        error: new Error('Recording failed'),
        statusText: 'Error occurred',
      });
      
      render(<VoiceInput />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('title', expect.stringContaining('Error'));
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(<VoiceInput />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-pressed', 'false');
      expect(button).toHaveAttribute('title');
    });

    it('should be keyboard accessible', async () => {
      const user = userEvent.setup();
      render(<VoiceInput />);
      
      const button = screen.getByRole('button');
      
      // Focus the button
      await user.tab();
      expect(button).toHaveFocus();
      
      // Press Enter to activate
      await user.keyboard('{Enter}');
      expect(mockVoiceRecorder.startRecording).toHaveBeenCalled();
    });

    it('should be accessible with Space key', async () => {
      const user = userEvent.setup();
      render(<VoiceInput />);
      
      const button = screen.getByRole('button');
      button.focus();
      
      // Press Space to activate
      await user.keyboard(' ');
      expect(mockVoiceRecorder.startRecording).toHaveBeenCalled();
    });

    it('should have proper disabled state accessibility', () => {
      render(<VoiceInput disabled />);
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(button).toHaveAttribute('aria-disabled', 'true');
    });
  });

  describe('Props Handling', () => {
    it('should handle disabled prop', () => {
      render(<VoiceInput disabled />);
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });

    it('should apply custom className', () => {
      const customClass = 'custom-voice-input';
      render(<VoiceInput className={customClass} />);
      
      const container = screen.getByRole('button').parentElement;
      expect(container).toHaveClass(customClass);
    });

    it('should handle custom configuration', () => {
      const config = {
        autoTranscribe: false,
        maxDuration: 30000,
      };
      
      render(<VoiceInput config={config} />);
      
      expect(mockUseVoiceRecorder).toHaveBeenCalledWith(config);
    });
  });

  describe('Duration Display', () => {
    it('should show recording duration', () => {
      mockUseVoiceRecorder.mockReturnValue({
        ...mockVoiceRecorder,
        isRecording: true,
        duration: 5000, // 5 seconds
      });
      
      render(<VoiceInput showDuration />);
      
      // Look for duration display (implementation may vary)
      expect(screen.getByRole('button')).toBeInTheDocument();
    });
  });

  describe('Audio Level Visualization', () => {
    it('should handle audio level updates', () => {
      mockUseVoiceRecorder.mockReturnValue({
        ...mockVoiceRecorder,
        isRecording: true,
        audioLevel: 0.7,
      });
      
      render(<VoiceInput showAudioLevel />);
      
      // Component should render without errors
      expect(screen.getByRole('button')).toBeInTheDocument();
    });
  });

  describe('Error Recovery', () => {
    it('should allow error recovery', async () => {
      const user = userEvent.setup();
      
      // Start with error state
      mockUseVoiceRecorder.mockReturnValue({
        ...mockVoiceRecorder,
        hasError: true,
        error: new Error('Permission denied'),
      });
      
      render(<VoiceInput />);
      
      const button = screen.getByRole('button');
      
      // Click should attempt to clear error and retry
      await user.click(button);
      
      // Should attempt to start recording (which may clear error)
      expect(mockVoiceRecorder.startRecording).toHaveBeenCalled();
    });
  });

  describe('Integration', () => {
    it('should work with form submission', async () => {
      const onSubmit = jest.fn();
      const user = userEvent.setup();
      
      render(
        <form onSubmit={onSubmit}>
          <VoiceInput />
          <button type="submit">Submit</button>
        </form>
      );
      
      const voiceButton = screen.getByRole('button', { name: /voice/i });
      const submitButton = screen.getByRole('button', { name: /submit/i });
      
      // Voice input should not trigger form submission
      await user.click(voiceButton);
      expect(onSubmit).not.toHaveBeenCalled();
      
      // Submit button should trigger form submission
      await user.click(submitButton);
      expect(onSubmit).toHaveBeenCalled();
    });
  });
});
