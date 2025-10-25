# 🎛️ Unhinged

> **Voice-First AI Control Center** - Native GTK desktop application with immediate voice interaction

## 🚀 **Quick Start - Voice-First Experience**

```bash
make start
```

**Launches native GUI with immediate voice capability** - hit the mic button and start talking!

## 🎤 **Voice-First User Experience**

- **Native Audio Capture**: Ubuntu system-level audio (no Python libraries)
- **Whisper Integration**: Auto-starting speech-to-text service
- **Immediate Interaction**: Zero setup - voice works right away
- **AI Chat Integration**: Voice → transcription → AI response pipeline

## 🏗️ **Architecture Overview**

```
📦 Unhinged/
├── control/native_gui/           # Native GTK4 desktop application
│   ├── tools/chat/              # Voice-first chat interface
│   ├── tools/vision/            # Camera and image analysis
│   ├── tools/input_capture/     # Keyboard/mouse monitoring
│   └── core/                    # Application framework
├── services/                    # AI services (auto-starting)
│   ├── speech-to-text/          # Whisper-based transcription
│   ├── text-to-speech/          # Audio generation
│   └── vision-ai/               # Image analysis
├── control/service_launcher.py  # Service orchestration
├── build/                       # Polyglot build system
└── docs/                        # LlmDocs-annotated documentation
```

## 🎯 **Core Features**

- **🎤 Voice-First Interface**: Native audio → Whisper → AI chat
- **📱 Mobile-Responsive GUI**: Touch-friendly native interface
- **🔧 Developer Tools**: API testing, service monitoring, logs
- **📊 System Monitoring**: Real-time system and service status
- **🎥 Vision Integration**: Camera capture and AI analysis
- **⌨️ Input Monitoring**: Keyboard/mouse capture for automation

## 📋 **Documentation**

- **For Developers**: See `/docs/` for comprehensive LlmDocs-annotated documentation
- **For LLM Agents**: Start with `/LLM_MASTER_PROMPT.md` before making any changes

## 🚀 **Status**

Some things work, some don't. The health dashboard will tell you which is which.

## 🎯 **For Developers**

Check `/docs/` for more details if needed.

## 🔧 **Commands**

```bash
make start               # Start everything
make clean               # Clean up
```

---

That's it. More details in `/docs/` if you really need them.
# Test change
