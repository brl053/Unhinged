# Python Build System - Centralized Strategy

## Philosophy: "One venv to rule them all"

### Current State
- Multiple requirements.txt files scattered across services
- Root venv/ for build system
- Services run without venv activation
- Generated clients have separate pyproject.toml

### Target State: Single Python Environment
```
build/python/
├── setup.py            # Central environment setup
├── requirements.txt    # Consolidated dependencies
├── venv/              # Single virtual environment
├── run.py             # Universal Python runner
└── deps/              # Vendored wheels for offline builds
```

### Idioms to Preserve
- **"Virtual environments isolate dependencies"** - Single venv for everything
- **"pip installs packages"** - Centralized dependency management
- **"PYTHONPATH controls imports"** - Module resolution
- **"__main__.py makes packages executable"** - Entry point convention
- **"Wheels are the standard"** - Binary distribution format

### Implementation Strategy
1. **Consolidate requirements** - Merge all requirements.txt files
2. **Single venv creation** - `python3 -m venv build/python/venv`
3. **Universal runner** - `build/python/run.py script.py args...`
4. **Path resolution** - Automatic PYTHONPATH setup
5. **Dependency vendoring** - Download wheels for offline builds

### Anti-Patterns to Avoid
- ❌ Multiple virtual environments
- ❌ System Python usage
- ❌ Conda complexity
- ❌ Poetry lock files
- ❌ setup.py install (use pip)

### Success Criteria
- Single command: `build/python/run.py services/speech-to-text/main.py`
- Zero scattered requirements.txt files
- Consistent Python execution everywhere
- Offline build capability

### Universal Runner
```python
#!/usr/bin/env python3
"""Universal Python runner for all Unhinged Python execution"""

import os
import sys
import subprocess
from pathlib import Path

def run_with_venv(script_path, args=None):
    # Activate venv
    venv_python = Path(__file__).parent / "venv" / "bin" / "python3"
    
    # Resolve script path
    if not Path(script_path).is_absolute():
        script_path = Path.cwd() / script_path
    
    # Build command
    cmd = [str(venv_python), str(script_path)] + (args or [])
    
    # Execute with proper environment
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent)
    
    return subprocess.run(cmd, env=env)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: run.py <script.py> [args...]")
        sys.exit(1)
    
    script = sys.argv[1]
    args = sys.argv[2:]
    run_with_venv(script, args)
```

### Dependency Consolidation
```python
# Merge all requirements.txt files
def consolidate_requirements():
    req_files = [
        "requirements.txt",
        "services/speech-to-text/requirements.txt",
        "services/text-to-speech/requirements.txt", 
        "services/vision-ai/requirements.txt",
        "generated/python/clients/requirements.txt"
    ]
    
    dependencies = set()
    for req_file in req_files:
        if Path(req_file).exists():
            dependencies.update(parse_requirements(req_file))
    
    # Resolve version conflicts
    resolved = resolve_version_conflicts(dependencies)
    
    # Write consolidated requirements
    write_requirements("build/python/requirements.txt", resolved)
```

### Execution Standardization
```bash
# Before (scattered execution)
python3 services/speech-to-text/main.py
source venv/bin/activate && python3 build/build.py
cd control/deployment && python3 deploy.py

# After (centralized execution)
build/python/run.py services/speech-to-text/main.py
build/python/run.py build/build.py
build/python/run.py control/deployment/deploy.py
```

## Next Agent Instructions
1. Implement `build/python/run.py` - Universal Python runner
2. Create `build/python/setup.py` - Environment setup script
3. Consolidate all requirements.txt files
4. Update Makefile to use centralized runner
5. Test all Python scripts with new runner
6. Remove scattered requirements.txt files

**Principle: "One Python environment, executed consistently everywhere"**
