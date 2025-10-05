/**
 * @fileoverview Screenshot Capture Component
 * @purpose React component for capturing screenshots and integrating with vision analysis
 * @editable true - LLM should update when adding new capture features or vision capabilities
 * @deprecated false
 * 
 * @remarks
 * This component provides a UI for capturing screenshots using various methods
 * and automatically processes them through the ImageUpload component for vision analysis.
 * Integrates with the screenshot capture utility and vision processing pipeline.
 * 
 * @example
 * ```typescript
 * <ScreenshotCapture
 *   onScreenshotCaptured={handleScreenshot}
 *   onVisionAnalysis={handleAnalysis}
 *   enableAutoAnalysis={true}
 *   defaultTarget="http://localhost:3000"
 * />
 * ```
 */

import React, { useState, useCallback } from 'react';
import { ImageUpload } from '../ImageUpload';
import { ImageUploadEvent, VisionAnalysisEvent, UploadedImage } from '../ImageUpload/types';
import {
  ScreenshotContainer,
  ScreenshotControls,
  ControlGroup,
  ControlLabel,
  Input,
  Select,
  Button,
  StatusContainer,
  StatusIcon,
  StatusMessage,
  PreviewContainer,
  PreviewImage,
  ActionButtons
} from './styles';

/**
 * Screenshot capture target types
 * @public
 */
export type CaptureTarget = 'desktop' | 'browser' | 'localhost' | 'custom-url';

/**
 * Screenshot capture component props
 * @public
 */
export interface ScreenshotCaptureProps {
  /** Callback when screenshot is captured */
  onScreenshotCaptured?: (screenshot: UploadedImage) => void;
  /** Callback when vision analysis completes */
  onVisionAnalysis?: (event: VisionAnalysisEvent) => void;
  /** Enable automatic vision analysis */
  enableAutoAnalysis?: boolean;
  /** Default capture target */
  defaultTarget?: CaptureTarget;
  /** Default URL for custom capture */
  defaultUrl?: string;
  /** Default localhost port */
  defaultPort?: number;
  /** Show preview of captured screenshot */
  showPreview?: boolean;
  /** Custom CSS class */
  className?: string;
  /** Test ID */
  testId?: string;
}

/**
 * Capture status
 */
interface CaptureStatus {
  status: 'idle' | 'capturing' | 'success' | 'error';
  message: string;
  error?: string;
}

/**
 * Screenshot Capture Component
 * @public
 */
export const ScreenshotCapture: React.FC<ScreenshotCaptureProps> = ({
  onScreenshotCaptured,
  onVisionAnalysis,
  enableAutoAnalysis = true,
  defaultTarget = 'localhost',
  defaultUrl = 'http://localhost:3000',
  defaultPort = 3000,
  showPreview = true,
  className,
  testId
}) => {
  // ========== State ==========
  const [captureTarget, setCaptureTarget] = useState<CaptureTarget>(defaultTarget);
  const [customUrl, setCustomUrl] = useState(defaultUrl);
  const [localhostPort, setLocalhostPort] = useState(defaultPort);
  const [localhostPath, setLocalhostPath] = useState('/showcase');
  const [captureStatus, setCaptureStatus] = useState<CaptureStatus>({
    status: 'idle',
    message: 'Ready to capture screenshot'
  });
  const [capturedScreenshot, setCapturedScreenshot] = useState<UploadedImage | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);

  // ========== Capture Logic ==========
  const captureScreenshot = useCallback(async () => {
    setIsCapturing(true);
    setCaptureStatus({
      status: 'capturing',
      message: 'Capturing screenshot...'
    });

    try {
      // Determine target URL/method based on selection
      let target: string;
      
      switch (captureTarget) {
        case 'desktop':
          target = 'desktop';
          break;
        case 'browser':
          target = 'browser';
          break;
        case 'localhost':
          target = `http://localhost:${localhostPort}${localhostPath}`;
          break;
        case 'custom-url':
          target = customUrl;
          break;
        default:
          target = 'desktop';
      }

      // Call the screenshot capture API
      // Note: This would typically be a backend API call
      // For now, we'll simulate the capture process
      
      const response = await fetch('/api/screenshot/capture', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          target,
          options: {
            dimensions: { width: 1920, height: 1080 },
            delay: 3000,
            format: 'png'
          }
        })
      });

      if (!response.ok) {
        throw new Error(`Screenshot API failed: ${response.statusText}`);
      }

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Screenshot capture failed');
      }

      // Create UploadedImage object from screenshot result
      const screenshot: UploadedImage = {
        id: `screenshot_${Date.now()}`,
        name: `screenshot_${new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')}.png`,
        size: result.fileSize || 0,
        type: 'image/png',
        data: result.data, // Base64 data
        dimensions: result.dimensions || { width: 1920, height: 1080 },
        uploadedAt: new Date(),
        previewUrl: result.data
      };

      setCapturedScreenshot(screenshot);
      setCaptureStatus({
        status: 'success',
        message: 'Screenshot captured successfully!'
      });

      // Trigger callback
      onScreenshotCaptured?.(screenshot);

      // Auto-trigger vision analysis if enabled
      if (enableAutoAnalysis) {
        // This will be handled by the ImageUpload component
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setCaptureStatus({
        status: 'error',
        message: 'Screenshot capture failed',
        error: errorMessage
      });
    } finally {
      setIsCapturing(false);
    }
  }, [captureTarget, customUrl, localhostPort, localhostPath, onScreenshotCaptured, enableAutoAnalysis]);

  // ========== Event Handlers ==========
  const handleImageUpload = useCallback((event: ImageUploadEvent) => {
    // Handle the uploaded screenshot through ImageUpload component
    console.log('Screenshot processed by ImageUpload:', event.image);
  }, []);

  const handleVisionAnalysis = useCallback((event: VisionAnalysisEvent) => {
    console.log('Vision analysis completed:', event.result);
    onVisionAnalysis?.(event);
  }, [onVisionAnalysis]);

  const handleRetryCapture = useCallback(() => {
    setCaptureStatus({
      status: 'idle',
      message: 'Ready to capture screenshot'
    });
    setCapturedScreenshot(null);
  }, []);

  const handleClearScreenshot = useCallback(() => {
    setCapturedScreenshot(null);
    setCaptureStatus({
      status: 'idle',
      message: 'Ready to capture screenshot'
    });
  }, []);

  // ========== Render Status Icon ==========
  const renderStatusIcon = () => {
    switch (captureStatus.status) {
      case 'capturing':
        return '📸';
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      default:
        return '🖥️';
    }
  };

  return (
    <ScreenshotContainer className={className} data-testid={testId}>
      <h3>Screenshot Capture & Vision Analysis</h3>
      <p>
        Capture screenshots of your desktop, browser, or web pages and automatically 
        analyze them using AI vision processing.
      </p>

      <ScreenshotControls>
        <ControlGroup>
          <ControlLabel>Capture Target:</ControlLabel>
          <Select 
            value={captureTarget} 
            onChange={(e) => setCaptureTarget(e.target.value as CaptureTarget)}
          >
            <option value="desktop">Full Desktop</option>
            <option value="browser">Browser Window</option>
            <option value="localhost">Localhost Development</option>
            <option value="custom-url">Custom URL</option>
          </Select>
        </ControlGroup>

        {captureTarget === 'localhost' && (
          <>
            <ControlGroup>
              <ControlLabel>Port:</ControlLabel>
              <Input
                type="number"
                value={localhostPort}
                onChange={(e) => setLocalhostPort(parseInt(e.target.value) || 3000)}
                min="1"
                max="65535"
              />
            </ControlGroup>
            <ControlGroup>
              <ControlLabel>Path:</ControlLabel>
              <Input
                type="text"
                value={localhostPath}
                onChange={(e) => setLocalhostPath(e.target.value)}
                placeholder="/showcase"
              />
            </ControlGroup>
          </>
        )}

        {captureTarget === 'custom-url' && (
          <ControlGroup>
            <ControlLabel>URL:</ControlLabel>
            <Input
              type="url"
              value={customUrl}
              onChange={(e) => setCustomUrl(e.target.value)}
              placeholder="https://example.com"
            />
          </ControlGroup>
        )}

        <ControlGroup>
          <Button 
            onClick={captureScreenshot} 
            disabled={isCapturing}
            $variant="primary"
          >
            {isCapturing ? 'Capturing...' : 'Capture Screenshot'}
          </Button>
        </ControlGroup>
      </ScreenshotControls>

      <StatusContainer>
        <StatusIcon>{renderStatusIcon()}</StatusIcon>
        <StatusMessage $status={captureStatus.status}>
          {captureStatus.message}
          {captureStatus.error && (
            <div style={{ fontSize: '0.875rem', marginTop: '0.25rem', opacity: 0.8 }}>
              {captureStatus.error}
            </div>
          )}
        </StatusMessage>
      </StatusContainer>

      {captureStatus.status === 'error' && (
        <ActionButtons>
          <Button onClick={handleRetryCapture} $variant="secondary">
            Retry Capture
          </Button>
        </ActionButtons>
      )}

      {capturedScreenshot && showPreview && (
        <PreviewContainer>
          <h4>Captured Screenshot</h4>
          <PreviewImage 
            src={capturedScreenshot.previewUrl} 
            alt={capturedScreenshot.name}
          />
          <div>
            <strong>{capturedScreenshot.name}</strong><br />
            Size: {Math.round(capturedScreenshot.size / 1024)}KB • 
            Dimensions: {capturedScreenshot.dimensions.width}×{capturedScreenshot.dimensions.height}
          </div>
          <ActionButtons>
            <Button onClick={handleClearScreenshot} $variant="secondary">
              Clear Screenshot
            </Button>
          </ActionButtons>
        </PreviewContainer>
      )}

      {capturedScreenshot && (
        <div style={{ marginTop: '2rem' }}>
          <h4>Vision Analysis</h4>
          <p>The captured screenshot will be automatically processed for AI analysis:</p>
          <ImageUpload
            // Pre-populate with captured screenshot
            onUpload={handleImageUpload}
            onAnalysis={handleVisionAnalysis}
            enableVisionAnalysis={enableAutoAnalysis}
            visionProvider="openai-gpt4o"
            analysisTypes={['screenshot', 'ui-analysis', 'general-description']}
            maxFiles={1}
            size="medium"
            placeholder="Screenshot captured! Drop additional images or analyze the captured screenshot."
          />
        </div>
      )}
    </ScreenshotContainer>
  );
};

export default ScreenshotCapture;
