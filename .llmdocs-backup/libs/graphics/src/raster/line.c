/**
 * @file line.c
 * @brief Bresenham line drawing algorithm implementation
 * 
 * Provides optimized line drawing using the classic Bresenham algorithm
 * with optimizations for horizontal, vertical, and diagonal lines.
 */

#include "unhinged_graphics.h"
#include <stdlib.h>
#include <math.h>

/* External functions from primitives.c */
extern void ug_internal_set_pixel(ug_surface_t* surface, int32_t x, int32_t y, ug_color_t color);
extern void ug_internal_draw_horizontal_line(ug_surface_t* surface, int32_t x1, int32_t x2, int32_t y, ug_color_t color);
extern void ug_internal_draw_vertical_line(ug_surface_t* surface, int32_t x, int32_t y1, int32_t y2, ug_color_t color);

/* Optimized Bresenham line algorithm */
ug_error_t ug_draw_line(ug_surface_t* surface, int32_t x0, int32_t y0, 
                        int32_t x1, int32_t y1, ug_color_t color) {
    if (!surface || !surface->pixels) {
        return UG_ERROR_INVALID_PARAM;
    }
    
    /* Handle special cases for optimization */
    if (y0 == y1) {
        /* Horizontal line */
        ug_internal_draw_horizontal_line(surface, x0, x1, y0, color);
        return UG_SUCCESS;
    }
    
    if (x0 == x1) {
        /* Vertical line */
        ug_internal_draw_vertical_line(surface, x0, y0, y1, color);
        return UG_SUCCESS;
    }
    
    /* General case: Bresenham's line algorithm */
    int32_t dx = abs(x1 - x0);
    int32_t dy = abs(y1 - y0);
    
    int32_t sx = x0 < x1 ? 1 : -1;
    int32_t sy = y0 < y1 ? 1 : -1;
    
    int32_t err = dx - dy;
    int32_t x = x0;
    int32_t y = y0;
    
    while (true) {
        ug_internal_set_pixel(surface, x, y, color);
        
        if (x == x1 && y == y1) {
            break;
        }
        
        int32_t e2 = 2 * err;
        
        if (e2 > -dy) {
            err -= dy;
            x += sx;
        }
        
        if (e2 < dx) {
            err += dx;
            y += sy;
        }
    }
    
    return UG_SUCCESS;
}

/* Anti-aliased line drawing using Wu's algorithm */
static inline float fpart(float x) {
    return x - (int)x;
}

static inline float rfpart(float x) {
    return 1.0f - fpart(x);
}

static inline int ipart(float x) {
    return (int)x;
}

static void plot_pixel_alpha(ug_surface_t* surface, int32_t x, int32_t y, ug_color_t color, float alpha) {
    if (x < 0 || y < 0 || x >= surface->width || y >= surface->height) {
        return;
    }
    
    /* Apply alpha to color */
    ug_color_t blended_color = color;
    blended_color.a = (uint8_t)(color.a * alpha);
    
    /* For now, just set the pixel directly. In a full implementation,
     * we would blend with the existing pixel */
    ug_internal_set_pixel(surface, x, y, blended_color);
}

ug_error_t ug_draw_line_antialiased(ug_surface_t* surface, int32_t x0, int32_t y0,
                                   int32_t x1, int32_t y1, ug_color_t color) {
    if (!surface || !surface->pixels) {
        return UG_ERROR_INVALID_PARAM;
    }
    
    /* Wu's anti-aliased line algorithm */
    bool steep = abs(y1 - y0) > abs(x1 - x0);
    
    if (steep) {
        /* Swap x and y coordinates */
        int32_t temp;
        temp = x0; x0 = y0; y0 = temp;
        temp = x1; x1 = y1; y1 = temp;
    }
    
    if (x0 > x1) {
        /* Swap start and end points */
        int32_t temp;
        temp = x0; x0 = x1; x1 = temp;
        temp = y0; y0 = y1; y1 = temp;
    }
    
    float dx = x1 - x0;
    float dy = y1 - y0;
    float gradient = dy / dx;
    
    /* Handle first endpoint */
    float xend = x0;
    float yend = y0 + gradient * (xend - x0);
    float xgap = rfpart(x0 + 0.5f);
    int32_t xpxl1 = (int32_t)xend;
    int32_t ypxl1 = ipart(yend);
    
    if (steep) {
        plot_pixel_alpha(surface, ypxl1, xpxl1, color, rfpart(yend) * xgap);
        plot_pixel_alpha(surface, ypxl1 + 1, xpxl1, color, fpart(yend) * xgap);
    } else {
        plot_pixel_alpha(surface, xpxl1, ypxl1, color, rfpart(yend) * xgap);
        plot_pixel_alpha(surface, xpxl1, ypxl1 + 1, color, fpart(yend) * xgap);
    }
    
    float intery = yend + gradient;
    
    /* Handle second endpoint */
    xend = x1;
    yend = y1 + gradient * (xend - x1);
    xgap = fpart(x1 + 0.5f);
    int32_t xpxl2 = (int32_t)xend;
    int32_t ypxl2 = ipart(yend);
    
    if (steep) {
        plot_pixel_alpha(surface, ypxl2, xpxl2, color, rfpart(yend) * xgap);
        plot_pixel_alpha(surface, ypxl2 + 1, xpxl2, color, fpart(yend) * xgap);
    } else {
        plot_pixel_alpha(surface, xpxl2, ypxl2, color, rfpart(yend) * xgap);
        plot_pixel_alpha(surface, xpxl2, ypxl2 + 1, color, fpart(yend) * xgap);
    }
    
    /* Main loop */
    for (int32_t x = xpxl1 + 1; x < xpxl2; x++) {
        if (steep) {
            plot_pixel_alpha(surface, ipart(intery), x, color, rfpart(intery));
            plot_pixel_alpha(surface, ipart(intery) + 1, x, color, fpart(intery));
        } else {
            plot_pixel_alpha(surface, x, ipart(intery), color, rfpart(intery));
            plot_pixel_alpha(surface, x, ipart(intery) + 1, color, fpart(intery));
        }
        intery += gradient;
    }
    
    return UG_SUCCESS;
}

/* Thick line drawing */
ug_error_t ug_draw_line_thick(ug_surface_t* surface, int32_t x0, int32_t y0,
                             int32_t x1, int32_t y1, int32_t thickness, ug_color_t color) {
    if (!surface || !surface->pixels || thickness <= 0) {
        return UG_ERROR_INVALID_PARAM;
    }
    
    if (thickness == 1) {
        return ug_draw_line(surface, x0, y0, x1, y1, color);
    }
    
    /* Calculate perpendicular offset for thick lines */
    float dx = x1 - x0;
    float dy = y1 - y0;
    float length = sqrtf(dx * dx + dy * dy);
    
    if (length == 0) {
        /* Point, draw as circle */
        return ug_draw_circle_filled(surface, x0, y0, thickness / 2, color);
    }
    
    /* Normalize perpendicular vector */
    float px = -dy / length;
    float py = dx / length;
    
    /* Calculate half thickness */
    float half_thickness = thickness / 2.0f;
    
    /* Draw multiple parallel lines */
    for (int32_t i = -thickness / 2; i <= thickness / 2; i++) {
        int32_t offset_x0 = x0 + (int32_t)(px * i);
        int32_t offset_y0 = y0 + (int32_t)(py * i);
        int32_t offset_x1 = x1 + (int32_t)(px * i);
        int32_t offset_y1 = y1 + (int32_t)(py * i);
        
        ug_draw_line(surface, offset_x0, offset_y0, offset_x1, offset_y1, color);
    }
    
    return UG_SUCCESS;
}

/* Line clipping using Cohen-Sutherland algorithm */
typedef enum {
    CLIP_INSIDE = 0,
    CLIP_LEFT = 1,
    CLIP_RIGHT = 2,
    CLIP_BOTTOM = 4,
    CLIP_TOP = 8
} clip_code_t;

static clip_code_t compute_clip_code(int32_t x, int32_t y, ug_rect_t clip_rect) {
    clip_code_t code = CLIP_INSIDE;
    
    if (x < clip_rect.x) {
        code |= CLIP_LEFT;
    } else if (x >= clip_rect.x + clip_rect.width) {
        code |= CLIP_RIGHT;
    }
    
    if (y < clip_rect.y) {
        code |= CLIP_BOTTOM;
    } else if (y >= clip_rect.y + clip_rect.height) {
        code |= CLIP_TOP;
    }
    
    return code;
}

ug_error_t ug_draw_line_clipped(ug_surface_t* surface, int32_t x0, int32_t y0,
                               int32_t x1, int32_t y1, ug_rect_t clip_rect, ug_color_t color) {
    if (!surface || !surface->pixels) {
        return UG_ERROR_INVALID_PARAM;
    }
    
    clip_code_t code0 = compute_clip_code(x0, y0, clip_rect);
    clip_code_t code1 = compute_clip_code(x1, y1, clip_rect);
    
    while (true) {
        if ((code0 | code1) == 0) {
            /* Both points inside */
            return ug_draw_line(surface, x0, y0, x1, y1, color);
        } else if (code0 & code1) {
            /* Both points outside same region */
            return UG_SUCCESS;
        } else {
            /* Line crosses boundary */
            clip_code_t code_out = code0 ? code0 : code1;
            int32_t x, y;
            
            if (code_out & CLIP_TOP) {
                x = x0 + (x1 - x0) * (clip_rect.y + clip_rect.height - 1 - y0) / (y1 - y0);
                y = clip_rect.y + clip_rect.height - 1;
            } else if (code_out & CLIP_BOTTOM) {
                x = x0 + (x1 - x0) * (clip_rect.y - y0) / (y1 - y0);
                y = clip_rect.y;
            } else if (code_out & CLIP_RIGHT) {
                y = y0 + (y1 - y0) * (clip_rect.x + clip_rect.width - 1 - x0) / (x1 - x0);
                x = clip_rect.x + clip_rect.width - 1;
            } else if (code_out & CLIP_LEFT) {
                y = y0 + (y1 - y0) * (clip_rect.x - x0) / (x1 - x0);
                x = clip_rect.x;
            }
            
            if (code_out == code0) {
                x0 = x;
                y0 = y;
                code0 = compute_clip_code(x0, y0, clip_rect);
            } else {
                x1 = x;
                y1 = y;
                code1 = compute_clip_code(x1, y1, clip_rect);
            }
        }
    }
}
