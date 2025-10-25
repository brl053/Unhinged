/**
 * @file unhinged_graphics.h
 * @brief Unhinged Native Graphics Rendering Layer
 * 
 * High-performance C graphics library providing:
 * - 2D rasterization primitives (Bresenham algorithms)
 * - Color operations and blending
 * - SIMD acceleration (AVX2, NEON)
 * - Platform detection and optimization
 * - Custom memory management
 * - Python CFFI bindings
 * 
 * This is the foundational graphics layer for the Unhinged project,
 * designed for maximum performance with direct CPU instruction access.
 * 
 * @author Unhinged Team
 * @version 1.0.0
 * @date 2025-10-25
 */

#ifndef UNHINGED_GRAPHICS_H
#define UNHINGED_GRAPHICS_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Version information */
#define UNHINGED_GRAPHICS_VERSION_MAJOR 1
#define UNHINGED_GRAPHICS_VERSION_MINOR 0
#define UNHINGED_GRAPHICS_VERSION_PATCH 0

/* API visibility */
#ifdef _WIN32
    #ifdef BUILDING_UNHINGED_GRAPHICS
        #define UG_API __declspec(dllexport)
    #else
        #define UG_API __declspec(dllimport)
    #endif
#else
    #define UG_API __attribute__((visibility("default")))
#endif

/* Error codes */
typedef enum {
    UG_SUCCESS = 0,
    UG_ERROR_INVALID_PARAM = -1,
    UG_ERROR_OUT_OF_MEMORY = -2,
    UG_ERROR_PLATFORM_NOT_SUPPORTED = -3,
    UG_ERROR_SIMD_NOT_AVAILABLE = -4,
    UG_ERROR_INITIALIZATION_FAILED = -5
} ug_error_t;

/* Basic types */
typedef struct {
    int32_t x, y;
} ug_point_t;

typedef struct {
    int32_t x, y, width, height;
} ug_rect_t;

typedef struct {
    uint8_t r, g, b, a;
} ug_color_t;

typedef struct {
    float r, g, b, a;
} ug_color_f_t;

/* Surface for rendering */
typedef struct {
    uint32_t *pixels;
    int32_t width;
    int32_t height;
    int32_t stride;
    size_t size;
} ug_surface_t;

/* Memory allocator */
typedef struct ug_allocator ug_allocator_t;

/* Platform capabilities */
typedef struct {
    bool has_avx2;
    bool has_neon;
    bool has_drm;
    bool has_wayland;
    const char *gpu_vendor;
    const char *platform_name;
} ug_platform_caps_t;

/* Blending modes */
typedef enum {
    UG_BLEND_NONE = 0,
    UG_BLEND_ALPHA,
    UG_BLEND_ADD,
    UG_BLEND_MULTIPLY,
    UG_BLEND_SCREEN
} ug_blend_mode_t;

/* Color spaces */
typedef enum {
    UG_COLOR_SPACE_RGB = 0,
    UG_COLOR_SPACE_HSV,
    UG_COLOR_SPACE_HSL,
    UG_COLOR_SPACE_LAB
} ug_color_space_t;

/* ============================================================================
 * Core API
 * ============================================================================ */

/**
 * Initialize the graphics library
 * @return UG_SUCCESS on success, error code on failure
 */
UG_API ug_error_t ug_init(void);

/**
 * Shutdown the graphics library
 */
UG_API void ug_shutdown(void);

/**
 * Get library version string
 * @return Version string (e.g., "1.0.0")
 */
UG_API const char* ug_get_version(void);

/**
 * Get platform capabilities
 * @return Platform capabilities structure
 */
UG_API ug_platform_caps_t ug_get_platform_caps(void);

/* ============================================================================
 * Memory Management
 * ============================================================================ */

/**
 * Create a custom allocator optimized for graphics operations
 * @param pool_size Size of memory pool in bytes
 * @return Allocator instance or NULL on failure
 */
UG_API ug_allocator_t* ug_allocator_create(size_t pool_size);

/**
 * Destroy allocator and free all memory
 * @param allocator Allocator to destroy
 */
UG_API void ug_allocator_destroy(ug_allocator_t* allocator);

/**
 * Allocate aligned memory from allocator
 * @param allocator Allocator instance
 * @param size Size in bytes
 * @param alignment Alignment requirement (must be power of 2)
 * @return Aligned memory pointer or NULL on failure
 */
UG_API void* ug_allocator_alloc(ug_allocator_t* allocator, size_t size, size_t alignment);

/**
 * Free memory allocated by allocator
 * @param allocator Allocator instance
 * @param ptr Memory pointer to free
 */
UG_API void ug_allocator_free(ug_allocator_t* allocator, void* ptr);

/* ============================================================================
 * Surface Management
 * ============================================================================ */

/**
 * Create a rendering surface
 * @param width Surface width in pixels
 * @param height Surface height in pixels
 * @param allocator Custom allocator (NULL for default)
 * @return Surface instance or NULL on failure
 */
UG_API ug_surface_t* ug_surface_create(int32_t width, int32_t height, ug_allocator_t* allocator);

/**
 * Destroy surface and free memory
 * @param surface Surface to destroy
 */
UG_API void ug_surface_destroy(ug_surface_t* surface);

/**
 * Clear surface with solid color
 * @param surface Target surface
 * @param color Clear color
 * @return UG_SUCCESS on success, error code on failure
 */
UG_API ug_error_t ug_surface_clear(ug_surface_t* surface, ug_color_t color);

/* ============================================================================
 * 2D Rasterization Primitives
 * ============================================================================ */

/**
 * Draw line using Bresenham algorithm
 * @param surface Target surface
 * @param x0, y0 Start point
 * @param x1, y1 End point
 * @param color Line color
 * @return UG_SUCCESS on success, error code on failure
 */
UG_API ug_error_t ug_draw_line(ug_surface_t* surface, int32_t x0, int32_t y0, 
                               int32_t x1, int32_t y1, ug_color_t color);

/**
 * Draw filled circle
 * @param surface Target surface
 * @param center_x, center_y Circle center
 * @param radius Circle radius
 * @param color Fill color
 * @return UG_SUCCESS on success, error code on failure
 */
UG_API ug_error_t ug_draw_circle_filled(ug_surface_t* surface, int32_t center_x, int32_t center_y,
                                        int32_t radius, ug_color_t color);

/**
 * Draw circle outline
 * @param surface Target surface
 * @param center_x, center_y Circle center
 * @param radius Circle radius
 * @param color Line color
 * @return UG_SUCCESS on success, error code on failure
 */
UG_API ug_error_t ug_draw_circle_outline(ug_surface_t* surface, int32_t center_x, int32_t center_y,
                                         int32_t radius, ug_color_t color);

/**
 * Draw filled rectangle
 * @param surface Target surface
 * @param rect Rectangle bounds
 * @param color Fill color
 * @return UG_SUCCESS on success, error code on failure
 */
UG_API ug_error_t ug_draw_rect_filled(ug_surface_t* surface, ug_rect_t rect, ug_color_t color);

/* ============================================================================
 * Color Operations
 * ============================================================================ */

/**
 * Convert color between color spaces
 * @param src_color Source color
 * @param src_space Source color space
 * @param dst_space Destination color space
 * @return Converted color
 */
UG_API ug_color_f_t ug_color_convert(ug_color_f_t src_color, ug_color_space_t src_space, 
                                     ug_color_space_t dst_space);

/**
 * Blend two colors using specified blend mode
 * @param src Source color
 * @param dst Destination color
 * @param mode Blend mode
 * @return Blended color
 */
UG_API ug_color_t ug_color_blend(ug_color_t src, ug_color_t dst, ug_blend_mode_t mode);

/**
 * Alpha blend two colors
 * @param src Source color (with alpha)
 * @param dst Destination color
 * @return Alpha-blended color
 */
UG_API ug_color_t ug_color_alpha_blend(ug_color_t src, ug_color_t dst);

/* ============================================================================
 * Window Management
 * ============================================================================ */

/**
 * Create a window using DRM framebuffer
 * @param width Window width (0 = use display width)
 * @param height Window height (0 = use display height)
 * @return UG_SUCCESS on success, error code on failure
 */
UG_API ug_error_t ug_window_create(uint32_t width, uint32_t height);

/**
 * Get window surface for drawing
 * @return Surface pointer or NULL on failure
 */
UG_API ug_surface_t* ug_window_get_surface(void);

/**
 * Present/flush window contents to screen
 */
UG_API void ug_window_present(void);

/**
 * Close window and free resources
 */
UG_API void ug_window_close(void);

/**
 * Check if window is open
 * @return true if window is open, false otherwise
 */
UG_API bool ug_window_is_open(void);

/**
 * Get window dimensions
 * @param width Pointer to store width (can be NULL)
 * @param height Pointer to store height (can be NULL)
 */
UG_API void ug_window_get_size(uint32_t *width, uint32_t *height);

/* ============================================================================
 * Text Rendering
 * ============================================================================ */

/**
 * Draw a single character using 8x8 bitmap font
 * @param surface Target surface
 * @param x, y Character position
 * @param c Character to draw (ASCII 32-126)
 * @param color Text color
 * @return UG_SUCCESS on success, error code on failure
 */
UG_API ug_error_t ug_draw_char(ug_surface_t* surface, int32_t x, int32_t y, char c, ug_color_t color);

/**
 * Draw text string using 8x8 bitmap font
 * @param surface Target surface
 * @param x, y Text position
 * @param text Text string to draw
 * @param color Text color
 * @return UG_SUCCESS on success, error code on failure
 */
UG_API ug_error_t ug_draw_text(ug_surface_t* surface, int32_t x, int32_t y, const char* text, ug_color_t color);

#ifdef __cplusplus
}
#endif

#endif /* UNHINGED_GRAPHICS_H */
