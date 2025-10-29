/**
 * @file circle.c
 * @brief Circle drawing algorithms using Bresenham and midpoint methods
 * 
 * Provides optimized circle drawing for both filled and outline circles
 * using the midpoint circle algorithm for efficiency.
 */

#include "unhinged_graphics.h"
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* External functions from primitives.c */
extern void ug_internal_set_pixel(ug_surface_t* surface, int32_t x, int32_t y, ug_color_t color);
extern void ug_internal_draw_horizontal_line(ug_surface_t* surface, int32_t x1, int32_t x2, int32_t y, ug_color_t color);

/* Plot 8 symmetric points for circle outline */
static void plot_circle_points(ug_surface_t* surface, int32_t cx, int32_t cy, 
                              int32_t x, int32_t y, ug_color_t color) {
    ug_internal_set_pixel(surface, cx + x, cy + y, color);
    ug_internal_set_pixel(surface, cx - x, cy + y, color);
    ug_internal_set_pixel(surface, cx + x, cy - y, color);
    ug_internal_set_pixel(surface, cx - x, cy - y, color);
    ug_internal_set_pixel(surface, cx + y, cy + x, color);
    ug_internal_set_pixel(surface, cx - y, cy + x, color);
    ug_internal_set_pixel(surface, cx + y, cy - x, color);
    ug_internal_set_pixel(surface, cx - y, cy - x, color);
}

/* Draw horizontal lines for filled circle */
static void fill_circle_lines(ug_surface_t* surface, int32_t cx, int32_t cy,
                             int32_t x, int32_t y, ug_color_t color) {
    /* Draw horizontal lines for the 4 quadrants */
    if (x != 0) {
        ug_internal_draw_horizontal_line(surface, cx - x, cx + x, cy + y, color);
        ug_internal_draw_horizontal_line(surface, cx - x, cx + x, cy - y, color);
    }
    
    if (y != 0 && y != x) {
        ug_internal_draw_horizontal_line(surface, cx - y, cx + y, cy + x, color);
        ug_internal_draw_horizontal_line(surface, cx - y, cx + y, cy - x, color);
    }
}

/* Midpoint circle algorithm for outline */
ug_error_t ug_draw_circle_outline(ug_surface_t* surface, int32_t center_x, int32_t center_y,
                                 int32_t radius, ug_color_t color) {
    if (!surface || !surface->pixels || radius < 0) {
        return UG_ERROR_INVALID_PARAM;
    }
    
    if (radius == 0) {
        ug_internal_set_pixel(surface, center_x, center_y, color);
        return UG_SUCCESS;
    }
    
    /* Midpoint circle algorithm */
    int32_t x = 0;
    int32_t y = radius;
    int32_t d = 1 - radius;
    
    /* Plot initial points */
    plot_circle_points(surface, center_x, center_y, x, y, color);
    
    while (x < y) {
        if (d < 0) {
            d += 2 * x + 3;
        } else {
            d += 2 * (x - y) + 5;
            y--;
        }
        x++;
        
        plot_circle_points(surface, center_x, center_y, x, y, color);
    }
    
    return UG_SUCCESS;
}

/* Midpoint circle algorithm for filled circle */
ug_error_t ug_draw_circle_filled(ug_surface_t* surface, int32_t center_x, int32_t center_y,
                                int32_t radius, ug_color_t color) {
    if (!surface || !surface->pixels || radius < 0) {
        return UG_ERROR_INVALID_PARAM;
    }
    
    if (radius == 0) {
        ug_internal_set_pixel(surface, center_x, center_y, color);
        return UG_SUCCESS;
    }
    
    /* Midpoint circle algorithm with horizontal line filling */
    int32_t x = 0;
    int32_t y = radius;
    int32_t d = 1 - radius;
    
    /* Fill initial lines */
    fill_circle_lines(surface, center_x, center_y, x, y, color);
    
    while (x < y) {
        if (d < 0) {
            d += 2 * x + 3;
        } else {
            d += 2 * (x - y) + 5;
            y--;
        }
        x++;
        
        fill_circle_lines(surface, center_x, center_y, x, y, color);
    }
    
    return UG_SUCCESS;
}

/* Anti-aliased circle outline using distance field */
ug_error_t ug_draw_circle_outline_antialiased(ug_surface_t* surface, int32_t center_x, int32_t center_y,
                                             int32_t radius, ug_color_t color) {
    if (!surface || !surface->pixels || radius < 0) {
        return UG_ERROR_INVALID_PARAM;
    }
    
    /* Bounding box for the circle */
    int32_t x_min = center_x - radius - 1;
    int32_t x_max = center_x + radius + 1;
    int32_t y_min = center_y - radius - 1;
    int32_t y_max = center_y + radius + 1;
    
    /* Clip to surface bounds */
    if (x_min < 0) x_min = 0;
    if (y_min < 0) y_min = 0;
    if (x_max >= surface->width) x_max = surface->width - 1;
    if (y_max >= surface->height) y_max = surface->height - 1;
    
    for (int32_t y = y_min; y <= y_max; y++) {
        for (int32_t x = x_min; x <= x_max; x++) {
            /* Calculate distance from center */
            float dx = x - center_x;
            float dy = y - center_y;
            float distance = sqrtf(dx * dx + dy * dy);
            
            /* Calculate alpha based on distance to circle edge */
            float edge_distance = fabsf(distance - radius);
            float alpha = 1.0f - edge_distance;
            
            if (alpha > 0.0f) {
                if (alpha > 1.0f) alpha = 1.0f;
                
                /* Apply alpha to color */
                ug_color_t aa_color = color;
                aa_color.a = (uint8_t)(color.a * alpha);
                
                ug_internal_set_pixel(surface, x, y, aa_color);
            }
        }
    }
    
    return UG_SUCCESS;
}

/* Ellipse drawing using midpoint algorithm */
ug_error_t ug_draw_ellipse_outline(ug_surface_t* surface, int32_t center_x, int32_t center_y,
                                  int32_t rx, int32_t ry, ug_color_t color) {
    if (!surface || !surface->pixels || rx < 0 || ry < 0) {
        return UG_ERROR_INVALID_PARAM;
    }
    
    if (rx == 0 && ry == 0) {
        ug_internal_set_pixel(surface, center_x, center_y, color);
        return UG_SUCCESS;
    }
    
    /* Midpoint ellipse algorithm */
    int32_t x = 0;
    int32_t y = ry;
    
    /* Region 1 */
    int32_t rx2 = rx * rx;
    int32_t ry2 = ry * ry;
    int32_t d1 = ry2 - rx2 * ry + rx2 / 4;
    
    /* Plot initial points */
    ug_internal_set_pixel(surface, center_x + x, center_y + y, color);
    ug_internal_set_pixel(surface, center_x - x, center_y + y, color);
    ug_internal_set_pixel(surface, center_x + x, center_y - y, color);
    ug_internal_set_pixel(surface, center_x - x, center_y - y, color);
    
    /* Region 1: slope > -1 */
    while (ry2 * x < rx2 * y) {
        if (d1 < 0) {
            d1 += ry2 * (2 * x + 3);
        } else {
            d1 += ry2 * (2 * x + 3) + rx2 * (-2 * y + 2);
            y--;
        }
        x++;
        
        ug_internal_set_pixel(surface, center_x + x, center_y + y, color);
        ug_internal_set_pixel(surface, center_x - x, center_y + y, color);
        ug_internal_set_pixel(surface, center_x + x, center_y - y, color);
        ug_internal_set_pixel(surface, center_x - x, center_y - y, color);
    }
    
    /* Region 2: slope <= -1 */
    int32_t d2 = ry2 * (x + 0.5f) * (x + 0.5f) + rx2 * (y - 1) * (y - 1) - rx2 * ry2;
    
    while (y >= 0) {
        if (d2 < 0) {
            d2 += ry2 * (2 * x + 2) + rx2 * (-2 * y + 3);
            x++;
        } else {
            d2 += rx2 * (-2 * y + 3);
        }
        y--;
        
        ug_internal_set_pixel(surface, center_x + x, center_y + y, color);
        ug_internal_set_pixel(surface, center_x - x, center_y + y, color);
        ug_internal_set_pixel(surface, center_x + x, center_y - y, color);
        ug_internal_set_pixel(surface, center_x - x, center_y - y, color);
    }
    
    return UG_SUCCESS;
}

/* Filled ellipse */
ug_error_t ug_draw_ellipse_filled(ug_surface_t* surface, int32_t center_x, int32_t center_y,
                                 int32_t rx, int32_t ry, ug_color_t color) {
    if (!surface || !surface->pixels || rx < 0 || ry < 0) {
        return UG_ERROR_INVALID_PARAM;
    }
    
    /* Simple implementation using scanline filling */
    for (int32_t y = -ry; y <= ry; y++) {
        /* Calculate x extent for this y */
        float y_norm = (float)y / ry;
        float x_extent = rx * sqrtf(1.0f - y_norm * y_norm);
        
        int32_t x_start = center_x - (int32_t)x_extent;
        int32_t x_end = center_x + (int32_t)x_extent;
        
        ug_internal_draw_horizontal_line(surface, x_start, x_end, center_y + y, color);
    }
    
    return UG_SUCCESS;
}

/* Arc drawing */
ug_error_t ug_draw_arc(ug_surface_t* surface, int32_t center_x, int32_t center_y,
                      int32_t radius, float start_angle, float end_angle, ug_color_t color) {
    if (!surface || !surface->pixels || radius < 0) {
        return UG_ERROR_INVALID_PARAM;
    }
    
    /* Normalize angles to 0-2π range */
    while (start_angle < 0) start_angle += 2 * M_PI;
    while (end_angle < 0) end_angle += 2 * M_PI;
    while (start_angle >= 2 * M_PI) start_angle -= 2 * M_PI;
    while (end_angle >= 2 * M_PI) end_angle -= 2 * M_PI;
    
    /* Calculate step size based on radius for smooth arc */
    float step = 1.0f / radius;
    if (step > 0.1f) step = 0.1f;
    
    /* Draw arc by stepping through angles */
    for (float angle = start_angle; angle <= end_angle; angle += step) {
        int32_t x = center_x + (int32_t)(radius * cosf(angle));
        int32_t y = center_y + (int32_t)(radius * sinf(angle));
        ug_internal_set_pixel(surface, x, y, color);
    }
    
    /* Ensure end point is drawn */
    int32_t end_x = center_x + (int32_t)(radius * cosf(end_angle));
    int32_t end_y = center_y + (int32_t)(radius * sinf(end_angle));
    ug_internal_set_pixel(surface, end_x, end_y, color);
    
    return UG_SUCCESS;
}
