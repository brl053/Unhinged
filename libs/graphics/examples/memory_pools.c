/**
 * @file memory_pools.c
 * @brief Memory pool management example
 */

#include "../include/unhinged_graphics.h"
#include <stdio.h>

int main() {
    printf("Memory Pool Management Example\n");
    
    ug_context_t* ctx = ug_create_context(640, 480);
    if (!ctx) {
        printf("Failed to create graphics context\n");
        return 1;
    }
    
    printf("Testing memory pool allocations...\n");
    
    // Test multiple context creation/destruction to test memory pools
    for (int i = 0; i < 10; i++) {
        ug_context_t* temp_ctx = ug_create_context(100, 100);
        if (temp_ctx) {
            ug_color_t color = {i * 25, 255 - i * 25, 128, 255};
            ug_draw_line(temp_ctx, 0, 0, 100, 100, color);
            ug_destroy_context(temp_ctx);
        }
    }
    
    printf("Memory pool test completed\n");
    
    ug_destroy_context(ctx);
    return 0;
}
