/**
 * @file dependency_tracker.c
 * @brief Core dependency tracker implementation
 * @author Unhinged Development Team
 * 
 * @llm-type service
 * @llm-legend Core dependency tracking service that orchestrates multi-language dependency analysis
 * @llm-key Manages parsers, graph construction, and output generation with thread-safe operations
 * @llm-map Central coordinator for all dependency tracking operations in the Unhinged platform
 * @llm-axiom All operations must be thread-safe and handle memory allocation failures gracefully
 * @llm-contract Provides consistent API for dependency analysis with proper error handling
 * @llm-token deptrack-core: main dependency tracking orchestration service
 */

#include "dependency_tracker.h"
#include <pthread.h>

// File cache structure (stub)
struct FileCache {
    void* data;  // TODO: Implement hash table for file caching
    pthread_mutex_t mutex;
};

// Config manager structure (stub)
struct ConfigManager {
    char* config_path;
    void* config_data;  // TODO: Implement configuration storage
};

// Output generator structure (stub)
struct OutputGenerator {
    OutputFormat format;
    char* template_path;
    void* options;
};

// Language name mapping
static const char* language_names[] = {
    [LANG_KOTLIN] = "Kotlin",
    [LANG_TYPESCRIPT] = "TypeScript", 
    [LANG_PYTHON] = "Python",
    [LANG_GO] = "Go",
    [LANG_RUST] = "Rust",
    [LANG_YAML] = "YAML",
    [LANG_SQL] = "SQL",
    [LANG_PROTO] = "Protocol Buffers",
    [LANG_UNKNOWN] = "Unknown"
};

// Dependency type name mapping
static const char* dependency_type_names[] = {
    [DEP_INTERNAL] = "Internal",
    [DEP_EXTERNAL] = "External",
    [DEP_BUILD_TOOL] = "Build Tool",
    [DEP_CONFIG] = "Configuration",
    [DEP_RUNTIME] = "Runtime"
};

// Error message mapping
static const char* error_messages[] = {
    [DEPTRACK_SUCCESS] = "Success",
    [-DEPTRACK_ERROR_INVALID_PARAM] = "Invalid parameter",
    [-DEPTRACK_ERROR_FILE_NOT_FOUND] = "File not found",
    [-DEPTRACK_ERROR_PARSE_FAILED] = "Parse failed",
    [-DEPTRACK_ERROR_MEMORY] = "Memory allocation failed",
    [-DEPTRACK_ERROR_THREAD] = "Thread operation failed",
    [-DEPTRACK_ERROR_CONFIG] = "Configuration error",
    [-DEPTRACK_ERROR_OUTPUT] = "Output generation failed"
};

DependencyTracker* deptrack_create(void) {
    DependencyTracker* tracker = calloc(1, sizeof(DependencyTracker));
    if (!tracker) {
        return NULL;
    }
    
    // Initialize mutex
    if (pthread_mutex_init(&tracker->mutex, NULL) != 0) {
        free(tracker);
        return NULL;
    }
    
    tracker->initialized = false;
    tracker->parser_count = 0;
    
    return tracker;
}

void deptrack_destroy(DependencyTracker* tracker) {
    if (!tracker) return;
    
    // Destroy mutex
    pthread_mutex_destroy(&tracker->mutex);
    
    // Clean up graph
    if (tracker->graph) {
        graph_destroy(tracker->graph);
    }
    
    // Clean up cache
    if (tracker->cache) {
        pthread_mutex_destroy(&tracker->cache->mutex);
        free(tracker->cache);
    }
    
    // Clean up config
    if (tracker->config) {
        free(tracker->config->config_path);
        free(tracker->config);
    }
    
    // Clean up output generator
    if (tracker->output) {
        free(tracker->output->template_path);
        free(tracker->output);
    }
    
    // Clean up parsers
    for (size_t i = 0; i < tracker->parser_count; i++) {
        if (tracker->parsers[i]) {
            // TODO: Implement parser cleanup
            free(tracker->parsers[i]);
        }
    }
    
    free(tracker);
}

int deptrack_initialize(DependencyTracker* tracker, const char* config_path) {
    if (!tracker) {
        return DEPTRACK_ERROR_INVALID_PARAM;
    }
    
    pthread_mutex_lock(&tracker->mutex);
    
    // Create graph
    tracker->graph = graph_create();
    if (!tracker->graph) {
        pthread_mutex_unlock(&tracker->mutex);
        return DEPTRACK_ERROR_MEMORY;
    }
    
    // Create cache
    tracker->cache = calloc(1, sizeof(FileCache));
    if (!tracker->cache) {
        pthread_mutex_unlock(&tracker->mutex);
        return DEPTRACK_ERROR_MEMORY;
    }
    
    if (pthread_mutex_init(&tracker->cache->mutex, NULL) != 0) {
        free(tracker->cache);
        tracker->cache = NULL;
        pthread_mutex_unlock(&tracker->mutex);
        return DEPTRACK_ERROR_THREAD;
    }
    
    // Create config manager
    tracker->config = calloc(1, sizeof(ConfigManager));
    if (!tracker->config) {
        pthread_mutex_unlock(&tracker->mutex);
        return DEPTRACK_ERROR_MEMORY;
    }
    
    if (config_path) {
        tracker->config->config_path = strdup(config_path);
    }
    
    // Create output generator
    tracker->output = calloc(1, sizeof(OutputGenerator));
    if (!tracker->output) {
        pthread_mutex_unlock(&tracker->mutex);
        return DEPTRACK_ERROR_MEMORY;
    }
    
    tracker->initialized = true;
    
    pthread_mutex_unlock(&tracker->mutex);
    return DEPTRACK_SUCCESS;
}

int deptrack_analyze_directory(DependencyTracker* tracker, const char* root_path) {
    if (!tracker || !root_path) {
        return DEPTRACK_ERROR_INVALID_PARAM;
    }
    
    if (!tracker->initialized) {
        return DEPTRACK_ERROR_CONFIG;
    }
    
    // TODO: Implement directory analysis
    // - Walk directory tree
    // - Identify files by language
    // - Parse each file with appropriate parser
    // - Build dependency graph
    
    return DEPTRACK_SUCCESS;
}

// Forward declaration for parser functions
extern ParsedFile* parse_kotlin_file(const char* filepath);

int deptrack_analyze_file(DependencyTracker* tracker, const char* filepath) {
    if (!tracker || !filepath) {
        return DEPTRACK_ERROR_INVALID_PARAM;
    }

    if (!tracker->initialized) {
        return DEPTRACK_ERROR_CONFIG;
    }

    printf("🔍 Analyzing file: %s\n", filepath);

    // Detect language
    Language lang = deptrack_detect_language(filepath);
    printf("  Language detected: %s\n", deptrack_language_name(lang));

    // Parse file based on language
    ParsedFile* parsed = NULL;
    switch (lang) {
        case LANG_KOTLIN:
            parsed = parse_kotlin_file(filepath);
            break;
        case LANG_TYPESCRIPT:
            // parsed = parse_typescript_file(filepath);
            printf("  TypeScript parsing not yet implemented\n");
            break;
        case LANG_PYTHON:
            // parsed = parse_python_file(filepath);
            printf("  Python parsing not yet implemented\n");
            break;
        default:
            printf("  No parser available for this language\n");
            return DEPTRACK_SUCCESS;
    }

    if (!parsed) {
        printf("  Failed to parse file\n");
        return DEPTRACK_ERROR_PARSE_FAILED;
    }

    printf("  Found %zu dependencies\n", parsed->dep_count);

    // Add to graph (simplified - just print for now)
    for (size_t i = 0; i < parsed->dep_count; i++) {
        Dependency* dep = &parsed->dependencies[i];
        printf("    - %s (%s) at line %d\n",
               dep->name,
               deptrack_dependency_type_name(dep->type),
               dep->line_number);
    }

    // TODO: Actually add to graph structure

    // Cleanup
    if (parsed->dependencies) {
        for (size_t i = 0; i < parsed->dep_count; i++) {
            free(parsed->dependencies[i].name);
            free(parsed->dependencies[i].version);
            free(parsed->dependencies[i].source_file);
        }
        free(parsed->dependencies);
    }
    free(parsed->filepath);
    free(parsed);

    return DEPTRACK_SUCCESS;
}

DependencyGraph* deptrack_get_graph(DependencyTracker* tracker) {
    if (!tracker) {
        return NULL;
    }
    
    return tracker->graph;
}

int deptrack_generate_output(DependencyTracker* tracker, OutputFormat format, const char* output_path) {
    if (!tracker || !output_path) {
        return DEPTRACK_ERROR_INVALID_PARAM;
    }
    
    // TODO: Implement output generation
    return DEPTRACK_SUCCESS;
}

Language deptrack_detect_language(const char* filepath) {
    if (!filepath) {
        return LANG_UNKNOWN;
    }
    
    const char* ext = strrchr(filepath, '.');
    if (!ext) {
        return LANG_UNKNOWN;
    }
    
    ext++; // Skip the dot
    
    if (strcmp(ext, "kt") == 0 || strcmp(ext, "kts") == 0) {
        return LANG_KOTLIN;
    } else if (strcmp(ext, "ts") == 0 || strcmp(ext, "tsx") == 0 || strcmp(ext, "js") == 0 || strcmp(ext, "jsx") == 0) {
        return LANG_TYPESCRIPT;
    } else if (strcmp(ext, "py") == 0) {
        return LANG_PYTHON;
    } else if (strcmp(ext, "go") == 0) {
        return LANG_GO;
    } else if (strcmp(ext, "rs") == 0) {
        return LANG_RUST;
    } else if (strcmp(ext, "yml") == 0 || strcmp(ext, "yaml") == 0) {
        return LANG_YAML;
    } else if (strcmp(ext, "sql") == 0) {
        return LANG_SQL;
    } else if (strcmp(ext, "proto") == 0) {
        return LANG_PROTO;
    }
    
    return LANG_UNKNOWN;
}

const char* deptrack_version_string(void) {
    return DEPTRACK_VERSION_STRING;
}

const char* deptrack_language_name(Language lang) {
    if (lang >= 0 && lang < sizeof(language_names) / sizeof(language_names[0])) {
        return language_names[lang];
    }
    return "Unknown";
}

const char* deptrack_dependency_type_name(DependencyType type) {
    if (type >= 0 && type < sizeof(dependency_type_names) / sizeof(dependency_type_names[0])) {
        return dependency_type_names[type];
    }
    return "Unknown";
}

const char* deptrack_error_string(DeptrackError error) {
    int index = (error <= 0) ? -error : 0;
    size_t array_size = sizeof(error_messages) / sizeof(error_messages[0]);

    // Fix signed/unsigned comparison and add proper bounds checking
    if (index >= 0 && index < (int)array_size) {
        return error_messages[index];
    }
    return "Unknown error";
}
