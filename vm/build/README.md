# UnhingedOS Build System

This directory contains the build tools and configuration for generating UnhingedOS images from source components.

## 📁 Directory Structure

### Build Scripts
- **`unhinged-os-builder.sh`** - Master build orchestrator
- **`os-configurator.sh`** - System configuration manager  
- **`setup-unhinged-os.sh`** - OS setup and initialization

### `profiles/`
**Purpose:** Build profile configurations for different UnhingedOS variants

- **`minimal.sh`** - Minimal voice-first OS (64MB RAM)
- **`desktop.sh`** - Full desktop environment (256MB RAM)
- **`server.sh`** - Headless server variant (128MB RAM)
- **`dev.sh`** - Development environment (512MB RAM)

## 🔧 Build Process

### 1. Profile Selection
Choose appropriate build profile based on target use case:
```bash
./unhinged-os-builder.sh --profile minimal
./unhinged-os-builder.sh --profile desktop
./unhinged-os-builder.sh --profile server
./unhinged-os-builder.sh --profile dev
```

### 2. Source Integration
Build system pulls components from `../os/` directory:
- `alpine-base/` - Base Alpine Linux components
- `unhinged-layer/` - UnhingedOS-specific services
- `boot-system/` - Boot and initialization
- `graphics-stack/` - Native graphics system

### 3. Alpine Customization
- Package selection based on profile
- Service configuration
- Kernel customization
- System optimization

### 4. Image Generation
- Bootable ISO creation
- QCOW2 VM image generation
- Optimization and compression
- Artifact placement in `../runtime/`

## ⚙️ Build Configuration

### Profile Structure
Each profile defines:
```bash
PROFILE_NAME="minimal"
MEMORY_SIZE="64MB"
CPU_CORES="1"
PACKAGES="alpine-base python3 py3-pip mesa-dri-gallium"
SERVICES="voice-interface graphics-basic"
GRAPHICS_MODE="basic"
VOICE_ENGINE="minimal"
```

### Environment Variables
```bash
# Build configuration
UNHINGED_BUILD_DIR="/tmp/unhinged-build"
UNHINGED_CACHE_DIR="$HOME/.cache/unhinged"
UNHINGED_DEBUG="0"

# Target configuration
TARGET_ARCH="x86_64"
TARGET_KERNEL="virt"
TARGET_INIT="openrc"
```

## 🎯 Build Profiles

### Minimal Profile
**Target:** Embedded systems, IoT devices
**Resources:** 64MB RAM, 1 CPU core
**Components:** Core voice interface, basic graphics
**Use Cases:** Voice-only interfaces, resource-constrained environments

### Desktop Profile  
**Target:** Primary desktop replacement
**Resources:** 256MB RAM, 2 CPU cores
**Components:** Full voice interface, complete graphics stack
**Use Cases:** Voice-controlled workstations, accessibility computing

### Server Profile
**Target:** Voice processing backend
**Resources:** 128MB RAM, 1-2 CPU cores  
**Components:** Voice engine, network services, minimal graphics
**Use Cases:** API servers, distributed voice computing

### Development Profile
**Target:** UnhingedOS development
**Resources:** 512MB RAM, 4 CPU cores
**Components:** Complete stack + development tools + debugging
**Use Cases:** OS development, system debugging, research

## 🔄 Development Workflow

### 1. Modify Sources
Edit components in `../os/` directory

### 2. Select Profile
Choose appropriate build profile for testing

### 3. Build Image
```bash
./unhinged-os-builder.sh --profile dev
```

### 4. Test & Validate
Deploy to `../runtime/` and test with `../testing/` framework

### 5. Iterate
Repeat cycle for rapid development

## 🛠️ Build Tools

### Core Scripts
- **unhinged-os-builder.sh** - Orchestrates entire build process
- **os-configurator.sh** - Handles system configuration
- **setup-unhinged-os.sh** - Manages OS initialization

### Utility Functions
- Profile validation and loading
- Package dependency resolution
- Image optimization and compression
- Build artifact management

### Integration Points
- Source component integration from `../os/`
- Runtime artifact deployment to `../runtime/`
- Testing framework integration with `../testing/`
- Documentation generation for `../docs/`

---

**UnhingedOS Build System: Systematic OS generation from source components**
