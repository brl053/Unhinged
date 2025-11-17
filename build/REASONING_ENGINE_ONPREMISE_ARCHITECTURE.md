# Reasoning Engine: On-Premise Architecture

**Status**: ✅ COMPLETE  
**Commits**: `c759e04`, `12f7799`  
**Architecture**: 100% Local, No External APIs  
**Test Coverage**: 43/43 tests passing (100%)

## Core Principle

**No external API calls. Ever.**

The Reasoning Engine uses **local Ollama service** (localhost:1500) for all LLM inference. This is an on-premise, private, open-source project. All reasoning happens locally.

## Architecture

```
User Query
    ↓
ReasoningEngine (local Ollama)
    ├─ _load_service() → TextGenerationService
    ├─ TextGenerationService (localhost:1500)
    └─ Ollama (local inference)
        └─ Mistral model (default)
```

## Key Components

### 1. ReasoningEngine
- **Default Model**: `mistral` (local Ollama)
- **Default Provider**: `ollama` (localhost:1500)
- **Service**: Uses `TextGenerationService` for all LLM calls
- **No External Dependencies**: Anthropic, OpenAI removed

### 2. TextGenerationService
- **Location**: `libs/services/text_generation_service.py`
- **Health Check**: Verifies Ollama at localhost:1500
- **Lazy Loading**: Initializes on first use
- **Error Handling**: Graceful fallback when service unavailable

### 3. Wrappers (All Updated)
- **SemanticSearchWithReasoning**: mistral/ollama
- **DAGBuilderWithReasoning**: mistral/ollama
- **CommandExecutorWithReasoning**: mistral/ollama

## Deployment

### Local Development
```bash
# Ollama runs on localhost:1500 (external port)
# Internal port: 11434
# Docker compose: build/orchestration/docker-compose.development.yml
```

### Production
```bash
# Same Ollama service on localhost:1500
# Docker compose: build/orchestration/docker-compose.production.yml
```

## Models Available

**Default**: `mistral` (fast, good reasoning)

**Other Options**:
- `neural-chat` (conversational)
- `llama2` (general purpose)
- `dolphin-mixtral` (advanced reasoning)

Pull models with: `ollama pull <model-name>`

## Testing

All 43 tests pass with mocked TextGenerationService:
- 13 core reasoning engine tests
- 5 integration tests
- 5 CLI tests
- 6 intent graph tests
- 3 query planner tests
- 11 graph executor tests

## System Engineer Perspective

This is **GNU/Linux thinking**:
- Use local services (Ollama)
- No cloud dependencies
- No API keys
- No rate limits
- No vendor lock-in
- Full control over inference
- Sovereign computation

## Next Steps

Phase 4: Query command integration with same on-premise architecture.

