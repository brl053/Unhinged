# 🚀 Unhinged Development Guide

## 🎯 Quick Start for Development

### **Frontend Development (Webpack Dev Server)**
```bash
cd frontend
npm install
npm run dev
```
- **URL**: http://localhost:3000
- **Hot Reload**: ✅ Enabled
- **TTS/STT**: ✅ Ready for testing

### **Backend Services (Docker)**
```bash
# Start only backend services (NO frontend container)
docker compose up backend whisper-tts llm database -d

# Or use the backend-only profile
docker compose --profile backend up -d
```

## 🏗️ Architecture

### **Development Setup**
- **Frontend**: Webpack dev server (`npm run dev`)
- **Backend**: Docker containers for services
- **Database**: PostgreSQL via Docker
- **LLM**: Ollama via Docker  
- **TTS/STT**: Whisper service via Docker

### **Service Ports**
- **Frontend**: http://localhost:3000 (webpack dev server)
- **Backend API**: http://localhost:8080 (Docker)
- **Whisper TTS**: http://localhost:8000 (Docker)
- **LLM Service**: http://localhost:11434 (Docker)
- **Database**: localhost:5432 (Docker)

## 🎤 Testing TTS/STT Features

1. **Start backend services**: `docker compose up backend whisper-tts llm database -d`
2. **Start frontend**: `cd frontend && npm run dev`
3. **Open browser**: http://localhost:3000
4. **Look for**: 
   - 🎤 Microphone button for voice input
   - 🔊 TTS toggle button
   - Red banner confirming webpack dev server

## 🚫 Common Issues

### **"Port 3000 already in use"**
```bash
# Stop any Docker frontend containers
docker stop frontend-service frontend-dev-service
docker rm frontend-service frontend-dev-service
```

### **Changes not showing in browser**
- Hard refresh: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
- Check browser console for errors
- Verify webpack dev server is running

### **API calls failing**
- Ensure backend services are running: `docker compose ps`
- Check service health: `curl http://localhost:8080/health`

## 📁 Docker Compose Files

- **`docker-compose.yml`**: Production (includes frontend container with profile)
- **`docker-compose.dev.yml`**: Development (includes frontend container - NOT recommended)
- **`docker-compose.prod.yml`**: Production optimized
- **`docker-compose.staging.yml`**: Staging environment

## ⚡ Hot Reload Confirmation

If webpack dev server is working, you should see:
- **Browser title**: "🎤 WEBPACK DEV SERVER RUNNING - TTS/STT READY! 🔊"
- **Red banner** in the chat interface
- **Console logs** showing hot module replacement

## 🎯 TTS/STT Implementation Status

- ✅ **Speech-to-Text**: Voice input component with Whisper integration
- ✅ **Text-to-Speech**: Audio synthesis with gTTS integration  
- ✅ **UI Components**: Voice input button, TTS toggle, audio visualization
- ✅ **Backend Services**: Kotlin TTS service, Python Whisper service
- ✅ **Hot Reload**: Webpack dev server with live updates
