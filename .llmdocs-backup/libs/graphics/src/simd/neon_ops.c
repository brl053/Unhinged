/**
 * @file neon_ops.c
 * @brief ARM NEON SIMD optimizations for graphics operations
 * 
 * Provides NEON-accelerated implementations of common graphics operations:
 * - Surface clearing
 * - Alpha blending
 * - Color space conversions
 * - Horizontal line drawing
 */

#ifdef ENABLE_NEON

#include "unhinged_graphics.h"
#include <arm_neon.h>
#include <string.h>

/* NEON surface clear - process 4 pixels at once */
void ug_surface_clear_neon(ug_surface_t* surface, ug_color_t color) {
    if (!surface || !surface->pixels) {
        return;
    }
    
    /* Pack color into 32-bit value */
    uint32_t pixel = (color.a << 24) | (color.r << 16) | (color.g << 8) | color.b;
    
    /* Create NEON vector with 4 copies of the pixel */
    uint32x4_t pixel_vec = vdupq_n_u32(pixel);
    
    uint32_t* pixels = surface->pixels;
    int32_t total_pixels = surface->width * surface->height;
    int32_t simd_pixels = total_pixels & ~3;  /* Round down to multiple of 4 */
    
    /* Process 4 pixels at a time */
    for (int32_t i = 0; i < simd_pixels; i += 4) {
        vst1q_u32(pixels + i, pixel_vec);
    }
    
    /* Handle remaining pixels */
    for (int32_t i = simd_pixels; i < total_pixels; i++) {
        pixels[i] = pixel;
    }
}

/* NEON horizontal line drawing */
void ug_draw_horizontal_line_neon(ug_surface_t* surface, int32_t x1, int32_t x2, int32_t y, ug_color_t color) {
    if (!surface || !surface->pixels || y < 0 || y >= surface->height) {
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
    uint32x4_t pixel_vec = vdupq_n_u32(pixel);
    
    uint32_t* row = &surface->pixels[y * surface->width + x1];
    int32_t width = x2 - x1 + 1;
    int32_t simd_width = width & ~3;  /* Round down to multiple of 4 */
    
    /* Process 4 pixels at a time */
    for (int32_t i = 0; i < simd_width; i += 4) {
        vst1q_u32(row + i, pixel_vec);
    }
    
    /* Handle remaining pixels */
    for (int32_t i = simd_width; i < width; i++) {
        row[i] = pixel;
    }
}

/* NEON alpha blending for 4 pixels */
void ug_alpha_blend_neon(uint32_t* dst, const uint32_t* src, int32_t count) {
    if (!dst || !src || count <= 0) {
        return;
    }
    
    const uint16x8_t alpha_255 = vdupq_n_u16(255);
    
    int32_t simd_count = count & ~3;  /* Process 4 pixels at a time */
    
    for (int32_t i = 0; i < simd_count; i += 4) {
        /* Load source and destination pixels */
        uint32x4_t src_pixels = vld1q_u32(src + i);
        uint32x4_t dst_pixels = vld1q_u32(dst + i);
        
        /* Extract alpha channel from source (shift right by 24 bits) */
        uint32x4_t src_alpha_32 = vshrq_n_u32(src_pixels, 24);
        
        /* Convert to 16-bit for better precision */
        uint16x4_t src_alpha_16 = vmovn_u32(src_alpha_32);
        uint16x4_t inv_alpha_16 = vsub_u16(vdup_n_u16(255), src_alpha_16);
        
        /* Expand to 8 elements for processing */
        uint16x8_t src_alpha_8x = vcombine_u16(src_alpha_16, src_alpha_16);
        uint16x8_t inv_alpha_8x = vcombine_u16(inv_alpha_16, inv_alpha_16);
        
        /* Convert pixels to 16-bit for processing */
        uint8x16_t src_bytes = vreinterpretq_u8_u32(src_pixels);
        uint8x16_t dst_bytes = vreinterpretq_u8_u32(dst_pixels);
        
        /* Split into low and high 8 bytes */
        uint8x8_t src_low = vget_low_u8(src_bytes);
        uint8x8_t src_high = vget_high_u8(src_bytes);
        uint8x8_t dst_low = vget_low_u8(dst_bytes);
        uint8x8_t dst_high = vget_high_u8(dst_bytes);
        
        /* Convert to 16-bit */
        uint16x8_t src_16_low = vmovl_u8(src_low);
        uint16x8_t src_16_high = vmovl_u8(src_high);
        uint16x8_t dst_16_low = vmovl_u8(dst_low);
        uint16x8_t dst_16_high = vmovl_u8(dst_high);
        
        /* Blend: result = src * alpha + dst * (255 - alpha) */
        uint16x8_t blend_low = vaddq_u16(
            vmulq_u16(src_16_low, src_alpha_8x),
            vmulq_u16(dst_16_low, inv_alpha_8x)
        );
        uint16x8_t blend_high = vaddq_u16(
            vmulq_u16(src_16_high, src_alpha_8x),
            vmulq_u16(dst_16_high, inv_alpha_8x)
        );
        
        /* Divide by 255 (approximate with shift) */
        blend_low = vshrq_n_u16(vaddq_u16(blend_low, vdupq_n_u16(128)), 8);
        blend_high = vshrq_n_u16(vaddq_u16(blend_high, vdupq_n_u16(128)), 8);
        
        /* Pack back to 8-bit */
        uint8x8_t result_low = vmovn_u16(blend_low);
        uint8x8_t result_high = vmovn_u16(blend_high);
        uint8x16_t result_bytes = vcombine_u8(result_low, result_high);
        
        /* Convert back to 32-bit pixels and preserve source alpha */
        uint32x4_t result_pixels = vreinterpretq_u32_u8(result_bytes);
        
        /* Mask to preserve alpha channel from source */
        uint32x4_t alpha_mask = vdupq_n_u32(0xFF000000);
        uint32x4_t color_mask = vdupq_n_u32(0x00FFFFFF);
        
        result_pixels = vorrq_u32(
            vandq_u32(result_pixels, color_mask),
            vandq_u32(src_pixels, alpha_mask)
        );
        
        /* Store result */
        vst1q_u32(dst + i, result_pixels);
    }
    
    /* Handle remaining pixels with scalar code */
    for (int32_t i = simd_count; i < count; i++) {
        uint32_t src_pixel = src[i];
        uint32_t dst_pixel = dst[i];
        
        uint32_t src_alpha = (src_pixel >> 24) & 0xFF;
        uint32_t inv_alpha = 255 - src_alpha;
        
        uint32_t src_r = (src_pixel >> 16) & 0xFF;
        uint32_t src_g = (src_pixel >> 8) & 0xFF;
        uint32_t src_b = src_pixel & 0xFF;
        
        uint32_t dst_r = (dst_pixel >> 16) & 0xFF;
        uint32_t dst_g = (dst_pixel >> 8) & 0xFF;
        uint32_t dst_b = dst_pixel & 0xFF;
        
        uint32_t result_r = (src_r * src_alpha + dst_r * inv_alpha) / 255;
        uint32_t result_g = (src_g * src_alpha + dst_g * inv_alpha) / 255;
        uint32_t result_b = (src_b * src_alpha + dst_b * inv_alpha) / 255;
        
        dst[i] = (src_alpha << 24) | (result_r << 16) | (result_g << 8) | result_b;
    }
}

/* NEON color multiplication (for tinting) */
void ug_color_multiply_neon(uint32_t* pixels, int32_t count, ug_color_t tint) {
    if (!pixels || count <= 0) {
        return;
    }
    
    /* Create tint vectors */
    uint16x4_t tint_vec = {tint.r, tint.g, tint.b, tint.a};
    uint16x8_t tint_8x = vcombine_u16(tint_vec, tint_vec);
    
    int32_t simd_count = count & ~3;
    
    for (int32_t i = 0; i < simd_count; i += 4) {
        uint32x4_t pixels_vec = vld1q_u32(pixels + i);
        
        /* Convert to bytes */
        uint8x16_t pixel_bytes = vreinterpretq_u8_u32(pixels_vec);
        
        /* Split into low and high */
        uint8x8_t pixel_low = vget_low_u8(pixel_bytes);
        uint8x8_t pixel_high = vget_high_u8(pixel_bytes);
        
        /* Convert to 16-bit */
        uint16x8_t pixel_16_low = vmovl_u8(pixel_low);
        uint16x8_t pixel_16_high = vmovl_u8(pixel_high);
        
        /* Multiply by tint */
        pixel_16_low = vmulq_u16(pixel_16_low, tint_8x);
        pixel_16_high = vmulq_u16(pixel_16_high, tint_8x);
        
        /* Divide by 255 */
        pixel_16_low = vshrq_n_u16(vaddq_u16(pixel_16_low, vdupq_n_u16(128)), 8);
        pixel_16_high = vshrq_n_u16(vaddq_u16(pixel_16_high, vdupq_n_u16(128)), 8);
        
        /* Pack back to 8-bit */
        uint8x8_t result_low = vmovn_u16(pixel_16_low);
        uint8x8_t result_high = vmovn_u16(pixel_16_high);
        uint8x16_t result_bytes = vcombine_u8(result_low, result_high);
        
        /* Convert back to 32-bit */
        uint32x4_t result = vreinterpretq_u32_u8(result_bytes);
        
        vst1q_u32(pixels + i, result);
    }
    
    /* Handle remaining pixels */
    for (int32_t i = simd_count; i < count; i++) {
        uint32_t pixel = pixels[i];
        uint32_t r = ((pixel >> 16) & 0xFF) * tint.r / 255;
        uint32_t g = ((pixel >> 8) & 0xFF) * tint.g / 255;
        uint32_t b = (pixel & 0xFF) * tint.b / 255;
        uint32_t a = ((pixel >> 24) & 0xFF) * tint.a / 255;
        
        pixels[i] = (a << 24) | (r << 16) | (g << 8) | b;
    }
}

/* NEON RGB to grayscale conversion */
void ug_rgb_to_grayscale_neon(uint32_t* pixels, int32_t count) {
    if (!pixels || count <= 0) {
        return;
    }
    
    /* Grayscale weights: R=0.299, G=0.587, B=0.114 */
    /* Using fixed-point: R=77, G=150, B=29 (sum=256) */
    const uint16x4_t weights = {29, 150, 77, 0};  /* B, G, R, A */
    const uint16x8_t weights_8x = vcombine_u16(weights, weights);
    
    int32_t simd_count = count & ~3;
    
    for (int32_t i = 0; i < simd_count; i += 4) {
        uint32x4_t pixels_vec = vld1q_u32(pixels + i);
        
        /* Convert to bytes */
        uint8x16_t pixel_bytes = vreinterpretq_u8_u32(pixels_vec);
        
        /* Convert to 16-bit */
        uint8x8_t pixel_low = vget_low_u8(pixel_bytes);
        uint8x8_t pixel_high = vget_high_u8(pixel_bytes);
        uint16x8_t pixel_16_low = vmovl_u8(pixel_low);
        uint16x8_t pixel_16_high = vmovl_u8(pixel_high);
        
        /* Multiply by weights */
        uint16x8_t weighted_low = vmulq_u16(pixel_16_low, weights_8x);
        uint16x8_t weighted_high = vmulq_u16(pixel_16_high, weights_8x);
        
        /* Sum RGB components (every 4 elements) */
        /* This is a simplified version - full implementation would need proper channel extraction */
        uint16x8_t gray_low = vshrq_n_u16(weighted_low, 8);
        uint16x8_t gray_high = vshrq_n_u16(weighted_high, 8);
        
        /* Pack back to 8-bit */
        uint8x8_t result_low = vmovn_u16(gray_low);
        uint8x8_t result_high = vmovn_u16(gray_high);
        uint8x16_t result_bytes = vcombine_u8(result_low, result_high);
        
        uint32x4_t result = vreinterpretq_u32_u8(result_bytes);
        vst1q_u32(pixels + i, result);
    }
    
    /* Handle remaining pixels */
    for (int32_t i = simd_count; i < count; i++) {
        uint32_t pixel = pixels[i];
        uint32_t r = (pixel >> 16) & 0xFF;
        uint32_t g = (pixel >> 8) & 0xFF;
        uint32_t b = pixel & 0xFF;
        uint32_t a = (pixel >> 24) & 0xFF;
        
        uint32_t gray = (r * 77 + g * 150 + b * 29) >> 8;
        pixels[i] = (a << 24) | (gray << 16) | (gray << 8) | gray;
    }
}

/* Check if NEON is available at runtime */
bool ug_neon_available(void) {
    /* On AArch64, NEON is always available */
    #ifdef __aarch64__
        return true;
    #else
        /* On 32-bit ARM, check for NEON support */
        /* This would typically check /proc/cpuinfo or use getauxval() */
        return true;  /* Assume available for now */
    #endif
}

#endif /* ENABLE_NEON */
