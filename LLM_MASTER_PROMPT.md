# UNHINGED REPOSITORY - MASTER LLM PROMPT
# ============================================================================
# CRITICAL: READ THIS BEFORE MAKING ANY CHANGES TO THE CODEBASE
# ============================================================================
#
# @llm-type quickstart
# @llm-legend Master guidance for LLM agents working in the Unhinged voice-first AI control center
# @llm-key Prevents file creation chaos and enforces voice-first architectural patterns
# @llm-map Entry point for LLM agents to understand voice-first GUI and service architecture
# @llm-axiom All LLM agents must read and follow these patterns before making changes
# @llm-contract Provides comprehensive guidance on voice-first development, native GUI, and service integration
# @llm-token llm-master-prompt: Essential guidance for AI agents working in voice-first Unhinged codebase

## Voice-First Architecture - Core Mission

### Primary Objective: Immediate Voice Interaction
- **`make start` → IMMEDIATE VOICE INPUT** - User can interact via voice immediately
- **NATIVE AUDIO CAPTURE** - Ubuntu system audio (arecord/PipeWire), avoiding Python audio libraries
- **AUTO-STARTING SERVICES** - Whisper transcription service initializes automatically
- **ZERO SETUP FRICTION** - Voice functionality available immediately after system initialization

### Voice Pipeline Architecture
```
Native Audio (arecord) → HTTP → Whisper Service → AI Response
```

### Dual-System Evolution Architecture
```
Ubuntu Host (GTK4 Control Plane) → manages → Alpine VM (Native C Graphics)
```
- **Host System**: GTK4 desktop application for control and monitoring
- **Guest System**: Headless Alpine VM with native C graphics and CLI
- **Evolution Path**: Current dual-system architecture transitioning to standalone Unhinged OS

## Critical Architecture Principles - Compliance Required

### 1. Voice-First Independence
- **NATIVE AUDIO OVER LIBRARIES** - Utilize OS capabilities rather than PyAudio/sounddevice
- **IMMEDIATE FUNCTIONALITY** - Voice functionality must be available immediately upon system startup
- **SERVICE INTEGRATION** - Auto-starting services via service_launcher.py
- **CLEAN STARTUP** - Zero theme errors, minimal console output

### 2. Native GUI Architecture
- **NATIVE C GRAPHICS RENDERING** - Avoid web browsers, Electron, and GTK dependencies
- **MOBILE-RESPONSIVE DESIGN** - Touch-friendly native interface design
- **SYSTEM INTEGRATION** - Leverage native OS capabilities over abstractions
- **PROFESSIONAL UX** - Maintain clean startup and clear user feedback

### 3. Centralized Build Philosophy
- **UNIFIED BUILD SYSTEM** - All build operations utilize `/build/` directory
- **CENTRALIZED PYTHON ENVIRONMENT** - Use `build/python/venv/` for all Python operations
- **CONSOLIDATED TOOLING** - Avoid scattered build tools (gradle wrappers, npm in arbitrary locations)
- **ORGANIZED GENERATED CONTENT** - All generated artifacts stored in `/generated/`

### 4. Documentation Standards
- **LLM-DOCS COMPLIANCE** - All files utilize @llm-type, @llm-legend, @llm-key patterns
- **VOICE ARCHITECTURE CONTEXT** - Document voice pipeline positioning and integration
- **SERVICE INTEGRATION DOCUMENTATION** - Provide clear service startup and health monitoring procedures
- **USER EXPERIENCE FOCUS** - Document immediate voice functionality requirements

### 5. Voice-First Validation Requirements
- **VOICE PIPELINE TESTING** - Conduct comprehensive end-to-end voice functionality testing
- **SERVICE AUTO-START** - Verify services initialize properly with `make start`
- **CLEAN STARTUP** - Ensure zero theme errors and professional user experience
- **IMMEDIATE INTERACTION** - Voice functionality must operate without additional setup

## Directory Structure - Architectural Boundaries

```
/
├── libs/                       # CORE LIBRARIES
│   ├── graphics/              # Native C graphics rendering library
│   │   ├── src/               # C graphics source code
│   │   ├── examples/          # Graphics examples and tests
│   │   └── build/             # Compiled graphics library
│   ├── event-framework/       # Structured logging and events
│   │   └── python/src/unhinged_events/ # Event logging with GUI session support
│   └── service-framework/     # Service communication patterns
├── control/service_launcher.py # SERVICE ORCHESTRATION (auto-start)
├── services/speech-to-text/    # WHISPER TRANSCRIPTION SERVICE
├── build/                      # CENTRALIZED BUILD SYSTEM (Python-based)
│   ├── python/                # Centralized Python environment
│   │   ├── run.py            # Universal Python runner (USE THIS!)
│   │   ├── requirements.txt  # Consolidated dependencies
│   │   └── venv/            # Centralized virtual environment
│   ├── modules/        # Language-specific builders
│   │   ├── dual_system_builder.py # Dual-system packaging
│   │   └── c_builder.py      # C graphics build module
│   ├── docs-generation/# Documentation automation (USE THIS!)
│   └── tools/          # Build utilities
├── control/            # SYSTEM CONTROL & GUI
│   ├── native_c_launcher.py  # Native C graphics launcher
│   ├── conversation_cli.py   # Voice-first CLI interface
│   ├── gtk4_gui/            # GTK4 desktop application components
│   ├── qemu_vm_launcher.py   # VM management and communication
│   ├── service_launcher.py   # Service orchestration
│   ├── static_html/    # HTML interfaces (for native rendering)
│   └── system/         # System control abstractions
├── generated/          # ALL GENERATED CONTENT (EVERYTHING GOES HERE)
│   ├── typescript/     # Generated TS clients
│   ├── python/         # Generated Python clients
│   ├── static_html/    # Generated HTML assets
│   └── reports/        # Build reports and analysis
├── proto/              # Protocol buffer definitions
├── services/           # Microservices (Python AI services)
├── platforms/          # Platform services (Kotlin persistence)
├── desktop/            # DESKTOP INTEGRATION
│   ├── unhinged-desktop-app  # Ubuntu GNOME desktop app (GTK4)
│   ├── auto_updater.py      # Automatic update system
│   ├── version.json         # Version management
│   └── unhinged.desktop     # Desktop entry
├── vm/                 # VIRTUAL MACHINE COMPONENTS
│   ├── alpine/              # Alpine Linux VM configuration
│   ├── test-*.py           # VM communication tests
│   └── shared/             # VM-host shared resources
├── docs/               # DOCUMENTATION (USE THIS, NOT READMES!)
├── llm/                # LLM-specific content
│   └── quickstart/     # LLM agent guidance (THIS FILE!)
└── README.md           # ONLY README - entry point to /docs/
```

## Build System Patterns

### Python Operations
```bash
# CORRECT: Use centralized Python
python3 build/python/run.py script.py

# WRONG: Random Python environments
cd some_dir && python script.py
```

### File Generation
```bash
# CORRECT: Generate to proper location
python3 build/build.py build proto-clients-all
# Output: generated/typescript/clients/

# WRONG: Generate anywhere else
protoc --js_out=frontend/src/generated/
```

### Build Commands
```bash
# CORRECT: Use build system
make build              # Fast development build
make generate          # Generate all artifacts
python3 build/build.py build dev-fast

# WRONG: Direct tool invocation
cd backend && ./gradlew build
cd frontend && npm run build
```

## Prohibited Patterns

### File Creation Anti-Patterns
- ❌ Creating files in repository root
- ❌ Creating `.backup` or `.old` files
- ❌ Creating `demo_*` or `test_*` files in root
- ❌ Creating temporary scripts outside `/build/`
- ❌ Creating package.json files outside designated areas

### Build Anti-Patterns
- ❌ Using external browsers for GUI
- ❌ Installing npm packages globally
- ❌ Creating gradle wrapper scripts
- ❌ Using system package managers for build deps
- ❌ Creating Docker files outside service directories

### Code Anti-Patterns
- ❌ Hardcoded paths that don't respect build structure
- ❌ Direct tool invocation bypassing build system
- ❌ Creating services without proper proto definitions
- ❌ Bypassing the centralized Python environment

## Required Patterns

### Before Making Changes
1. **Check build system** - Use `make status` to understand current state
2. **Use centralized tools** - All Python through `build/python/`
3. **Generate properly** - All generated content to `/generated/`
4. **Test build** - Run `make build` to verify changes

### File Creation Rules
1. **Generated content** → `/generated/`
2. **Build scripts** → `/build/`
3. **Documentation** → `/docs/`
4. **Services** → `/services/` or `/platforms/`
5. **Control logic** → `/control/`

### Build Integration
1. **Add to build-config.yml** if creating new build targets
2. **Update .gitignore** for new generated content
3. **Use build modules** for language-specific operations
4. **Cache appropriately** using build system caching

## 🔧 COMMON OPERATIONS

### Adding a New Service
```bash
# 1. Create service directory
mkdir services/new-service

# 2. Add proto definition
vim proto/new_service.proto

# 3. Generate clients
make generate-clients

# 4. Update build config
vim build-config.yml
```

### Adding Build Functionality
```bash
# 1. Create build module
vim build/modules/new_builder.py

# 2. Register in orchestrator
vim build/orchestrator.py

# 3. Add to config
vim build-config.yml

# 4. Test
python3 build/build.py build new-target
```

## Success Criteria

### For LLM Agents
- [ ] No files created in repository root
- [ ] All Python operations use centralized environment
- [ ] All generated content goes to `/generated/`
- [ ] Build system integration for new functionality
- [ ] Proper .gitignore updates for new content
- [ ] Documentation updates for new patterns

### For Build System
- [ ] Single command builds (`make build`)
- [ ] Proper caching and incremental builds
- [ ] Clear error messages and recovery
- [ ] Independence from external tools
- [ ] Reproducible across environments

## Emergency Procedures

### Architecture Violation Response
1. **HALT OPERATIONS** - Avoid compounding architectural violations
2. **REMEDIATION** - Remove any files created in incorrect locations
3. **COMPLIANCE RESTORATION** - Follow established architectural patterns
4. **VALIDATION** - Ensure build system functionality remains intact

### If Build System Breaks
1. **Check status** - `make status` and `python3 build/build.py status`
2. **Clean and rebuild** - `make clean && make build`
3. **Check dependencies** - Ensure centralized Python env is intact
4. **Consult documentation** - Check `/build/README.md`

## Reference Documentation

- `/build/README.md` - Build system overview
- `/build/TODO.md` - Build system roadmap
- `Makefile` - Available commands and patterns
- `build-config.yml` - Build targets and configuration
- `.gitignore` - Repository inclusion and exclusion patterns

---

**ARCHITECTURAL PRINCIPLE: This system maintains complete independence. External dependencies are minimized. All components are built internally. System autonomy is preserved.**
