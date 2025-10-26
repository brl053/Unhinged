/**
 * @file memory_pools.c
 * @brief Memory pool management example
 */

#include "../include/unhinged_graphics.h"
#include <stdio.h>

int main() {
    printf("Memory Pool Management Example\n");
    
    ug_surface_t* surface = ug_surface_create(640, 480, NULL);
    if (!surface) {
        printf("Failed to create graphics surface\n");
        return 1;
    }
    
    printf("Testing memory pool allocations...\n");
    
    // Test multiple context creation/destruction to test memory pools
    for (int i = 0; i < 10; i++) {
        ug_surface_t* temp_surface = ug_surface_create(100, 100, NULL);
        if (temp_surface) {
            ug_color_t color = {i * 25, 255 - i * 25, 128, 255};
            ug_draw_line(temp_surface, 0, 0, 100, 100, color);
            ug_surface_destroy(temp_surface);
        }
    }
    
    printf("Memory pool test completed\n");
    
    ug_surface_destroy(surface);
    return 0;
}
