/**
 * @fileoverview Image Upload Component Exports
 * @purpose Public API exports for the image upload component with vision processing
 * @editable true - LLM should update exports when adding new features
 * @deprecated false
 */

export { default as ImageUpload } from './ImageUpload';
export { useImageUpload } from './useImageUpload';

export type {
  ImageUploadProps,
  UploadedImage,
  VisionAnalysisResult,
  UploadProgress,
  ImageUploadEvent,
  VisionAnalysisEvent,
  ImageFormat,
  UploadStatus,
  UploadSize,
  VisionProvider,
  AnalysisType,
  UIElement,
  CodeSnippet,
  AccessibilityIssue
} from './types';

export { DEFAULT_UPLOAD_CONFIG } from './types';
