# Unhinged Desktop Application

**@llm-doc Ubuntu GNOME Desktop Application for Unhinged Platform**  
**@llm-version 1.0.0**  
**@llm-date 2025-01-26**  
**@llm-author Unhinged Team**

## Overview

Native Ubuntu GNOME desktop application that provides the same functionality as `make start` through a modern graphical interface. Built with GTK4 and Libadwaita for authentic Ubuntu integration.

## Features

### 🖥️ Native Desktop Integration
- **GTK4/Libadwaita**: Modern Ubuntu GNOME interface
- **Desktop File**: Appears in application menu and desktop
- **System Integration**: Follows Ubuntu design guidelines
- **Keyboard Shortcuts**: Standard GNOME shortcuts (Ctrl+Q to quit)

### 🚀 Platform Control
- **Multiple Launch Modes**: Enhanced, Simple, QoL, Custom ISO
- **Real-time Status**: Visual progress indication and status updates
- **Live Output**: Real-time log display with enhanced formatting
- **Error Handling**: User-friendly error dialogs and notifications

### 🔧 User Experience
- **Toast Notifications**: Non-intrusive status updates
- **About Dialog**: Application information and links
- **Preferences**: Configurable settings (future expansion)
- **Menu Integration**: Standard application menu with actions

## Installation

### Quick Install (Recommended)
```bash
# Install for current user
./install-desktop-app.sh --user

# Or install system-wide (requires sudo)
sudo ./install-desktop-app.sh --system
```

### Package Installation
```bash
# Create distribution package
./create-distribution-package.sh

# Install DEB package
sudo dpkg -i dist/unhinged_1.0.0.deb
```

### Manual Installation
```bash
# Copy desktop file
cp unhinged.desktop ~/.local/share/applications/

# Update desktop database
update-desktop-database ~/.local/share/applications/

# Make executable
chmod +x unhinged-desktop-app
```

## Usage

### Launch Methods
1. **Application Menu**: Search for "Unhinged" in Ubuntu's application menu
2. **Command Line**: Run `./unhinged-desktop-app` or `unhinged` (if installed)
3. **Desktop Icon**: Double-click if placed on desktop

### Launch Modes
- **Enhanced (Recommended)**: Full bidirectional VM communication
- **Simple Communication**: Basic unidirectional VM → Host
- **Quality of Life**: Enhanced UX with automatic Makefile integration
- **Custom ISO**: Launch with custom Alpine ISO

### Interface Elements
- **Platform Control**: Start/stop buttons with mode selection
- **Status Display**: Real-time status with visual indicators
- **Output Log**: Live output from platform operations
- **Menu**: About, preferences, and quit options

## Requirements

### System Requirements
- Ubuntu 20.04 LTS or later
- GNOME desktop environment
- Python 3.8+

### Dependencies
```bash
# Install required packages
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1
```

### Verification
```bash
# Test GTK4/Libadwaita availability
python3 -c "import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Adw', '1'); print('OK')"
```

## Development

### File Structure
```
desktop/
├── unhinged-desktop-app          # Main GTK4 application
├── unhinged.desktop              # Desktop integration file
├── unhinged-icon.svg             # Application icon (SVG)
├── install-desktop-app.sh        # Installation script
├── create-distribution-package.sh # Package creation script
├── test-desktop-app.py           # Test suite
└── README.md                     # This file
```

### Testing
```bash
# Run comprehensive tests
./test-desktop-app.py

# Test installation
./install-desktop-app.sh --test

# Test application syntax
python3 -m py_compile unhinged-desktop-app
```

### Building Packages
```bash
# Create all distribution packages
./create-distribution-package.sh

# Create specific package type
./create-distribution-package.sh deb      # DEB package only
./create-distribution-package.sh appimage # AppImage structure
./create-distribution-package.sh guide    # Installation guide
```

## Architecture

### Application Structure
- **UnhingedDesktopApp**: Main GTK4 application class
- **Backend Integration**: Calls existing Makefile targets
- **UI Components**: Modern Libadwaita widgets
- **Error Handling**: Comprehensive error dialogs and logging

### Communication Flow
1. User selects launch mode and clicks "Start Platform"
2. Application calls appropriate `make` target in background thread
3. Real-time output streams to GUI log display
4. Status updates and notifications provide user feedback
5. Error handling shows user-friendly dialogs

### Integration Points
- **Makefile System**: Calls `make start`, `make start-simple`, etc.
- **VM Communication**: Integrates with existing VM launchers
- **Desktop Environment**: Native Ubuntu GNOME integration

## Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check dependencies
python3 -c "import gi; gi.require_version('Gtk', '4.0')"

# Install missing packages
sudo apt install gir1.2-gtk-4.0 gir1.2-adw-1
```

#### Desktop File Not Appearing
```bash
# Update desktop database
update-desktop-database ~/.local/share/applications/

# Check file permissions
ls -la ~/.local/share/applications/unhinged.desktop
```

#### Platform Launch Fails
- Check that you're in the Unhinged project root directory
- Verify Makefile exists and has required targets
- Check output log for specific error messages

### Debug Mode
```bash
# Run with debug output
G_MESSAGES_DEBUG=all ./unhinged-desktop-app

# Check application logs
journalctl --user -f | grep unhinged
```

## Contributing

### Code Style
- Follow GTK4/Libadwaita best practices
- Use LlmDoc documentation standards
- Maintain Ubuntu GNOME design guidelines

### Testing
- Add tests to `test-desktop-app.py`
- Test on multiple Ubuntu versions
- Verify accessibility features

### Packaging
- Update version numbers in all files
- Test installation on clean systems
- Validate desktop file format

## License

MIT License - see project root for full license text.

## Links

- **Project Homepage**: https://github.com/unhinged/platform
- **Issues**: https://github.com/unhinged/platform/issues
- **Documentation**: https://github.com/unhinged/platform/wiki
- **Ubuntu GNOME Guidelines**: https://developer.gnome.org/hig/

---

**@llm-principle** Native desktop integration with existing backend  
**@llm-culture** Independence through accessible graphical interface  
**@llm-achievement** Complete Ubuntu GNOME desktop application ready for distribution
