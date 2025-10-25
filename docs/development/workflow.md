# 🔄 Development Workflow

## Overview

Standard development workflow for the Unhinged project with voice-first user experience focus.

## Development Cycle

### 1. Setup
```bash
make setup          # Initial project setup
make check-deps     # Verify dependencies
```

### 2. Development
```bash
make dev            # Start development environment
make start          # Launch voice-first GUI
make test           # Run test suite
```

### 3. Building
```bash
make build          # Build all components
make generate       # Generate build artifacts
make validate       # Validate build outputs
```

### 4. Documentation
```bash
make docs-update    # Update all documentation
make docs-validate  # Validate documentation
make context        # Generate AI context
```

## Voice Pipeline Development

### Testing Voice Features
```bash
# Test native audio capture
python3 control/native_gui/tools/chat/bridge/native_audio_capture.py

# Test Whisper service
curl -X POST -F "audio=@test.wav" http://localhost:1101/transcribe

# Test complete pipeline
make start  # Then use mic button in GUI
```

### Service Integration
```bash
# Check service status
python3 control/service_launcher.py --status

# Start services manually
python3 control/service_launcher.py --timeout 60

# Stop services
python3 control/service_launcher.py --stop
```

## Code Standards

### LlmDocs Annotations
All new code must include structured LlmDocs annotations:
- `@llm-type`: Component classification
- `@llm-legend`: High-level purpose
- `@llm-key`: Core functionality
- `@llm-map`: Architectural position
- `@llm-axiom`: Design principles
- `@llm-contract`: Interface contracts
- `@llm-token`: Searchable identifier

### Commit Standards
- Use structured commit messages
- Include @llm-* tags in commit messages
- Reference architectural principles
- Document voice pipeline changes

## Testing Strategy

### Voice Pipeline Testing
1. **Native Audio**: Test system audio capture
2. **Whisper Service**: Test transcription accuracy
3. **GUI Integration**: Test mic button functionality
4. **End-to-End**: Test complete voice → AI flow

### Service Testing
1. **Auto-start**: Test service launcher integration
2. **Health Checks**: Verify service monitoring
3. **Error Handling**: Test graceful degradation
4. **Performance**: Monitor startup times

## Deployment

### Local Deployment
```bash
make start          # Full system with voice
make start-offline  # GUI only (no services)
```

### Production Considerations
- Voice pipeline requires audio hardware
- Service dependencies must be available
- GTK4 required for native GUI
- Docker required for backend services
