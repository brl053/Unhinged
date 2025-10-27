# Unhinged

> **Voice-First AI Control Center** - Native C graphics desktop application with immediate voice interaction

## Quick Start - Voice-First Experience

```bash
./unhinged
```

**Launches native C graphics GUI with immediate voice capability** - activate the microphone and begin voice interaction.

### Normal User (Toyota Experience)
- Single command: `./unhinged`
- Desktop icon integration
- All complexity hidden

### Power User (Car Enthusiast Experience)
- Development mode: `./unhinged dev`
- Component control: `./unhinged graphics build`
- System administration: `./unhinged admin services`

## Voice-First User Experience

- **Native Audio Capture**: Ubuntu system-level audio (no Python libraries)
- **Whisper Integration**: Auto-starting speech-to-text service
- **Immediate Interaction**: Zero setup required - voice functionality available immediately
- **AI Chat Integration**: Voice → transcription → AI response pipeline

## Architecture Overview

```
📦 Unhinged/
├── libs/
│   ├── graphics/                # Native C graphics rendering library
│   │   ├── src/                 # C graphics source code
│   │   ├── examples/            # Hello world and demos
│   │   └── include/             # Graphics API headers
│   └── design_system/           # Two-tier design system architecture
│       ├── tokens/              # Semantic design tokens (YAML)
│       ├── build/               # Platform generators (GTK4, etc.)
│       └── generated/           # Generated CSS and styling
├── control/                     # Desktop application
│   ├── native_gui/              # GTK4 + Libadwaita interface
│   ├── native_c_launcher.py     # Native C graphics launcher
│   └── service_launcher.py      # Service orchestration
├── services/                    # AI services (auto-starting)
│   ├── speech-to-text/          # Whisper-based transcription
│   ├── text-to-speech/          # Audio generation
│   └── vision-ai/               # Image analysis
├── build/                       # Polyglot build system
└── docs/                        # LlmDocs-annotated documentation
```

## Core Features

- **Voice-First Interface**: Native audio → Whisper → AI chat
- **Mobile-Responsive GUI**: Touch-friendly native interface
- **Design System**: Two-tier semantic token architecture with GTK4 CSS generation
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
# Normal User Commands
./unhinged                    # Start complete system
./unhinged stop               # Graceful shutdown

# Power User Commands
./unhinged dev                # Development mode
./unhinged graphics build     # Build graphics subsystem
./unhinged build generate     # Generate design artifacts
./unhinged admin services     # Manage services
./unhinged debug status       # Debug system state

# Legacy Commands (deprecated)
make start               # Use './unhinged' instead
make clean               # Use './unhinged build clean' instead
```

---

Additional technical documentation and implementation details are available in the `/docs/` directory.
