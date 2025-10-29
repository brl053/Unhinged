cmake_minimum_required(VERSION 3.16)
project(dependency_tracker VERSION 1.0.0 LANGUAGES C)

# Set C standard
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Compiler flags
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -Wpedantic")
set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -g -O0 -DDEBUG")
set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -O3 -DNDEBUG")

# Memory sanitizer for tests (optional)
option(ENABLE_SANITIZER "Enable AddressSanitizer for memory leak detection" OFF)
if(ENABLE_SANITIZER)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsanitize=address -fno-omit-frame-pointer")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=address")
    message(STATUS "AddressSanitizer enabled")
endif()

# Include directories
include_directories(include)

# Find optional packages
find_package(PkgConfig QUIET)

# Check for optional libraries
if(PkgConfig_FOUND)
    pkg_check_modules(JSON_C json-c)
    if(JSON_C_FOUND)
        include_directories(${JSON_C_INCLUDE_DIRS})
        link_directories(${JSON_C_LIBRARY_DIRS})
        add_definitions(-DHAVE_JSON_C)
        message(STATUS "JSON-C found: ${JSON_C_VERSION}")
    else()
        message(STATUS "JSON-C not found - using built-in JSON handling")
    endif()
else()
    message(STATUS "PkgConfig not found - using built-in JSON handling")
endif()

# Source files
set(CORE_SOURCES
    src/core/dependency_tracker.c
    src/core/graph.c
    src/core/file_cache.c
    src/core/config_manager.c
    src/core/memory_manager.c
)

set(PARSER_SOURCES
    src/parsers/kotlin_parser.c
    src/parsers/typescript_parser.c
    src/parsers/python_parser.c
    src/parsers/yaml_parser.c
    src/parsers/proto_parser.c
    src/parsers/parser_utils.c
)

set(ANALYSIS_SOURCES
    src/analysis/dependency_resolver.c
    src/analysis/graph_analyzer.c
    src/analysis/feature_dag.c
    src/analysis/conflict_detector.c
)

set(OUTPUT_SOURCES
    src/output/json_generator.c
    src/output/dot_generator.c
    src/output/mermaid_generator.c
    src/output/markdown_generator.c
)

set(UTILS_SOURCES
    src/utils/string_utils.c
    src/utils/file_utils.c
    src/utils/hash_map.c
    src/utils/vector.c
)

# All source files
set(ALL_SOURCES
    ${CORE_SOURCES}
    ${PARSER_SOURCES}
    ${ANALYSIS_SOURCES}
    ${OUTPUT_SOURCES}
    ${UTILS_SOURCES}
)

# Main executable
add_executable(deptrack src/main.c ${ALL_SOURCES})
if(JSON_C_FOUND)
    target_link_libraries(deptrack ${JSON_C_LIBRARIES} pthread)
else()
    target_link_libraries(deptrack pthread)
endif()

# Test executable
set(TEST_SOURCES
    tests/test_main.c
    tests/test_core.c
    tests/test_parsers.c
    tests/test_graph.c
    tests/test_kotlin_parser.c
    tests/test_typescript_parser.c
    tests/test_python_parser.c
    tests/test_yaml_parser.c
    tests/test_integration.c
    tests/test_utils.c
)

add_executable(test_runner ${TEST_SOURCES} ${ALL_SOURCES})
if(JSON_C_FOUND)
    target_link_libraries(test_runner ${JSON_C_LIBRARIES} pthread)
else()
    target_link_libraries(test_runner pthread)
endif()
target_compile_definitions(test_runner PRIVATE TESTING)

# Install targets
install(TARGETS deptrack DESTINATION bin)
install(DIRECTORY include/ DESTINATION include/dependency-tracker)

# Custom targets
add_custom_target(test
    COMMAND ./test_runner
    DEPENDS test_runner
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMENT "Running dependency tracker tests"
)

add_custom_target(test-verbose
    COMMAND ./test_runner --verbose
    DEPENDS test_runner
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMENT "Running dependency tracker tests with verbose output"
)

add_custom_target(test-sanitizer
    COMMAND ${CMAKE_COMMAND} -DENABLE_SANITIZER=ON -B build-sanitizer -S ${CMAKE_SOURCE_DIR}
    COMMAND ${CMAKE_COMMAND} --build build-sanitizer
    COMMAND ${CMAKE_COMMAND} -E chdir build-sanitizer ./test_runner
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Running tests with AddressSanitizer for memory leak detection"
)

add_custom_target(coverage
    COMMAND gcov ${ALL_SOURCES}
    DEPENDS test_runner
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMENT "Generating test coverage report"
)

# Documentation target
find_program(DOXYGEN_EXECUTABLE doxygen)
if(DOXYGEN_EXECUTABLE)
    add_custom_target(docs
        COMMAND doxygen ${CMAKE_SOURCE_DIR}/docs/Doxyfile
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMENT "Generating API documentation"
    )
endif()

# Formatting target
find_program(CLANG_FORMAT_EXECUTABLE clang-format)
if(CLANG_FORMAT_EXECUTABLE)
    add_custom_target(format
        COMMAND find src include tests -name "*.c" -o -name "*.h" | xargs clang-format -i
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMENT "Formatting source code"
    )
endif()

# Static analysis target
find_program(CPPCHECK_EXECUTABLE cppcheck)
find_program(CLANG_TIDY_EXECUTABLE clang-tidy)

if(CPPCHECK_EXECUTABLE)
    add_custom_target(analyze-cppcheck
        COMMAND cppcheck --enable=all --std=c11 --error-exitcode=1
                --suppress=missingIncludeSystem --inline-suppr
                src/ include/
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMENT "Running cppcheck static analysis"
    )
endif()

if(CLANG_TIDY_EXECUTABLE)
    add_custom_target(analyze-clang-tidy
        COMMAND find src include -name "*.c" -o -name "*.h" |
                xargs clang-tidy --checks=-*,readability-*,performance-*,bugprone-*
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMENT "Running clang-tidy static analysis"
    )
endif()

# Combined static analysis target
add_custom_target(analyze)
if(CPPCHECK_EXECUTABLE)
    add_dependencies(analyze analyze-cppcheck)
endif()
if(CLANG_TIDY_EXECUTABLE)
    add_dependencies(analyze analyze-clang-tidy)
endif()

# Print configuration summary
message(STATUS "Dependency Tracker Configuration:")
message(STATUS "  Version: ${PROJECT_VERSION}")
message(STATUS "  Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  C Compiler: ${CMAKE_C_COMPILER}")
message(STATUS "  C Flags: ${CMAKE_C_FLAGS}")
message(STATUS "  JSON-C found: ${JSON_C_FOUND}")
if(JSON_C_FOUND)
    message(STATUS "  JSON-C version: ${JSON_C_VERSION}")
endif()
