/**
 * @file dependency_tracker.h
 * @brief Main header file for the Unhinged Dependency Tracker
 * @author Unhinged Development Team
 * @version 1.0.0
 * @date 2025-10-05
 * 
 * @llm-type interface
 * @llm-legend Comprehensive dependency tracking system for multi-language monorepo analysis
 * @llm-key Provides C-based high-performance parsing and analysis of dependency relationships
 * @llm-map Core interface for all dependency tracking operations across the Unhinged platform
 * @llm-axiom All dependency operations must be thread-safe and memory-efficient
 * @llm-contract Provides consistent API for dependency analysis across all supported languages
 * @llm-token deptrack: comprehensive dependency analysis and visualization system
 */

#ifndef DEPENDENCY_TRACKER_H
#define DEPENDENCY_TRACKER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>

#ifdef __cplusplus
extern "C" {
#endif

// Version information
#define DEPTRACK_VERSION_MAJOR 1
#define DEPTRACK_VERSION_MINOR 0
#define DEPTRACK_VERSION_PATCH 0
#define DEPTRACK_VERSION_STRING "1.0.0"

// Configuration constants
#define MAX_LANGUAGES 10
#define MAX_PATH_LENGTH 4096
#define MAX_NAME_LENGTH 256
#define MAX_VERSION_LENGTH 64
#define MAX_DEPENDENCIES 1000
#define MAX_FILE_EXTENSIONS 10

// Forward declarations
typedef struct DependencyTracker DependencyTracker;
typedef struct LanguageParser LanguageParser;
typedef struct DependencyGraph DependencyGraph;
typedef struct FileCache FileCache;
typedef struct ConfigManager ConfigManager;
typedef struct OutputGenerator OutputGenerator;

// Enumerations
typedef enum {
    LANG_KOTLIN,
    LANG_TYPESCRIPT,
    LANG_PYTHON,
    LANG_GO,
    LANG_RUST,
    LANG_YAML,
    LANG_SQL,
    LANG_PROTO,
    LANG_UNKNOWN
} Language;

typedef enum {
    DEP_INTERNAL,    // Internal project dependency
    DEP_EXTERNAL,    // External package dependency
    DEP_BUILD_TOOL,  // Build system dependency
    DEP_CONFIG,      // Configuration dependency
    DEP_RUNTIME      // Runtime dependency
} DependencyType;

typedef enum {
    RESOLVE_SUCCESS,
    RESOLVE_NOT_FOUND,
    RESOLVE_VERSION_CONFLICT,
    RESOLVE_CIRCULAR,
    RESOLVE_ERROR
} ResolveStatus;

typedef enum {
    NODE_SERVICE,
    NODE_LIBRARY,
    NODE_CONFIG,
    NODE_DATABASE,
    NODE_API,
    NODE_FEATURE
} NodeType;

typedef enum {
    OUTPUT_JSON,
    OUTPUT_DOT,
    OUTPUT_MERMAID,
    OUTPUT_HTML,
    OUTPUT_MARKDOWN
} OutputFormat;

// Core data structures
typedef struct {
    char* name;
    char* version;
    DependencyType type;
    char* source_file;
    int line_number;
    ResolveStatus status;
    void* metadata;
} Dependency;

typedef struct {
    char* filepath;
    Language language;
    time_t last_modified;
    Dependency* dependencies;
    size_t dep_count;
    size_t dep_capacity;
    void* parse_metadata;
} ParsedFile;

typedef struct {
    char* id;
    char* name;
    NodeType type;
    char* filepath;
    char** dependencies;
    size_t dep_count;
    void* metadata;
} GraphNode;

typedef struct {
    char* from_id;
    char* to_id;
    DependencyType type;
    char* version_constraint;
    void* metadata;
} GraphEdge;

typedef struct DependencyGraph {
    GraphNode* nodes;
    GraphEdge* edges;
    size_t node_count;
    size_t edge_count;
    size_t node_capacity;
    size_t edge_capacity;
    void* node_index;  // HashMap for fast lookups
    pthread_mutex_t mutex;  // Thread safety for concurrent graph modifications
} DependencyGraph;

// Parser function types
typedef ParsedFile* (*ParseFunction)(const char* filepath);
typedef ResolveStatus (*ResolveFunction)(Dependency* dep, void* context);

typedef struct LanguageParser {
    Language language;
    char* name;
    char** file_extensions;
    size_t extension_count;
    ParseFunction parse_file;
    ResolveFunction resolve_deps;
    void* config;
} LanguageParser;

// Main tracker structure
typedef struct DependencyTracker {
    LanguageParser* parsers[MAX_LANGUAGES];
    size_t parser_count;
    DependencyGraph* graph;
    FileCache* cache;
    ConfigManager* config;
    OutputGenerator* output;
    pthread_mutex_t mutex;
    bool initialized;
} DependencyTracker;

// Core API functions
DependencyTracker* deptrack_create(void);
void deptrack_destroy(DependencyTracker* tracker);
int deptrack_initialize(DependencyTracker* tracker, const char* config_path);
int deptrack_analyze_directory(DependencyTracker* tracker, const char* root_path);
int deptrack_analyze_file(DependencyTracker* tracker, const char* filepath);
DependencyGraph* deptrack_get_graph(DependencyTracker* tracker);
int deptrack_generate_output(DependencyTracker* tracker, OutputFormat format, const char* output_path);

// Graph operations
DependencyGraph* graph_create(void);
void graph_destroy(DependencyGraph* graph);
int graph_add_node(DependencyGraph* graph, const GraphNode* node);
int graph_add_edge(DependencyGraph* graph, const GraphEdge* edge);
GraphNode* graph_find_node(DependencyGraph* graph, const char* id);
int graph_detect_cycles(DependencyGraph* graph);

// Parser registration
int deptrack_register_parser(DependencyTracker* tracker, LanguageParser* parser);
LanguageParser* deptrack_get_parser(DependencyTracker* tracker, Language lang);
Language deptrack_detect_language(const char* filepath);

// Utility functions
const char* deptrack_version_string(void);
const char* deptrack_language_name(Language lang);
const char* deptrack_dependency_type_name(DependencyType type);
const char* deptrack_resolve_status_name(ResolveStatus status);

// Error handling
typedef enum {
    DEPTRACK_SUCCESS = 0,
    DEPTRACK_ERROR_INVALID_PARAM = -1,
    DEPTRACK_ERROR_FILE_NOT_FOUND = -2,
    DEPTRACK_ERROR_PARSE_FAILED = -3,
    DEPTRACK_ERROR_MEMORY = -4,
    DEPTRACK_ERROR_THREAD = -5,
    DEPTRACK_ERROR_CONFIG = -6,
    DEPTRACK_ERROR_OUTPUT = -7
} DeptrackError;

const char* deptrack_error_string(DeptrackError error);

// Testing support
#ifdef TESTING
typedef struct {
    int tests_run;
    int tests_passed;
    int tests_failed;
    char* current_test;
} TestContext;

extern TestContext* g_test_context;

#define TEST_ASSERT(condition, message) \
    do { \
        g_test_context->tests_run++; \
        if (condition) { \
            g_test_context->tests_passed++; \
        } else { \
            g_test_context->tests_failed++; \
            fprintf(stderr, "FAIL: %s - %s\n", g_test_context->current_test, message); \
        } \
    } while(0)

#define TEST_ASSERT_EQ(expected, actual, message) \
    TEST_ASSERT((expected) == (actual), message)

#define TEST_ASSERT_STR_EQ(expected, actual, message) \
    TEST_ASSERT(strcmp((expected), (actual)) == 0, message)

#define TEST_ASSERT_NOT_NULL(ptr, message) \
    TEST_ASSERT((ptr) != NULL, message)

#define TEST_ASSERT_NULL(ptr, message) \
    TEST_ASSERT((ptr) == NULL, message)

void test_context_init(void);
void test_context_cleanup(void);
void test_run(const char* test_name, void (*test_func)(void));
void test_print_summary(void);

#endif // TESTING

#ifdef __cplusplus
}
#endif

#endif // DEPENDENCY_TRACKER_H
