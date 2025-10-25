# Examples for Unhinged Graphics Library

# Basic drawing example
add_executable(basic_drawing
    basic_drawing.c
)

target_link_libraries(basic_drawing unhinged_graphics)

# Performance test example
add_executable(performance_test
    performance_test.c
)

target_link_libraries(performance_test unhinged_graphics)

# SIMD comparison example
add_executable(simd_comparison
    simd_comparison.c
)

target_link_libraries(simd_comparison unhinged_graphics)

# Memory pool example
add_executable(memory_pools
    memory_pools.c
)

target_link_libraries(memory_pools unhinged_graphics)

# Hello World example
add_executable(hello_world
    hello_world.c
)

target_link_libraries(hello_world unhinged_graphics)
