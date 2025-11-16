/**
 * @file test_primitives.c
 * @brief Test primitives rendering functions
 */

#include "../include/unhinged_graphics.h"
#include <stdio.h>
#include <assert.h>

int test_primitives() {
    printf("Testing graphics primitives...\n");
    
    // Basic test - just ensure functions exist and don't crash
    ug_context_t* ctx = ug_create_context(800, 600);
    if (!ctx) {
        printf("Failed to create graphics context\n");
        return 1;
    }
    
    // Test basic drawing functions
    ug_color_t red = {255, 0, 0, 255};
    ug_draw_line(ctx, 0, 0, 100, 100, red);
    ug_draw_circle(ctx, 50, 50, 25, red);
    
    ug_destroy_context(ctx);
    printf("Primitives test passed\n");
    return 0;
}

int main() {
    return test_primitives();
}
