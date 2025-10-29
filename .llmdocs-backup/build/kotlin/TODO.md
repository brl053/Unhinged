# Kotlin/JVM Build System - Centralized Strategy

## Philosophy: "Kotlin is Java with better syntax, treat it as such"

### Current State
- Gradle scattered across `platforms/`, `libs/`, `generated/`
- No centralized dependency management
- Build system coexistence chaos

### Target State: Pure JVM Toolchain
```
build/kotlin/
├── compile.py          # kotlinc wrapper with classpath magic
├── dependencies.txt    # Maven coordinates, no Gradle
├── runtime.py          # java -cp runner
└── stdlib/            # Kotlin stdlib + coroutines (vendored)
```

### Idioms to Preserve
- **"Kotlin compiles to JVM bytecode"** - Use kotlinc directly
- **"Classpath is king"** - Manual dependency resolution via Maven Central
- **"JAR files are just ZIP files"** - Direct manipulation, no build tools
- **"Main-Class manifest"** - Executable JARs without frameworks

### Implementation Strategy
1. **Vendor Kotlin stdlib** - Download kotlin-stdlib.jar, kotlin-coroutines.jar
2. **Maven coordinate resolution** - Parse dependencies.txt, download JARs
3. **Classpath construction** - Build classpath string from JARs
4. **Direct kotlinc invocation** - `kotlinc -cp $CLASSPATH -d output src/**/*.kt`
5. **JAR packaging** - `jar cf app.jar -C output .` with manifest

### Anti-Patterns to Avoid
- ❌ Gradle wrapper scripts
- ❌ Build.gradle.kts complexity
- ❌ Plugin ecosystems
- ❌ IDE-specific configurations

### Success Criteria
- Single command: `build/kotlin/compile.py platform/service-name/`
- Zero Gradle files
- Reproducible builds
- Fast incremental compilation

### Dependencies Format
```
# build/kotlin/dependencies.txt
org.jetbrains.kotlin:kotlin-stdlib:1.9.20
org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3
io.ktor:ktor-server-core:2.3.5
```

### Future: Kotlin Native
- **"Kotlin/Native compiles to machine code"** - konanc for system services
- **"No JVM overhead"** - Direct executable generation
- **"Interop with C"** - Native library integration

## Next Agent Instructions
1. Implement `build/kotlin/compile.py` - kotlinc wrapper
2. Create dependency resolver for Maven Central
3. Build classpath construction logic
4. Test with existing Kotlin services
5. Eliminate all Gradle files

**Principle: "If it runs on the JVM, we can build it without Gradle"**
