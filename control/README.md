# 🎛️ Unhinged Control Plane

**The Line in the Sand**: Unified control plane for build orchestration, service management, and human-in-the-loop workflows with plug-and-play browser experience.

## 🚀 **Quick Start**

### **1. Start the Control Plane**
```bash
# Start DAG server
python3 -m control

# Or start with custom port
python3 -m control --port 9001
```

### **2. Open Browser Interface**
```bash
# Quick launcher with menu
./control/open.sh

# Direct access to specific interfaces
./control/open.sh --dag          # DAG Control Dashboard
./control/open.sh --status       # System Status & Monitoring
./control/open.sh --all          # Open all interfaces
```

### **3. Manual Browser Access**
Open any of these files directly in your browser:
- `control/static_html/dag-control.html` - Main DAG control interface
- `control/static_html/index.html` - System status dashboard
- `control/static_html/text-test.html` - Text generation testing
- `control/static_html/image-test.html` - Vision AI testing
- `control/static_html/voice-test.html` - Voice processing testing

## 🏗️ **Architecture**

### **Unified Control Plane Structure**
```
control/                           # THE Control Plane
├── __init__.py                   # Core DAG engine
├── __main__.py                   # CLI entry point
├── dag.py                        # DAG execution engine
├── server.py                     # HTTP API (port 9000)
├── human.py                      # Human interface integration
├── config.py                     # Configuration
├── open.sh                       # Browser launcher
│
└── static_html/                  # Browser Interface
    ├── shared/
    │   ├── config.js            # Service configuration
    │   └── styles.css           # Unified styling
    ├── dag-control.html         # DAG control interface
    ├── dag-approval.html        # Human approval workflow
    ├── index.html               # System status dashboard
    ├── text-test.html           # Text generation testing
    ├── image-test.html          # Vision AI testing
    └── voice-test.html          # Voice processing testing
```

## 🎯 **Core Features**

### **DAG Build Orchestration**
- ✅ **Cycle Detection**: Prevents infinite dependency loops
- ✅ **Parallel Execution**: Optimal build performance with dependency awareness
- ✅ **Human Approval**: Configurable approval workflows for critical operations
- ✅ **Real-time Monitoring**: Live execution status and performance metrics

### **Plug-and-Play Browser Experience**
- ✅ **Zero Dependencies**: Pure HTML/CSS/JS that works immediately
- ✅ **File:// Protocol**: Works without web server
- ✅ **Universal Compatibility**: Runs in any modern browser
- ✅ **Self-Contained**: Everything in one directory

### **Self-Serve Debug & Reports**
- ✅ **LLM-Ready Reports**: Pre-formatted for copy-paste to AI assistants
- ✅ **System Diagnostics**: One-click system status reports
- ✅ **Error Analysis**: Structured error reports with context
- ✅ **Performance Metrics**: Build timing and optimization suggestions

## 🎛️ **Available Build Targets**

### **Development Targets**
- **`dev-fast`**: Fast development build with intelligent caching
- **`dev-full`**: Complete development environment with all services

### **Testing Targets**
- **`test-suite`**: Comprehensive test suite (unit, integration, e2e)

### **Production Targets**
- **`production-build`**: Production build with optimization and validation
- **`deploy-staging`**: Deploy to staging environment

## 📡 **API Endpoints**

The control plane provides a RESTful API on port 9000:

```bash
# Health check
GET /dag/health

# Available targets
GET /dag/targets

# Execution plan for target
GET /dag/plan/{target}

# Current DAG status
GET /dag/status

# Execute target
POST /dag/execute
{"target": "dev-fast"}

# Human approval
POST /dag/approve
{"approval_id": "...", "approved": true}

# Reset DAG
POST /dag/reset
```

## 🧪 **Testing & Validation**

### **Run Test Suite**
```bash
# Full test suite
python3 test_control_plane.py

# Control plane internal tests
python3 -m control --test

# Sample DAG execution
python3 -m control --sample

# Validate installation
python3 -m control --validate
```

### **Test Results**
- ✅ **Import Tests**: All modules load correctly
- ✅ **DAG Functionality**: Cycle detection and execution order
- ✅ **HTTP Server**: All endpoints responding correctly
- ✅ **Human Interface**: HTML generation working
- ✅ **Configuration**: All config loading properly
- ✅ **Integration**: End-to-end DAG execution working

## 🎨 **Design Philosophy**

### **Raw JS + HTML Approach**
- **No Build Tools**: Direct HTML/CSS/JS that works immediately
- **Copy-Paste Friendly**: All reports in plain text/HTML
- **Universal Access**: Works on any system with a browser
- **Self-Documenting**: Code is readable and modifiable

### **Human-Centric Design**
- **Visual Control**: Browser-based DAG visualization
- **Approval Workflows**: Human oversight for critical operations
- **Emergency Controls**: Stop, pause, rollback capabilities
- **Clear Feedback**: Real-time status and progress indicators

### **Plug-and-Play Experience**
- **Single Directory**: Everything in `control/`
- **Zero Setup**: Just run and open browser
- **Self-Contained**: No external dependencies
- **Immediate Value**: Works out of the box

## 🔧 **Configuration**

### **Control Plane Settings**
Edit `control/config.py` to customize:
- Server port (default: 9000)
- Human approval timeouts
- Parallel execution limits
- Build target definitions

### **Service Integration**
The control plane integrates with existing services:
- **Backend**: http://localhost:8080
- **Frontend**: http://localhost:3000
- **Whisper TTS**: http://localhost:8000
- **Vision AI**: http://localhost:8001
- **Ollama LLM**: http://localhost:11434

## 🎉 **Ready to Use**

The control plane is now your unified interface for:
- ✅ **Build Orchestration**: DAG-based builds with human oversight
- ✅ **Service Management**: Health monitoring and status tracking
- ✅ **Debug & Reports**: Self-serve debugging with LLM-ready output
- ✅ **Testing & Validation**: Comprehensive testing across all services

**Get started immediately:**
```bash
python3 -m control        # Start the control plane
./control/open.sh --dag   # Open DAG control dashboard
```

Welcome to the Unhinged Control Plane! 🚀
