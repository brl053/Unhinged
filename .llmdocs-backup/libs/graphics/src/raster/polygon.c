/**
 * @file polygon.c
 * @brief Polygon rasterization implementation
 * 
 * Minimal implementation for polygon rendering to satisfy CMake build.
 */

#include "../../include/unhinged_graphics.h"

/**
 * Draw a simple polygon (placeholder implementation)
 */
void ug_draw_polygon(ug_surface_t* surface, const ug_point_t* points, int count, ug_color_t color) {
    if (!surface || !points || count < 3) {
        return;
    }

    // Placeholder: Draw lines between consecutive points
    for (int i = 0; i < count; i++) {
        int next = (i + 1) % count;
        ug_draw_line(surface, points[i].x, points[i].y, points[next].x, points[next].y, color);
    }
}

/**
 * Fill a polygon (placeholder implementation)
 */
void ug_fill_polygon(ug_surface_t* surface, const ug_point_t* points, int count, ug_color_t color) {
    if (!surface || !points || count < 3) {
        return;
    }

    // Placeholder: Just draw the outline for now
    ug_draw_polygon(surface, points, count, color);
}
