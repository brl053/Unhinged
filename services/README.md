# Unhinged Services - Centralized Python Execution

## Universal Python Runner

All Python services now use the centralized Python environment and universal runner:

```bash
# Run any service
build/python/run.py services/<service-name>/main.py

# Examples
build/python/run.py services/speech-to-text/main.py
build/python/run.py services/text-to-speech/main.py
build/python/run.py services/vision-ai/main.py
```

## Service Dependencies

All service dependencies are now managed centrally in:
- `requirements.txt` - Core ML/AI and big data libraries with Python 3.12 compatibility

### Previously Scattered Dependencies (REMOVED):
- ❌ `services/speech-to-text/requirements.txt` - REMOVED
- ❌ `services/text-to-speech/requirements.txt` - REMOVED  
- ❌ `services/vision-ai/requirements.txt` - REMOVED
- ❌ `requirements.txt` (root) - REMOVED
- ❌ `generated/python/clients/requirements.txt` - REMOVED

### Service-Specific Notes:

#### Speech-to-Text Service
- **Dependencies**: openai-whisper, torch, torchaudio, gtts
- **Status**: ✅ Working - Whisper model loads successfully, needs proto generation for gRPC
- **Run**: `build/python/run.py services/speech-to-text/main.py`
- **Issues**: Port 8000 conflict, missing audio_pb2 for gRPC

#### Text-to-Speech Service
- **Dependencies**: gtts, pyttsx3, torch
- **Status**: ⚠️ Partial - gtts installed, path issues fixed, needs TTS library for advanced features
- **Run**: `build/python/run.py services/text-to-speech/main.py`
- **Issues**: Advanced TTS models have Python 3.12 compatibility issues

#### Vision AI Service
- **Dependencies**: torch, torchvision, transformers, opencv-python
- **Status**: ✅ Working - BLIP model loading successfully, path issues fixed
- **Run**: `build/python/run.py services/vision-ai/main.py`
- **Issues**: None major, model loading takes time

## Environment Setup

1. **Create centralized environment**:
   ```bash
   cd build/python && python3 setup.py
   ```

2. **Verify installation**:
   ```bash
   build/python/run.py --shell
   ```

3. **Interactive development**:
   ```bash
   build/python/run.py --jupyter
   ```

## Migration Complete

✅ **Centralized Python Environment**: Single venv in `build/python/venv/`
✅ **Universal Runner**: `build/python/run.py` for all Python execution
✅ **Consolidated Dependencies**: All requirements in `build/python/`
✅ **Makefile Updated**: Uses `$(PYTHON_RUN)` variable
✅ **Scattered Requirements Removed**: No more dependency hidey holes
✅ **Old venv Removed**: Eliminated root `venv/` directory

## Next Steps

1. **Add missing ML libraries** to `requirements-core.txt` as Python 3.12 compatible versions become available
2. **Test all services** with centralized environment
3. **Add service-specific configuration** files (not requirements) as needed
4. **Implement ETL pipelines** using the Apache stack integration
