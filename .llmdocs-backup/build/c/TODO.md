# C/C++ Build System - Centralized Strategy

## Philosophy: "C is simple, keep it simple"

### Current State
- No centralized C/C++ build system
- Proto generation creates C++ clients
- No dependency management for C libraries

### Target State: Pure Compiler Toolchain
```
build/c/
├── compile.py          # gcc/clang wrapper with include magic
├── libraries.txt       # System libraries and vendored deps
├── link.py            # Linker with library resolution
└── vendor/            # Vendored C libraries (header-only preferred)
```

### Idioms to Preserve
- **"C compiles to object files"** - gcc -c for compilation units
- **"Linker combines object files"** - ld/gcc for final executable
- **"Headers define interfaces"** - .h files are contracts
- **"Libraries are collections of object files"** - .a/.so linking
- **"Make is overkill for simple projects"** - Direct compiler invocation

### Implementation Strategy
1. **Vendor dependencies** - Copy headers/sources into vendor/
2. **Include path management** - -I flags for header discovery
3. **Compilation units** - One .c/.cpp → one .o mapping
4. **Dependency tracking** - Parse #include for rebuild detection
5. **Static linking preferred** - Avoid .so complexity where possible

### Anti-Patterns to Avoid
- ❌ CMake complexity
- ❌ Autotools madness
- ❌ pkg-config dependencies
- ❌ System package managers

### Success Criteria
- Single command: `build/c/compile.py services/native-service/`
- Zero Makefiles/CMakeLists.txt
- Reproducible builds across platforms
- Fast incremental compilation

### Libraries Format
```
# build/c/libraries.txt
# System libraries (link with -l)
pthread
m
dl

# Vendored libraries (copy to vendor/)
https://github.com/cJSON/cJSON/raw/master/cJSON.h
https://github.com/cJSON/cJSON/raw/master/cJSON.c
```

### Compilation Strategy
```python
# Pseudo-code for build/c/compile.py
def compile_c_project(project_dir):
    sources = find_c_files(project_dir)
    objects = []
    
    for source in sources:
        if needs_rebuild(source):
            object_file = compile_unit(source, include_paths, defines)
            objects.append(object_file)
    
    executable = link_objects(objects, libraries)
    return executable
```

### Platform Considerations
- **Linux**: gcc, standard libraries
- **macOS**: clang, framework linking
- **Windows**: MinGW or clang, static linking preferred

### Future: WebAssembly
- **"C compiles to WASM"** - emscripten for browser targets
- **"WASM is portable"** - Single compilation for all platforms
- **"No system dependencies"** - Self-contained modules

## Next Agent Instructions
1. Implement `build/c/compile.py` - gcc/clang wrapper
2. Create library vendoring system
3. Build dependency tracking for headers
4. Test with simple C programs
5. Add protobuf C generation support

**Principle: "If it compiles with gcc, we can build it without Make"**
