/**
 * @file hello_world.c
 * @brief Hello World window using native C graphics
 * 
 * Creates a window and displays "Hello World" text.
 * Uses DRM framebuffer for direct hardware rendering.
 */

#include "../include/unhinged_graphics.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>

static volatile bool running = true;

void signal_handler(int sig) {
    running = false;
}

int main() {
    printf("Unhinged Graphics - Hello World Example\n");
    printf("=======================================\n\n");
    
    // Set up signal handler for clean exit
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Initialize graphics library
    ug_error_t result = ug_init();
    if (result != UG_SUCCESS) {
        printf("Failed to initialize graphics library: %d\n", result);
        return 1;
    }
    
    printf("Graphics library initialized\n");
    
    // Show platform capabilities
    ug_platform_caps_t caps = ug_get_platform_caps();
    printf("Platform: %s\n", caps.platform_name ? caps.platform_name : "Unknown");
    printf("SIMD: AVX2=%s, NEON=%s\n", 
           caps.has_avx2 ? "Yes" : "No",
           caps.has_neon ? "Yes" : "No");
    printf("Graphics: DRM=%s, Wayland=%s\n",
           caps.has_drm ? "Yes" : "No",
           caps.has_wayland ? "Yes" : "No");
    printf("\n");
    
    // Create window
    printf("Creating window...\n");
    result = ug_window_create(800, 600);
    if (result != UG_SUCCESS) {
        printf("Failed to create window: %d\n", result);
        printf("Note: This requires DRM access. Try running as root or add user to 'video' group.\n");
        ug_shutdown();
        return 1;
    }
    
    printf("Window created successfully\n");
    
    // Get window surface
    ug_surface_t* surface = ug_window_get_surface();
    if (!surface) {
        printf("Failed to get window surface\n");
        ug_window_close();
        ug_shutdown();
        return 1;
    }
    
    printf("Surface obtained: %dx%d\n", surface->width, surface->height);
    
    // Clear screen with dark blue background
    ug_color_t bg_color = {20, 30, 50, 255}; // Dark blue
    ug_surface_clear(surface, bg_color);
    
    // Draw "Hello World" text
    ug_color_t text_color = {255, 255, 255, 255}; // White
    ug_draw_text(surface, 50, 50, "Hello World!", text_color);
    
    // Draw some additional text
    ug_color_t green = {0, 255, 0, 255};
    ug_draw_text(surface, 50, 80, "Native C Graphics Rendering", green);
    
    ug_color_t yellow = {255, 255, 0, 255};
    ug_draw_text(surface, 50, 110, "No GTK, No X11, No Wayland", yellow);
    
    ug_color_t cyan = {0, 255, 255, 255};
    ug_draw_text(surface, 50, 140, "Direct DRM Framebuffer", cyan);
    
    // Draw some graphics primitives
    ug_color_t red = {255, 0, 0, 255};
    ug_draw_line(surface, 50, 200, 750, 200, red);
    
    ug_color_t blue = {0, 0, 255, 255};
    ug_draw_circle_filled(surface, 400, 300, 50, blue);
    
    ug_rect_t rect = {600, 250, 100, 100};
    ug_color_t purple = {255, 0, 255, 255};
    ug_draw_rect_filled(surface, rect, purple);
    
    // Present the frame
    ug_window_present();
    
    printf("\nHello World window displayed!\n");
    printf("Press Ctrl+C to exit...\n\n");
    
    // Main loop - just wait for signal
    while (running) {
        sleep(1);
    }
    
    printf("\nShutting down...\n");
    
    // Cleanup
    free(surface); // Free the surface wrapper (not the actual framebuffer)
    ug_window_close();
    ug_shutdown();
    
    printf("Goodbye!\n");
    return 0;
}
