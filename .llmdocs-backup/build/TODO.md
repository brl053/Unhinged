# Unhinged Build System - Polyglot Centralization Strategy

## Philosophy: "One build system, many languages, zero external tools"

### Current State: Build System Chaos
- ✅ Python: Scattered venvs and requirements
- ❌ Kotlin: Gradle scattered across projects  
- ❌ Java: No centralized build system
- ❌ C/C++: No build system at all
- ❌ NPM: **PURGED** (JavaScript independence achieved)

### Target State: Unified Toolchain
```
build/
├── python/         # Centralized Python environment
├── kotlin/         # Pure kotlinc toolchain  
├── java/           # Pure javac toolchain
├── c/              # Pure gcc/clang toolchain
├── modules/        # Build orchestration (Python)
└── orchestrator.py # Language-agnostic build coordinator
```

### Core Principles
1. **"No external build tools"** - Direct compiler invocation only
2. **"Vendor everything"** - Dependencies live in our repo
3. **"Single entry point"** - `make build` orchestrates everything
4. **"Language idioms preserved"** - Respect each language's nature
5. **"Reproducible builds"** - Same input = same output, always

### Language Strategies

#### Python: "One venv to rule them all"
- Single virtual environment in `build/python/venv/`
- Universal runner: `build/python/run.py script.py`
- Consolidated dependencies in `build/python/requirements.txt`

#### Kotlin: "Kotlin is Java with better syntax"
- Direct kotlinc invocation with classpath magic
- Maven coordinate resolution, no Gradle
- JAR packaging with manifest generation

#### Java: "Java is bytecode, Maven is XML hell"  
- Pure javac compilation with dependency resolution
- Classpath construction from Maven Central JARs
- Executable JAR creation with main class detection

#### C/C++: "C is simple, keep it simple"
- Direct gcc/clang invocation with include paths
- Vendored libraries in `build/c/vendor/`
- Static linking preferred, no pkg-config

### Anti-Patterns to Eliminate
- ❌ Gradle wrapper scripts and build.gradle.kts files
- ❌ Maven pom.xml complexity
- ❌ CMake/Autotools madness
- ❌ NPM package.json dependencies
- ❌ System package managers for build deps

### Implementation Phases

#### Phase 1: Python Centralization (IMMEDIATE)
1. Create `build/python/run.py` universal runner
2. Consolidate all requirements.txt files
3. Update Makefile to use centralized Python
4. Test all Python scripts with new runner

#### Phase 2: Kotlin Independence (NEXT)
1. Implement `build/kotlin/compile.py` kotlinc wrapper
2. Create Maven Central dependency resolver
3. Eliminate all Gradle files
4. Test with existing Kotlin services

#### Phase 3: Java Foundation (FUTURE)
1. Implement `build/java/compile.py` javac wrapper
2. Add protobuf Java client compilation
3. Create executable JAR packaging

#### Phase 4: C/C++ Foundation (FUTURE)
1. Implement `build/c/compile.py` gcc wrapper
2. Create library vendoring system
3. Add protobuf C++ client compilation

### Success Metrics
- **Zero external build tools** - No gradle, maven, cmake, npm
- **Single command builds** - `make build` compiles everything
- **Reproducible across machines** - Same output everywhere
- **Fast incremental builds** - Only rebuild what changed
- **Offline capable** - No network dependencies after setup

### Build Orchestration
```python
# build/orchestrator.py - Language-agnostic coordinator
def build_project(project_path):
    language = detect_language(project_path)
    
    if language == "python":
        return build_python_project(project_path)
    elif language == "kotlin":
        return build_kotlin_project(project_path)
    elif language == "java":
        return build_java_project(project_path)
    elif language == "c":
        return build_c_project(project_path)
    else:
        raise UnsupportedLanguage(language)
```

## Next Agent Instructions
1. **START WITH PYTHON** - Implement centralized Python environment
2. **ELIMINATE GRADLE** - Replace with pure kotlinc toolchain
3. **TEST INCREMENTALLY** - Ensure each language works before moving to next
4. **PRESERVE IDIOMS** - Respect language-specific conventions
5. **VENDOR DEPENDENCIES** - Reduce external network dependencies

**Ultimate Goal: "If it compiles, we can build it without external tools"**
