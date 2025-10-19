# Text-to-Speech Service

This service provides local Text-to-Speech (TTS) capabilities for the Unhinged project using Coqui TTS.

## Features

- **Local TTS**: Uses Coqui TTS for high-quality neural voice synthesis
- **Human-like Voices**: Neural models for natural-sounding speech
- **Multi-speaker Support**: Some models support multiple speakers
- **Offline Processing**: Runs completely locally, no external API calls
- **Health Checks**: Built-in health monitoring

## API Endpoints

### Health Check
- **GET** `/health` - Returns service health status

### Text-to-Speech
- **POST** `/synthesize` - Convert text to speech
  - JSON body: `{"text": "text to speak", "speaker": "optional_speaker_name"}`
  - Returns: WAV audio file

### Speakers
- **GET** `/speakers` - Get available speakers for multi-speaker models

### Service Info
- **GET** `/info` - Returns service capabilities and configuration

## Usage Examples

### Health Check
```bash
curl http://localhost:8002/health
```

### Synthesize Speech
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"text": "Hello world, this is local neural text to speech!"}' \
  http://localhost:8002/synthesize --output speech.wav
```

### Get Available Speakers
```bash
curl http://localhost:8002/speakers
```

## Configuration

### Environment Variables
- `TTS_MODEL_NAME`: Coqui TTS model to use (default: `tts_models/en/ljspeech/tacotron2-DDC`)
- `TTS_CACHE_DIR`: Directory to cache models (default: `/app/models`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

### Supported Models
- `tts_models/en/ljspeech/tacotron2-DDC` - Single speaker, good quality
- `tts_models/en/vctk/vits` - Multi-speaker model
- `tts_models/en/ljspeech/glow-tts` - Fast inference
- Many more available in Coqui TTS model zoo

## Performance

- **Model Loading**: ~30-60 seconds on first startup
- **Inference Speed**: Faster than real-time on modern hardware
- **Memory Usage**: ~500MB-2GB depending on model
- **GPU Support**: Automatically uses GPU if available

## Architecture

This service is designed to be:
- **Scalable**: Separate from speech-to-text for independent scaling
- **Local**: No external dependencies or API calls
- **High Quality**: Neural models for human-like voice synthesis
- **Flexible**: Support for different models and speakers
