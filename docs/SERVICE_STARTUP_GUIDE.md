# Unhinged Service Startup Guide

## Quick Fix for Current Issues

### Immediate Solutions

**1. Fix LogContainer Bug (FIXED)**
- The `LogContainer` AttributeError has been resolved with proper error handling
- Status tab logging should now work without crashes

**2. Start Chat Service (REQUIRED)**
```bash
# Start the chat service manually (required for "Create Session" functionality)
./venv-production/bin/python services/chat-with-sessions/minimal_grpc_server.py &
```

**3. Verify Chat Service is Running**
```bash
# Check if chat service is accessible
ss -tln | grep 9095
# Should show: LISTEN 0 4096 *:9095 *:*
```

### Proper Service Startup Sequence

#### Option 1: Use the New Startup Script (RECOMMENDED)
```bash
# Start all services in correct order
python3 control/start_unhinged_services.py --verbose

# Check service status
python3 control/service_launcher.py --status
```

#### Option 2: Manual Startup (Step by Step)
```bash
# 1. Ensure Docker containers are running
docker compose -f build/orchestration/docker-compose.production.yml up -d

# 2. Wait for containers to be healthy (30-60 seconds)
docker ps  # Check health status

# 3. Start chat service (CRITICAL for GUI functionality)
./venv-production/bin/python services/chat-with-sessions/minimal_grpc_server.py &

# 4. Verify services
python3 control/service_launcher.py --status

# 5. Launch GUI
./unhinged
```

## Service Architecture Overview

### Required Services for Full Functionality

1. **Docker Containers** (Port Range: 1200-1500)
   - `ollama-service`: LLM service (port 1500)
   - `unhinged-postgres`: Database (port 1200)
   - `unhinged-redis`: Session storage (port 1201)
   - `persistence-platform-service`: Kotlin persistence (port 1300)

2. **Python AI Services** (Port Range: 1100-1199, gRPC: 9090-9099)
   - `speech-to-text-service`: Whisper transcription (gRPC 1191)
   - `text-to-speech-service`: Voice synthesis (gRPC 9092)
   - `vision-ai-service`: Image analysis (gRPC 9093)

3. **Chat Service** (Port 9095) - **CRITICAL**
   - `chat-with-sessions`: gRPC chat service with session management
   - **This service is REQUIRED for "Create Session" functionality**

### Service Health Status

Check service health with:
```bash
python3 control/service_launcher.py --status
```

Expected output:
```
🟢 LLM Service (Ollama): {'running': True, 'port': 1500}
🟢 Persistence Platform: {'running': True, 'port': 1300}
🟢 Database: {'running': True, 'port': 1200}
🟢 Chat Service: {'running': True, 'port': 9095}
```

## Platform Handler Functionality

### What "Start Platform" Should Do

The Platform Launcher in the Status tab now:
1. Runs `python3 control/service_launcher.py --timeout 60`
2. Starts essential services without recursive GUI launch
3. Provides real-time status updates in the logs

### Available Platform Commands

- `start-services`: Start all essential services
- `stop-services`: Stop running services
- `status`: Show current service status
- `generate`: Generate build artifacts
- `clean`: Clean build artifacts
- `test`: Run system tests

## Voice-First Pipeline

### Expected Behavior After Proper Startup

1. **Immediate Voice Input**: Native audio capture should work
2. **Speech Transcription**: Whisper service processes voice input
3. **Chat Functionality**: "Create Session" creates new chat sessions
4. **AI Response**: LLM service provides intelligent responses

### Voice Pipeline Flow
```
Native Audio (arecord) → HTTP → Whisper Service (1191) → Chat Service (9095) → LLM Service (1500) → Response
```

## Troubleshooting

### "Cannot invoke RPC on closed channel!" Error

**Cause**: Chat service not running on port 9095
**Solution**:
```bash
./venv-production/bin/python services/chat-with-sessions/minimal_grpc_server.py &
ss -tln | grep 9095  # Verify it's running
```

### "Service chat unavailable, retrying..." Error

**Cause**: gRPC service discovery issue
**Solution**:
1. Verify chat service is running: `ss -tln | grep 9095`
2. Check service registry: `python3 control/service_launcher.py --status`
3. Restart chat service if needed

### Platform Handler Not Responding

**Cause**: Recursive command execution or missing dependencies
**Solution**: Platform Handler now uses `control/service_launcher.py` instead of `./unhinged start`

### Docker Services Unhealthy

**Cause**: Services still starting up or configuration issues
**Solution**:
```bash
# Check container status
docker ps

# Check container logs
docker logs ollama-service
docker logs speech-to-text-service

# Restart if needed
docker compose -f build/orchestration/docker-compose.production.yml restart
```

## Development Workflow

### Recommended Startup Order for Development

1. **Terminal 1**: Start Docker services
   ```bash
   docker compose -f build/orchestration/docker-compose.production.yml up
   ```

2. **Terminal 2**: Start chat service
   ```bash
   ./venv-production/bin/python services/chat-with-sessions/minimal_grpc_server.py
   ```

3. **Terminal 3**: Launch GUI
   ```bash
   ./unhinged
   ```

### Testing Service Functionality

```bash
# Test chat service gRPC endpoint
python3 -c "
import grpc
channel = grpc.insecure_channel('localhost:9095')
print('Chat service accessible:', channel.get_state())
"

# Test LLM service HTTP endpoint
curl -f http://localhost:1500/api/tags

# Test complete service status
python3 control/service_launcher.py --status
```

## Integration with GUI

### Expected GUI Behavior After Fixes

1. **Status Tab**: 
   - Platform Launcher button works
   - Logs display without AttributeError
   - Service status updates properly

2. **OS Chatroom Tab**:
   - "Create Session" button creates new sessions
   - Chat messages send and receive properly
   - Voice transcription integrates with chat

3. **Voice Pipeline**:
   - Microphone activation works immediately
   - Speech-to-text transcription appears in chat input
   - Voice-first interaction is seamless

The service startup issues have been systematically addressed with proper error handling, correct service startup sequence, and comprehensive troubleshooting guidance.
