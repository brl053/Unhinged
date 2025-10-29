# UnhingedOS Build System

## 🎯 Overview

The UnhingedOS build system transforms source components into bootable operating system images through a systematic, profile-based approach. It supports multiple OS variants optimized for different use cases while maintaining reproducible, deterministic builds.

## 🏗️ Build Architecture

### Build Pipeline
```
Source Components → Profile Selection → Alpine Customization → ISO Generation → VM Image
       ↓                   ↓                    ↓                   ↓             ↓
   os/ directory    build/profiles/    Package Selection    Bootable ISO    QCOW2 Image
```

### Directory Structure
```
vm/
├── os/                          # UnhingedOS source components
│   ├── alpine-base/            # Base Alpine Linux components
│   ├── unhinged-layer/         # UnhingedOS-specific layer
│   ├── boot-system/            # Boot and init system
│   └── graphics-stack/         # Native graphics system
├── build/                      # Build system tools
│   ├── unhinged-os-builder.sh  # Master OS builder
│   ├── os-configurator.sh      # OS configuration script
│   └── profiles/               # Build profiles
│       ├── minimal.sh          # Minimal voice-first OS
│       ├── desktop.sh          # Full desktop environment
│       ├── server.sh           # Headless server variant
│       └── dev.sh              # Development environment
├── runtime/                    # Build artifacts
│   ├── images/                 # VM disk images (.qcow2)
│   ├── isos/                   # Bootable ISOs
│   └── shared/                 # Host-VM communication
└── testing/                    # Testing framework
    ├── boot-tests/             # Boot sequence validation
    ├── graphics-tests/         # Graphics system testing
    └── integration-tests/      # Full system testing
```

## 📦 Build Profiles

### Minimal Profile (64MB RAM)
**Purpose:** Core voice-first interface with minimal resource usage
```bash
make unhinged-os-minimal
```
**Components:**
- Alpine Linux base (32MB)
- Voice interface engine (16MB)
- Basic graphics stack (16MB)
- Essential services only

**Use Cases:**
- Embedded systems
- IoT devices
- Resource-constrained environments
- Voice-only interfaces

### Desktop Profile (256MB RAM)
**Purpose:** Full voice-first desktop environment
```bash
make unhinged-os-desktop
```
**Components:**
- Complete voice interface (64MB)
- Full graphics stack with compositing (128MB)
- Desktop services and utilities (64MB)
- Multi-application support

**Use Cases:**
- Primary desktop replacement
- Voice-controlled workstations
- Accessibility-focused computing
- Demonstration systems

### Server Profile (128MB RAM)
**Purpose:** Headless voice processing server
```bash
make unhinged-os-server
```
**Components:**
- Voice processing engine (96MB)
- Network services (16MB)
- Minimal graphics (16MB)
- Server utilities

**Use Cases:**
- Voice processing backend
- API server for voice services
- Distributed voice computing
- Cloud deployments

### Development Profile (512MB RAM)
**Purpose:** Full development environment with debugging tools
```bash
make unhinged-os-dev
```
**Components:**
- Complete OS stack (256MB)
- Development tools (128MB)
- Debugging utilities (64MB)
- Performance profiling (64MB)

**Use Cases:**
- UnhingedOS development
- System debugging
- Performance optimization
- Research and experimentation

## 🔧 Build Commands

### Quick Start
```bash
# Build minimal UnhingedOS
make unhinged-os-minimal

# Start development VM
make vm-start

# Run integration tests
make vm-test
```

### Advanced Build Options
```bash
# Build specific profile
./build/unhinged-os-builder.sh --profile minimal
./build/unhinged-os-builder.sh --profile desktop
./build/unhinged-os-builder.sh --profile server
./build/unhinged-os-builder.sh --profile dev

# Custom configuration
./build/unhinged-os-builder.sh --profile desktop --memory 512MB --debug

# Clean build (remove all artifacts)
make vm-clean

# Rebuild from scratch
make vm-rebuild
```

### Development Workflow
```bash
# 1. Modify source components
vim os/unhinged-layer/voice-interface.c

# 2. Build development image
make unhinged-os-dev

# 3. Start VM for testing
make vm-start-dev

# 4. Run specific tests
make vm-test-voice

# 5. Deploy changes
make vm-deploy
```

## ⚙️ Build Configuration

### Profile Configuration Files
Each profile is defined by a configuration script in `build/profiles/`:

```bash
# build/profiles/minimal.sh
PROFILE_NAME="minimal"
MEMORY_SIZE="64MB"
CPU_CORES="1"
PACKAGES="alpine-base python3 py3-pip"
SERVICES="voice-interface"
GRAPHICS_MODE="basic"
```

### Environment Variables
```bash
# Build environment
export UNHINGED_BUILD_DIR="/tmp/unhinged-build"
export UNHINGED_CACHE_DIR="$HOME/.cache/unhinged"
export UNHINGED_DEBUG="1"

# VM configuration
export QEMU_MEMORY="256M"
export QEMU_CPUS="2"
export QEMU_DISPLAY="none"
```

### Custom Builds
```bash
# Create custom profile
cp build/profiles/minimal.sh build/profiles/custom.sh
vim build/profiles/custom.sh

# Build custom profile
./build/unhinged-os-builder.sh --profile custom
```

## 🧪 Testing Integration

### Automated Testing
```bash
# Run all tests
make vm-test-all

# Specific test categories
make vm-test-boot        # Boot sequence tests
make vm-test-graphics    # Graphics system tests
make vm-test-voice       # Voice interface tests
make vm-test-integration # Full system integration
```

### Manual Testing
```bash
# Start VM with console access
make vm-start-console

# Start VM with graphics
make vm-start-graphics

# Start VM with debugging
make vm-start-debug
```

### Performance Testing
```bash
# Boot time measurement
make vm-test-boot-time

# Memory usage analysis
make vm-test-memory

# Voice latency testing
make vm-test-voice-latency
```

## 🔄 Development Cycle

### 1. Source Modification
- Edit components in `os/` directory
- Follow UnhingedOS coding standards
- Update documentation as needed

### 2. Local Build
```bash
# Quick development build
make unhinged-os-dev-quick

# Full development build
make unhinged-os-dev
```

### 3. Testing
```bash
# Unit tests
make vm-test-unit

# Integration tests
make vm-test-integration

# Performance validation
make vm-test-performance
```

### 4. Validation
```bash
# Code quality checks
make vm-lint

# Security validation
make vm-security-scan

# Documentation validation
make vm-docs-check
```

### 5. Deployment
```bash
# Create production image
make unhinged-os-production

# Package for distribution
make vm-package

# Deploy to target environment
make vm-deploy-production
```

## 🛠️ Build Tools

### Core Build Scripts
- **`unhinged-os-builder.sh`** - Master build orchestrator
- **`os-configurator.sh`** - System configuration manager
- **`setup-unhinged-os.sh`** - OS setup and initialization

### Utility Scripts
- **`vm-manager.sh`** - VM lifecycle management
- **`image-optimizer.sh`** - Image size optimization
- **`test-runner.sh`** - Automated test execution

### Build Dependencies
```bash
# Required tools
sudo apt install qemu-kvm qemu-utils docker.io

# Alpine build tools
docker pull alpine:3.22.2

# Development tools
sudo apt install build-essential cmake git
```

## 📊 Build Metrics

### Build Times (Approximate)
- **Minimal Profile:** 2-3 minutes
- **Desktop Profile:** 5-7 minutes
- **Server Profile:** 3-4 minutes
- **Development Profile:** 8-10 minutes

### Image Sizes
- **Minimal ISO:** 64MB
- **Desktop ISO:** 256MB
- **Server ISO:** 128MB
- **Development ISO:** 512MB

### Resource Requirements
- **Build Host:** 2GB RAM, 4GB disk space
- **Docker:** 1GB RAM for Alpine builds
- **QEMU:** 512MB RAM for testing

## 🔍 Troubleshooting

### Common Issues
```bash
# Build fails with missing dependencies
make vm-install-deps

# QEMU fails to start
make vm-check-kvm

# Image too large
make vm-optimize-image

# Tests fail
make vm-debug-tests
```

### Debug Mode
```bash
# Enable verbose build output
export UNHINGED_DEBUG=1
make unhinged-os-dev

# Build with debugging symbols
make unhinged-os-dev-debug

# Interactive build debugging
make vm-build-interactive
```

---

**UnhingedOS Build System: Systematic, reproducible OS generation**
