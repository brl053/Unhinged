/**
 * @file error.c
 * @brief Error handling and reporting
 */

#include "unhinged_graphics.h"
#include <stdio.h>

static bool g_initialized = false;

const char* ug_get_version(void) {
    return "1.0.0";
}

ug_error_t ug_init(void) {
    if (g_initialized) {
        return UG_SUCCESS;
    }
    
    /* Initialize platform capabilities */
    ug_get_platform_caps();
    
    g_initialized = true;
    return UG_SUCCESS;
}

void ug_shutdown(void) {
    g_initialized = false;
}
