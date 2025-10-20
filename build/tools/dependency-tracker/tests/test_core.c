/**
 * @file test_core.c
 * @brief Core infrastructure tests for dependency tracker
 * @author Unhinged Development Team
 * 
 * @llm-type function
 * @llm-legend Tests fundamental dependency tracker operations and data structures
 * @llm-key Validates core initialization, memory management, and basic operations
 * @llm-map Foundation tests that must pass before any other functionality can work
 * @llm-contract Ensures core components are reliable and memory-safe
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "dependency_tracker.h"

// Test helper functions
static void setup_test_environment(void) {
    // Create test directories and files if needed
}

static void cleanup_test_environment(void) {
    // Clean up any test artifacts
}

// Core infrastructure tests
void test_dependency_tracker_create_destroy(void) {
    DependencyTracker* tracker = deptrack_create();
    TEST_ASSERT_NOT_NULL(tracker, "Tracker creation should succeed");
    
    if (tracker) {
        TEST_ASSERT_EQ(false, tracker->initialized, "New tracker should not be initialized");
        TEST_ASSERT_EQ(0, tracker->parser_count, "New tracker should have no parsers");
        TEST_ASSERT_NOT_NULL(&tracker->mutex, "Mutex should be initialized");
        
        deptrack_destroy(tracker);
    }
}

void test_dependency_tracker_initialization(void) {
    DependencyTracker* tracker = deptrack_create();
    TEST_ASSERT_NOT_NULL(tracker, "Tracker creation should succeed");
    
    if (tracker) {
        // Test initialization with NULL config (should use defaults)
        int result = deptrack_initialize(tracker, NULL);
        TEST_ASSERT_EQ(DEPTRACK_SUCCESS, result, "Initialization with NULL config should succeed");
        TEST_ASSERT_EQ(true, tracker->initialized, "Tracker should be marked as initialized");
        TEST_ASSERT_NOT_NULL(tracker->graph, "Graph should be created during initialization");
        TEST_ASSERT_NOT_NULL(tracker->cache, "Cache should be created during initialization");
        
        deptrack_destroy(tracker);
    }
}

void test_dependency_tracker_invalid_params(void) {
    // Test NULL parameter handling
    DependencyTracker* null_tracker = NULL;
    
    int result = deptrack_initialize(null_tracker, NULL);
    TEST_ASSERT_EQ(DEPTRACK_ERROR_INVALID_PARAM, result, "Initialize with NULL tracker should fail");
    
    result = deptrack_analyze_directory(null_tracker, "/some/path");
    TEST_ASSERT_EQ(DEPTRACK_ERROR_INVALID_PARAM, result, "Analyze with NULL tracker should fail");
    
    DependencyTracker* tracker = deptrack_create();
    if (tracker) {
        result = deptrack_analyze_directory(tracker, NULL);
        TEST_ASSERT_EQ(DEPTRACK_ERROR_INVALID_PARAM, result, "Analyze with NULL path should fail");
        
        deptrack_destroy(tracker);
    }
}

void test_version_information(void) {
    const char* version = deptrack_version_string();
    TEST_ASSERT_NOT_NULL(version, "Version string should not be NULL");
    TEST_ASSERT_STR_EQ(DEPTRACK_VERSION_STRING, version, "Version string should match constant");
}

void test_language_detection(void) {
    // Test language detection from file extensions
    Language lang;
    
    lang = deptrack_detect_language("test.kt");
    TEST_ASSERT_EQ(LANG_KOTLIN, lang, "Should detect Kotlin files");
    
    lang = deptrack_detect_language("test.kts");
    TEST_ASSERT_EQ(LANG_KOTLIN, lang, "Should detect Kotlin script files");
    
    lang = deptrack_detect_language("test.ts");
    TEST_ASSERT_EQ(LANG_TYPESCRIPT, lang, "Should detect TypeScript files");
    
    lang = deptrack_detect_language("test.tsx");
    TEST_ASSERT_EQ(LANG_TYPESCRIPT, lang, "Should detect TypeScript React files");
    
    lang = deptrack_detect_language("test.js");
    TEST_ASSERT_EQ(LANG_TYPESCRIPT, lang, "Should detect JavaScript files as TypeScript");
    
    lang = deptrack_detect_language("test.py");
    TEST_ASSERT_EQ(LANG_PYTHON, lang, "Should detect Python files");
    
    lang = deptrack_detect_language("test.yml");
    TEST_ASSERT_EQ(LANG_YAML, lang, "Should detect YAML files");
    
    lang = deptrack_detect_language("test.yaml");
    TEST_ASSERT_EQ(LANG_YAML, lang, "Should detect YAML files with .yaml extension");
    
    lang = deptrack_detect_language("test.proto");
    TEST_ASSERT_EQ(LANG_PROTO, lang, "Should detect Protocol Buffer files");
    
    lang = deptrack_detect_language("test.unknown");
    TEST_ASSERT_EQ(LANG_UNKNOWN, lang, "Should return UNKNOWN for unrecognized extensions");
    
    lang = deptrack_detect_language(NULL);
    TEST_ASSERT_EQ(LANG_UNKNOWN, lang, "Should return UNKNOWN for NULL input");
}

void test_language_name_conversion(void) {
    const char* name;
    
    name = deptrack_language_name(LANG_KOTLIN);
    TEST_ASSERT_STR_EQ("Kotlin", name, "Kotlin language name should be correct");
    
    name = deptrack_language_name(LANG_TYPESCRIPT);
    TEST_ASSERT_STR_EQ("TypeScript", name, "TypeScript language name should be correct");
    
    name = deptrack_language_name(LANG_PYTHON);
    TEST_ASSERT_STR_EQ("Python", name, "Python language name should be correct");
    
    name = deptrack_language_name(LANG_YAML);
    TEST_ASSERT_STR_EQ("YAML", name, "YAML language name should be correct");
    
    name = deptrack_language_name(LANG_PROTO);
    TEST_ASSERT_STR_EQ("Protocol Buffers", name, "Proto language name should be correct");
    
    name = deptrack_language_name(LANG_UNKNOWN);
    TEST_ASSERT_STR_EQ("Unknown", name, "Unknown language name should be correct");
}

void test_dependency_type_names(void) {
    const char* name;
    
    name = deptrack_dependency_type_name(DEP_INTERNAL);
    TEST_ASSERT_STR_EQ("Internal", name, "Internal dependency type name should be correct");
    
    name = deptrack_dependency_type_name(DEP_EXTERNAL);
    TEST_ASSERT_STR_EQ("External", name, "External dependency type name should be correct");
    
    name = deptrack_dependency_type_name(DEP_BUILD_TOOL);
    TEST_ASSERT_STR_EQ("Build Tool", name, "Build tool dependency type name should be correct");
    
    name = deptrack_dependency_type_name(DEP_CONFIG);
    TEST_ASSERT_STR_EQ("Configuration", name, "Config dependency type name should be correct");
    
    name = deptrack_dependency_type_name(DEP_RUNTIME);
    TEST_ASSERT_STR_EQ("Runtime", name, "Runtime dependency type name should be correct");
}

void test_error_handling(void) {
    const char* error_msg;
    
    error_msg = deptrack_error_string(DEPTRACK_SUCCESS);
    TEST_ASSERT_STR_EQ("Success", error_msg, "Success error message should be correct");
    
    error_msg = deptrack_error_string(DEPTRACK_ERROR_INVALID_PARAM);
    TEST_ASSERT_STR_EQ("Invalid parameter", error_msg, "Invalid param error message should be correct");
    
    error_msg = deptrack_error_string(DEPTRACK_ERROR_FILE_NOT_FOUND);
    TEST_ASSERT_STR_EQ("File not found", error_msg, "File not found error message should be correct");
    
    error_msg = deptrack_error_string(DEPTRACK_ERROR_MEMORY);
    TEST_ASSERT_STR_EQ("Memory allocation failed", error_msg, "Memory error message should be correct");
}

void test_thread_safety_basic(void) {
    DependencyTracker* tracker = deptrack_create();
    TEST_ASSERT_NOT_NULL(tracker, "Tracker creation should succeed");
    
    if (tracker) {
        // Test that mutex is properly initialized
        int lock_result = pthread_mutex_trylock(&tracker->mutex);
        TEST_ASSERT_EQ(0, lock_result, "Mutex should be lockable");
        
        if (lock_result == 0) {
            int unlock_result = pthread_mutex_unlock(&tracker->mutex);
            TEST_ASSERT_EQ(0, unlock_result, "Mutex should be unlockable");
        }
        
        deptrack_destroy(tracker);
    }
}

void test_memory_management(void) {
    // Test multiple create/destroy cycles
    for (int i = 0; i < 10; i++) {
        DependencyTracker* tracker = deptrack_create();
        TEST_ASSERT_NOT_NULL(tracker, "Tracker creation should succeed in loop");
        
        if (tracker) {
            int result = deptrack_initialize(tracker, NULL);
            TEST_ASSERT_EQ(DEPTRACK_SUCCESS, result, "Initialization should succeed in loop");
            
            deptrack_destroy(tracker);
        }
    }
}

// Test runner for core tests
void run_core_tests(void) {
    setup_test_environment();
    
    test_run("dependency_tracker_create_destroy", test_dependency_tracker_create_destroy);
    test_run("dependency_tracker_initialization", test_dependency_tracker_initialization);
    test_run("dependency_tracker_invalid_params", test_dependency_tracker_invalid_params);
    test_run("version_information", test_version_information);
    test_run("language_detection", test_language_detection);
    test_run("language_name_conversion", test_language_name_conversion);
    test_run("dependency_type_names", test_dependency_type_names);
    test_run("error_handling", test_error_handling);
    test_run("thread_safety_basic", test_thread_safety_basic);
    test_run("memory_management", test_memory_management);
    
    cleanup_test_environment();
}
