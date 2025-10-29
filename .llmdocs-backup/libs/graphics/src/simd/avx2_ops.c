/**
 * @file avx2_ops.c
 * @brief AVX2 SIMD optimizations for graphics operations
 * 
 * Provides AVX2-accelerated implementations of common graphics operations:
 * - Surface clearing
 * - Alpha blending
 * - Color space conversions
 * - Horizontal line drawing
 */

#ifdef ENABLE_AVX2

#include "unhinged_graphics.h"
#include <immintrin.h>
#include <string.h>

/* AVX2 surface clear - process 8 pixels at once */
void ug_surface_clear_avx2(ug_surface_t* surface, ug_color_t color) {
    if (!surface || !surface->pixels) {
        return;
    }
    
    /* Pack color into 32-bit value */
    uint32_t pixel = (color.a << 24) | (color.r << 16) | (color.g << 8) | color.b;
    
    /* Create AVX2 vector with 8 copies of the pixel */
    __m256i pixel_vec = _mm256_set1_epi32(pixel);
    
    uint32_t* pixels = surface->pixels;
    int32_t total_pixels = surface->width * surface->height;
    int32_t simd_pixels = total_pixels & ~7;  /* Round down to multiple of 8 */
    
    /* Process 8 pixels at a time */
    for (int32_t i = 0; i < simd_pixels; i += 8) {
        _mm256_storeu_si256((__m256i*)(pixels + i), pixel_vec);
    }
    
    /* Handle remaining pixels */
    for (int32_t i = simd_pixels; i < total_pixels; i++) {
        pixels[i] = pixel;
    }
}

/* AVX2 horizontal line drawing */
void ug_draw_horizontal_line_avx2(ug_surface_t* surface, int32_t x1, int32_t x2, int32_t y, ug_color_t color) {
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
    __m256i pixel_vec = _mm256_set1_epi32(pixel);
    
    uint32_t* row = &surface->pixels[y * surface->width + x1];
    int32_t width = x2 - x1 + 1;
    int32_t simd_width = width & ~7;  /* Round down to multiple of 8 */
    
    /* Process 8 pixels at a time */
    for (int32_t i = 0; i < simd_width; i += 8) {
        _mm256_storeu_si256((__m256i*)(row + i), pixel_vec);
    }
    
    /* Handle remaining pixels */
    for (int32_t i = simd_width; i < width; i++) {
        row[i] = pixel;
    }
}

/* AVX2 alpha blending for 8 pixels */
void ug_alpha_blend_avx2(uint32_t* dst, const uint32_t* src, int32_t count) {
    if (!dst || !src || count <= 0) {
        return;
    }
    
    const __m256i alpha_mask = _mm256_set1_epi32(0xFF000000);
    const __m256i rb_mask = _mm256_set1_epi32(0x00FF00FF);
    const __m256i g_mask = _mm256_set1_epi32(0x0000FF00);
    const __m256i one = _mm256_set1_epi16(1);
    const __m256i alpha_255 = _mm256_set1_epi16(255);
    
    int32_t simd_count = count & ~7;  /* Process 8 pixels at a time */
    
    for (int32_t i = 0; i < simd_count; i += 8) {
        /* Load source and destination pixels */
        __m256i src_pixels = _mm256_loadu_si256((__m256i*)(src + i));
        __m256i dst_pixels = _mm256_loadu_si256((__m256i*)(dst + i));
        
        /* Extract alpha channel from source */
        __m256i src_alpha = _mm256_and_si256(_mm256_srli_epi32(src_pixels, 24), _mm256_set1_epi32(0xFF));
        
        /* Convert to 16-bit for better precision */
        __m256i src_alpha_16 = _mm256_unpacklo_epi8(src_alpha, _mm256_setzero_si256());
        __m256i inv_alpha_16 = _mm256_sub_epi16(alpha_255, src_alpha_16);
        
        /* Separate R,B and G channels for processing */
        __m256i src_rb = _mm256_and_si256(src_pixels, rb_mask);
        __m256i src_g = _mm256_and_si256(src_pixels, g_mask);
        __m256i dst_rb = _mm256_and_si256(dst_pixels, rb_mask);
        __m256i dst_g = _mm256_and_si256(dst_pixels, g_mask);
        
        /* Convert to 16-bit */
        __m256i src_rb_16 = _mm256_unpacklo_epi8(src_rb, _mm256_setzero_si256());
        __m256i src_g_16 = _mm256_unpacklo_epi8(src_g, _mm256_setzero_si256());
        __m256i dst_rb_16 = _mm256_unpacklo_epi8(dst_rb, _mm256_setzero_si256());
        __m256i dst_g_16 = _mm256_unpacklo_epi8(dst_g, _mm256_setzero_si256());
        
        /* Blend: result = src * alpha + dst * (255 - alpha) */
        __m256i blend_rb = _mm256_add_epi16(
            _mm256_mullo_epi16(src_rb_16, src_alpha_16),
            _mm256_mullo_epi16(dst_rb_16, inv_alpha_16)
        );
        __m256i blend_g = _mm256_add_epi16(
            _mm256_mullo_epi16(src_g_16, src_alpha_16),
            _mm256_mullo_epi16(dst_g_16, inv_alpha_16)
        );
        
        /* Divide by 255 (approximate with shift and add) */
        blend_rb = _mm256_srli_epi16(_mm256_add_epi16(blend_rb, _mm256_set1_epi16(128)), 8);
        blend_g = _mm256_srli_epi16(_mm256_add_epi16(blend_g, _mm256_set1_epi16(128)), 8);
        
        /* Pack back to 8-bit and combine channels */
        __m256i result_rb = _mm256_packus_epi16(blend_rb, _mm256_setzero_si256());
        __m256i result_g = _mm256_packus_epi16(blend_g, _mm256_setzero_si256());
        
        result_rb = _mm256_and_si256(result_rb, rb_mask);
        result_g = _mm256_and_si256(result_g, g_mask);
        
        /* Combine with original alpha */
        __m256i result = _mm256_or_si256(_mm256_or_si256(result_rb, result_g), 
                                        _mm256_and_si256(src_pixels, alpha_mask));
        
        /* Store result */
        _mm256_storeu_si256((__m256i*)(dst + i), result);
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

/* AVX2 color multiplication (for tinting) */
void ug_color_multiply_avx2(uint32_t* pixels, int32_t count, ug_color_t tint) {
    if (!pixels || count <= 0) {
        return;
    }
    
    /* Convert tint to 16-bit values */
    __m256i tint_r = _mm256_set1_epi16(tint.r);
    __m256i tint_g = _mm256_set1_epi16(tint.g);
    __m256i tint_b = _mm256_set1_epi16(tint.b);
    __m256i tint_a = _mm256_set1_epi16(tint.a);
    
    const __m256i rb_mask = _mm256_set1_epi32(0x00FF00FF);
    const __m256i g_mask = _mm256_set1_epi32(0x0000FF00);
    const __m256i alpha_mask = _mm256_set1_epi32(0xFF000000);
    
    int32_t simd_count = count & ~7;
    
    for (int32_t i = 0; i < simd_count; i += 8) {
        __m256i pixels_vec = _mm256_loadu_si256((__m256i*)(pixels + i));
        
        /* Extract channels */
        __m256i r = _mm256_and_si256(_mm256_srli_epi32(pixels_vec, 16), _mm256_set1_epi32(0xFF));
        __m256i g = _mm256_and_si256(_mm256_srli_epi32(pixels_vec, 8), _mm256_set1_epi32(0xFF));
        __m256i b = _mm256_and_si256(pixels_vec, _mm256_set1_epi32(0xFF));
        __m256i a = _mm256_and_si256(_mm256_srli_epi32(pixels_vec, 24), _mm256_set1_epi32(0xFF));
        
        /* Convert to 16-bit and multiply */
        __m256i r_16 = _mm256_unpacklo_epi8(r, _mm256_setzero_si256());
        __m256i g_16 = _mm256_unpacklo_epi8(g, _mm256_setzero_si256());
        __m256i b_16 = _mm256_unpacklo_epi8(b, _mm256_setzero_si256());
        __m256i a_16 = _mm256_unpacklo_epi8(a, _mm256_setzero_si256());
        
        r_16 = _mm256_mullo_epi16(r_16, tint_r);
        g_16 = _mm256_mullo_epi16(g_16, tint_g);
        b_16 = _mm256_mullo_epi16(b_16, tint_b);
        a_16 = _mm256_mullo_epi16(a_16, tint_a);
        
        /* Divide by 255 */
        r_16 = _mm256_srli_epi16(_mm256_add_epi16(r_16, _mm256_set1_epi16(128)), 8);
        g_16 = _mm256_srli_epi16(_mm256_add_epi16(g_16, _mm256_set1_epi16(128)), 8);
        b_16 = _mm256_srli_epi16(_mm256_add_epi16(b_16, _mm256_set1_epi16(128)), 8);
        a_16 = _mm256_srli_epi16(_mm256_add_epi16(a_16, _mm256_set1_epi16(128)), 8);
        
        /* Pack back to 8-bit */
        __m256i r_8 = _mm256_packus_epi16(r_16, _mm256_setzero_si256());
        __m256i g_8 = _mm256_packus_epi16(g_16, _mm256_setzero_si256());
        __m256i b_8 = _mm256_packus_epi16(b_16, _mm256_setzero_si256());
        __m256i a_8 = _mm256_packus_epi16(a_16, _mm256_setzero_si256());
        
        /* Combine channels */
        __m256i result = _mm256_or_si256(
            _mm256_or_si256(_mm256_slli_epi32(a_8, 24), _mm256_slli_epi32(r_8, 16)),
            _mm256_or_si256(_mm256_slli_epi32(g_8, 8), b_8)
        );
        
        _mm256_storeu_si256((__m256i*)(pixels + i), result);
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

/* Check if AVX2 is available at runtime */
bool ug_avx2_available(void) {
    /* This would typically use CPUID instruction */
    /* For now, return true if compiled with AVX2 support */
    return true;
}

#endif /* ENABLE_AVX2 */
