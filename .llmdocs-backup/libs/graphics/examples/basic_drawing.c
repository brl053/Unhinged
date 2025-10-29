/**
 * @file basic_drawing.c
 * @brief Basic drawing example for Unhinged Graphics Library
 * 
 * Demonstrates core functionality including:
 * - Surface creation and management
 * - Basic drawing primitives
 * - Color operations
 * - Platform capability detection
 */

#include "unhinged_graphics.h"
#include <stdio.h>
#include <stdlib.h>

int main() {
    printf("Unhinged Graphics Library - Basic Drawing Example\n");
    printf("================================================\n\n");
    
    /* Initialize graphics library */
    ug_error_t result = ug_init();
    if (result != UG_SUCCESS) {
        printf("Failed to initialize graphics library: %d\n", result);
        return 1;
    }
    
    printf("Graphics library initialized successfully\n");
    printf("Version: %s\n\n", ug_get_version());
    
    /* Display platform capabilities */
    ug_platform_caps_t caps = ug_get_platform_caps();
    printf("Platform Capabilities:\n");
    printf("  Platform: %s\n", caps.platform_name);
    printf("  GPU Vendor: %s\n", caps.gpu_vendor);
    printf("  AVX2 Support: %s\n", caps.has_avx2 ? "Yes" : "No");
    printf("  NEON Support: %s\n", caps.has_neon ? "Yes" : "No");
    printf("  DRM Support: %s\n", caps.has_drm ? "Yes" : "No");
    printf("  Wayland Support: %s\n\n", caps.has_wayland ? "Yes" : "No");
    
    /* Create a custom allocator */
    ug_allocator_t* allocator = ug_allocator_create(1024 * 1024);  /* 1MB pool */
    if (!allocator) {
        printf("Failed to create custom allocator\n");
        ug_shutdown();
        return 1;
    }
    
    printf("Created custom allocator with 1MB pool\n");
    
    /* Create rendering surface */
    int32_t width = 800;
    int32_t height = 600;
    ug_surface_t* surface = ug_surface_create(width, height, allocator);
    if (!surface) {
        printf("Failed to create surface\n");
        ug_allocator_destroy(allocator);
        ug_shutdown();
        return 1;
    }
    
    printf("Created %dx%d rendering surface\n\n", width, height);
    
    /* Define some colors */
    ug_color_t white = {255, 255, 255, 255};
    ug_color_t red = {255, 0, 0, 255};
    ug_color_t green = {0, 255, 0, 255};
    ug_color_t blue = {0, 0, 255, 255};
    ug_color_t yellow = {255, 255, 0, 255};
    ug_color_t purple = {128, 0, 128, 255};
    
    /* Clear surface with white background */
    result = ug_surface_clear(surface, white);
    if (result != UG_SUCCESS) {
        printf("Failed to clear surface: %d\n", result);
        goto cleanup;
    }
    
    printf("Drawing primitives...\n");
    
    /* Draw some lines */
    ug_draw_line(surface, 50, 50, 750, 50, red);      /* Top horizontal line */
    ug_draw_line(surface, 50, 550, 750, 550, red);    /* Bottom horizontal line */
    ug_draw_line(surface, 50, 50, 50, 550, green);    /* Left vertical line */
    ug_draw_line(surface, 750, 50, 750, 550, green);  /* Right vertical line */
    
    /* Draw diagonal lines */
    ug_draw_line(surface, 50, 50, 750, 550, blue);    /* Diagonal 1 */
    ug_draw_line(surface, 750, 50, 50, 550, blue);    /* Diagonal 2 */
    
    /* Draw filled rectangles */
    ug_rect_t rect1 = {100, 100, 150, 100};
    ug_draw_rect_filled(surface, rect1, yellow);
    
    ug_rect_t rect2 = {550, 400, 150, 100};
    ug_draw_rect_filled(surface, rect2, purple);
    
    /* Draw circles */
    ug_draw_circle_filled(surface, 200, 300, 50, red);
    ug_draw_circle_outline(surface, 400, 300, 75, green);
    ug_draw_circle_filled(surface, 600, 200, 30, blue);
    
    printf("Basic drawing completed!\n\n");
    
    /* Test color blending */
    printf("Testing color blending...\n");
    
    ug_color_t src_color = {255, 0, 0, 128};  /* Semi-transparent red */
    ug_color_t dst_color = {0, 255, 0, 255};  /* Opaque green */
    
    ug_color_t blended = ug_color_alpha_blend(src_color, dst_color);
    printf("Alpha blend result: R=%d, G=%d, B=%d, A=%d\n", 
           blended.r, blended.g, blended.b, blended.a);
    
    ug_color_t multiplied = ug_color_blend(src_color, dst_color, UG_BLEND_MULTIPLY);
    printf("Multiply blend result: R=%d, G=%d, B=%d, A=%d\n", 
           multiplied.r, multiplied.g, multiplied.b, multiplied.a);
    
    /* Test color space conversion */
    printf("\nTesting color space conversion...\n");
    
    ug_color_f_t rgb_color = {1.0f, 0.5f, 0.0f, 1.0f};  /* Orange */
    ug_color_f_t hsv_color = ug_color_convert(rgb_color, UG_COLOR_SPACE_RGB, UG_COLOR_SPACE_HSV);
    printf("RGB(1.0, 0.5, 0.0) -> HSV(%.3f, %.3f, %.3f)\n", 
           hsv_color.r, hsv_color.g, hsv_color.b);
    
    ug_color_f_t back_to_rgb = ug_color_convert(hsv_color, UG_COLOR_SPACE_HSV, UG_COLOR_SPACE_RGB);
    printf("HSV -> RGB(%.3f, %.3f, %.3f) (should match original)\n", 
           back_to_rgb.r, back_to_rgb.g, back_to_rgb.b);
    
    printf("\nExample completed successfully!\n");
    printf("Note: This example demonstrates the API but doesn't save the rendered image.\n");
    printf("In a real application, you would copy the surface pixels to a display buffer.\n");

cleanup:
    /* Cleanup resources */
    ug_surface_destroy(surface);
    ug_allocator_destroy(allocator);
    ug_shutdown();
    
    return 0;
}
