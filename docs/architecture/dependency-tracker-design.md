# 🔍 Dependency Tracker Architecture - Unhinged Platform

> **Purpose**: Design comprehensive C-based dependency tracker for the entire monorepo
> **Approach**: Test-Driven Development with feature DAG generation
> **Scope**: Multi-language support (Kotlin, TypeScript, Python, Go, Rust, YAML, SQL)

## 🎯 **Design Goals**

### **Primary Objectives**
1. **Speed**: C implementation for fast analysis of large codebases
2. **Completeness**: Track all dependency types across all languages
3. **Accuracy**: Precise dependency resolution with version tracking
4. **Visualization**: Generate feature DAGs and dependency graphs
5. **Integration**: Seamless integration with existing documentation system

### **Performance Requirements**
- **Parse 1000+ files in <5 seconds**
- **Memory efficient**: <100MB for entire Unhinged monorepo
- **Incremental updates**: Only reparse changed files
- **Concurrent processing**: Multi-threaded file analysis

## 🏗️ **Architecture Overview**

### **Core Components**

```c
// Main dependency tracker structure
typedef struct {
    LanguageParser* parsers[MAX_LANGUAGES];
    DependencyGraph* graph;
    FileCache* cache;
    ConfigManager* config;
    OutputGenerator* output;
} DependencyTracker;

// Language-specific parsers
typedef struct {
    char* language;
    char** file_extensions;
    ParseFunction parse_file;
    ResolveFunction resolve_deps;
} LanguageParser;

// Dependency graph representation
typedef struct {
    Node* nodes;
    Edge* edges;
    size_t node_count;
    size_t edge_count;
    HashMap* node_index;
} DependencyGraph;
```

### **Language Support Matrix**

| Language | Build Files | Import/Require | Version Files | Status |
|----------|-------------|----------------|---------------|---------|
| **Kotlin** | `build.gradle.kts`, `settings.gradle.kts` | `import`, `package` | `gradle.properties` | ✅ Priority 1 |
| **TypeScript** | `package.json`, `tsconfig.json` | `import`, `require` | `package-lock.json` | ✅ Priority 1 |
| **Python** | `requirements.txt`, `pyproject.toml` | `import`, `from` | `Pipfile.lock` | ✅ Priority 1 |
| **Go** | `go.mod`, `go.sum` | `import` | `go.mod` | ✅ Priority 2 |
| **Rust** | `Cargo.toml`, `Cargo.lock` | `use`, `extern crate` | `Cargo.lock` | ✅ Priority 2 |
| **YAML** | `docker-compose.yml`, `*.yml` | `depends_on`, `volumes` | N/A | ✅ Priority 1 |
| **SQL** | `*.sql` | References, FKs | Migration versions | ✅ Priority 3 |
| **Proto** | `*.proto` | `import` | N/A | ✅ Priority 1 |

## 🔧 **Detailed Component Design**

### **1. File Parser Engine**

```c
// Generic file parser interface
typedef struct {
    char* filepath;
    char* language;
    time_t last_modified;
    Dependency* dependencies;
    size_t dep_count;
    ParseMetadata* metadata;
} ParsedFile;

// Dependency representation
typedef struct {
    char* name;
    char* version;
    DependencyType type;  // INTERNAL, EXTERNAL, BUILD_TOOL
    char* source_file;
    int line_number;
    ResolveStatus status; // RESOLVED, UNRESOLVED, ERROR
} Dependency;

// Parser functions for each language
ParsedFile* parse_kotlin_file(const char* filepath);
ParsedFile* parse_typescript_file(const char* filepath);
ParsedFile* parse_python_file(const char* filepath);
ParsedFile* parse_yaml_file(const char* filepath);
```

### **2. Dependency Resolution Engine**

```c
// Dependency resolver
typedef struct {
    HashMap* package_registry;  // External packages
    HashMap* internal_modules;  // Internal project modules
    VersionResolver* version_resolver;
    ConflictDetector* conflict_detector;
} DependencyResolver;

// Resolution functions
ResolveResult resolve_dependency(Dependency* dep, DependencyResolver* resolver);
ConflictReport* detect_version_conflicts(DependencyGraph* graph);
UpdatePlan* suggest_updates(DependencyGraph* graph);
```

### **3. Graph Generation & Analysis**

```c
// Graph analysis functions
typedef struct {
    Node** critical_path;
    size_t path_length;
    float complexity_score;
    CircularDep* circular_deps;
    size_t circular_count;
} GraphAnalysis;

GraphAnalysis* analyze_dependency_graph(DependencyGraph* graph);
FeatureDAG* generate_feature_dag(DependencyGraph* graph);
ComponentMap* identify_components(DependencyGraph* graph);
```

### **4. Output Generation**

```c
// Output formats
typedef enum {
    OUTPUT_JSON,
    OUTPUT_DOT,      // Graphviz
    OUTPUT_MERMAID,  // Mermaid diagrams
    OUTPUT_HTML,     // Interactive visualization
    OUTPUT_MARKDOWN  // Documentation
} OutputFormat;

// Output generator
typedef struct {
    OutputFormat format;
    char* template_path;
    RenderOptions* options;
} OutputGenerator;

int generate_output(DependencyGraph* graph, OutputGenerator* gen, const char* output_path);
```

## 🧪 **Test-Driven Development Plan**

### **Phase 1: Core Infrastructure Tests**

```c
// test_core.c
void test_dependency_tracker_init();
void test_file_cache_operations();
void test_config_manager_loading();
void test_memory_management();

// test_parsers.c  
void test_kotlin_gradle_parsing();
void test_typescript_package_parsing();
void test_python_requirements_parsing();
void test_yaml_compose_parsing();

// test_graph.c
void test_graph_creation();
void test_node_insertion();
void test_edge_creation();
void test_circular_detection();
```

### **Phase 2: Language Parser Tests**

```c
// test_kotlin_parser.c
void test_parse_build_gradle_kts();
void test_parse_kotlin_imports();
void test_resolve_kotlin_dependencies();
void test_kotlin_version_extraction();

// test_typescript_parser.c
void test_parse_package_json();
void test_parse_typescript_imports();
void test_resolve_npm_dependencies();
void test_typescript_version_conflicts();

// test_python_parser.c
void test_parse_requirements_txt();
void test_parse_python_imports();
void test_resolve_pip_dependencies();
void test_python_virtual_env_detection();
```

### **Phase 3: Integration Tests**

```c
// test_integration.c
void test_full_monorepo_analysis();
void test_cross_language_dependencies();
void test_docker_compose_integration();
void test_performance_large_codebase();
void test_incremental_updates();
```

## 📊 **Feature DAG Generation**

### **DAG Node Types**

```c
typedef enum {
    NODE_SERVICE,      // Microservice
    NODE_LIBRARY,      // Shared library
    NODE_CONFIG,       // Configuration file
    NODE_DATABASE,     // Database schema
    NODE_API,          // API endpoint
    NODE_FEATURE       // Business feature
} NodeType;

typedef struct {
    char* id;
    char* name;
    NodeType type;
    char** dependencies;
    size_t dep_count;
    FeatureMetadata* metadata;
} FeatureNode;
```

### **DAG Analysis Capabilities**

1. **Critical Path Analysis**: Identify longest dependency chains
2. **Bottleneck Detection**: Find nodes with highest fan-in/fan-out
3. **Impact Analysis**: Determine blast radius of changes
4. **Parallel Execution**: Identify independent work streams
5. **Risk Assessment**: Highlight fragile dependency relationships

## 🔗 **Integration Points**

### **Make Integration**

```makefile
# New dependency tracking targets
deps-analyze: ## Analyze all dependencies in monorepo
	@./tools/dependency-tracker/bin/deptrack analyze --output=json

deps-graph: ## Generate dependency visualization
	@./tools/dependency-tracker/bin/deptrack graph --format=mermaid

deps-validate: ## Validate dependency consistency
	@./tools/dependency-tracker/bin/deptrack validate --strict

deps-update: ## Check for available updates
	@./tools/dependency-tracker/bin/deptrack update --dry-run

deps-feature-dag: ## Generate feature dependency DAG
	@./tools/dependency-tracker/bin/deptrack feature-dag --output=docs/architecture/
```

### **Documentation System Integration**

```c
// Integration with existing docs system
int generate_dependency_docs(DependencyGraph* graph, const char* docs_path);
int update_architecture_diagrams(FeatureDAG* dag, const char* output_path);
int validate_documentation_links(DependencyGraph* graph, const char* docs_root);
```

## 🚀 **Implementation Roadmap**

### **Week 1: Core Infrastructure**
- [ ] Set up C project structure with CMake
- [ ] Implement core data structures (Graph, Node, Edge)
- [ ] Create file system utilities and caching
- [ ] Write comprehensive test suite for core components

### **Week 2: Language Parsers**
- [ ] Implement Kotlin/Gradle parser
- [ ] Implement TypeScript/npm parser  
- [ ] Implement Python/pip parser
- [ ] Implement YAML/Docker parser

### **Week 3: Graph Analysis**
- [ ] Implement dependency resolution engine
- [ ] Add circular dependency detection
- [ ] Create graph analysis algorithms
- [ ] Build feature DAG generator

### **Week 4: Integration & Output**
- [ ] Create output generators (JSON, DOT, Mermaid)
- [ ] Integrate with Make system
- [ ] Connect to documentation automation
- [ ] Performance optimization and testing

## 📈 **Success Metrics**

### **Performance Targets**
- **Parse Speed**: <5 seconds for entire Unhinged monorepo
- **Memory Usage**: <100MB peak memory consumption
- **Accuracy**: >95% dependency resolution accuracy
- **Coverage**: 100% of supported file types parsed

### **Quality Metrics**
- **Test Coverage**: >90% code coverage
- **Documentation**: Complete API documentation
- **Integration**: Seamless Make workflow integration
- **Usability**: Clear error messages and helpful output

---

**Next Step**: Implement TDD test suite and begin core infrastructure development.
