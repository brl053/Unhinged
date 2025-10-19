# Speech-to-Text Service

This service provides Speech-to-Text (STT) capabilities for the Unhinged project using OpenAI's Whisper model.

## Features

- **Speech-to-Text**: Uses OpenAI's Whisper model for accurate transcription
- **Health Checks**: Built-in health monitoring
- **Multi-language Support**: Supports 99+ languages
- **Local Processing**: Runs completely offline, no external API calls

## API Endpoints

### Health Check
- **GET** `/health` - Returns service health status

### Speech-to-Text
- **POST** `/transcribe` - Upload audio file for transcription
  - Form data: `audio` (audio file)
  - Returns: `{"text": "transcribed text", "language": "detected_language"}`

# Text-to-Speech functionality has been moved to a dedicated service
# See services/text-to-speech for TTS capabilities

### Service Info
- **GET** `/info` - Returns service capabilities and configuration

## Usage Examples

### Health Check
```bash
curl http://localhost:8000/health
```

### Transcribe Audio
```bash
curl -X POST -F "audio=@audio.wav" http://localhost:8000/transcribe
```

### Synthesize Speech
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "language": "en"}' \
  http://localhost:8000/synthesize --output speech.mp3
```

## Supported Languages

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)

## Docker Integration

The service is integrated into the main docker-compose.yml and will start automatically with the rest of the Unhinged stack.

Port: 8000
Container: whisper-tts-service
