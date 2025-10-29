# Ubuntu Dependencies - KISS Package Manager

Simple YAML-based package manager for Ubuntu dependencies.

## Quick Start

```bash
# For new Ubuntu users - install everything
make ubuntu-setup

# Or just start (auto-checks dependencies)
make start

# Manual dependency management
make deps-list                    # List available packages
make deps-install-essential       # Install essential packages
make deps-install-graphics        # Install graphics packages
```

## What Gets Installed

**Essential packages:**
- `cmake` - Build system
- `build-essential` - GCC, make, etc.
- `python3-dev` - Python headers
- `cffi` - Python C FFI library (installed in `/build/python/venv/`)

**Graphics packages:**
- `libdrm-dev` - Direct Rendering Manager headers
- `libwayland-dev` - Wayland compositor headers

## Files

- `dependencies.yaml` - Package definitions
- `package_manager.py` - Simple installer script
- `../python/` - Centralized Python environment system
- `README.md` - This file

## Python Environment

Ubuntu 24.04+ has "externally-managed-environment" restrictions that prevent `pip install --user`.
We solve this with the existing centralized Python virtual environment in `/build/python/venv/`:

```bash
# Setup Python environment (includes ML/AI dependencies)
make setup-python

# Use Python from venv
build/python/venv/bin/python -c "import cffi; print('✅ cffi works!')"

# Run Python scripts with the environment
python3 build/python/run.py your_script.py
```

## Design Philosophy

**KISS (Keep It Simple, Stupid):**
- Ubuntu-only (no multi-platform complexity)
- Direct apt-get commands (no fancy dependency resolution)
- Simple YAML structure (package → install command)
- Minimal Python script (no external dependencies)

## Usage Examples

```bash
# List what's available
python3 package_manager.py list

# Install a specific package
python3 package_manager.py install cmake

# Install a group
python3 package_manager.py install-group essential
```

## Adding New Packages

Edit `dependencies.yaml`:

```yaml
packages:
  new-package:
    description: "Description here"
    install: "apt-get install -y package-name"
    optional: true  # Optional packages ask for confirmation

groups:
  my-group:
    - new-package
    - existing-package
```

That's it! No complex configuration, no multi-platform support, no dependency resolution algorithms. Just simple Ubuntu package installation.
