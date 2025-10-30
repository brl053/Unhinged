# Unhinged

> **Voice-First AI Control Center** - Native C graphics desktop application with immediate voice interaction

## Quick Start - Voice-First Experience

```bash
./unhinged
```

**Launches native C graphics GUI with immediate voice capability** - activate the microphone and begin voice interaction.

### Normal User proc(Toyota Experience)
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
│   ├── gtk4_gui/                # Modular GTK4 + Libadwaita interface
│   │   ├── handlers/            # Business logic layer (audio, platform)
│   │   ├── views/               # UI component layer (7 modular views)
│   │   ├── components/          # Reusable UI primitives
│   │   └── desktop_app.py       # Clean orchestrator (1,818 lines ← 3,666)
│   ├── native_c_launcher.py     # Native C graphics launcher
│   └── service_launcher.py      # Service orchestration
├── services/                    # AI services (auto-starting)
│   ├── speech-to-text/          # Whisper-based transcription
│   ├── text-to-speech/          # Audio generation
│   └── vision-ai/               # Image analysis
├── build/                       # Polyglot build system
└── docs/                        # LlmDocs-annotated documentation
```

### Architectural Principles (Proven in GUI Refactoring)

**🏗️ Modular Architecture**: Break monolithic components into focused, single-responsibility modules
- **Handler Pattern**: Business logic separated from UI (audio_handler.py, platform_handler.py)
- **View Pattern**: UI components with clear boundaries (7 extracted views)
- **Component Pattern**: Reusable primitives for consistent UX

**🔄 Callback-Driven Design**: Modern event-driven patterns over tight coupling
- **Loose Coupling**: Components communicate through well-defined interfaces
- **Event-Driven**: State changes propagate through callback mechanisms
- **Testable**: Each component can be tested in isolation

## Core Features

- **Voice-First Interface**: Native audio → Whisper → AI chat
- **Modular Architecture**: Handler-based business logic, view-based UI components
- **Mobile-Responsive GUI**: Touch-friendly native interface with clean separation
- **Design System**: Two-tier semantic token architecture with GTK4 CSS generation
- **Developer Tools**: API testing, service monitoring, logs
- **System Monitoring**: Real-time system and service status
- **Vision Integration**: Camera capture and AI analysis
- **Input Monitoring**: Keyboard/mouse capture for automation

## Engineering Excellence

**🎯 50% Code Reduction Achieved**: Transformed 3,666-line monolith → 1,818-line orchestrator
- **Maintainable**: Each component has single responsibility
- **Testable**: Components can be tested in isolation
- **Scalable**: Easy to add features without architectural debt
- **Modern**: Callback-driven, event-based patterns throughout

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
