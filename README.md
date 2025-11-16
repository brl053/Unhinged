# Unhinged

> 

    God chose me from all programmers to make His temple. He gave me divine intellect. I wrote all 120,000 lines of code in TempleOS from scratch -- x86_64 kernel, 64-bit compiler, assembler, editor, graphics library, flight simulator, first person shooter, tools like grep and merge.

    I am the best programmer.

    No. I specialized in programming before the Internet. I do not want to dilute my microcontroller assembly skills with Internet skills.

    I have been paid to program in VAX, 8086, 68000, 8051, PIC and Avr assembly on bare metal.

    My first job was working on Ticketmaster's VAX operating system.

    TempleOS is what I am trained for.

- Terry Andrew Davis

### Thank you to...
- Terry Andrew Davis
- Aaron Schwartz
- Fredrik Neij
- Peter Sunde
- Gottfrid Svartholm
- Mike Mentzer
- Ray Mentzer
- Tom Platz
- Gregg Doucette
- Alan Turing
- AMD 
- Threads
- IG Reels
- PewDiePie

### Big "fuck you" to...
- Linus Torvald (<3)
- Sam Altman
- Arnold Schwarzenegger
- Elon Musk
- OpenAI
- ChatGPT
- Meta
- Jensen Huang
- Bill Gates
- Microsoft
- Windows
- Intel
- Apple
- Google
- Facebook
- Twitter
- Instagram
- Tiktok

---




> **Voice-First AI Control Center** - Native C graphics desktop application with immediate voice interaction

## Python Environment

**Single Source of Truth**: `build/python/venv/`

All Python dependencies are consolidated in one unified virtual environment located at `build/python/venv/`. This is the only Python environment used by:
- GTK4 desktop application
- All backend services
- Build and development tools

See `build/requirements-unified.txt` for the complete dependency list.

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
- **For Autonomous Development**: See `docs/AUTONOMOUS_LOOP_GUIDE.md` for the LLM agent development loop

## Autonomous Development Loop

LLM agents (like Augment) can autonomously develop and test the system using the structured development loop:

```python
from build.development_loop import DevelopmentLoop

loop = DevelopmentLoop()
task = loop.create_task(...)
loop.start_task(task)
result = loop.execute_shell_command(...)
loop.complete_task(task, result)
```

All tasks and results are logged to `/build/tmp/` for feedback and iteration.

See `docs/AUTONOMOUS_LOOP_GUIDE.md` for complete documentation.

## System Status

System components are in various stages of implementation. The health dashboard provides current operational status.

## For Developers

Comprehensive documentation available in `/docs/` directory.

## Available Commands

```bash
# Normal User Commands
./unhinged                    # Start services + launch GUI (default)
./unhinged system gui         # Launch GUI only
./unhinged system start       # Start services only
./unhinged system stop        # Graceful shutdown
./unhinged system status      # Check system health
./unhinged system restart     # Restart system

# Development Commands
./unhinged dev lint           # Run linting
./unhinged dev static-analysis # Run static analysis
./unhinged dev build          # Build project

# Admin Commands
./unhinged admin services list    # List running services
./unhinged admin services health  # Check service health
./unhinged admin preflight check  # Run preflight checks
./unhinged admin debug status     # Show system state

# VM Commands
./unhinged vm win10           # Launch Windows 10 VM
./unhinged vm templeos        # Launch TempleOS VM
./unhinged vm stop            # Stop running VM
```

---

Additional technical documentation and implementation details are available in the `/docs/` directory.
