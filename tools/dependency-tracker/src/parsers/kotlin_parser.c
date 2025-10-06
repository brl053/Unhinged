/**
 * @file kotlin_parser.c
 * @brief Kotlin/Gradle parser implementation
 * @author Unhinged Development Team
 */

#include "dependency_tracker.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

// Simple Gradle dependency parser
ParsedFile* parse_kotlin_gradle_file(const char* filepath) {
    FILE* file = fopen(filepath, "r");
    if (!file) {
        return NULL;
    }

    ParsedFile* parsed = calloc(1, sizeof(ParsedFile));
    if (!parsed) {
        fclose(file);
        return NULL;
    }

    parsed->filepath = strdup(filepath);
    parsed->language = LANG_KOTLIN;
    parsed->dependencies = calloc(MAX_DEPENDENCIES, sizeof(Dependency));
    parsed->dep_count = 0;
    parsed->dep_capacity = MAX_DEPENDENCIES;

    char line[1024];
    int line_number = 0;

    while (fgets(line, sizeof(line), file) && parsed->dep_count < MAX_DEPENDENCIES) {
        line_number++;

        // Remove newline
        line[strcspn(line, "\n")] = 0;

        // Look for implementation("...") or api("...") dependencies
        char* impl_start = strstr(line, "implementation(\"");
        char* api_start = strstr(line, "api(\"");
        char* dep_start = impl_start ? impl_start + 16 : (api_start ? api_start + 5 : NULL);

        if (dep_start) {
            char* dep_end = strchr(dep_start, '"');
            if (dep_end) {
                size_t dep_len = dep_end - dep_start;
                if (dep_len > 0 && dep_len < MAX_NAME_LENGTH) {
                    Dependency* dep = &parsed->dependencies[parsed->dep_count];
                    dep->name = strndup(dep_start, dep_len);
                    dep->type = strstr(dep->name, "org.jetbrains.kotlin") ? DEP_BUILD_TOOL : DEP_EXTERNAL;
                    dep->source_file = strdup(filepath);
                    dep->line_number = line_number;
                    dep->status = RESOLVE_SUCCESS;
                    dep->version = strdup("unknown"); // TODO: Parse version

                    parsed->dep_count++;

                    printf("  Found dependency: %s (line %d)\n", dep->name, line_number);
                }
            }
        }
    }

    fclose(file);
    return parsed;
}

// Main parser entry point
ParsedFile* parse_kotlin_file(const char* filepath) {
    if (!filepath) return NULL;

    // Check if it's a Gradle file
    if (strstr(filepath, "build.gradle.kts") || strstr(filepath, "build.gradle")) {
        return parse_kotlin_gradle_file(filepath);
    }

    // For .kt files, we'd parse imports here (stub for now)
    return NULL;
}
