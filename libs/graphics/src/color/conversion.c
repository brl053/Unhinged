/**
 * @file conversion.c
 * @brief Color format conversion utilities
 * 
 * Provides utilities for converting between different color formats
 * and gamma correction operations.
 */

#include "unhinged_graphics.h"
#include <math.h>

/* Gamma correction */
float ug_gamma_to_linear(float gamma_value) {
    if (gamma_value <= 0.04045f) {
        return gamma_value / 12.92f;
    } else {
        return powf((gamma_value + 0.055f) / 1.055f, 2.4f);
    }
}

float ug_linear_to_gamma(float linear_value) {
    if (linear_value <= 0.0031308f) {
        return 12.92f * linear_value;
    } else {
        return 1.055f * powf(linear_value, 1.0f / 2.4f) - 0.055f;
    }
}

/* Convert uint8 color to float color */
ug_color_f_t ug_color_u8_to_float(ug_color_t color) {
    return (ug_color_f_t){
        .r = color.r / 255.0f,
        .g = color.g / 255.0f,
        .b = color.b / 255.0f,
        .a = color.a / 255.0f
    };
}

/* Convert float color to uint8 color */
ug_color_t ug_color_float_to_u8(ug_color_f_t color) {
    return (ug_color_t){
        .r = (uint8_t)(color.r * 255.0f + 0.5f),
        .g = (uint8_t)(color.g * 255.0f + 0.5f),
        .b = (uint8_t)(color.b * 255.0f + 0.5f),
        .a = (uint8_t)(color.a * 255.0f + 0.5f)
    };
}

/* Premultiply alpha */
ug_color_f_t ug_color_premultiply_alpha(ug_color_f_t color) {
    return (ug_color_f_t){
        .r = color.r * color.a,
        .g = color.g * color.a,
        .b = color.b * color.a,
        .a = color.a
    };
}

/* Unpremultiply alpha */
ug_color_f_t ug_color_unpremultiply_alpha(ug_color_f_t color) {
    if (color.a == 0.0f) {
        return (ug_color_f_t){0, 0, 0, 0};
    }
    
    return (ug_color_f_t){
        .r = color.r / color.a,
        .g = color.g / color.a,
        .b = color.b / color.a,
        .a = color.a
    };
}
