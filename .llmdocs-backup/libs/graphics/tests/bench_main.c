/**
 * @file bench_main.c
 * @brief Benchmark main for graphics performance testing
 */

#include "../include/unhinged_graphics.h"
#include <stdio.h>
#include <time.h>

int main() {
    printf("Graphics Performance Benchmark\n");
    
    ug_context_t* ctx = ug_create_context(1920, 1080);
    if (!ctx) {
        printf("Failed to create graphics context\n");
        return 1;
    }
    
    clock_t start = clock();
    
    // Simple benchmark - draw many lines
    ug_color_t color = {255, 255, 255, 255};
    for (int i = 0; i < 10000; i++) {
        ug_draw_line(ctx, i % 1920, i % 1080, (i + 100) % 1920, (i + 100) % 1080, color);
    }
    
    clock_t end = clock();
    double cpu_time_used = ((double) (end - start)) / CLOCKS_PER_SEC;
    
    printf("Drew 10,000 lines in %f seconds\n", cpu_time_used);
    
    ug_destroy_context(ctx);
    return 0;
}
