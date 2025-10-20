/**
 * @file test_main.c
 * @brief Main test runner for dependency tracker
 * @author Unhinged Development Team
 * 
 * @llm-type function
 * @llm-legend Comprehensive test suite runner using Test-Driven Development methodology
 * @llm-key Orchestrates all test suites, provides detailed reporting, and ensures code quality
 * @llm-map Entry point for all dependency tracker testing, integrates with CI/CD pipeline
 * @llm-contract Runs all tests and returns appropriate exit codes for automation
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include "dependency_tracker.h"

// Test context global variable
TestContext* g_test_context = NULL;

// Test infrastructure implementation
void test_context_init(void) {
    g_test_context = malloc(sizeof(TestContext));
    if (g_test_context) {
        g_test_context->tests_run = 0;
        g_test_context->tests_passed = 0;
        g_test_context->tests_failed = 0;
        g_test_context->current_test = NULL;
    }
}

void test_context_cleanup(void) {
    if (g_test_context) {
        free(g_test_context->current_test);
        free(g_test_context);
        g_test_context = NULL;
    }
}

void test_run(const char* test_name, void (*test_func)(void)) {
    if (!g_test_context) return;

    // Set current test name
    free(g_test_context->current_test);
    g_test_context->current_test = strdup(test_name);

    // For now, always show test names (verbose will be handled by main)
    printf("  Running: %s\n", test_name);

    // Run the test
    test_func();

    printf("    ✅ Completed\n");
}

void test_print_summary(void) {
    if (!g_test_context) return;

    printf("\nTest Results:\n");
    printf("  Tests Run: %d\n", g_test_context->tests_run);
    printf("  Passed: %d\n", g_test_context->tests_passed);
    printf("  Failed: %d\n", g_test_context->tests_failed);
}

// Test function declarations
void run_core_tests(void);
void run_parser_tests(void);
void run_graph_tests(void);
void run_kotlin_parser_tests(void);
void run_typescript_parser_tests(void);
void run_python_parser_tests(void);
void run_yaml_parser_tests(void);
void run_integration_tests(void);
void run_utils_tests(void);

// Test suite structure
typedef struct {
    const char* name;
    void (*run_tests)(void);
    bool enabled;
} TestSuite;

static TestSuite test_suites[] = {
    {"Core Infrastructure", run_core_tests, true},
    {"Parser Framework", run_parser_tests, true},
    {"Graph Operations", run_graph_tests, true},
    {"Kotlin Parser", run_kotlin_parser_tests, true},
    {"TypeScript Parser", run_typescript_parser_tests, true},
    {"Python Parser", run_python_parser_tests, true},
    {"YAML Parser", run_yaml_parser_tests, true},
    {"Integration Tests", run_integration_tests, true},
    {"Utility Functions", run_utils_tests, true},
    {NULL, NULL, false}
};

// Command line options
static struct option long_options[] = {
    {"verbose", no_argument, 0, 'v'},
    {"suite", required_argument, 0, 's'},
    {"list", no_argument, 0, 'l'},
    {"help", no_argument, 0, 'h'},
    {"coverage", no_argument, 0, 'c'},
    {"benchmark", no_argument, 0, 'b'},
    {0, 0, 0, 0}
};

static bool verbose = false;
static bool run_coverage = false;
static bool run_benchmark = false;
static char* specific_suite = NULL;

void print_usage(const char* program_name) {
    printf("Usage: %s [OPTIONS]\n", program_name);
    printf("\nOptions:\n");
    printf("  -v, --verbose     Enable verbose output\n");
    printf("  -s, --suite NAME  Run specific test suite\n");
    printf("  -l, --list        List available test suites\n");
    printf("  -c, --coverage    Generate coverage report\n");
    printf("  -b, --benchmark   Run performance benchmarks\n");
    printf("  -h, --help        Show this help message\n");
    printf("\nTest Suites:\n");
    for (int i = 0; test_suites[i].name != NULL; i++) {
        printf("  - %s\n", test_suites[i].name);
    }
}

void list_test_suites(void) {
    printf("Available Test Suites:\n");
    for (int i = 0; test_suites[i].name != NULL; i++) {
        printf("  %d. %s\n", i + 1, test_suites[i].name);
    }
}

void print_test_header(const char* suite_name) {
    printf("\n");
    printf("=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "\n");
    printf("  RUNNING: %s\n", suite_name);
    printf("=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "\n");
}

void print_test_summary(void) {
    printf("\n");
    printf("=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "\n");
    printf("  TEST SUMMARY\n");
    printf("=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "\n");
    
    if (g_test_context) {
        printf("  Total Tests Run: %d\n", g_test_context->tests_run);
        printf("  Tests Passed:    %d\n", g_test_context->tests_passed);
        printf("  Tests Failed:    %d\n", g_test_context->tests_failed);
        
        if (g_test_context->tests_failed == 0) {
            printf("  Result:          ✅ ALL TESTS PASSED\n");
        } else {
            printf("  Result:          ❌ %d TESTS FAILED\n", g_test_context->tests_failed);
        }
        
        double pass_rate = (double)g_test_context->tests_passed / g_test_context->tests_run * 100.0;
        printf("  Pass Rate:       %.1f%%\n", pass_rate);
    }
    
    printf("=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "\n");
}

void run_benchmarks(void) {
    printf("\n🚀 Running Performance Benchmarks...\n");
    
    // TODO: Implement performance benchmarks
    // - Large file parsing benchmarks
    // - Memory usage benchmarks
    // - Concurrent processing benchmarks
    // - Graph analysis performance
    
    printf("⚠️  Benchmarks not yet implemented\n");
}

void generate_coverage_report(void) {
    printf("\n📊 Generating Coverage Report...\n");
    
    // Run gcov to generate coverage data
    int result = system("gcov *.gcno > /dev/null 2>&1");
    if (result == 0) {
        printf("✅ Coverage data generated\n");
        printf("📄 Coverage files: *.gcov\n");
        
        // Parse coverage data and show summary
        // TODO: Implement coverage parsing and reporting
        printf("⚠️  Coverage parsing not yet implemented\n");
    } else {
        printf("❌ Failed to generate coverage data\n");
        printf("💡 Make sure to compile with --coverage flag\n");
    }
}

int main(int argc, char* argv[]) {
    int option_index = 0;
    int c;
    
    // Parse command line arguments
    while ((c = getopt_long(argc, argv, "vs:lhcb", long_options, &option_index)) != -1) {
        switch (c) {
            case 'v':
                verbose = true;
                break;
            case 's':
                specific_suite = optarg;
                break;
            case 'l':
                list_test_suites();
                return 0;
            case 'h':
                print_usage(argv[0]);
                return 0;
            case 'c':
                run_coverage = true;
                break;
            case 'b':
                run_benchmark = true;
                break;
            case '?':
                print_usage(argv[0]);
                return 1;
            default:
                break;
        }
    }
    
    // Initialize test context
    test_context_init();
    
    printf("🧪 Unhinged Dependency Tracker Test Suite\n");
    printf("📅 Version: %s\n", DEPTRACK_VERSION_STRING);
    printf("🔧 Build: %s %s\n", __DATE__, __TIME__);
    
    if (verbose) {
        printf("🔍 Verbose mode enabled\n");
    }
    
    // Run specific test suite if requested
    if (specific_suite) {
        bool found = false;
        for (int i = 0; test_suites[i].name != NULL; i++) {
            if (strcmp(test_suites[i].name, specific_suite) == 0) {
                print_test_header(test_suites[i].name);
                test_suites[i].run_tests();
                found = true;
                break;
            }
        }
        
        if (!found) {
            printf("❌ Test suite '%s' not found\n", specific_suite);
            list_test_suites();
            test_context_cleanup();
            return 1;
        }
    } else {
        // Run all enabled test suites
        for (int i = 0; test_suites[i].name != NULL; i++) {
            if (test_suites[i].enabled) {
                print_test_header(test_suites[i].name);
                test_suites[i].run_tests();
            }
        }
    }
    
    // Print test summary
    print_test_summary();
    
    // Run additional features if requested
    if (run_benchmark) {
        run_benchmarks();
    }
    
    if (run_coverage) {
        generate_coverage_report();
    }
    
    // Determine exit code
    int exit_code = 0;
    if (g_test_context && g_test_context->tests_failed > 0) {
        exit_code = 1;
    }
    
    // Cleanup
    test_context_cleanup();
    
    return exit_code;
}
