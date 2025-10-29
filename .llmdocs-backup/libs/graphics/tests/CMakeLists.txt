# Test suite for Unhinged Graphics Library

# Test executable
add_executable(test_graphics
    test_main.c
    test_primitives.c
    test_memory.c
    test_color.c
    test_platform.c
    test_simd.c
)

# Link with graphics library
target_link_libraries(test_graphics unhinged_graphics)

# Add test
add_test(NAME graphics_tests COMMAND test_graphics)

# Performance benchmarks
add_executable(bench_graphics
    bench_main.c
    bench_primitives.c
    bench_memory.c
    bench_simd.c
)

target_link_libraries(bench_graphics unhinged_graphics)

# Example programs
add_executable(example_basic
    examples/basic_drawing.c
)

target_link_libraries(example_basic unhinged_graphics)

add_executable(example_performance
    examples/performance_test.c
)

target_link_libraries(example_performance unhinged_graphics)
