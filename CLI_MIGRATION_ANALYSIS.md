# CLI Migration Analysis - Services Inventory

## Current CLI Commands (Already Migrated)
✅ **generate text** - TextGenerationService (Ollama/OpenAI/Anthropic)
✅ **image generate** - ImageGenerationService (Stable Diffusion)
✅ **transcribe audio** - TranscriptionService (Whisper)
✅ **voice generate** - TTSService (Text-to-Speech)

## Available Services for Migration

### 1. **ChatService** (HIGH PRIORITY)
- **Location**: `libs/services/chat_service.py`
- **Purpose**: Multi-turn conversation with context management
- **CLI Command**: `unhinged chat` or `unhinged generate chat`
- **Proposed Usage**:
  ```bash
  unhinged chat "What is quantum computing?"
  unhinged chat -f conversation.txt
  echo "Tell me a joke" | unhinged chat
  ```
- **Status**: Ready for migration
- **Complexity**: Medium (context management)

### 2. **VideoGenerationService** (MEDIUM PRIORITY)
- **Location**: `libs/services/video_generation_service.py`
- **Purpose**: Generate videos from text/images
- **CLI Command**: `unhinged video generate`
- **Proposed Usage**:
  ```bash
  unhinged video generate "a sunset over mountains" -d 5
  unhinged video generate -f script.txt --fps 30
  ```
- **Status**: Ready for migration
- **Complexity**: Medium (output handling)

### 3. **ShortformVideoService** (MEDIUM PRIORITY)
- **Location**: `libs/services/shortform_video_service.py`
- **Purpose**: Generate TikTok/Reels/Shorts from scripts
- **CLI Command**: `unhinged video shortform`
- **Proposed Usage**:
  ```bash
  unhinged video shortform "script content" --platform tiktok
  unhinged video shortform -f script.txt --platform reels
  ```
- **Status**: Ready for migration
- **Complexity**: High (orchestrates multiple services)

### 4. **ScriptParserService** (LOW PRIORITY)
- **Location**: `libs/services/script_parser_service.py`
- **Purpose**: Parse scripts into structured format
- **CLI Command**: `unhinged parse script`
- **Proposed Usage**:
  ```bash
  unhinged parse script "script content"
  unhinged parse script -f script.txt
  ```
- **Status**: Utility service, lower priority
- **Complexity**: Low

### 5. **HybridGUIAnalysisService** (FUTURE)
- **Location**: `libs/services/yolo_analysis_service.py`
- **Purpose**: GUI element detection (OpenCV + YOLOv8)
- **CLI Command**: `unhinged analyze gui`
- **Status**: Specialized, future consideration
- **Complexity**: High (image processing)

## Migration Pattern (Established)

All CLI commands follow this pattern:
1. **Command Group**: `@click.group()` decorator
2. **Subcommand**: `@group.command()` decorator
3. **Arguments**: Varargs for flexible input (`nargs=-1`)
4. **Options**: File input (`-f`), output (`-o`), model/provider selection
5. **Input Sources**: Arguments, file, stdin (in priority order)
6. **Error Handling**: Custom exception types with recovery suggestions
7. **Service Integration**: Lazy-load service, call method, handle errors
8. **Output**: Log success/info, write to file or stdout

## Recommended Migration Order

### Phase 1 (Immediate)
- [ ] ChatService → `unhinged chat`
- [ ] VideoGenerationService → `unhinged video generate`

### Phase 2 (Next)
- [ ] ShortformVideoService → `unhinged video shortform`
- [ ] ScriptParserService → `unhinged parse script`

### Phase 3 (Future)
- [ ] HybridGUIAnalysisService → `unhinged analyze gui`

## Service Dependencies

- **ShortformVideoService** depends on:
  - ImageGenerationService ✅ (already CLI)
  - TTSService ✅ (already CLI)
  - VideoGenerationService (Phase 1)
  - ScriptParserService (Phase 2)

- **VideoGenerationService** depends on:
  - ImageGenerationService ✅ (already CLI)

## Notes

- All services use centralized error handling framework
- Port mappings managed via `vm services` command
- Health checks integrated into service initialization
- Tests follow Click CliRunner pattern



## Implementation Effort Estimates

| Service | Complexity | Est. Time | Tests | Notes |
|---------|-----------|-----------|-------|-------|
| ChatService | Medium | 2-3h | 8-10 | Context management, multi-turn |
| VideoGenerationService | Medium | 2-3h | 6-8 | Output file handling |
| ShortformVideoService | High | 4-5h | 10-12 | Orchestrates 4 services |
| ScriptParserService | Low | 1-2h | 4-6 | Utility, simple I/O |
| HybridGUIAnalysisService | High | 3-4h | 8-10 | Image processing, YOLO |

**Total Estimated Effort**: ~12-17 hours for all services

## Quick Start: Migrating a Service

### Template for New CLI Command

```python
# cli/commands/new_command.py
import sys
from pathlib import Path
import click
from cli.utils import log_error, log_info, log_success

try:
    from libs.services import NewService
except ImportError:
    from libs.services.new_service import NewService

@click.group()
def new_command():
    """Description of what this command does."""
    pass

@new_command.command()
@click.argument("input_arg", nargs=-1, required=False)
@click.option("-o", "--output", type=click.Path(), help="Output file")
@click.option("-f", "--file", type=click.Path(exists=True), help="Input file")
def subcommand(input_arg, output, file):
    """Subcommand description."""
    try:
        # Get input from file/arg/stdin
        if file:
            content = Path(file).read_text().strip()
        elif input_arg:
            content = " ".join(input_arg)
        else:
            content = click.get_text_stream("stdin").read().strip()

        if not content:
            log_error("Input cannot be empty")
            sys.exit(1)

        log_info(f"Processing: {content[:50]}...")
        service = NewService()
        result = service.process(content)

        if output:
            Path(output).write_text(result)
            log_success(f"Saved to: {output}")
        else:
            click.echo(result)

    except Exception as e:
        log_error(f"Operation failed: {e}")
        sys.exit(1)
```

### Integration Steps

1. Create `cli/commands/new_command.py` using template
2. Add import to `cli/commands/__init__.py`
3. Register in `cli/main.py` with `@cli.add_command(new_command)`
4. Create tests in `tests/test_cli_new_command.py`
5. Run: `./unhinged dev static-analysis` (pre-commit hooks)
6. Commit with descriptive message

## Service Readiness Checklist

- [ ] Service has clear input/output contract
- [ ] Service has error handling with custom exceptions
- [ ] Service has tests (unit + integration)
- [ ] Service documentation exists
- [ ] Service is containerized (if applicable)
- [ ] Port mappings documented (if applicable)
