/**
 * @file performance_test.c
 * @brief Performance testing example
 */

#include "../include/unhinged_graphics.h"
#include <stdio.h>
#include <time.h>

int main() {
    printf("Graphics Performance Test Example\n");
    
    ug_context_t* ctx = ug_create_context(800, 600);
    if (!ctx) {
        printf("Failed to create graphics context\n");
        return 1;
    }
    
    printf("Running performance tests...\n");
    
    // Test line drawing performance
    clock_t start = clock();
    ug_color_t color = {0, 255, 0, 255};
    for (int i = 0; i < 1000; i++) {
        ug_draw_line(ctx, 0, i % 600, 800, (i + 300) % 600, color);
    }
    clock_t end = clock();
    
    double time_taken = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("Line drawing: 1000 lines in %f seconds\n", time_taken);
    
    ug_destroy_context(ctx);
    return 0;
}
