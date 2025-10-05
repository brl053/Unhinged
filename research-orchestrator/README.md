# Research Orchestrator

AI-powered research and artifact generation for the Unhinged Platform. This system acts as an intelligent orchestrator that asks clarifying questions, conducts comprehensive research using Perplexity AI, and generates ready-to-use code artifacts.

## Overview

Instead of complex shell scripts, this Python-based system provides:

1. **Interactive Questioning** - Asks clarifying questions to understand your needs
2. **AI-Powered Research** - Uses Perplexity AI for comprehensive technical research  
3. **Artifact Generation** - Creates React components, TypeScript types, documentation, tests
4. **Secure API Management** - Handles API keys securely without git commits

## Quick Start

### 1. Setup

```bash
cd projects/Unhinged/research-orchestrator
python setup.py
```

### 2. Configure API Key

```bash
python orchestrator.py setup
```

### 3. Test Connection

```bash
python orchestrator.py test
```

### 4. Start Researching

```bash
python orchestrator.py research "Please add MonacoEditor to the project"
```

## Usage Examples

### Your MonacoEditor Use Case

```bash
# Your exact request
python orchestrator.py research "Please add MonacoEditor to the project"
```

**The orchestrator will ask:**
- What type of integration? (React component, API wrapper, etc.)
- What's your use case? (code editing, syntax highlighting, etc.)
- What depth? (quick setup, full customization, enterprise-grade)
- Platform features? (theming, auth, real-time collaboration)
- Additional requirements?

**Then it will:**
- Craft a precise Perplexity query based on your answers
- Wait for comprehensive research results
- Generate all necessary artifacts (components, types, tests, docs)
- Present everything to you with sources and related questions

### Other Examples

```bash
# API integration research
python orchestrator.py research "Add GraphQL to our backend"

# Technology comparison
python orchestrator.py research "Should we use React or Vue for our frontend?"

# Architecture decisions
python orchestrator.py research "How should we implement real-time collaboration?"
```

## Generated Artifacts

Based on your answers, the system generates:

### React Component Integration
- `MonacoEditorWrapper.tsx` - Main React component
- `MonacoEditorTypes.ts` - TypeScript interfaces
- `useMonacoEditor.ts` - Custom React hooks
- `MonacoEditorWrapper.test.tsx` - Jest/RTL tests
- `MonacoEditorWrapper.stories.tsx` - Storybook stories

### API Client Integration  
- `MonacoEditorClient.ts` - API client class
- `MonacoEditorTypes.ts` - Request/response types
- Tests and documentation

### Backend Service Integration
- `MonacoEditorService.kt` - Kotlin service for Ktor
- Integration with existing Unhinged services

### Documentation
- `MonacoEditor_README.md` - Complete integration guide
- `MonacoEditor_Implementation_Guide.md` - Step-by-step instructions
- Full research report with sources and citations

## Interactive Workflow

```
You: "Please add MonacoEditor to the project"

Orchestrator: 
┌─ What type of integration do you need?
│  1. React component wrapper  ← (You choose this)
│  2. Standalone JavaScript integration
│  3. API client/wrapper
│  4. Backend service integration
│  5. Full-stack implementation
└─

Orchestrator: "What's your primary use case?"
You: "Code editing for our platform with syntax highlighting"

Orchestrator: "What level of implementation depth?"
You: "Enterprise-grade" (full customization)

Orchestrator: "Do you need Unhinged Platform theme integration?"
You: "Yes"

Orchestrator: "Do you need authentication integration?"  
You: "Yes"

Orchestrator: "Do you need real-time collaboration features?"
You: "Yes"

Orchestrator: 
┌─ Research Plan:
│  Technology: MonacoEditor
│  Integration: React component wrapper
│  Use Case: Code editing with syntax highlighting
│  Depth: Enterprise-grade
│  Platform Features: theming, auth, realtime
└─ Proceed? [Y/n]

[Researching MonacoEditor...]
[Generating artifacts...]

Results:
✓ MonacoEditorWrapper.tsx - Enterprise React component
✓ MonacoEditorTypes.ts - Complete TypeScript definitions  
✓ useMonacoEditor.ts - Custom hooks with platform integration
✓ Tests, stories, and comprehensive documentation
✓ Full research report with 15+ sources
```

## Architecture

```
orchestrator.py          # Main interactive orchestrator
├── perplexity_client.py # Perplexity AI API client
├── artifact_generator.py # Code/doc generation
├── config.py           # Secure configuration
└── templates/          # Jinja2 templates for artifacts
```

## Configuration

### Environment Variables
```bash
PERPLEXITY_API_KEY=your-key-here  # Optional, better to use secure config
```

### Secure Configuration
API keys are stored in `~/.config/unhinged/secrets.json` with 600 permissions and automatic gitignore protection.

## Advanced Features

### Custom Templates
Add your own Jinja2 templates in `templates/` directory for custom artifact generation.

### Batch Processing
```python
from orchestrator import ResearchOrchestrator

orchestrator = ResearchOrchestrator()
requests = [
    "Add MonacoEditor to the project",
    "Add GraphQL to our API", 
    "Implement real-time notifications"
]

for request in requests:
    orchestrator.handle_request(request)
```

### Integration with Existing Workflow
```python
# In your existing Python scripts
from orchestrator import ResearchOrchestrator

def add_technology(tech_name: str, integration_type: str):
    orchestrator = ResearchOrchestrator()
    request = f"Please add {tech_name} as a {integration_type} to the project"
    return orchestrator.handle_request(request)
```

## Output Locations

- **Generated Artifacts**: `~/.local/share/unhinged/research/`
- **Research Reports**: `~/.local/share/unhinged/research/`
- **Cache**: `~/.local/share/unhinged/cache/`
- **Configuration**: `~/.config/unhinged/`

## Security

- ✅ API keys stored securely with restricted permissions
- ✅ Automatic gitignore patterns prevent commits
- ✅ No sensitive data in environment variables
- ✅ Encrypted local storage
- ✅ Access logging for audit trails

## Dependencies

- `requests` - HTTP client for Perplexity API
- `rich` - Beautiful terminal output
- `click` - CLI framework
- `jinja2` - Template engine for artifacts
- `pydantic` - Configuration management
- `python-dotenv` - Environment variable support

## Troubleshooting

### API Key Issues
```bash
python orchestrator.py setup  # Re-run setup
python orchestrator.py test   # Test connection
```

### Missing Dependencies
```bash
python setup.py  # Re-run setup
```

### Template Issues
Templates are auto-generated if missing. For custom templates, add to `templates/` directory.

## Examples

### Run the MonacoEditor Example
```bash
python example_monaco.py
```

This demonstrates the exact workflow for your use case with interactive questioning and artifact generation.

---

**This system transforms your simple request "Please add MonacoEditor to the project" into a comprehensive research session with ready-to-use code artifacts, all while keeping your API keys secure and never committing them to git.**
