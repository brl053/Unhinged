/**
 * @fileoverview Image Upload Component Types
 * @purpose Type definitions for the drag-and-drop image upload component with vision processing
 * @editable true - LLM should update types when adding new upload features or vision capabilities
 * @deprecated false
 * 
 * @remarks
 * This component supports multiple image formats, drag-and-drop functionality, and integrates
 * with vision processing APIs. All types are designed for future extensibility with local
 * vision models and batch processing capabilities.
 * 
 * @example
 * ```typescript
 * // Basic usage
 * <ImageUpload
 *   onUpload={handleImageUpload}
 *   acceptedFormats={['image/png', 'image/jpeg']}
 *   maxFileSize={10 * 1024 * 1024} // 10MB
 * />
 * ```
 */

import { ReactNode } from 'react';

/**
 * Supported image file formats for upload
 * @public
 */
export type ImageFormat = 
  | 'image/jpeg'
  | 'image/jpg' 
  | 'image/png'
  | 'image/webp'
  | 'image/gif'
  | 'image/bmp'
  | 'image/svg+xml';

/**
 * Upload status states
 * @public
 */
export type UploadStatus = 
  | 'idle'
  | 'dragging'
  | 'uploading'
  | 'processing'
  | 'success'
  | 'error';

/**
 * Image upload size presets
 * @public
 */
export type UploadSize = 'small' | 'medium' | 'large' | 'full';

/**
 * Vision processing provider options
 * @public
 */
export type VisionProvider = 
  | 'openai-gpt4o'
  | 'claude-vision'
  | 'google-vision'
  | 'azure-vision'
  | 'local-model';

/**
 * Vision analysis types
 * @public
 */
export type AnalysisType = 
  | 'screenshot'
  | 'ui-analysis'
  | 'code-analysis'
  | 'text-extraction'
  | 'general-description'
  | 'accessibility-audit';

/**
 * Uploaded image file information
 * @public
 */
export interface UploadedImage {
  /** Unique identifier for the uploaded image */
  id: string;
  /** Original file name */
  name: string;
  /** File size in bytes */
  size: number;
  /** MIME type of the image */
  type: ImageFormat;
  /** Base64 encoded image data */
  data: string;
  /** Image dimensions */
  dimensions: {
    width: number;
    height: number;
  };
  /** Upload timestamp */
  uploadedAt: Date;
  /** Optional preview URL for display */
  previewUrl?: string;
}

/**
 * Vision analysis result
 * @public
 */
export interface VisionAnalysisResult {
  /** Unique analysis ID */
  id: string;
  /** Image that was analyzed */
  imageId: string;
  /** Type of analysis performed */
  analysisType: AnalysisType;
  /** Vision provider used */
  provider: VisionProvider;
  /** Analysis results */
  results: {
    /** Main description/interpretation */
    description: string;
    /** Extracted text (if applicable) */
    extractedText?: string[];
    /** UI elements detected (if UI analysis) */
    uiElements?: UIElement[];
    /** Code snippets detected (if code analysis) */
    codeSnippets?: CodeSnippet[];
    /** Accessibility issues (if accessibility audit) */
    accessibilityIssues?: AccessibilityIssue[];
    /** Confidence score (0-1) */
    confidence: number;
  };
  /** Processing metadata */
  metadata: {
    /** Processing time in milliseconds */
    processingTime: number;
    /** Token usage (for API providers) */
    tokenUsage?: {
      input: number;
      output: number;
      cost: number;
    };
    /** Analysis timestamp */
    analyzedAt: Date;
  };
}

/**
 * UI element detected in screenshot analysis
 * @public
 */
export interface UIElement {
  /** Element type */
  type: 'button' | 'input' | 'text' | 'image' | 'link' | 'container' | 'other';
  /** Element description */
  description: string;
  /** Bounding box coordinates (if available) */
  boundingBox?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  /** Element text content */
  text?: string;
  /** Confidence score */
  confidence: number;
}

/**
 * Code snippet detected in image
 * @public
 */
export interface CodeSnippet {
  /** Programming language detected */
  language: string;
  /** Code content */
  code: string;
  /** Line numbers (if available) */
  lineNumbers?: number[];
  /** Confidence score */
  confidence: number;
}

/**
 * Accessibility issue detected
 * @public
 */
export interface AccessibilityIssue {
  /** Issue type */
  type: 'contrast' | 'alt-text' | 'keyboard-nav' | 'aria-labels' | 'other';
  /** Issue description */
  description: string;
  /** Severity level */
  severity: 'low' | 'medium' | 'high' | 'critical';
  /** Suggested fix */
  suggestion?: string;
}

/**
 * Upload progress information
 * @public
 */
export interface UploadProgress {
  /** Current upload status */
  status: UploadStatus;
  /** Progress percentage (0-100) */
  progress: number;
  /** Current operation message */
  message: string;
  /** Error information (if status is 'error') */
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

/**
 * Image upload event data
 * @public
 */
export interface ImageUploadEvent {
  /** Uploaded image information */
  image: UploadedImage;
  /** Upload progress */
  progress: UploadProgress;
}

/**
 * Vision analysis event data
 * @public
 */
export interface VisionAnalysisEvent {
  /** Analysis result */
  result: VisionAnalysisResult;
  /** Original image */
  image: UploadedImage;
}

/**
 * Main ImageUpload component props
 * @public
 */
export interface ImageUploadProps {
  // Core functionality
  /** Callback when image is uploaded */
  onUpload?: (event: ImageUploadEvent) => void;
  /** Callback when vision analysis completes */
  onAnalysis?: (event: VisionAnalysisEvent) => void;
  /** Callback for upload progress updates */
  onProgress?: (progress: UploadProgress) => void;
  /** Callback for errors */
  onError?: (error: { code: string; message: string; details?: any }) => void;
  
  // Configuration
  /** Accepted image formats */
  acceptedFormats?: ImageFormat[];
  /** Maximum file size in bytes */
  maxFileSize?: number;
  /** Maximum number of files */
  maxFiles?: number;
  /** Component size preset */
  size?: UploadSize;
  /** Custom width */
  width?: string | number;
  /** Custom height */
  height?: string | number;
  
  // Vision processing
  /** Enable automatic vision analysis */
  enableVisionAnalysis?: boolean;
  /** Vision provider to use */
  visionProvider?: VisionProvider;
  /** Types of analysis to perform */
  analysisTypes?: AnalysisType[];
  /** Vision processing options */
  visionOptions?: {
    /** Image quality for processing ('low' | 'high') */
    quality?: 'low' | 'high';
    /** Maximum image dimensions for processing */
    maxDimensions?: { width: number; height: number };
    /** Enable result caching */
    enableCaching?: boolean;
  };
  
  // UI customization
  /** Custom upload area content */
  children?: ReactNode;
  /** Custom placeholder text */
  placeholder?: string;
  /** Show upload progress */
  showProgress?: boolean;
  /** Show analysis results */
  showAnalysisResults?: boolean;
  /** Disabled state */
  disabled?: boolean;
  /** Read-only mode */
  readOnly?: boolean;
  
  // Styling
  /** Custom CSS class */
  className?: string;
  /** Custom inline styles */
  style?: React.CSSProperties;
  /** Test ID for testing */
  testId?: string;
}

/**
 * Default configuration values
 * @public
 */
export const DEFAULT_UPLOAD_CONFIG = {
  acceptedFormats: [
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/webp'
  ] as ImageFormat[],
  maxFileSize: 10 * 1024 * 1024, // 10MB
  maxFiles: 5,
  size: 'medium' as UploadSize,
  enableVisionAnalysis: true,
  visionProvider: 'openai-gpt4o' as VisionProvider,
  analysisTypes: ['screenshot', 'general-description'] as AnalysisType[],
  visionOptions: {
    quality: 'high' as const,
    maxDimensions: { width: 1920, height: 1080 },
    enableCaching: true,
  },
  showProgress: true,
  showAnalysisResults: true,
} as const;
