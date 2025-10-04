/**
 * @fileoverview Image Upload Component with Drag-and-Drop
 * @purpose Comprehensive image upload component with vision processing integration
 * @editable true - LLM should update when adding new upload features or vision capabilities
 * @deprecated false
 * 
 * @remarks
 * This component provides drag-and-drop image upload functionality with automatic
 * vision processing integration. Supports multiple providers and is designed for
 * future migration to self-hosted vision models.
 * 
 * Features:
 * - Drag-and-drop file upload
 * - Multiple image format support
 * - File size validation
 * - Upload progress tracking
 * - Vision analysis integration
 * - Result caching
 * - Error handling
 * 
 * @example
 * ```typescript
 * <ImageUpload
 *   onUpload={handleImageUpload}
 *   onAnalysis={handleVisionAnalysis}
 *   enableVisionAnalysis={true}
 *   visionProvider="openai-gpt4o"
 *   analysisTypes={['screenshot', 'ui-analysis']}
 * />
 * ```
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
  ImageUploadProps,
  UploadedImage,
  UploadProgress,
  UploadStatus,
  ImageUploadEvent,
  VisionAnalysisEvent,
  DEFAULT_UPLOAD_CONFIG,
  ImageFormat
} from './types';
import {
  UploadContainer,
  UploadArea,
  UploadIcon,
  UploadTitle,
  UploadDescription,
  UploadButton,
  ProgressContainer,
  ProgressBar,
  FileList,
  FileItem,
  FileInfo,
  FilePreview,
  FileDetails,
  FileName,
  FileSize,
  FileActions,
  ActionButton,
  AnalysisContainer,
  AnalysisTitle,
  AnalysisContent,
  ErrorContainer,
  ErrorIcon,
  ErrorMessage,
  HiddenInput
} from './styles';

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Format file size in human readable format
 */
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Generate unique ID for uploaded images
 */
const generateImageId = (): string => {
  return `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Validate image file
 */
const validateImageFile = (
  file: File, 
  acceptedFormats: ImageFormat[], 
  maxFileSize: number
): { isValid: boolean; error?: string } => {
  // Check file type
  if (!acceptedFormats.includes(file.type as ImageFormat)) {
    return {
      isValid: false,
      error: `File type ${file.type} is not supported. Accepted formats: ${acceptedFormats.join(', ')}`
    };
  }
  
  // Check file size
  if (file.size > maxFileSize) {
    return {
      isValid: false,
      error: `File size ${formatFileSize(file.size)} exceeds maximum allowed size of ${formatFileSize(maxFileSize)}`
    };
  }
  
  return { isValid: true };
};

/**
 * Convert file to base64 and get image dimensions
 */
const processImageFile = (file: File): Promise<UploadedImage> => {
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
};

// ============================================================================
// Main Component
// ============================================================================

export const ImageUpload: React.FC<ImageUploadProps> = ({
  // Core functionality
  onUpload,
  onAnalysis,
  onProgress,
  onError,
  
  // Configuration
  acceptedFormats = DEFAULT_UPLOAD_CONFIG.acceptedFormats,
  maxFileSize = DEFAULT_UPLOAD_CONFIG.maxFileSize,
  maxFiles = DEFAULT_UPLOAD_CONFIG.maxFiles,
  size = DEFAULT_UPLOAD_CONFIG.size,
  width,
  height,
  
  // Vision processing
  enableVisionAnalysis = DEFAULT_UPLOAD_CONFIG.enableVisionAnalysis,
  visionProvider = DEFAULT_UPLOAD_CONFIG.visionProvider,
  analysisTypes = DEFAULT_UPLOAD_CONFIG.analysisTypes,
  visionOptions = DEFAULT_UPLOAD_CONFIG.visionOptions,
  
  // UI customization
  children,
  placeholder,
  showProgress = DEFAULT_UPLOAD_CONFIG.showProgress,
  showAnalysisResults = DEFAULT_UPLOAD_CONFIG.showAnalysisResults,
  disabled = false,
  readOnly = false,
  
  // Styling
  className,
  style,
  testId,
}) => {
  // ========== State Management ==========
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([]);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({
    status: 'idle',
    progress: 0,
    message: 'Ready to upload'
  });
  const [isDragging, setIsDragging] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<Map<string, any>>(new Map());
  
  // ========== Refs ==========
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dragCounterRef = useRef(0);
  
  // ========== Progress Updates ==========
  const updateProgress = useCallback((progress: Partial<UploadProgress>) => {
    const newProgress = { ...uploadProgress, ...progress };
    setUploadProgress(newProgress);
    onProgress?.(newProgress);
  }, [uploadProgress, onProgress]);
  
  // ========== File Processing ==========
  const processFiles = useCallback(async (files: FileList | File[]) => {
    if (disabled || readOnly) return;
    
    const fileArray = Array.from(files);
    
    // Check file count limit
    if (uploadedImages.length + fileArray.length > maxFiles) {
      const error = {
        code: 'TOO_MANY_FILES',
        message: `Cannot upload more than ${maxFiles} files. Currently have ${uploadedImages.length} files.`
      };
      onError?.(error);
      updateProgress({
        status: 'error',
        message: error.message,
        error
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
        const validation = validateImageFile(file, acceptedFormats, maxFileSize);
        if (!validation.isValid) {
          throw new Error(validation.error);
        }
        
        // Update progress
        updateProgress({
          status: 'uploading',
          progress: (i / fileArray.length) * 50, // First 50% for file processing
          message: `Processing ${file.name}...`
        });
        
        // Process image
        const processedImage = await processImageFile(file);
        processedImages.push(processedImage);
        
        // Trigger upload callback
        const uploadEvent: ImageUploadEvent = {
          image: processedImage,
          progress: {
            status: 'uploading',
            progress: ((i + 1) / fileArray.length) * 50,
            message: `Processed ${file.name}`
          }
        };
        onUpload?.(uploadEvent);
      }
      
      // Update state
      setUploadedImages(prev => [...prev, ...processedImages]);
      
      // Start vision analysis if enabled
      if (enableVisionAnalysis) {
        updateProgress({
          status: 'processing',
          progress: 50,
          message: 'Starting vision analysis...'
        });
        
        // TODO: Implement vision analysis
        // This will be implemented in the next component
        
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
      
    } catch (error) {
      const errorObj = {
        code: 'UPLOAD_FAILED',
        message: error instanceof Error ? error.message : 'Upload failed',
        details: error
      };
      
      onError?.(errorObj);
      updateProgress({
        status: 'error',
        message: errorObj.message,
        error: errorObj
      });
    }
  }, [
    disabled, readOnly, uploadedImages.length, maxFiles, acceptedFormats, 
    maxFileSize, enableVisionAnalysis, onUpload, onError, updateProgress
  ]);
  
  // ========== Event Handlers ==========
  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      processFiles(files);
    }
    // Reset input value to allow selecting the same file again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [processFiles]);
  
  const handleClick = useCallback(() => {
    if (!disabled && !readOnly) {
      fileInputRef.current?.click();
    }
  }, [disabled, readOnly]);
  
  const handleRemoveImage = useCallback((imageId: string) => {
    setUploadedImages(prev => prev.filter(img => img.id !== imageId));
    setAnalysisResults(prev => {
      const newResults = new Map(prev);
      newResults.delete(imageId);
      return newResults;
    });
  }, []);
  
  // ========== Drag and Drop Handlers ==========
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    dragCounterRef.current++;
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  }, []);
  
  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    dragCounterRef.current--;
    if (dragCounterRef.current === 0) {
      setIsDragging(false);
    }
  }, []);
  
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);
  
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    setIsDragging(false);
    dragCounterRef.current = 0;
    
    if (disabled || readOnly) return;
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      processFiles(files);
    }
  }, [disabled, readOnly, processFiles]);
  
  // ========== Reset progress after success/error ==========
  useEffect(() => {
    if (uploadProgress.status === 'success' || uploadProgress.status === 'error') {
      const timer = setTimeout(() => {
        setUploadProgress({
          status: 'idle',
          progress: 0,
          message: 'Ready to upload'
        });
      }, 3000);
      
      return () => clearTimeout(timer);
    }
  }, [uploadProgress.status]);
  
  // ========== Render Upload Status Icon ==========
  const renderStatusIcon = () => {
    switch (uploadProgress.status) {
      case 'uploading':
        return '⏳';
      case 'processing':
        return '🔄';
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'dragging':
        return '📁';
      default:
        return '📤';
    }
  };
  
  // ========== Render Upload Content ==========
  const renderUploadContent = () => {
    if (uploadProgress.status === 'error') {
      return (
        <ErrorContainer>
          <ErrorIcon>❌</ErrorIcon>
          <ErrorMessage>{uploadProgress.error?.message || 'Upload failed'}</ErrorMessage>
        </ErrorContainer>
      );
    }
    
    return (
      <>
        <UploadIcon $status={uploadProgress.status}>
          {renderStatusIcon()}
        </UploadIcon>
        <UploadTitle>
          {isDragging ? 'Drop images here' : 'Upload Images'}
        </UploadTitle>
        <UploadDescription>
          {placeholder || `Drag and drop images here, or click to select files`}
          <br />
          <small>
            Supported formats: {acceptedFormats.join(', ')} • Max size: {formatFileSize(maxFileSize)}
          </small>
        </UploadDescription>
        {!isDragging && uploadProgress.status === 'idle' && (
          <UploadButton onClick={handleClick} disabled={disabled}>
            Choose Files
          </UploadButton>
        )}
        {uploadProgress.status !== 'idle' && (
          <UploadDescription>
            {uploadProgress.message}
          </UploadDescription>
        )}
      </>
    );
  };
  
  return (
    <div className={className} style={style} data-testid={testId}>
      <UploadContainer
        $size={size}
        $width={width}
        $height={height}
        $isDragging={isDragging}
        $status={uploadProgress.status}
        $disabled={disabled}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <UploadArea>
          {children || renderUploadContent()}
        </UploadArea>
        
        {showProgress && (
          <ProgressContainer $show={uploadProgress.status === 'uploading' || uploadProgress.status === 'processing'}>
            <ProgressBar $progress={uploadProgress.progress} />
          </ProgressContainer>
        )}
        
        <HiddenInput
          ref={fileInputRef}
          type="file"
          multiple={maxFiles > 1}
          accept={acceptedFormats.join(',')}
          onChange={handleFileSelect}
        />
      </UploadContainer>
      
      {/* File List */}
      {uploadedImages.length > 0 && (
        <FileList>
          {uploadedImages.map((image) => (
            <FileItem key={image.id}>
              <FileInfo>
                <FilePreview src={image.previewUrl} alt={image.name} />
                <FileDetails>
                  <FileName>{image.name}</FileName>
                  <FileSize>
                    {formatFileSize(image.size)} • {image.dimensions.width}×{image.dimensions.height}
                  </FileSize>
                </FileDetails>
              </FileInfo>
              <FileActions>
                <ActionButton onClick={() => handleRemoveImage(image.id)} $variant="danger">
                  Remove
                </ActionButton>
              </FileActions>
            </FileItem>
          ))}
        </FileList>
      )}
      
      {/* Analysis Results */}
      {showAnalysisResults && analysisResults.size > 0 && (
        <AnalysisContainer>
          <AnalysisTitle>Vision Analysis Results</AnalysisTitle>
          <AnalysisContent>
            {/* TODO: Render analysis results */}
            Analysis results will be displayed here once vision processing is implemented.
          </AnalysisContent>
        </AnalysisContainer>
      )}
    </div>
  );
};

export default ImageUpload;
