/**
 * @file test_main.c
 * @brief Main test runner for Unhinged Graphics Library
 */

#include "unhinged_graphics.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>

/* Test counter */
static int tests_run = 0;
static int tests_passed = 0;

#define TEST(name) \
    do { \
        printf("Running test: %s... ", #name); \
        tests_run++; \
        if (test_##name()) { \
            printf("PASSED\n"); \
            tests_passed++; \
        } else { \
            printf("FAILED\n"); \
        } \
    } while(0)

/* Basic initialization test */
bool test_initialization() {
    ug_error_t result = ug_init();
    if (result != UG_SUCCESS) {
        return false;
    }
    
    const char* version = ug_get_version();
    if (!version || strlen(version) == 0) {
        return false;
    }
    
    ug_shutdown();
    return true;
}

/* Platform capabilities test */
bool test_platform_caps() {
    ug_init();
    
    ug_platform_caps_t caps = ug_get_platform_caps();
    
    /* Platform name should not be null */
    if (!caps.platform_name || strlen(caps.platform_name) == 0) {
        ug_shutdown();
        return false;
    }
    
    /* GPU vendor should not be null */
    if (!caps.gpu_vendor || strlen(caps.gpu_vendor) == 0) {
        ug_shutdown();
        return false;
    }
    
    ug_shutdown();
    return true;
}

/* Memory allocator test */
bool test_memory_allocator() {
    ug_allocator_t* allocator = ug_allocator_create(1024 * 1024);
    if (!allocator) {
        return false;
    }
    
    /* Test basic allocation */
    void* ptr1 = ug_allocator_alloc(allocator, 1024, 16);
    if (!ptr1) {
        ug_allocator_destroy(allocator);
        return false;
    }
    
    /* Test aligned allocation */
    void* ptr2 = ug_allocator_alloc(allocator, 512, 32);
    if (!ptr2) {
        ug_allocator_destroy(allocator);
        return false;
    }
    
    /* Check alignment */
    if (((uintptr_t)ptr2 & 31) != 0) {
        ug_allocator_destroy(allocator);
        return false;
    }
    
    /* Free memory */
    ug_allocator_free(allocator, ptr1);
    ug_allocator_free(allocator, ptr2);
    
    ug_allocator_destroy(allocator);
    return true;
}

/* Surface creation test */
bool test_surface_creation() {
    ug_init();
    
    ug_surface_t* surface = ug_surface_create(800, 600, NULL);
    if (!surface) {
        ug_shutdown();
        return false;
    }
    
    ug_surface_destroy(surface);
    ug_shutdown();
    return true;
}

/* Basic drawing test */
bool test_basic_drawing() {
    ug_init();
    
    ug_surface_t* surface = ug_surface_create(100, 100, NULL);
    if (!surface) {
        ug_shutdown();
        return false;
    }
    
    /* Test surface clear */
    ug_color_t white = {255, 255, 255, 255};
    ug_error_t result = ug_surface_clear(surface, white);
    if (result != UG_SUCCESS) {
        ug_surface_destroy(surface);
        ug_shutdown();
        return false;
    }
    
    /* Test line drawing */
    ug_color_t red = {255, 0, 0, 255};
    result = ug_draw_line(surface, 10, 10, 90, 90, red);
    if (result != UG_SUCCESS) {
        ug_surface_destroy(surface);
        ug_shutdown();
        return false;
    }
    
    /* Test circle drawing */
    ug_color_t blue = {0, 0, 255, 255};
    result = ug_draw_circle_filled(surface, 50, 50, 20, blue);
    if (result != UG_SUCCESS) {
        ug_surface_destroy(surface);
        ug_shutdown();
        return false;
    }
    
    /* Test rectangle drawing */
    ug_color_t green = {0, 255, 0, 255};
    ug_rect_t rect = {20, 20, 30, 30};
    result = ug_draw_rect_filled(surface, rect, green);
    if (result != UG_SUCCESS) {
        ug_surface_destroy(surface);
        ug_shutdown();
        return false;
    }
    
    ug_surface_destroy(surface);
    ug_shutdown();
    return true;
}

/* Color blending test */
bool test_color_blending() {
    ug_color_t src = {255, 0, 0, 128};  /* Semi-transparent red */
    ug_color_t dst = {0, 255, 0, 255};  /* Opaque green */
    
    ug_color_t result = ug_color_alpha_blend(src, dst);
    
    /* Result should be a blend of red and green */
    if (result.r == 0 || result.g == 0) {
        return false;
    }
    
    /* Test other blend modes */
    ug_color_t multiply = ug_color_blend(src, dst, UG_BLEND_MULTIPLY);
    ug_color_t add = ug_color_blend(src, dst, UG_BLEND_ADD);
    
    return true;
}

/* Color space conversion test */
bool test_color_conversion() {
    ug_color_f_t rgb = {1.0f, 0.5f, 0.0f, 1.0f};  /* Orange */
    
    /* Convert RGB to HSV and back */
    ug_color_f_t hsv = ug_color_convert(rgb, UG_COLOR_SPACE_RGB, UG_COLOR_SPACE_HSV);
    ug_color_f_t back_to_rgb = ug_color_convert(hsv, UG_COLOR_SPACE_HSV, UG_COLOR_SPACE_RGB);
    
    /* Check if conversion is approximately correct */
    float tolerance = 0.01f;
    if (fabsf(rgb.r - back_to_rgb.r) > tolerance ||
        fabsf(rgb.g - back_to_rgb.g) > tolerance ||
        fabsf(rgb.b - back_to_rgb.b) > tolerance) {
        return false;
    }
    
    return true;
}

/* Error handling test */
bool test_error_handling() {
    /* Test invalid parameters */
    ug_surface_t* invalid_surface = ug_surface_create(-1, -1, NULL);
    if (invalid_surface != NULL) {
        return false;
    }
    
    /* Test null pointer handling */
    ug_error_t result = ug_surface_clear(NULL, (ug_color_t){0, 0, 0, 0});
    if (result == UG_SUCCESS) {
        return false;  /* Should fail with null surface */
    }
    
    return true;
}

int main() {
    printf("Unhinged Graphics Library - Test Suite\n");
    printf("=====================================\n\n");
    
    /* Run all tests */
    TEST(initialization);
    TEST(platform_caps);
    TEST(memory_allocator);
    TEST(surface_creation);
    TEST(basic_drawing);
    TEST(color_blending);
    TEST(color_conversion);
    TEST(error_handling);
    
    /* Print results */
    printf("\n=====================================\n");
    printf("Test Results: %d/%d tests passed\n", tests_passed, tests_run);
    
    if (tests_passed == tests_run) {
        printf("All tests PASSED! ✅\n");
        return 0;
    } else {
        printf("Some tests FAILED! ❌\n");
        return 1;
    }
}
