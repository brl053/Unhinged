# Unhinged Dual-System Evolution Architecture

## Overview

Unhinged operates under a **dual-system evolution strategy** during the transition phase where the Unhinged OS is gaining independence from the parent Ubuntu host system.

## System Architecture

### Current Evolution State
```
Parent Host System: Ubuntu GNU/Linux + GTK4 Control Plane
    ↓ (manages and monitors)
Guest Unhinged System: Headless Alpine + QEMU VM + Unhinged Native Graphics CLI
```

**Evolution Path:**
```
Current: QEMU VM + Alpine Kernel + Unhinged CLI
    ↓
Future:  Standalone Unhinged OS
```

## Dual-System Components

### 1. Parent Host System (Ubuntu)
- **Role**: Control plane renderer and service orchestrator
- **Technology**: GTK4/Libadwaita desktop application
- **Responsibilities**:
  - Monitor and manage headless Alpine VM
  - Provide visual interface for system status
  - Coordinate Docker-based services (virtualized namespace abstractions)
  - Session logging and diagnostics
  - Voice pipeline integration (arecord → Whisper → AI)

### 2. Guest Unhinged System (Alpine VM)
- **Role**: Native Unhinged OS environment
- **Technology**: Native C graphics with DRM framebuffer
- **Responsibilities**:
  - Conversation-based CLI interface
  - Direct hardware access through DRM
  - Native Unhinged service execution
  - Voice-first interaction processing

## Architectural Decisions

### GTK4 Control Plane Preservation
The existing GTK4 desktop application is **intentionally preserved** as the control plane renderer for the parent Ubuntu host system. This is not a violation of the "NO GTK" principle but rather an architectural decision during the transition phase.

**Rationale:**
- Provides stable control interface during OS evolution
- Enables monitoring of headless Alpine VM
- Maintains compatibility with existing Ubuntu infrastructure
- Facilitates debugging and development workflow

### Native C Graphics Hard Requirement
Native C graphics compilation is a **HARD REQUIREMENT** for the dual-system architecture:

- **DRM Headers**: Required for framebuffer access
- **libdrm**: Essential for direct hardware rendering
- **Compilation Test**: Must pass before system proceeds
- **Hard Fail**: System cannot operate without functional native graphics

## Feature Parity Requirement

Both GUI systems must maintain **critical feature parity**:

### GTK4 Control Plane Features
- System status monitoring
- Service management
- Session logging visualization
- Voice pipeline control
- VM management interface

### Native C Graphics Features
- Conversation-based CLI
- Direct voice interaction
- Hardware-accelerated rendering
- Low-level system access
- Real-time performance

## Implementation Guidelines

### 1. Abstraction Layer Respect
- Maintain clean separation between host and guest systems
- Design features to work seamlessly across both environments
- Respect the in-vitro nature of the current Unhinged OS (CLI-based window)

### 2. Voice-First Integration
- Both systems must integrate with voice pipeline
- Conversation interface accessible from both GTK4 and Alpine
- Immediate voice interaction capability required

### 3. Session Logging
- Centralized logging system captures events from both systems
- Enhanced diagnostics for graphics build failures
- Comprehensive error reporting and noise reduction

## Service Integration

### Docker-Based Services (Transition Phase)
Current services operate as **virtualized namespace abstractions** until native Unhinged services are ready:
- Speech-to-text service (port 1101)
- AI processing pipeline
- System monitoring services

### Native Unhinged Services (Future)
Target architecture for standalone Unhinged OS:
- Direct hardware service access
- Native process management
- Integrated voice processing
- Real-time system interaction

## Development Workflow

### Build Requirements
1. **Native C Graphics**: Must compile successfully (hard fail requirement)
2. **GTK4 Control Plane**: Must integrate with existing services
3. **Alpine VM**: Must provide functional CLI environment
4. **Voice Pipeline**: Must work across both systems

### Testing Strategy
- Feature parity validation between systems
- Voice interaction testing in both environments
- Graphics rendering verification
- Session logging accuracy

## Future Evolution

### Phase 1: Current (Dual-System)
- GTK4 control plane managing Alpine VM
- Native C graphics foundation established
- Conversation CLI implemented
- Voice pipeline integrated

### Phase 2: Transition
- Gradual migration of services to native Unhinged
- Reduced dependency on Ubuntu host
- Enhanced native graphics capabilities
- Improved voice-first interaction

### Phase 3: Standalone
- Full Unhinged OS independence
- Native service ecosystem
- Direct hardware management
- Complete voice-first architecture

## Technical Specifications

### Graphics Requirements
- **DRM Support**: Direct Rendering Manager access
- **Framebuffer**: Hardware framebuffer manipulation
- **SIMD**: AVX2/NEON optimization support
- **Memory Management**: Custom allocators for performance

### Voice Pipeline
- **Input**: arecord audio capture
- **Processing**: Whisper speech-to-text
- **AI**: Large language model integration
- **Output**: Both visual and audio feedback

### Session Management
- **Logging**: Centralized event framework
- **Diagnostics**: Detailed error reporting
- **Monitoring**: Real-time system status
- **Recovery**: Graceful failure handling

---

**Author**: Unhinged Development Team  
**Version**: 1.0.0  
**Date**: 2025-10-26  
**Status**: Active Development
