/**
 * @file main.c
 * @brief Main entry point for dependency tracker CLI
 * @author Unhinged Development Team
 * 
 * @llm-type function
 * @llm-legend Command-line interface for comprehensive dependency analysis across the Unhinged monorepo
 * @llm-key Provides subcommands for analysis, graph generation, validation, and feature DAG creation
 * @llm-map Entry point for dependency tracking operations, integrates with Make system and CI/CD
 * @llm-contract Provides consistent CLI interface with proper exit codes and error handling
 * @llm-token deptrack-cli: command-line interface for dependency analysis and visualization
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include "dependency_tracker.h"

// Command definitions
typedef enum {
    CMD_ANALYZE,
    CMD_GRAPH,
    CMD_VALIDATE,
    CMD_UPDATE,
    CMD_FEATURE_DAG,
    CMD_HELP,
    CMD_VERSION,
    CMD_UNKNOWN
} Command;

// Global options
typedef struct {
    Command command;
    char* root_path;
    char* output_path;
    OutputFormat output_format;
    bool verbose;
    bool dry_run;
    bool strict;
} CliOptions;

static struct option long_options[] = {
    {"help", no_argument, 0, 'h'},
    {"version", no_argument, 0, 'V'},
    {"verbose", no_argument, 0, 'v'},
    {"output", required_argument, 0, 'o'},
    {"format", required_argument, 0, 'f'},
    {"dry-run", no_argument, 0, 'n'},
    {"strict", no_argument, 0, 's'},
    {"root", required_argument, 0, 'r'},
    {0, 0, 0, 0}
};

void print_usage(const char* program_name) {
    printf("Unhinged Dependency Tracker v%s\n", DEPTRACK_VERSION_STRING);
    printf("Usage: %s [COMMAND] [OPTIONS]\n\n", program_name);
    
    printf("Commands:\n");
    printf("  analyze      Analyze dependencies in monorepo\n");
    printf("  graph        Generate dependency visualization\n");
    printf("  validate     Validate dependency consistency\n");
    printf("  update       Check for available updates\n");
    printf("  feature-dag  Generate feature dependency DAG\n");
    printf("  help         Show this help message\n");
    printf("  version      Show version information\n\n");
    
    printf("Options:\n");
    printf("  -h, --help           Show help message\n");
    printf("  -V, --version        Show version information\n");
    printf("  -v, --verbose        Enable verbose output\n");
    printf("  -o, --output PATH    Output file path\n");
    printf("  -f, --format FORMAT  Output format (json|dot|mermaid|html|markdown)\n");
    printf("  -n, --dry-run        Show what would be done without executing\n");
    printf("  -s, --strict         Enable strict validation mode\n");
    printf("  -r, --root PATH      Root directory to analyze (default: current)\n\n");
    
    printf("Examples:\n");
    printf("  %s analyze --root=/path/to/project --output=deps.json\n", program_name);
    printf("  %s graph --format=mermaid --output=deps.md\n", program_name);
    printf("  %s validate --strict\n", program_name);
    printf("  %s feature-dag --output=docs/architecture/\n", program_name);
}

void print_version(void) {
    printf("Unhinged Dependency Tracker\n");
    printf("Version: %s\n", DEPTRACK_VERSION_STRING);
    printf("Build: %s %s\n", __DATE__, __TIME__);
    printf("Author: Unhinged Development Team\n");
}

Command parse_command(const char* cmd_str) {
    if (!cmd_str) return CMD_UNKNOWN;
    
    if (strcmp(cmd_str, "analyze") == 0) return CMD_ANALYZE;
    if (strcmp(cmd_str, "graph") == 0) return CMD_GRAPH;
    if (strcmp(cmd_str, "validate") == 0) return CMD_VALIDATE;
    if (strcmp(cmd_str, "update") == 0) return CMD_UPDATE;
    if (strcmp(cmd_str, "feature-dag") == 0) return CMD_FEATURE_DAG;
    if (strcmp(cmd_str, "help") == 0) return CMD_HELP;
    if (strcmp(cmd_str, "version") == 0) return CMD_VERSION;
    
    return CMD_UNKNOWN;
}

OutputFormat parse_output_format(const char* format_str) {
    if (!format_str) return OUTPUT_JSON;
    
    if (strcmp(format_str, "json") == 0) return OUTPUT_JSON;
    if (strcmp(format_str, "dot") == 0) return OUTPUT_DOT;
    if (strcmp(format_str, "mermaid") == 0) return OUTPUT_MERMAID;
    if (strcmp(format_str, "html") == 0) return OUTPUT_HTML;
    if (strcmp(format_str, "markdown") == 0) return OUTPUT_MARKDOWN;
    
    return OUTPUT_JSON; // Default
}

int parse_options(int argc, char* argv[], CliOptions* options) {
    // Initialize defaults
    options->command = CMD_UNKNOWN;
    options->root_path = strdup(".");
    options->output_path = NULL;
    options->output_format = OUTPUT_JSON;
    options->verbose = false;
    options->dry_run = false;
    options->strict = false;
    
    // Parse command if provided
    if (argc > 1 && argv[1][0] != '-') {
        options->command = parse_command(argv[1]);
        optind = 2; // Start parsing options from argv[2]
    }
    
    int c;
    int option_index = 0;
    
    while ((c = getopt_long(argc, argv, "hVvo:f:nsr:", long_options, &option_index)) != -1) {
        switch (c) {
            case 'h':
                options->command = CMD_HELP;
                break;
            case 'V':
                options->command = CMD_VERSION;
                break;
            case 'v':
                options->verbose = true;
                break;
            case 'o':
                free(options->output_path);
                options->output_path = strdup(optarg);
                break;
            case 'f':
                options->output_format = parse_output_format(optarg);
                break;
            case 'n':
                options->dry_run = true;
                break;
            case 's':
                options->strict = true;
                break;
            case 'r':
                free(options->root_path);
                options->root_path = strdup(optarg);
                break;
            case '?':
                return -1;
            default:
                break;
        }
    }
    
    return 0;
}

void cleanup_options(CliOptions* options) {
    free(options->root_path);
    free(options->output_path);
}

int cmd_analyze(const CliOptions* options) {
    printf("🔍 Analyzing dependencies in: %s\n", options->root_path);
    
    if (options->verbose) {
        printf("  Output: %s\n", options->output_path ? options->output_path : "stdout");
        printf("  Format: %s\n", options->output_format == OUTPUT_JSON ? "JSON" : "Other");
    }
    
    DependencyTracker* tracker = deptrack_create();
    if (!tracker) {
        fprintf(stderr, "❌ Failed to create dependency tracker\n");
        return 1;
    }
    
    int result = deptrack_initialize(tracker, NULL);
    if (result != DEPTRACK_SUCCESS) {
        fprintf(stderr, "❌ Failed to initialize tracker: %s\n", deptrack_error_string(result));
        deptrack_destroy(tracker);
        return 1;
    }
    
    result = deptrack_analyze_directory(tracker, options->root_path);
    if (result != DEPTRACK_SUCCESS) {
        fprintf(stderr, "❌ Analysis failed: %s\n", deptrack_error_string(result));
        deptrack_destroy(tracker);
        return 1;
    }
    
    if (options->output_path) {
        result = deptrack_generate_output(tracker, options->output_format, options->output_path);
        if (result != DEPTRACK_SUCCESS) {
            fprintf(stderr, "❌ Output generation failed: %s\n", deptrack_error_string(result));
            deptrack_destroy(tracker);
            return 1;
        }
        printf("✅ Analysis complete: %s\n", options->output_path);
    } else {
        printf("✅ Analysis complete\n");
    }
    
    deptrack_destroy(tracker);
    return 0;
}

int cmd_graph(const CliOptions* options) {
    printf("📊 Generating dependency graph\n");
    
    // TODO: Implement graph generation
    printf("⚠️  Graph generation not yet implemented\n");
    return 0;
}

int cmd_validate(const CliOptions* options) {
    printf("🔍 Validating dependencies\n");
    
    if (options->strict) {
        printf("  Strict mode enabled\n");
    }
    
    // TODO: Implement validation
    printf("⚠️  Validation not yet implemented\n");
    return 0;
}

int cmd_update(const CliOptions* options) {
    printf("🔄 Checking for updates\n");
    
    if (options->dry_run) {
        printf("  Dry run mode - no changes will be made\n");
    }
    
    // TODO: Implement update checking
    printf("⚠️  Update checking not yet implemented\n");
    return 0;
}

int cmd_feature_dag(const CliOptions* options) {
    printf("🗺️  Generating feature dependency DAG\n");
    
    // TODO: Implement feature DAG generation
    printf("⚠️  Feature DAG generation not yet implemented\n");
    return 0;
}

int main(int argc, char* argv[]) {
    CliOptions options;
    
    if (parse_options(argc, argv, &options) != 0) {
        print_usage(argv[0]);
        return 1;
    }
    
    int result = 0;
    
    switch (options.command) {
        case CMD_ANALYZE:
            result = cmd_analyze(&options);
            break;
        case CMD_GRAPH:
            result = cmd_graph(&options);
            break;
        case CMD_VALIDATE:
            result = cmd_validate(&options);
            break;
        case CMD_UPDATE:
            result = cmd_update(&options);
            break;
        case CMD_FEATURE_DAG:
            result = cmd_feature_dag(&options);
            break;
        case CMD_HELP:
            print_usage(argv[0]);
            break;
        case CMD_VERSION:
            print_version();
            break;
        case CMD_UNKNOWN:
        default:
            if (argc == 1) {
                print_usage(argv[0]);
            } else {
                fprintf(stderr, "❌ Unknown command. Use --help for usage information.\n");
                result = 1;
            }
            break;
    }
    
    cleanup_options(&options);
    return result;
}
