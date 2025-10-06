# Vision AI Service

This service provides image analysis, description, and processing capabilities for the Unhinged project.

## Features

- **Image Analysis**: Uses BLIP (Bootstrapping Language-Image Pre-training) model for image understanding
- **Image Description**: Generates natural language descriptions of uploaded images
- **Conditional Description**: Supports prompt-based image description
- **Health Checks**: Built-in health monitoring
- **Multi-format Support**: Supports common image formats (JPEG, PNG, GIF, etc.)

## API Endpoints

### Health Check
- **GET** `/health` - Returns service health status

### Image Analysis
- **POST** `/analyze` - Upload image for basic analysis and description
  - Form data: `image` (image file)
  - Returns: `{"description": "generated description", "metadata": {...}}`

### Image Description
- **POST** `/describe` - Upload image for detailed description
  - Form data: `image` (image file), `prompt` (optional text prompt)
  - Returns: `{"description": "detailed description", "prompt_used": "..."}`

## Usage Examples

### Basic Image Analysis
```bash
curl -X POST http://localhost:8001/analyze \
  -F "image=@screenshot.png"
```

### Prompted Image Description
```bash
curl -X POST http://localhost:8001/describe \
  -F "image=@screenshot.png" \
  -F "prompt=What is happening in this image?"
```

## Model Information

- **Primary Model**: Salesforce/blip-image-captioning-base
- **Framework**: PyTorch + Transformers
- **GPU Support**: Automatic CUDA detection and usage
- **Memory Requirements**: ~2GB GPU memory recommended

## Environment Variables

- `ENABLE_FLASK`: Enable HTTP API server (default: true)
- `ENABLE_GRPC`: Enable gRPC server (default: false, not yet implemented)
- `VISION_MODEL`: Vision model to use (default: openai/clip-vit-base-patch32)

## Docker Usage

```bash
# Build the image
docker build -t vision-ai-service .

# Run the service
docker run -p 8001:8001 vision-ai-service
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python main.py
```
