# Unhinged

> **Voice-First AI Control Center** - Native C graphics desktop application with immediate voice interaction

## Quick Start - Voice-First Experience

```bash
make start
```

**Launches native C graphics GUI with immediate voice capability** - activate the microphone and begin voice interaction.

## Voice-First User Experience

- **Native Audio Capture**: Ubuntu system-level audio (no Python libraries)
- **Whisper Integration**: Auto-starting speech-to-text service
- **Immediate Interaction**: Zero setup required - voice functionality available immediately
- **AI Chat Integration**: Voice → transcription → AI response pipeline

## Architecture Overview

```
📦 Unhinged/
├── libs/graphics/               # Native C graphics rendering library
│   ├── src/                     # C graphics source code
│   ├── examples/                # Hello world and demos
│   └── include/                 # Graphics API headers
├── control/native_c_launcher.py # Native C graphics launcher
├── services/                    # AI services (auto-starting)
│   ├── speech-to-text/          # Whisper-based transcription
│   ├── text-to-speech/          # Audio generation
│   └── vision-ai/               # Image analysis
├── control/service_launcher.py  # Service orchestration
├── build/                       # Polyglot build system
└── docs/                        # LlmDocs-annotated documentation
```

## Core Features

- **Voice-First Interface**: Native audio → Whisper → AI chat
- **Mobile-Responsive GUI**: Touch-friendly native interface
- **Developer Tools**: API testing, service monitoring, logs
- **System Monitoring**: Real-time system and service status
- **Vision Integration**: Camera capture and AI analysis
- **Input Monitoring**: Keyboard/mouse capture for automation

## Documentation

- **For Developers**: See `/docs/` for comprehensive LlmDocs-annotated documentation
- **For LLM Agents**: Start with `/LLM_MASTER_PROMPT.md` before making any changes

## System Status

System components are in various stages of implementation. The health dashboard provides current operational status.

## For Developers

Comprehensive documentation available in `/docs/` directory.

## Available Commands

```bash
make start               # Initialize all system components
make clean               # Clean build artifacts and temporary files
```

---

Additional technical documentation and implementation details are available in the `/docs/` directory.
