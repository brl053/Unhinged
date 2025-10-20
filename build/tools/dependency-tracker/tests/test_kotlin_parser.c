/**
 * @file test_kotlin_parser.c
 * @brief Kotlin parser tests
 */

#include "dependency_tracker.h"

void test_kotlin_gradle_parsing(void) {
    // TODO: Implement Kotlin Gradle parsing tests
    TEST_ASSERT(true, "Kotlin Gradle parsing test placeholder");
}

void test_kotlin_import_parsing(void) {
    // TODO: Implement Kotlin import parsing tests
    TEST_ASSERT(true, "Kotlin import parsing test placeholder");
}

void run_kotlin_parser_tests(void) {
    test_run("kotlin_gradle_parsing", test_kotlin_gradle_parsing);
    test_run("kotlin_import_parsing", test_kotlin_import_parsing);
}
