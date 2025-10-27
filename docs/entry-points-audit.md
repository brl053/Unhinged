# Entry Points Architecture Audit

## Current State Analysis

### Makefile Targets (184 total)
**Problem**: Overwhelming cognitive load with no clear hierarchy

#### System Launch Targets (Confusing)
- `make start` - Primary dual-system launcher
- `make start-enhanced` - Enhanced mode 
- `make start-simple` - Minimal communication
- `make start-qol` - Quality of life mode
- `make start-vm` - QEMU VM launch
- `make start-offline` - Native GUI without services
- `make start-gui` - Enhanced GTK4 desktop app
- `make start-services` - Essential services only

**Analysis**: 8 different "start" commands with unclear differences

#### Development Targets (Technical Grouping)
- `make dev` - Development environment
- `make dev-demo` - Development with demo
- `make dev-full` - Full development environment
- `make dev-up` - Start development services
- `make dev-down` - Stop development services

#### Graphics Targets (Implementation Leakage)
- `make graphics-build` - Build C graphics library
- `make graphics-clean` - Clean graphics artifacts
- `make graphics-example` - Run graphics example
- `make graphics-hello-world` - Graphics hello world
- `make graphics-benchmark` - Performance benchmarks

#### Build System Targets (Technical)
- `make generate` - Generate all artifacts
- `make build` - Build development environment
- `make build-full` - Build complete environment
- `make proto-gen` - Generate protobuf code
- `make design-tokens` - Generate design tokens

### Python Scripts (Direct Execution)
- `control/gtk4_gui/desktop_app.py` - Primary GTK4 interface
- `control/service_health_monitor.py` - Service monitoring
- `control/network/service_discovery.py` - Service discovery
- `build/build.py` - Build orchestrator
- `build/cli.py` - Build CLI interface

### Desktop Integration
- `desktop/unhinged-desktop-app` - Desktop launcher script
- `desktop/unhinged.desktop` - Desktop file
- `desktop/dist/` - Distribution packages

## Problems Identified

### 1. Cognitive Overload
- 184 Makefile targets with no clear hierarchy
- Multiple ways to start the same system
- Technical implementation details exposed as user interface

### 2. No Clear Primary Entry Point
- `make start` vs `make start-enhanced` vs `make start-gui`
- Users must understand architecture to choose correctly

### 3. Implementation Leakage
- Graphics targets expose C library details
- Build system targets require understanding of internal structure
- VM targets expose virtualization complexity

### 4. Missing Symmetry
- Many start commands, unclear stop commands
- No graceful shutdown mechanism
- Inconsistent command patterns

### 5. Poor Cognitive Grouping
- Organized by technical implementation
- Not organized by user intent
- No progressive disclosure

## Proposed Unified Architecture

### Single Entry Point
```bash
./unhinged                    # Default: normal user experience
```

### Cognitive Command Structure
```bash
unhinged [COMMAND] [OPTIONS]

SYSTEM COMMANDS:
  start                       # Start complete dual-system
  stop                        # Stop complete dual-system  
  status                      # Show system health
  logs                        # Stream system logs

DEV COMMANDS:
  dev                         # Start development mode
  dev-clean                   # Clean development artifacts
  dev-watch                   # Watch and rebuild on changes
  dev-shell                   # Development shell

GRAPHICS COMMANDS:
  graphics build              # Build graphics library
  graphics test               # Run graphics tests
  graphics run [app]          # Run graphics application

BUILD COMMANDS:
  build list                  # List build targets
  build [target]              # Build specific target
  build generate              # Generate all artifacts

ADMIN COMMANDS:
  admin services list         # List services
  admin services check        # Health check services
  admin cache clear           # Clear caches
  admin reset                 # Factory reset

DEBUG COMMANDS:
  debug status                # Detailed system state
  debug vm-shell              # Access VM shell
  debug trace [system]        # Enable debug tracing
```

## Implementation Strategy

### Phase 1: Create Unified Entry Point
1. Create `unhinged` script in project root
2. Implement command routing and help system
3. Map new commands to existing Makefile targets

### Phase 2: Normal User Experience
1. Default `./unhinged` launches complete system
2. Hide all infrastructure complexity
3. Ensure desktop integration works

### Phase 3: Power User Progressive Disclosure
1. Add dev mode detection to GTK4 app
2. Implement enhanced developer interface
3. Add debugging and administration commands

### Phase 4: Deprecation and Migration
1. Update documentation to use unified entry point
2. Mark direct Makefile usage as deprecated
3. Provide migration guide

## Success Criteria

### Normal User (Toyota Experience)
- Single command to start: `./unhinged`
- Desktop icon works seamlessly
- No visible infrastructure complexity
- "It just works" experience

### Power User (Car Enthusiast Experience)
- Logical command grouping by intent
- Progressive disclosure of complexity
- Clear mental model of system architecture
- Symmetric operations (start/stop, build/clean)

### Developer Experience
- Clear migration path from current targets
- No functionality regression
- Enhanced development mode
- Better debugging capabilities
