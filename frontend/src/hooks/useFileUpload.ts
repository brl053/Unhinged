/**
 * File Upload Hook
 * 
 * Headless file upload hook using react-dropzone.
 * Provides drag & drop functionality with upload progress tracking.
 * Integrates with Ktor backend file upload endpoints.
 * 
 * @author Augment Agent
 * @version 1.0.0
 */

import { useCallback, useState } from 'react';
import { useDropzone, FileWithPath, DropzoneOptions } from 'react-dropzone';
import { useMutation } from '@tanstack/react-query';
import { apiHelpers, FileUploadResponse } from '@/services/api';
import { dbHelpers } from '@/services/db';

// Upload progress interface
export interface UploadProgress {
  fileId: string;
  progress: number;
  status: 'pending' | 'uploading' | 'completed' | 'failed';
  error?: string;
}

// Hook configuration interface
export interface FileUploadConfig extends Omit<DropzoneOptions, 'onDrop'> {
  /** Cache files locally before upload */
  cacheLocally?: boolean;
  /** Auto-upload files when dropped */
  autoUpload?: boolean;
  /** Maximum file size in bytes */
  maxSize?: number;
  /** Accepted file types */
  acceptedTypes?: Record<string, string[]>;
}

// Hook return interface
export interface FileUploadReturn {
  // Dropzone props
  getRootProps: () => any;
  getInputProps: () => any;
  
  // State
  isDragActive: boolean;
  acceptedFiles: FileWithPath[];
  rejectedFiles: any[];
  
  // Upload state
  uploadProgress: Record<string, UploadProgress>;
  isUploading: boolean;
  
  // Actions
  uploadFile: (file: File) => void;
  uploadFiles: (files: File[]) => void;
  clearFiles: () => void;
  removeFile: (fileId: string) => void;
  
  // Error state
  error: Error | null;
}

// Default configuration
const DEFAULT_CONFIG = {
  cacheLocally: true,
  autoUpload: true,
  maxSize: 10485760, // 10MB
  acceptedTypes: {
    'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
    'audio/*': ['.mp3', '.webm', '.wav', '.m4a'],
    'video/*': ['.mp4', '.webm', '.mov', '.avi'],
    'text/*': ['.txt', '.md', '.json'],
    'application/pdf': ['.pdf']
  }
};

/**
 * File Upload Hook
 * 
 * Provides headless file upload functionality with drag & drop support.
 * Files can be cached locally and uploaded to the backend with progress tracking.
 * 
 * @param config - Configuration options
 * @returns File upload controls and state
 * 
 * @example
 * ```tsx
 * const FileUploadZone = () => {
 *   const { 
 *     getRootProps, 
 *     getInputProps, 
 *     isDragActive, 
 *     acceptedFiles,
 *     uploadProgress,
 *     isUploading 
 *   } = useFileUpload({
 *     maxSize: 5242880, // 5MB
 *     autoUpload: true
 *   });
 *   
 *   return (
 *     <div {...getRootProps()}>
 *       <input {...getInputProps()} />
 *       {isDragActive ? (
 *         <p>Drop files here...</p>
 *       ) : (
 *         <p>Drag & drop files here, or click to select</p>
 *       )}
 *       {isUploading && <p>Uploading...</p>}
 *     </div>
 *   );
 * };
 * ```
 */
export const useFileUpload = (config: FileUploadConfig = {}): FileUploadReturn => {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  
  // Internal state
  const [uploadProgress, setUploadProgress] = useState<Record<string, UploadProgress>>({});
  const [acceptedFiles, setAcceptedFiles] = useState<FileWithPath[]>([]);

  // File upload mutation
  const {
    mutate: uploadSingleFile,
    isPending: isUploading,
    error
  } = useMutation({
    mutationFn: async ({ file, fileId }: { file: File; fileId: string }): Promise<FileUploadResponse> => {
      console.log('📤 Starting file upload:', { name: file.name, size: file.size, type: file.type });
      
      // Update progress to uploading
      setUploadProgress(prev => ({
        ...prev,
        [fileId]: { fileId, progress: 0, status: 'uploading' }
      }));

      try {
        // Cache file locally if enabled
        if (finalConfig.cacheLocally) {
          await dbHelpers.fileCache.addToQueue(file);
          console.log('💾 File cached locally');
        }

        // Upload to backend
        const result = await apiHelpers.uploadFile(file);
        
        console.log('✅ File uploaded successfully:', result);
        
        // Update progress to completed
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: { fileId, progress: 100, status: 'completed' }
        }));

        return result;

      } catch (error) {
        console.error('❌ File upload failed:', error);
        
        // Update progress to failed
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: { 
            fileId, 
            progress: 0, 
            status: 'failed',
            error: error instanceof Error ? error.message : 'Upload failed'
          }
        }));
        
        throw error;
      }
    },
    onError: (error, { fileId }) => {
      console.error('❌ Upload mutation failed:', error);
    }
  });

  // Handle file drop
  const onDrop = useCallback((droppedFiles: FileWithPath[], rejectedFiles: any[]) => {
    console.log('📁 Files dropped:', { 
      accepted: droppedFiles.length, 
      rejected: rejectedFiles.length 
    });

    // Add to accepted files
    setAcceptedFiles(prev => [...prev, ...droppedFiles]);

    // Log rejected files
    if (rejectedFiles.length > 0) {
      console.warn('⚠️ Rejected files:', rejectedFiles.map(f => ({
        name: f.file.name,
        errors: f.errors.map((e: any) => e.message)
      })));
    }

    // Auto-upload if enabled
    if (finalConfig.autoUpload) {
      droppedFiles.forEach(file => {
        const fileId = `${file.name}-${Date.now()}`;
        
        // Initialize progress
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: { fileId, progress: 0, status: 'pending' }
        }));

        // Start upload
        uploadSingleFile({ file, fileId });
      });
    }
  }, [finalConfig.autoUpload, uploadSingleFile]);

  // Dropzone configuration
  const dropzoneConfig: DropzoneOptions = {
    onDrop,
    accept: finalConfig.acceptedTypes,
    maxSize: finalConfig.maxSize,
    multiple: true,
    ...config // Allow overriding any dropzone options
  };

  const {
    getRootProps,
    getInputProps,
    isDragActive
  } = useDropzone(dropzoneConfig);

  // Manual upload functions
  const uploadFile = useCallback((file: File) => {
    const fileId = `${file.name}-${Date.now()}`;
    
    console.log('📤 Manual file upload triggered:', file.name);
    
    setUploadProgress(prev => ({
      ...prev,
      [fileId]: { fileId, progress: 0, status: 'pending' }
    }));

    uploadSingleFile({ file, fileId });
  }, [uploadSingleFile]);

  const uploadFiles = useCallback((files: File[]) => {
    console.log('📤 Bulk file upload triggered:', files.length);
    files.forEach(uploadFile);
  }, [uploadFile]);

  // Clear functions
  const clearFiles = useCallback(() => {
    console.log('🗑️ Clearing all files');
    setAcceptedFiles([]);
    setUploadProgress({});
  }, []);

  const removeFile = useCallback((fileId: string) => {
    console.log('🗑️ Removing file:', fileId);
    
    setUploadProgress(prev => {
      const { [fileId]: removed, ...rest } = prev;
      return rest;
    });
    
    // Also remove from accepted files if it matches
    setAcceptedFiles(prev => 
      prev.filter(file => `${file.name}-${Date.now()}` !== fileId)
    );
  }, []);

  // Computed state
  const hasUploading = Object.values(uploadProgress).some(p => p.status === 'uploading');
  const hasCompleted = Object.values(uploadProgress).some(p => p.status === 'completed');
  const hasFailed = Object.values(uploadProgress).some(p => p.status === 'failed');

  return {
    // Dropzone props
    getRootProps,
    getInputProps,
    
    // State
    isDragActive,
    acceptedFiles,
    rejectedFiles: [], // TODO: Handle rejected files in onDrop callback
    
    // Upload state
    uploadProgress,
    isUploading: isUploading || hasUploading,
    
    // Actions
    uploadFile,
    uploadFiles,
    clearFiles,
    removeFile,
    
    // Error state
    error
  };
};

// Utility hook for upload statistics
export const useUploadStats = (uploadProgress: Record<string, UploadProgress>) => {
  const total = Object.keys(uploadProgress).length;
  const pending = Object.values(uploadProgress).filter(p => p.status === 'pending').length;
  const uploading = Object.values(uploadProgress).filter(p => p.status === 'uploading').length;
  const completed = Object.values(uploadProgress).filter(p => p.status === 'completed').length;
  const failed = Object.values(uploadProgress).filter(p => p.status === 'failed').length;
  
  const overallProgress = total > 0 
    ? Math.round((completed / total) * 100)
    : 0;
  
  return {
    total,
    pending,
    uploading,
    completed,
    failed,
    overallProgress,
    isComplete: total > 0 && completed === total,
    hasErrors: failed > 0
  };
};
