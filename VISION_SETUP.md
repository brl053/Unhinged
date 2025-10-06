# 🖼️ Vision Processing Setup Guide

This guide explains how to set up and use the new image processing capabilities in the Unhinged project.

## 🏗️ Architecture Overview

The vision processing system follows the same clean architecture pattern as the audio processing:

```
Frontend (image-test.html)
    ↓
Backend (Kotlin - Clean Architecture)
    ↓ HTTP API calls
Vision AI Service (Python - BLIP model)
```

### Components

1. **Vision AI Service** (`services/vision-ai/`)
   - Python Flask service with BLIP image captioning model
   - Provides HTTP API for image analysis and description
   - Runs on port 8001

2. **Backend Vision Module** (`backend/src/main/kotlin/com/unhinged/*/vision/`)
   - Domain layer: Core business logic and entities
   - Application layer: Use cases and workflows
   - Infrastructure layer: HTTP client to vision service
   - Presentation layer: REST API endpoints

3. **Frontend Test Page** (`image-test.html`)
   - Drag-and-drop image upload
   - Multiple analysis options
   - Real-time results display

## 🚀 Quick Start

### 1. Start the Services

```bash
# Start vision service only (simple setup)
docker compose -f docker-compose.simple.yml up vision-ai

# Or start full stack
docker compose up vision-ai backend
```

### 2. Test the Setup

```bash
# Run the automated test suite
node test-vision-pipeline.js

# Or test manually
open image-test.html
```

### 3. Upload and Analyze Images

1. Open `image-test.html` in your browser
2. Check that services are healthy (green status)
3. Drag and drop an image or click to upload
4. Choose analysis type:
   - **Analyze**: Complete analysis with metadata and tags
   - **Describe**: Natural language description
   - **Detect**: Object detection (experimental)

## 📡 API Endpoints

### Vision Service (Port 8001)

- `GET /health` - Service health check
- `POST /analyze` - Basic image analysis
- `POST /describe` - Detailed image description

### Backend API (Port 8080)

- `GET /api/v1/vision/health` - Backend health check
- `POST /api/v1/vision/analyze` - Complete image analysis
- `POST /api/v1/vision/describe` - Image description with prompt
- `POST /api/v1/vision/detect` - Object detection

## 🔧 Configuration

### Environment Variables

**Vision AI Service:**
- `ENABLE_FLASK=true` - Enable HTTP API
- `ENABLE_GRPC=false` - Disable gRPC (not implemented yet)
- `VISION_MODEL=Salesforce/blip-image-captioning-base` - Model to use
- `LOG_LEVEL=INFO` - Logging level

### Docker Volumes

- `vision-models:/root/.cache/transformers` - Model cache
- `image-uploads:/app/uploads` - Temporary image storage

## 🧪 Testing

### Automated Tests

```bash
# Run the complete test suite
node test-vision-pipeline.js
```

### Manual Testing

1. **Service Health:**
   ```bash
   curl http://localhost:8001/health
   curl http://localhost:8080/api/v1/vision/health
   ```

2. **Image Analysis:**
   ```bash
   curl -X POST http://localhost:8080/api/v1/vision/analyze \
     -F "image=@screenshot.png" \
     -F "generateTags=true"
   ```

3. **Image Description:**
   ```bash
   curl -X POST http://localhost:8080/api/v1/vision/describe \
     -F "image=@screenshot.png" \
     -F "prompt=What is happening in this image?"
   ```

## 🎯 Supported Features

### ✅ Implemented
- Image upload and validation
- Basic image analysis with BLIP model
- Natural language descriptions
- Image metadata extraction
- Tag generation from descriptions
- Health monitoring
- Error handling and validation

### 🚧 Planned
- Object detection with bounding boxes
- gRPC API implementation
- Multiple vision models support
- Image classification
- OCR text extraction
- Batch processing

## 🐛 Troubleshooting

### Common Issues

1. **Vision service unhealthy:**
   ```bash
   # Check if container is running
   docker ps | grep vision-ai
   
   # Check logs
   docker logs vision-ai-service
   
   # Restart service
   docker compose restart vision-ai
   ```

2. **Model loading takes time:**
   - First startup downloads ~500MB model
   - Wait for health check to pass (up to 3 minutes)
   - Check logs for download progress

3. **Out of memory errors:**
   - Vision models require ~2GB RAM
   - Increase Docker memory limits
   - Consider using smaller models

4. **Image upload fails:**
   - Check file size (max 10MB)
   - Verify supported formats (JPEG, PNG, GIF, BMP, WebP)
   - Check CORS settings for cross-origin requests

### Performance Tips

- **GPU Acceleration:** Install CUDA for faster processing
- **Model Caching:** Models are cached after first download
- **Image Optimization:** Resize large images before upload
- **Batch Processing:** Process multiple images together (future feature)

## 🔗 Integration Examples

### JavaScript/Frontend
```javascript
const formData = new FormData();
formData.append('image', imageFile);
formData.append('prompt', 'Describe this image in detail');

const response = await fetch('/api/v1/vision/describe', {
    method: 'POST',
    body: formData
});

const result = await response.json();
console.log(result.description);
```

### cURL
```bash
curl -X POST http://localhost:8080/api/v1/vision/analyze \
  -F "image=@image.jpg" \
  -F "generateTags=true" \
  -F "maxDescriptionLength=200"
```

## 📚 Next Steps

1. **Try the demo:** Open `image-test.html` and upload some images
2. **Explore the API:** Use the endpoints in your applications
3. **Customize models:** Experiment with different vision models
4. **Integrate with chat:** Add image analysis to chat conversations
5. **Scale up:** Deploy with proper GPU support for production

---

**Need help?** Check the logs, run the test suite, or refer to the main project documentation.
