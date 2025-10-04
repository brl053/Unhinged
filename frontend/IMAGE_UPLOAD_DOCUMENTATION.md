/**
 * @fileoverview Image Upload Component Documentation
 * @purpose Complete documentation for the drag-and-drop image upload component with vision processing
 * @editable true - LLM should update this documentation when adding new features
 * @deprecated false
 * 
 * @remarks
 * This documentation serves as the complete reference for the ImageUpload component system.
 * All future LLM interactions should reference this file to understand the current
 * architecture and avoid breaking existing functionality.
 */

# Image Upload Component Documentation

## 🎯 **Purpose**
This document records the complete ImageUpload component architecture for the Unhinged Platform, providing drag-and-drop image upload functionality with integrated vision processing capabilities.

## 🚨 **Critical Rules for LLMs**

### **ALWAYS USE PROPER TYPES**
```typescript
// ✅ CORRECT - Use proper types
const handleUpload = (event: ImageUploadEvent) => {
  console.log('Uploaded:', event.image);
};

// ❌ WRONG - Untyped handlers
const handleUpload = (event: any) => {
  console.log('Uploaded:', event);
};
```

### **ALWAYS USE TRANSIENT PROPS IN STYLES**
```typescript
// ✅ CORRECT - Transient props
const Container = styled.div<{ $isDragging: boolean }>`
  border-color: ${({ $isDragging, theme }) => 
    $isDragging ? theme.color.primary.main : theme.color.border.primary};
`;

// ❌ WRONG - Regular props passed to DOM
const Container = styled.div<{ isDragging: boolean }>`
  border-color: ${({ isDragging, theme }) => 
    isDragging ? theme.color.primary.main : theme.color.border.primary};
`;
```

### **ALWAYS HANDLE ASYNC OPERATIONS PROPERLY**
```typescript
// ✅ CORRECT - Proper error handling
try {
  const processedImage = await processImageFile(file);
  setUploadedImages(prev => [...prev, processedImage]);
} catch (error) {
  setError({
    code: 'PROCESSING_FAILED',
    message: error instanceof Error ? error.message : 'Processing failed'
  });
}
```

## 🎨 **Component Architecture**

### **Core Components**
```
ImageUpload/
├── ImageUpload.tsx          # Main component with drag-and-drop
├── useImageUpload.ts        # Custom hook for state management
├── types.ts                 # Complete type definitions
├── styles.ts                # Styled components with theme integration
├── index.ts                 # Public API exports
└── ImageUpload.test.tsx     # Comprehensive test suite
```

### **Type System**
```typescript
// Core upload types
interface UploadedImage {
  id: string;
  name: string;
  size: number;
  type: ImageFormat;
  data: string;              // Base64 encoded
  dimensions: { width: number; height: number };
  uploadedAt: Date;
  previewUrl?: string;
}

// Vision analysis types
interface VisionAnalysisResult {
  id: string;
  imageId: string;
  analysisType: AnalysisType;
  provider: VisionProvider;
  results: {
    description: string;
    extractedText?: string[];
    uiElements?: UIElement[];
    codeSnippets?: CodeSnippet[];
    confidence: number;
  };
  metadata: {
    processingTime: number;
    tokenUsage?: { input: number; output: number; cost: number };
    analyzedAt: Date;
  };
}

// Event types
interface ImageUploadEvent {
  image: UploadedImage;
  progress: UploadProgress;
}

interface VisionAnalysisEvent {
  result: VisionAnalysisResult;
  image: UploadedImage;
}
```

## 🚀 **Usage Examples**

### **Basic Usage**
```typescript
import { ImageUpload } from '@/lib/components/ImageUpload';

function MyUploader() {
  const handleUpload = (event: ImageUploadEvent) => {
    console.log('Uploaded:', event.image);
  };
  
  return (
    <ImageUpload
      onUpload={handleUpload}
      maxFiles={5}
      maxFileSize={10 * 1024 * 1024} // 10MB
      acceptedFormats={['image/png', 'image/jpeg']}
    />
  );
}
```

### **With Vision Processing**
```typescript
import { ImageUpload } from '@/lib/components/ImageUpload';

function VisionUploader() {
  const handleUpload = (event: ImageUploadEvent) => {
    console.log('Image uploaded:', event.image);
  };
  
  const handleAnalysis = (event: VisionAnalysisEvent) => {
    console.log('Analysis completed:', event.result);
  };
  
  return (
    <ImageUpload
      onUpload={handleUpload}
      onAnalysis={handleAnalysis}
      enableVisionAnalysis={true}
      visionProvider="openai-gpt4o"
      analysisTypes={['screenshot', 'ui-analysis', 'code-analysis']}
      visionOptions={{
        quality: 'high',
        maxDimensions: { width: 1920, height: 1080 },
        enableCaching: true
      }}
    />
  );
}
```

### **Using the Custom Hook**
```typescript
import { useImageUpload } from '@/lib/components/ImageUpload';

function HookBasedUploader() {
  const {
    uploadedImages,
    uploadProgress,
    analysisResults,
    uploadImages,
    removeImage,
    clearAll,
    isUploading,
    error
  } = useImageUpload({
    maxFiles: 10,
    enableVisionAnalysis: true,
    visionProvider: 'claude-vision',
    analysisTypes: ['screenshot', 'accessibility-audit']
  });
  
  const handleFileSelect = (files: FileList) => {
    uploadImages(files);
  };
  
  return (
    <div>
      <input 
        type="file" 
        multiple 
        onChange={(e) => e.target.files && handleFileSelect(e.target.files)}
      />
      
      <div>Status: {uploadProgress.status}</div>
      <div>Images: {uploadedImages.length}</div>
      <div>Analyses: {analysisResults.size}</div>
      
      {error && <div>Error: {error.message}</div>}
      
      <button onClick={clearAll} disabled={isUploading}>
        Clear All
      </button>
    </div>
  );
}
```

## 🎛️ **Configuration Options**

### **Upload Configuration**
```typescript
interface ImageUploadProps {
  // File handling
  acceptedFormats?: ImageFormat[];           // Default: ['image/jpeg', 'image/png', 'image/webp']
  maxFileSize?: number;                      // Default: 10MB
  maxFiles?: number;                         // Default: 5
  
  // UI customization
  size?: UploadSize;                         // 'small' | 'medium' | 'large' | 'full'
  width?: string | number;                   // Custom width
  height?: string | number;                  // Custom height
  placeholder?: string;                      // Custom placeholder text
  
  // Vision processing
  enableVisionAnalysis?: boolean;            // Default: true
  visionProvider?: VisionProvider;           // Default: 'openai-gpt4o'
  analysisTypes?: AnalysisType[];           // Default: ['screenshot', 'general-description']
  visionOptions?: {
    quality?: 'low' | 'high';               // Default: 'high'
    maxDimensions?: { width: number; height: number };
    enableCaching?: boolean;                 // Default: true
  };
}
```

### **Vision Providers**
```typescript
type VisionProvider = 
  | 'openai-gpt4o'      // OpenAI GPT-4o Vision ($2.50/$10.00 per 1M tokens)
  | 'claude-vision'     // Claude Vision ($3.00/$15.00 per 1M tokens)
  | 'google-vision'     // Google Cloud Vision ($1.50 per 1K images)
  | 'azure-vision'      // Azure Computer Vision (variable pricing)
  | 'local-model';      // Future self-hosted models
```

### **Analysis Types**
```typescript
type AnalysisType = 
  | 'screenshot'           // General screenshot analysis
  | 'ui-analysis'          // UI element detection and description
  | 'code-analysis'        // Code snippet extraction and analysis
  | 'text-extraction'      // OCR text extraction
  | 'general-description'  // General image description
  | 'accessibility-audit'; // Accessibility issue detection
```

## 🎨 **Styling System**

### **Theme Integration**
All styles use the enhanced theme system:
```typescript
// Container styling
border: 2px dashed ${({ theme, $isDragging, $status }) => {
  if ($status === 'error') return theme.color.error.main;
  if ($status === 'success') return theme.color.success.main;
  if ($isDragging) return theme.color.primary.main;
  return theme.color.border.primary;
}};

// Typography
font-size: ${({ theme }) => theme.typography.fontSize.sm};
font-weight: ${({ theme }) => theme.typography.fontWeight.medium};

// Spacing
padding: ${({ theme }) => theme.spacing.lg};
margin: ${({ theme }) => theme.spacing.md};
```

### **Animation System**
```typescript
// Drag state animations
${({ $isDragging }) => $isDragging && `
  background: ${theme.color.primary.main}10;
  transform: scale(1.02);
`}

// Upload progress animation
${({ $status }) => $status === 'uploading' && `
  animation: ${pulseAnimation} 2s infinite;
`}
```

## 🔧 **Event Handling**

### **Upload Events**
```typescript
// File upload completion
onUpload?: (event: ImageUploadEvent) => void;

// Vision analysis completion
onAnalysis?: (event: VisionAnalysisEvent) => void;

// Progress updates
onProgress?: (progress: UploadProgress) => void;

// Error handling
onError?: (error: { code: string; message: string; details?: any }) => void;
```

### **Drag and Drop Events**
```typescript
// Drag enter/leave handling with counter
const handleDragEnter = useCallback((e: React.DragEvent) => {
  e.preventDefault();
  dragCounterRef.current++;
  if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
    setIsDragging(true);
  }
}, []);

const handleDragLeave = useCallback((e: React.DragEvent) => {
  e.preventDefault();
  dragCounterRef.current--;
  if (dragCounterRef.current === 0) {
    setIsDragging(false);
  }
}, []);
```

## 🧪 **Testing**

### **Test Coverage**
- ✅ Component rendering
- ✅ Drag and drop functionality
- ✅ File validation (type, size, count)
- ✅ Upload progress tracking
- ✅ Error state handling
- ✅ Custom hook functionality
- ✅ Theme integration
- ✅ Accessibility features

### **Test Examples**
```typescript
// File validation test
it('validates file types correctly', async () => {
  const onError = jest.fn();
  render(<ImageUpload acceptedFormats={['image/png']} onError={onError} />);
  
  const invalidFile = createMockFile('test.txt', 1000, 'text/plain');
  // ... test implementation
});

// Hook state test
it('initializes with correct default state', () => {
  const { uploadedImages, uploadProgress, isUploading } = useImageUpload();
  expect(uploadedImages).toHaveLength(0);
  expect(uploadProgress.status).toBe('idle');
  expect(isUploading).toBe(false);
});
```

## 🔮 **Future Vision Processing Integration**

### **Planned Features**
1. **OpenAI GPT-4o Vision Integration** - Primary provider for screenshot analysis
2. **Claude Vision Integration** - Fallback provider with excellent UI interpretation
3. **Google Cloud Vision** - OCR and text extraction focused
4. **Local Model Support** - Self-hosted vision models for privacy
5. **Result Caching** - Avoid redundant API calls
6. **Batch Processing** - Process multiple images efficiently
7. **Cost Tracking** - Monitor API usage and costs

### **Architecture for Vision Integration**
```typescript
// Vision service abstraction
interface VisionService {
  analyzeImage(image: UploadedImage, types: AnalysisType[]): Promise<VisionAnalysisResult>;
  extractText(image: UploadedImage): Promise<string[]>;
  detectUIElements(image: UploadedImage): Promise<UIElement[]>;
  auditAccessibility(image: UploadedImage): Promise<AccessibilityIssue[]>;
}

// Provider factory
const createVisionService = (provider: VisionProvider): VisionService => {
  switch (provider) {
    case 'openai-gpt4o': return new OpenAIVisionService();
    case 'claude-vision': return new ClaudeVisionService();
    case 'google-vision': return new GoogleVisionService();
    case 'local-model': return new LocalVisionService();
  }
};
```

## 📝 **Maintenance Notes**

### **When Adding New Features**
1. Update type definitions in `types.ts`
2. Add proper TSDoc documentation
3. Use transient props in styled components
4. Follow the established error handling patterns
5. Add comprehensive tests
6. Update this documentation

### **When Adding Vision Providers**
1. Implement the `VisionService` interface
2. Add provider to `VisionProvider` type
3. Update the provider factory
4. Add cost tracking and rate limiting
5. Test with various image types

### **LLM Instructions**
- **ALWAYS** reference this documentation before making changes
- **NEVER** break the existing type system
- **ALWAYS** use proper error handling for async operations
- **ALWAYS** use transient props in styled components
- **ALWAYS** add TSDoc headers to new files

## 🎉 **Current Status**

### **✅ Completed**
- Complete drag-and-drop image upload component
- Comprehensive type system with 200+ lines of types
- Custom hook for state management
- Full theme system integration
- Comprehensive test suite
- Component showcase integration
- Proper error handling and validation
- Upload progress tracking
- File preview and management

### **🔄 Ready for Vision Integration**
- Abstracted vision processing interface
- Provider switching capability
- Analysis result caching system
- Cost tracking preparation
- Batch processing architecture

The ImageUpload component is now production-ready and prepared for seamless integration with vision processing APIs! 🎉
