# Java Build System - Centralized Strategy

## Philosophy: "Java is bytecode, Maven is XML hell"

### Current State
- No pure Java services (Kotlin handles JVM)
- Generated Java clients from protobuf
- Gradle handles Kotlin compilation

### Target State: Pure JDK Toolchain
```
build/java/
├── compile.py          # javac wrapper with classpath magic
├── dependencies.txt    # Maven coordinates, no XML
├── runtime.py          # java -cp runner with main class detection
└── libs/              # Downloaded JAR dependencies
```

### Idioms to Preserve
- **"Java compiles to .class files"** - javac for compilation
- **"Classpath is everything"** - CLASSPATH environment variable
- **"JAR files are ZIP files with manifest"** - jar command for packaging
- **"Main-Class in manifest"** - Entry point specification
- **"Package structure mirrors directory structure"** - com/example/App.class

### Implementation Strategy
1. **Maven coordinate resolution** - Download JARs from Maven Central
2. **Classpath construction** - Build classpath from dependencies
3. **Source compilation** - `javac -cp $CLASSPATH -d output src/**/*.java`
4. **JAR packaging** - `jar cf app.jar -C output . --main-class=Main`
5. **Execution** - `java -cp app.jar:$CLASSPATH Main`

### Anti-Patterns to Avoid
- ❌ Maven pom.xml complexity
- ❌ Gradle build scripts
- ❌ Ant XML configurations
- ❌ IDE project files

### Success Criteria
- Single command: `build/java/compile.py generated/java/clients/`
- Zero build.xml/pom.xml files
- Reproducible builds
- Fast incremental compilation

### Dependencies Format
```
# build/java/dependencies.txt
com.google.protobuf:protobuf-java:3.21.0
io.grpc:grpc-core:1.50.0
io.grpc:grpc-stub:1.50.0
io.grpc:grpc-protobuf:1.50.0
```

### Compilation Strategy
```python
# Pseudo-code for build/java/compile.py
def compile_java_project(project_dir):
    java_files = find_java_files(project_dir)
    classpath = build_classpath_from_dependencies()
    
    # Compile all Java files
    cmd = f"javac -cp {classpath} -d output {' '.join(java_files)}"
    run_command(cmd)
    
    # Create JAR with manifest
    main_class = detect_main_class(java_files)
    create_jar_with_manifest("output", main_class)
```

### Package Management
```python
# Maven Central dependency resolution
def download_dependency(coordinate):
    # Parse "group:artifact:version"
    group, artifact, version = coordinate.split(':')
    
    # Construct Maven Central URL
    url = f"https://repo1.maven.org/maven2/{group.replace('.', '/')}/{artifact}/{version}/{artifact}-{version}.jar"
    
    # Download to build/java/libs/
    download_jar(url, f"libs/{artifact}-{version}.jar")
```

### Future: GraalVM Native
- **"Java compiles to native code"** - native-image for executables
- **"No JVM startup time"** - Instant execution
- **"Smaller memory footprint"** - No heap overhead

## Next Agent Instructions
1. Implement `build/java/compile.py` - javac wrapper
2. Create Maven Central dependency resolver
3. Build classpath construction logic
4. Test with generated Java protobuf clients
5. Add main class detection for executable JARs

**Principle: "If it runs on the JVM, we can build it with javac"**
