# GUI Launch Guide - Unhinged Platform

## Quick Start

### Option 1: Start Everything (Services + GUI)
```bash
./unhinged
```
This is the **default behavior** - starts all services and launches the GTK4 GUI.

### Option 2: Start Services Only
```bash
./unhinged system start
```
Starts all backend services without launching the GUI.

### Option 3: Launch GUI Only
```bash
./unhinged system gui
```
Launches the GTK4 GUI (assumes services are already running).

### Option 4: Direct GUI Launch
```bash
python3 control/gtk4_gui/launch.py
```
Direct Python launcher for the GUI application.

---

## System Commands

```bash
./unhinged system start      # Start services
./unhinged system gui        # Launch GUI
./unhinged system stop       # Stop everything
./unhinged system status     # Check system health
./unhinged system restart    # Restart system
```

---

## Development Commands

```bash
./unhinged dev lint              # Run linting
./unhinged dev static-analysis   # Run static analysis
./unhinged dev build             # Build project
```

---

## Architecture

```
./unhinged (bash shim)
    ↓
control/cli/main.py (Click CLI)
    ├─ system.start()      → Preflight + Services
    ├─ system.gui()        → GTK4 GUI
    ├─ system.stop()       → Graceful shutdown
    └─ system.status()     → Health check

control/gtk4_gui/launch.py
    ↓
control/gtk4_gui/desktop_app/app.py (UnhingedDesktopApp)
    ↓
GTK4 Application (Libadwaita)
```

---

## Troubleshooting

### GUI won't start
```bash
# Check if services are running
./unhinged system status

# Start services explicitly
./unhinged system start

# Then launch GUI
./unhinged system gui
```

### Services won't start
```bash
# Run preflight checks
./unhinged admin preflight check

# Check logs
./unhinged admin debug logs
```

### Clean restart
```bash
./unhinged system stop
sleep 2
./unhinged system start
./unhinged system gui
```

---

## Status: ✅ OPERATIONAL

- ✅ Default `./unhinged` starts services + GUI
- ✅ `./unhinged system gui` launches GUI only
- ✅ All commands working
- ✅ Backward compatible with previous behavior

