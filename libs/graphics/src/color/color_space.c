/**
 * @file color_space.c
 * @brief Color space conversion functions
 * 
 * Provides conversions between different color spaces:
 * - RGB ↔ HSV
 * - RGB ↔ HSL  
 * - RGB ↔ LAB
 * - Gamma correction and linear color space operations
 */

#include "unhinged_graphics.h"
#include <math.h>

/* Utility functions */
static inline float clamp_f(float value, float min, float max) {
    if (value < min) return min;
    if (value > max) return max;
    return value;
}

static inline float max3_f(float a, float b, float c) {
    return fmaxf(fmaxf(a, b), c);
}

static inline float min3_f(float a, float b, float c) {
    return fminf(fminf(a, b), c);
}

/* RGB to HSV conversion */
static ug_color_f_t rgb_to_hsv(ug_color_f_t rgb) {
    float r = rgb.r;
    float g = rgb.g;
    float b = rgb.b;
    
    float max_val = max3_f(r, g, b);
    float min_val = min3_f(r, g, b);
    float delta = max_val - min_val;
    
    ug_color_f_t hsv;
    hsv.a = rgb.a;
    
    /* Value */
    hsv.b = max_val;  /* V component */
    
    /* Saturation */
    if (max_val == 0.0f) {
        hsv.g = 0.0f;  /* S component */
    } else {
        hsv.g = delta / max_val;
    }
    
    /* Hue */
    if (delta == 0.0f) {
        hsv.r = 0.0f;  /* H component */
    } else if (max_val == r) {
        hsv.r = 60.0f * fmodf((g - b) / delta, 6.0f);
    } else if (max_val == g) {
        hsv.r = 60.0f * ((b - r) / delta + 2.0f);
    } else {
        hsv.r = 60.0f * ((r - g) / delta + 4.0f);
    }
    
    if (hsv.r < 0.0f) {
        hsv.r += 360.0f;
    }
    
    /* Normalize hue to 0-1 range */
    hsv.r /= 360.0f;
    
    return hsv;
}

/* HSV to RGB conversion */
static ug_color_f_t hsv_to_rgb(ug_color_f_t hsv) {
    float h = hsv.r * 360.0f;  /* Convert back to degrees */
    float s = hsv.g;
    float v = hsv.b;
    
    ug_color_f_t rgb;
    rgb.a = hsv.a;
    
    if (s == 0.0f) {
        /* Achromatic (grey) */
        rgb.r = rgb.g = rgb.b = v;
        return rgb;
    }
    
    float c = v * s;
    float x = c * (1.0f - fabsf(fmodf(h / 60.0f, 2.0f) - 1.0f));
    float m = v - c;
    
    float r_prime, g_prime, b_prime;
    
    if (h >= 0.0f && h < 60.0f) {
        r_prime = c; g_prime = x; b_prime = 0.0f;
    } else if (h >= 60.0f && h < 120.0f) {
        r_prime = x; g_prime = c; b_prime = 0.0f;
    } else if (h >= 120.0f && h < 180.0f) {
        r_prime = 0.0f; g_prime = c; b_prime = x;
    } else if (h >= 180.0f && h < 240.0f) {
        r_prime = 0.0f; g_prime = x; b_prime = c;
    } else if (h >= 240.0f && h < 300.0f) {
        r_prime = x; g_prime = 0.0f; b_prime = c;
    } else {
        r_prime = c; g_prime = 0.0f; b_prime = x;
    }
    
    rgb.r = r_prime + m;
    rgb.g = g_prime + m;
    rgb.b = b_prime + m;
    
    return rgb;
}

/* RGB to HSL conversion */
static ug_color_f_t rgb_to_hsl(ug_color_f_t rgb) {
    float r = rgb.r;
    float g = rgb.g;
    float b = rgb.b;
    
    float max_val = max3_f(r, g, b);
    float min_val = min3_f(r, g, b);
    float delta = max_val - min_val;
    
    ug_color_f_t hsl;
    hsl.a = rgb.a;
    
    /* Lightness */
    hsl.b = (max_val + min_val) / 2.0f;  /* L component */
    
    if (delta == 0.0f) {
        /* Achromatic */
        hsl.r = 0.0f;  /* H component */
        hsl.g = 0.0f;  /* S component */
    } else {
        /* Saturation */
        if (hsl.b < 0.5f) {
            hsl.g = delta / (max_val + min_val);
        } else {
            hsl.g = delta / (2.0f - max_val - min_val);
        }
        
        /* Hue */
        if (max_val == r) {
            hsl.r = 60.0f * fmodf((g - b) / delta, 6.0f);
        } else if (max_val == g) {
            hsl.r = 60.0f * ((b - r) / delta + 2.0f);
        } else {
            hsl.r = 60.0f * ((r - g) / delta + 4.0f);
        }
        
        if (hsl.r < 0.0f) {
            hsl.r += 360.0f;
        }
        
        /* Normalize hue to 0-1 range */
        hsl.r /= 360.0f;
    }
    
    return hsl;
}

/* HSL to RGB conversion */
static ug_color_f_t hsl_to_rgb(ug_color_f_t hsl) {
    float h = hsl.r * 360.0f;  /* Convert back to degrees */
    float s = hsl.g;
    float l = hsl.b;
    
    ug_color_f_t rgb;
    rgb.a = hsl.a;
    
    if (s == 0.0f) {
        /* Achromatic */
        rgb.r = rgb.g = rgb.b = l;
        return rgb;
    }
    
    float c = (1.0f - fabsf(2.0f * l - 1.0f)) * s;
    float x = c * (1.0f - fabsf(fmodf(h / 60.0f, 2.0f) - 1.0f));
    float m = l - c / 2.0f;
    
    float r_prime, g_prime, b_prime;
    
    if (h >= 0.0f && h < 60.0f) {
        r_prime = c; g_prime = x; b_prime = 0.0f;
    } else if (h >= 60.0f && h < 120.0f) {
        r_prime = x; g_prime = c; b_prime = 0.0f;
    } else if (h >= 120.0f && h < 180.0f) {
        r_prime = 0.0f; g_prime = c; b_prime = x;
    } else if (h >= 180.0f && h < 240.0f) {
        r_prime = 0.0f; g_prime = x; b_prime = c;
    } else if (h >= 240.0f && h < 300.0f) {
        r_prime = x; g_prime = 0.0f; b_prime = c;
    } else {
        r_prime = c; g_prime = 0.0f; b_prime = x;
    }
    
    rgb.r = r_prime + m;
    rgb.g = g_prime + m;
    rgb.b = b_prime + m;
    
    return rgb;
}

/* RGB to LAB conversion (simplified, assumes sRGB) */
static ug_color_f_t rgb_to_lab(ug_color_f_t rgb) {
    /* Convert sRGB to linear RGB */
    float r = rgb.r <= 0.04045f ? rgb.r / 12.92f : powf((rgb.r + 0.055f) / 1.055f, 2.4f);
    float g = rgb.g <= 0.04045f ? rgb.g / 12.92f : powf((rgb.g + 0.055f) / 1.055f, 2.4f);
    float b = rgb.b <= 0.04045f ? rgb.b / 12.92f : powf((rgb.b + 0.055f) / 1.055f, 2.4f);
    
    /* Convert to XYZ (using sRGB matrix) */
    float x = 0.4124564f * r + 0.3575761f * g + 0.1804375f * b;
    float y = 0.2126729f * r + 0.7151522f * g + 0.0721750f * b;
    float z = 0.0193339f * r + 0.1191920f * g + 0.9503041f * b;
    
    /* Normalize by D65 white point */
    x /= 0.95047f;
    y /= 1.00000f;
    z /= 1.08883f;
    
    /* Apply LAB transformation */
    float fx = x > 0.008856f ? powf(x, 1.0f/3.0f) : (7.787f * x + 16.0f/116.0f);
    float fy = y > 0.008856f ? powf(y, 1.0f/3.0f) : (7.787f * y + 16.0f/116.0f);
    float fz = z > 0.008856f ? powf(z, 1.0f/3.0f) : (7.787f * z + 16.0f/116.0f);
    
    ug_color_f_t lab;
    lab.r = 116.0f * fy - 16.0f;  /* L component */
    lab.g = 500.0f * (fx - fy);   /* A component */
    lab.b = 200.0f * (fy - fz);   /* B component */
    lab.a = rgb.a;
    
    /* Normalize to 0-1 range */
    lab.r /= 100.0f;
    lab.g = (lab.g + 128.0f) / 256.0f;
    lab.b = (lab.b + 128.0f) / 256.0f;
    
    return lab;
}

/* LAB to RGB conversion (simplified) */
static ug_color_f_t lab_to_rgb(ug_color_f_t lab) {
    /* Denormalize from 0-1 range */
    float l = lab.r * 100.0f;
    float a = lab.g * 256.0f - 128.0f;
    float b = lab.b * 256.0f - 128.0f;
    
    /* Convert LAB to XYZ */
    float fy = (l + 16.0f) / 116.0f;
    float fx = a / 500.0f + fy;
    float fz = fy - b / 200.0f;
    
    float x = fx > 0.206897f ? fx * fx * fx : (fx - 16.0f/116.0f) / 7.787f;
    float y = fy > 0.206897f ? fy * fy * fy : (fy - 16.0f/116.0f) / 7.787f;
    float z = fz > 0.206897f ? fz * fz * fz : (fz - 16.0f/116.0f) / 7.787f;
    
    /* Scale by D65 white point */
    x *= 0.95047f;
    y *= 1.00000f;
    z *= 1.08883f;
    
    /* Convert XYZ to linear RGB */
    float r =  3.2404542f * x - 1.5371385f * y - 0.4985314f * z;
    float g = -0.9692660f * x + 1.8760108f * y + 0.0415560f * z;
    float b_lin =  0.0556434f * x - 0.2040259f * y + 1.0572252f * z;
    
    /* Convert linear RGB to sRGB */
    ug_color_f_t rgb;
    rgb.r = r <= 0.0031308f ? 12.92f * r : 1.055f * powf(r, 1.0f/2.4f) - 0.055f;
    rgb.g = g <= 0.0031308f ? 12.92f * g : 1.055f * powf(g, 1.0f/2.4f) - 0.055f;
    rgb.b = b_lin <= 0.0031308f ? 12.92f * b_lin : 1.055f * powf(b_lin, 1.0f/2.4f) - 0.055f;
    rgb.a = lab.a;
    
    /* Clamp to valid range */
    rgb.r = clamp_f(rgb.r, 0.0f, 1.0f);
    rgb.g = clamp_f(rgb.g, 0.0f, 1.0f);
    rgb.b = clamp_f(rgb.b, 0.0f, 1.0f);
    
    return rgb;
}

/* Public API */
ug_color_f_t ug_color_convert(ug_color_f_t src_color, ug_color_space_t src_space, 
                             ug_color_space_t dst_space) {
    if (src_space == dst_space) {
        return src_color;
    }
    
    /* Convert to RGB as intermediate format */
    ug_color_f_t rgb_color;
    
    switch (src_space) {
        case UG_COLOR_SPACE_RGB:
            rgb_color = src_color;
            break;
        case UG_COLOR_SPACE_HSV:
            rgb_color = hsv_to_rgb(src_color);
            break;
        case UG_COLOR_SPACE_HSL:
            rgb_color = hsl_to_rgb(src_color);
            break;
        case UG_COLOR_SPACE_LAB:
            rgb_color = lab_to_rgb(src_color);
            break;
        default:
            return src_color;
    }
    
    /* Convert from RGB to target format */
    switch (dst_space) {
        case UG_COLOR_SPACE_RGB:
            return rgb_color;
        case UG_COLOR_SPACE_HSV:
            return rgb_to_hsv(rgb_color);
        case UG_COLOR_SPACE_HSL:
            return rgb_to_hsl(rgb_color);
        case UG_COLOR_SPACE_LAB:
            return rgb_to_lab(rgb_color);
        default:
            return rgb_color;
    }
}
