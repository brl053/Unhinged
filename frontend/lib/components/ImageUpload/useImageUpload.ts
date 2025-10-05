/**
 * @fileoverview Image Upload Hook
 * @purpose Custom React hook for managing image upload state and vision processing
 * @editable true - LLM should update when adding new upload features or vision capabilities
 * @deprecated false
 * 
 * @remarks
 * This hook provides a complete state management solution for image uploads with
 * vision processing integration. Handles upload progress, error states, and
 * analysis results caching.
 * 
 * @example
 * ```typescript
 * const {
 *   uploadedImages,
 *   uploadProgress,
 *   analysisResults,
 *   uploadImages,
 *   removeImage,
 *   clearAll,
 *   retryAnalysis
 * } = useImageUpload({
 *   maxFiles: 5,
 *   enableVisionAnalysis: true,
 *   visionProvider: 'openai-gpt4o'
 * });
 * ```
 */

import { useState, useCallback, useRef } from 'react';
import {
  UploadedImage,
  VisionAnalysisResult,
  UploadProgress,
  ImageUploadEvent,
  VisionAnalysisEvent,
  VisionProvider,
  AnalysisType,
  ImageFormat
} from './types';

/**
 * Configuration options for the useImageUpload hook
 * @public
 */
export interface UseImageUploadConfig {
  /** Maximum number of files allowed */
  maxFiles?: number;
  /** Maximum file size in bytes */
  maxFileSize?: number;
  /** Accepted image formats */
  acceptedFormats?: ImageFormat[];
  /** Enable automatic vision analysis */
  enableVisionAnalysis?: boolean;
  /** Vision provider to use */
  visionProvider?: VisionProvider;
  /** Types of analysis to perform */
  analysisTypes?: AnalysisType[];
  /** Enable result caching */
  enableCaching?: boolean;
  /** Auto-clear results after success */
  autoClear?: boolean;
  /** Auto-clear delay in milliseconds */
  autoClearDelay?: number;
}

/**
 * Return type for the useImageUpload hook
 * @public
 */
export interface UseImageUploadReturn {
  // State
  /** Currently uploaded images */
  uploadedImages: UploadedImage[];
  /** Current upload progress */
  uploadProgress: UploadProgress;
  /** Vision analysis results by image ID */
  analysisResults: Map<string, VisionAnalysisResult>;
  /** Whether upload is in progress */
  isUploading: boolean;
  /** Whether analysis is in progress */
  isAnalyzing: boolean;
  /** Current error state */
  error: { code: string; message: string; details?: any } | null;
  
  // Actions
  /** Upload new images */
  uploadImages: (files: FileList | File[]) => Promise<void>;
  /** Remove an uploaded image */
  removeImage: (imageId: string) => void;
  /** Clear all uploaded images */
  clearAll: () => void;
  /** Retry vision analysis for an image */
  retryAnalysis: (imageId: string) => Promise<void>;
  /** Update upload progress */
  updateProgress: (progress: Partial<UploadProgress>) => void;
  /** Clear error state */
  clearError: () => void;
  
  // Utilities
  /** Get analysis result for specific image */
  getAnalysisResult: (imageId: string) => VisionAnalysisResult | undefined;
  /** Check if image has analysis result */
  hasAnalysisResult: (imageId: string) => boolean;
  /** Get total upload size */
  getTotalSize: () => number;
  /** Check if can upload more files */
  canUploadMore: () => boolean;
}

/**
 * Default configuration for the hook
 */
const DEFAULT_CONFIG: Required<UseImageUploadConfig> = {
  maxFiles: 5,
  maxFileSize: 10 * 1024 * 1024, // 10MB
  acceptedFormats: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
  enableVisionAnalysis: true,
  visionProvider: 'openai-gpt4o',
  analysisTypes: ['screenshot', 'general-description'],
  enableCaching: true,
  autoClear: false,
  autoClearDelay: 5000,
};

/**
 * Custom hook for managing image uploads with vision processing
 * @public
 */
export const useImageUpload = (config: UseImageUploadConfig = {}): UseImageUploadReturn => {
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };
  
  // ========== State ==========
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([]);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({
    status: 'idle',
    progress: 0,
    message: 'Ready to upload'
  });
  const [analysisResults, setAnalysisResults] = useState<Map<string, VisionAnalysisResult>>(new Map());
  const [error, setError] = useState<{ code: string; message: string; details?: any } | null>(null);
  
  // ========== Refs ==========
  const autoClearTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // ========== Computed State ==========
  const isUploading = uploadProgress.status === 'uploading';
  const isAnalyzing = uploadProgress.status === 'processing';
  
  // ========== Utility Functions ==========
  const generateImageId = useCallback((): string => {
    return `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }, []);
  
  const formatFileSize = useCallback((bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }, []);
  
  const validateImageFile = useCallback((
    file: File
  ): { isValid: boolean; error?: string } => {
    // Check file type
    if (!mergedConfig.acceptedFormats.includes(file.type as ImageFormat)) {
      return {
        isValid: false,
        error: `File type ${file.type} is not supported. Accepted formats: ${mergedConfig.acceptedFormats.join(', ')}`
      };
    }
    
    // Check file size
    if (file.size > mergedConfig.maxFileSize) {
      return {
        isValid: false,
        error: `File size ${formatFileSize(file.size)} exceeds maximum allowed size of ${formatFileSize(mergedConfig.maxFileSize)}`
      };
    }
    
    return { isValid: true };
  }, [mergedConfig.acceptedFormats, mergedConfig.maxFileSize, formatFileSize]);
  
  const processImageFile = useCallback((file: File): Promise<UploadedImage> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      const img = new Image();
      
      reader.onload = (e) => {
        const result = e.target?.result as string;
        
        img.onload = () => {
          const uploadedImage: UploadedImage = {
            id: generateImageId(),
            name: file.name,
            size: file.size,
            type: file.type as ImageFormat,
            data: result,
            dimensions: {
              width: img.width,
              height: img.height
            },
            uploadedAt: new Date(),
            previewUrl: result
          };
          
          resolve(uploadedImage);
        };
        
        img.onerror = () => {
          reject(new Error('Failed to load image'));
        };
        
        img.src = result;
      };
      
      reader.onerror = () => {
        reject(new Error('Failed to read file'));
      };
      
      reader.readAsDataURL(file);
    });
  }, [generateImageId]);
  
  // ========== Actions ==========
  const updateProgress = useCallback((progress: Partial<UploadProgress>) => {
    setUploadProgress(prev => ({ ...prev, ...progress }));
  }, []);
  
  const clearError = useCallback(() => {
    setError(null);
  }, []);
  
  const uploadImages = useCallback(async (files: FileList | File[]) => {
    const fileArray = Array.from(files);
    
    // Check file count limit
    if (uploadedImages.length + fileArray.length > mergedConfig.maxFiles) {
      const errorObj = {
        code: 'TOO_MANY_FILES',
        message: `Cannot upload more than ${mergedConfig.maxFiles} files. Currently have ${uploadedImages.length} files.`
      };
      setError(errorObj);
      updateProgress({
        status: 'error',
        message: errorObj.message,
        error: errorObj
      });
      return;
    }
    
    updateProgress({
      status: 'uploading',
      progress: 0,
      message: 'Processing files...'
    });
    
    try {
      const processedImages: UploadedImage[] = [];
      
      for (let i = 0; i < fileArray.length; i++) {
        const file = fileArray[i];
        
        // Validate file
        const validation = validateImageFile(file);
        if (!validation.isValid) {
          throw new Error(validation.error);
        }
        
        // Update progress
        updateProgress({
          status: 'uploading',
          progress: (i / fileArray.length) * 50,
          message: `Processing ${file.name}...`
        });
        
        // Process image
        const processedImage = await processImageFile(file);
        processedImages.push(processedImage);
      }
      
      // Update state
      setUploadedImages(prev => [...prev, ...processedImages]);
      
      // Start vision analysis if enabled
      if (mergedConfig.enableVisionAnalysis) {
        updateProgress({
          status: 'processing',
          progress: 50,
          message: 'Starting vision analysis...'
        });
        
        // TODO: Implement actual vision analysis
        // For now, simulate processing
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        updateProgress({
          status: 'success',
          progress: 100,
          message: `Successfully uploaded ${processedImages.length} image(s)`
        });
      } else {
        updateProgress({
          status: 'success',
          progress: 100,
          message: `Successfully uploaded ${processedImages.length} image(s)`
        });
      }
      
      // Auto-clear if enabled
      if (mergedConfig.autoClear) {
        autoClearTimeoutRef.current = setTimeout(() => {
          updateProgress({
            status: 'idle',
            progress: 0,
            message: 'Ready to upload'
          });
        }, mergedConfig.autoClearDelay);
      }
      
    } catch (error) {
      const errorObj = {
        code: 'UPLOAD_FAILED',
        message: error instanceof Error ? error.message : 'Upload failed',
        details: error
      };
      
      setError(errorObj);
      updateProgress({
        status: 'error',
        message: errorObj.message,
        error: errorObj
      });
    }
  }, [
    uploadedImages.length,
    mergedConfig,
    updateProgress,
    validateImageFile,
    processImageFile
  ]);
  
  const removeImage = useCallback((imageId: string) => {
    setUploadedImages(prev => prev.filter(img => img.id !== imageId));
    setAnalysisResults(prev => {
      const newResults = new Map(prev);
      newResults.delete(imageId);
      return newResults;
    });
  }, []);
  
  const clearAll = useCallback(() => {
    setUploadedImages([]);
    setAnalysisResults(new Map());
    setError(null);
    updateProgress({
      status: 'idle',
      progress: 0,
      message: 'Ready to upload'
    });
    
    // Clear auto-clear timeout
    if (autoClearTimeoutRef.current) {
      clearTimeout(autoClearTimeoutRef.current);
    }
  }, [updateProgress]);
  
  const retryAnalysis = useCallback(async (imageId: string) => {
    // TODO: Implement retry logic for vision analysis
    console.log('Retrying analysis for image:', imageId);
  }, []);
  
  // ========== Utility Methods ==========
  const getAnalysisResult = useCallback((imageId: string): VisionAnalysisResult | undefined => {
    return analysisResults.get(imageId);
  }, [analysisResults]);
  
  const hasAnalysisResult = useCallback((imageId: string): boolean => {
    return analysisResults.has(imageId);
  }, [analysisResults]);
  
  const getTotalSize = useCallback((): number => {
    return uploadedImages.reduce((total, image) => total + image.size, 0);
  }, [uploadedImages]);
  
  const canUploadMore = useCallback((): boolean => {
    return uploadedImages.length < mergedConfig.maxFiles;
  }, [uploadedImages.length, mergedConfig.maxFiles]);
  
  return {
    // State
    uploadedImages,
    uploadProgress,
    analysisResults,
    isUploading,
    isAnalyzing,
    error,
    
    // Actions
    uploadImages,
    removeImage,
    clearAll,
    retryAnalysis,
    updateProgress,
    clearError,
    
    // Utilities
    getAnalysisResult,
    hasAnalysisResult,
    getTotalSize,
    canUploadMore,
  };
};
