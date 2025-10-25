/**
 * @file blending.c
 * @brief Color blending operations and alpha compositing
 * 
 * Provides various blending modes and alpha compositing functions
 * optimized for real-time graphics rendering.
 */

#include "unhinged_graphics.h"

/* Utility functions */
static inline uint8_t clamp_u8(int32_t value) {
    if (value < 0) return 0;
    if (value > 255) return 255;
    return (uint8_t)value;
}

static inline float clamp_f(float value) {
    if (value < 0.0f) return 0.0f;
    if (value > 1.0f) return 1.0f;
    return value;
}

/* Convert uint8 color to float */
static inline ug_color_f_t u8_to_float(ug_color_t color) {
    return (ug_color_f_t){
        .r = color.r / 255.0f,
        .g = color.g / 255.0f,
        .b = color.b / 255.0f,
        .a = color.a / 255.0f
    };
}

/* Convert float color to uint8 */
static inline ug_color_t float_to_u8(ug_color_f_t color) {
    return (ug_color_t){
        .r = clamp_u8((int32_t)(color.r * 255.0f + 0.5f)),
        .g = clamp_u8((int32_t)(color.g * 255.0f + 0.5f)),
        .b = clamp_u8((int32_t)(color.b * 255.0f + 0.5f)),
        .a = clamp_u8((int32_t)(color.a * 255.0f + 0.5f))
    };
}

/* Alpha blending (Porter-Duff "over" operation) */
ug_color_t ug_color_alpha_blend(ug_color_t src, ug_color_t dst) {
    if (src.a == 0) {
        return dst;
    }
    if (src.a == 255) {
        return src;
    }
    
    /* Convert to float for precision */
    float src_alpha = src.a / 255.0f;
    float dst_alpha = dst.a / 255.0f;
    float inv_src_alpha = 1.0f - src_alpha;
    
    /* Calculate result alpha */
    float result_alpha = src_alpha + dst_alpha * inv_src_alpha;
    
    if (result_alpha == 0.0f) {
        return (ug_color_t){0, 0, 0, 0};
    }
    
    /* Calculate premultiplied colors */
    float src_r = (src.r / 255.0f) * src_alpha;
    float src_g = (src.g / 255.0f) * src_alpha;
    float src_b = (src.b / 255.0f) * src_alpha;
    
    float dst_r = (dst.r / 255.0f) * dst_alpha * inv_src_alpha;
    float dst_g = (dst.g / 255.0f) * dst_alpha * inv_src_alpha;
    float dst_b = (dst.b / 255.0f) * dst_alpha * inv_src_alpha;
    
    /* Combine and unpremultiply */
    float result_r = (src_r + dst_r) / result_alpha;
    float result_g = (src_g + dst_g) / result_alpha;
    float result_b = (src_b + dst_b) / result_alpha;
    
    return (ug_color_t){
        .r = clamp_u8((int32_t)(result_r * 255.0f + 0.5f)),
        .g = clamp_u8((int32_t)(result_g * 255.0f + 0.5f)),
        .b = clamp_u8((int32_t)(result_b * 255.0f + 0.5f)),
        .a = clamp_u8((int32_t)(result_alpha * 255.0f + 0.5f))
    };
}

/* General blending function */
ug_color_t ug_color_blend(ug_color_t src, ug_color_t dst, ug_blend_mode_t mode) {
    switch (mode) {
        case UG_BLEND_NONE:
            return src;
            
        case UG_BLEND_ALPHA:
            return ug_color_alpha_blend(src, dst);
            
        case UG_BLEND_ADD: {
            return (ug_color_t){
                .r = clamp_u8((int32_t)src.r + dst.r),
                .g = clamp_u8((int32_t)src.g + dst.g),
                .b = clamp_u8((int32_t)src.b + dst.b),
                .a = clamp_u8((int32_t)src.a + dst.a)
            };
        }
        
        case UG_BLEND_MULTIPLY: {
            return (ug_color_t){
                .r = (src.r * dst.r) / 255,
                .g = (src.g * dst.g) / 255,
                .b = (src.b * dst.b) / 255,
                .a = (src.a * dst.a) / 255
            };
        }
        
        case UG_BLEND_SCREEN: {
            return (ug_color_t){
                .r = 255 - ((255 - src.r) * (255 - dst.r)) / 255,
                .g = 255 - ((255 - src.g) * (255 - dst.g)) / 255,
                .b = 255 - ((255 - src.b) * (255 - dst.b)) / 255,
                .a = 255 - ((255 - src.a) * (255 - dst.a)) / 255
            };
        }
        
        default:
            return src;
    }
}

/* Advanced blending modes using float precision */
ug_color_t ug_color_blend_advanced(ug_color_t src, ug_color_t dst, ug_blend_mode_t mode, float opacity) {
    ug_color_f_t src_f = u8_to_float(src);
    ug_color_f_t dst_f = u8_to_float(dst);
    ug_color_f_t result_f;
    
    /* Apply opacity to source */
    src_f.a *= opacity;
    
    switch (mode) {
        case UG_BLEND_NONE:
            result_f = src_f;
            break;
            
        case UG_BLEND_ALPHA: {
            float alpha = src_f.a;
            float inv_alpha = 1.0f - alpha;
            
            result_f.r = src_f.r * alpha + dst_f.r * inv_alpha;
            result_f.g = src_f.g * alpha + dst_f.g * inv_alpha;
            result_f.b = src_f.b * alpha + dst_f.b * inv_alpha;
            result_f.a = alpha + dst_f.a * inv_alpha;
            break;
        }
        
        case UG_BLEND_ADD:
            result_f.r = clamp_f(src_f.r + dst_f.r);
            result_f.g = clamp_f(src_f.g + dst_f.g);
            result_f.b = clamp_f(src_f.b + dst_f.b);
            result_f.a = clamp_f(src_f.a + dst_f.a);
            break;
            
        case UG_BLEND_MULTIPLY:
            result_f.r = src_f.r * dst_f.r;
            result_f.g = src_f.g * dst_f.g;
            result_f.b = src_f.b * dst_f.b;
            result_f.a = src_f.a * dst_f.a;
            break;
            
        case UG_BLEND_SCREEN:
            result_f.r = 1.0f - (1.0f - src_f.r) * (1.0f - dst_f.r);
            result_f.g = 1.0f - (1.0f - src_f.g) * (1.0f - dst_f.g);
            result_f.b = 1.0f - (1.0f - src_f.b) * (1.0f - dst_f.b);
            result_f.a = 1.0f - (1.0f - src_f.a) * (1.0f - dst_f.a);
            break;
            
        default:
            result_f = src_f;
            break;
    }
    
    return float_to_u8(result_f);
}

/* Overlay blend mode */
ug_color_t ug_color_blend_overlay(ug_color_t src, ug_color_t dst) {
    ug_color_f_t src_f = u8_to_float(src);
    ug_color_f_t dst_f = u8_to_float(dst);
    ug_color_f_t result_f;
    
    /* Overlay formula */
    result_f.r = dst_f.r < 0.5f ? 
        2.0f * src_f.r * dst_f.r : 
        1.0f - 2.0f * (1.0f - src_f.r) * (1.0f - dst_f.r);
        
    result_f.g = dst_f.g < 0.5f ? 
        2.0f * src_f.g * dst_f.g : 
        1.0f - 2.0f * (1.0f - src_f.g) * (1.0f - dst_f.g);
        
    result_f.b = dst_f.b < 0.5f ? 
        2.0f * src_f.b * dst_f.b : 
        1.0f - 2.0f * (1.0f - src_f.b) * (1.0f - dst_f.b);
        
    result_f.a = src_f.a;
    
    return float_to_u8(result_f);
}

/* Soft light blend mode */
ug_color_t ug_color_blend_soft_light(ug_color_t src, ug_color_t dst) {
    ug_color_f_t src_f = u8_to_float(src);
    ug_color_f_t dst_f = u8_to_float(dst);
    ug_color_f_t result_f;
    
    /* Soft light formula */
    result_f.r = (1.0f - 2.0f * src_f.r) * dst_f.r * dst_f.r + 2.0f * src_f.r * dst_f.r;
    result_f.g = (1.0f - 2.0f * src_f.g) * dst_f.g * dst_f.g + 2.0f * src_f.g * dst_f.g;
    result_f.b = (1.0f - 2.0f * src_f.b) * dst_f.b * dst_f.b + 2.0f * src_f.b * dst_f.b;
    result_f.a = src_f.a;
    
    return float_to_u8(result_f);
}

/* Hard light blend mode */
ug_color_t ug_color_blend_hard_light(ug_color_t src, ug_color_t dst) {
    ug_color_f_t src_f = u8_to_float(src);
    ug_color_f_t dst_f = u8_to_float(dst);
    ug_color_f_t result_f;
    
    /* Hard light formula */
    result_f.r = src_f.r < 0.5f ? 
        2.0f * src_f.r * dst_f.r : 
        1.0f - 2.0f * (1.0f - src_f.r) * (1.0f - dst_f.r);
        
    result_f.g = src_f.g < 0.5f ? 
        2.0f * src_f.g * dst_f.g : 
        1.0f - 2.0f * (1.0f - src_f.g) * (1.0f - dst_f.g);
        
    result_f.b = src_f.b < 0.5f ? 
        2.0f * src_f.b * dst_f.b : 
        1.0f - 2.0f * (1.0f - src_f.b) * (1.0f - dst_f.b);
        
    result_f.a = src_f.a;
    
    return float_to_u8(result_f);
}

/* Color dodge blend mode */
ug_color_t ug_color_blend_color_dodge(ug_color_t src, ug_color_t dst) {
    ug_color_f_t src_f = u8_to_float(src);
    ug_color_f_t dst_f = u8_to_float(dst);
    ug_color_f_t result_f;
    
    /* Color dodge formula */
    result_f.r = src_f.r >= 1.0f ? 1.0f : clamp_f(dst_f.r / (1.0f - src_f.r));
    result_f.g = src_f.g >= 1.0f ? 1.0f : clamp_f(dst_f.g / (1.0f - src_f.g));
    result_f.b = src_f.b >= 1.0f ? 1.0f : clamp_f(dst_f.b / (1.0f - src_f.b));
    result_f.a = src_f.a;
    
    return float_to_u8(result_f);
}

/* Color burn blend mode */
ug_color_t ug_color_blend_color_burn(ug_color_t src, ug_color_t dst) {
    ug_color_f_t src_f = u8_to_float(src);
    ug_color_f_t dst_f = u8_to_float(dst);
    ug_color_f_t result_f;
    
    /* Color burn formula */
    result_f.r = src_f.r <= 0.0f ? 0.0f : clamp_f(1.0f - (1.0f - dst_f.r) / src_f.r);
    result_f.g = src_f.g <= 0.0f ? 0.0f : clamp_f(1.0f - (1.0f - dst_f.g) / src_f.g);
    result_f.b = src_f.b <= 0.0f ? 0.0f : clamp_f(1.0f - (1.0f - dst_f.b) / src_f.b);
    result_f.a = src_f.a;
    
    return float_to_u8(result_f);
}

/* Difference blend mode */
ug_color_t ug_color_blend_difference(ug_color_t src, ug_color_t dst) {
    return (ug_color_t){
        .r = abs((int32_t)src.r - (int32_t)dst.r),
        .g = abs((int32_t)src.g - (int32_t)dst.g),
        .b = abs((int32_t)src.b - (int32_t)dst.b),
        .a = src.a
    };
}

/* Exclusion blend mode */
ug_color_t ug_color_blend_exclusion(ug_color_t src, ug_color_t dst) {
    ug_color_f_t src_f = u8_to_float(src);
    ug_color_f_t dst_f = u8_to_float(dst);
    ug_color_f_t result_f;
    
    /* Exclusion formula */
    result_f.r = src_f.r + dst_f.r - 2.0f * src_f.r * dst_f.r;
    result_f.g = src_f.g + dst_f.g - 2.0f * src_f.g * dst_f.g;
    result_f.b = src_f.b + dst_f.b - 2.0f * src_f.b * dst_f.b;
    result_f.a = src_f.a;
    
    return float_to_u8(result_f);
}
