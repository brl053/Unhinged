/**
 * @file primitives.c
 * @brief Surface management and basic drawing primitives
 * 
 * Provides core surface operations and pixel manipulation functions
 * that serve as the foundation for all rendering operations.
 */

#include "unhinged_graphics.h"
#include <stdlib.h>
#include <string.h>

/* Internal surface functions */
static inline bool is_point_in_bounds(ug_surface_t* surface, int32_t x, int32_t y) {
    return x >= 0 && y >= 0 && x < surface->width && y < surface->height;
}

static inline void set_pixel(ug_surface_t* surface, int32_t x, int32_t y, ug_color_t color) {
    if (!is_point_in_bounds(surface, x, y)) {
        return;
    }
    
    uint32_t pixel = (color.a << 24) | (color.r << 16) | (color.g << 8) | color.b;
    surface->pixels[y * surface->width + x] = pixel;
}

static inline ug_color_t get_pixel(ug_surface_t* surface, int32_t x, int32_t y) {
    if (!is_point_in_bounds(surface, x, y)) {
        return (ug_color_t){0, 0, 0, 0};
    }
    
    uint32_t pixel = surface->pixels[y * surface->width + x];
    return (ug_color_t){
        .r = (pixel >> 16) & 0xFF,
        .g = (pixel >> 8) & 0xFF,
        .b = pixel & 0xFF,
        .a = (pixel >> 24) & 0xFF
    };
}

/* Surface management */
ug_surface_t* ug_surface_create(int32_t width, int32_t height, ug_allocator_t* allocator) {
    if (width <= 0 || height <= 0) {
        return NULL;
    }
    
    ug_surface_t* surface;
    uint32_t* pixels;
    
    size_t surface_size = sizeof(ug_surface_t);
    size_t pixels_size = width * height * sizeof(uint32_t);
    
    if (allocator) {
        /* Use custom allocator */
        surface = ug_allocator_alloc(allocator, surface_size, 16);
        if (!surface) {
            return NULL;
        }
        
        pixels = ug_allocator_alloc(allocator, pixels_size, 16);
        if (!pixels) {
            ug_allocator_free(allocator, surface);
            return NULL;
        }
    } else {
        /* Use system allocator */
        surface = malloc(surface_size);
        if (!surface) {
            return NULL;
        }
        
        pixels = malloc(pixels_size);
        if (!pixels) {
            free(surface);
            return NULL;
        }
    }
    
    /* Initialize surface */
    surface->pixels = pixels;
    surface->width = width;
    surface->height = height;
    surface->stride = width;
    surface->size = pixels_size;
    
    /* Clear to transparent black */
    memset(pixels, 0, pixels_size);
    
    return surface;
}

void ug_surface_destroy(ug_surface_t* surface) {
    if (!surface) {
        return;
    }
    
    /* Note: We don't know which allocator was used, so we assume system malloc
     * In a real implementation, we'd store allocator reference in surface */
    free(surface->pixels);
    free(surface);
}

ug_error_t ug_surface_clear(ug_surface_t* surface, ug_color_t color) {
    if (!surface || !surface->pixels) {
        return UG_ERROR_INVALID_PARAM;
    }
    
    uint32_t pixel = (color.a << 24) | (color.r << 16) | (color.g << 8) | color.b;
    
    /* Fast clear using 32-bit writes */
    for (int32_t i = 0; i < surface->width * surface->height; i++) {
        surface->pixels[i] = pixel;
    }
    
    return UG_SUCCESS;
}

/* Basic rectangle drawing */
ug_error_t ug_draw_rect_filled(ug_surface_t* surface, ug_rect_t rect, ug_color_t color) {
    if (!surface || !surface->pixels) {
        return UG_ERROR_INVALID_PARAM;
    }
    
    /* Clip rectangle to surface bounds */
    int32_t x1 = rect.x < 0 ? 0 : rect.x;
    int32_t y1 = rect.y < 0 ? 0 : rect.y;
    int32_t x2 = rect.x + rect.width > surface->width ? surface->width : rect.x + rect.width;
    int32_t y2 = rect.y + rect.height > surface->height ? surface->height : rect.y + rect.height;
    
    if (x1 >= x2 || y1 >= y2) {
        return UG_SUCCESS;  /* Nothing to draw */
    }
    
    uint32_t pixel = (color.a << 24) | (color.r << 16) | (color.g << 8) | color.b;
    
    /* Draw filled rectangle */
    for (int32_t y = y1; y < y2; y++) {
        for (int32_t x = x1; x < x2; x++) {
            surface->pixels[y * surface->width + x] = pixel;
        }
    }
    
    return UG_SUCCESS;
}

/* Pixel manipulation utilities */
ug_error_t ug_set_pixel_safe(ug_surface_t* surface, int32_t x, int32_t y, ug_color_t color) {
    if (!surface || !surface->pixels) {
        return UG_ERROR_INVALID_PARAM;
    }
    
    set_pixel(surface, x, y, color);
    return UG_SUCCESS;
}

ug_color_t ug_get_pixel_safe(ug_surface_t* surface, int32_t x, int32_t y) {
    if (!surface || !surface->pixels) {
        return (ug_color_t){0, 0, 0, 0};
    }
    
    return get_pixel(surface, x, y);
}

/* Fast horizontal line for optimization */
static void draw_horizontal_line(ug_surface_t* surface, int32_t x1, int32_t x2, int32_t y, ug_color_t color) {
    if (y < 0 || y >= surface->height) {
        return;
    }
    
    /* Ensure x1 <= x2 */
    if (x1 > x2) {
        int32_t temp = x1;
        x1 = x2;
        x2 = temp;
    }
    
    /* Clip to surface bounds */
    if (x1 < 0) x1 = 0;
    if (x2 >= surface->width) x2 = surface->width - 1;
    
    if (x1 > x2) {
        return;
    }
    
    uint32_t pixel = (color.a << 24) | (color.r << 16) | (color.g << 8) | color.b;
    uint32_t* row = &surface->pixels[y * surface->width];
    
    for (int32_t x = x1; x <= x2; x++) {
        row[x] = pixel;
    }
}

/* Fast vertical line for optimization */
static void draw_vertical_line(ug_surface_t* surface, int32_t x, int32_t y1, int32_t y2, ug_color_t color) {
    if (x < 0 || x >= surface->width) {
        return;
    }
    
    /* Ensure y1 <= y2 */
    if (y1 > y2) {
        int32_t temp = y1;
        y1 = y2;
        y2 = temp;
    }
    
    /* Clip to surface bounds */
    if (y1 < 0) y1 = 0;
    if (y2 >= surface->height) y2 = surface->height - 1;
    
    if (y1 > y2) {
        return;
    }
    
    uint32_t pixel = (color.a << 24) | (color.r << 16) | (color.g << 8) | color.b;
    
    for (int32_t y = y1; y <= y2; y++) {
        surface->pixels[y * surface->width + x] = pixel;
    }
}

/* Utility functions for other modules */
void ug_internal_set_pixel(ug_surface_t* surface, int32_t x, int32_t y, ug_color_t color) {
    set_pixel(surface, x, y, color);
}

void ug_internal_draw_horizontal_line(ug_surface_t* surface, int32_t x1, int32_t x2, int32_t y, ug_color_t color) {
    draw_horizontal_line(surface, x1, x2, y, color);
}

void ug_internal_draw_vertical_line(ug_surface_t* surface, int32_t x, int32_t y1, int32_t y2, ug_color_t color) {
    draw_vertical_line(surface, x, y1, y2, color);
}
