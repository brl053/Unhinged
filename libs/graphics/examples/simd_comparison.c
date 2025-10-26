/**
 * @file simd_comparison.c
 * @brief SIMD performance comparison example
 */

#include "../include/unhinged_graphics.h"
#include <stdio.h>
#include <time.h>

int main() {
    printf("SIMD Performance Comparison Example\n");
    
    ug_surface_t* surface = ug_surface_create(1024, 768, NULL);
    if (!surface) {
        printf("Failed to create graphics surface\n");
        return 1;
    }
    
    printf("Testing SIMD optimizations...\n");
    
    // Test circle drawing with potential SIMD optimizations
    clock_t start = clock();
    ug_color_t color = {255, 0, 255, 255};
    for (int i = 0; i < 500; i++) {
        ug_draw_circle_filled(surface, i % 1024, i % 768, 10 + (i % 50), color);
    }
    clock_t end = clock();
    
    double time_taken = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("Circle drawing: 500 circles in %f seconds\n", time_taken);
    
    ug_surface_destroy(surface);
    return 0;
}
