/**
 * @file window.c
 * @brief Simple window creation using DRM framebuffer
 * 
 * Creates a window by opening DRM device and setting up framebuffer.
 * No X11, no Wayland - direct hardware access.
 */

#include "unhinged_graphics.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <linux/fb.h>
#include <errno.h>

#ifdef __linux__
#include <xf86drm.h>
#include <xf86drmMode.h>
#endif

typedef struct {
    int drm_fd;
    uint32_t connector_id;
    uint32_t crtc_id;
    uint32_t fb_id;
    uint32_t *framebuffer;
    uint32_t width;
    uint32_t height;
    uint32_t pitch;
    size_t size;
    bool is_open;
} ug_window_t;

static ug_window_t g_window = {0};

/**
 * Find a suitable DRM connector and CRTC
 */
static bool find_drm_resources(int drm_fd, uint32_t *connector_id, uint32_t *crtc_id, 
                              uint32_t *width, uint32_t *height) {
#ifdef __linux__
    drmModeRes *resources = drmModeGetResources(drm_fd);
    if (!resources) {
        return false;
    }

    // Find first connected connector
    for (int i = 0; i < resources->count_connectors; i++) {
        drmModeConnector *connector = drmModeGetConnector(drm_fd, resources->connectors[i]);
        if (connector && connector->connection == DRM_MODE_CONNECTED && connector->count_modes > 0) {
            *connector_id = connector->connector_id;
            *width = connector->modes[0].hdisplay;
            *height = connector->modes[0].vdisplay;
            
            // Find CRTC
            if (connector->encoder_id) {
                drmModeEncoder *encoder = drmModeGetEncoder(drm_fd, connector->encoder_id);
                if (encoder) {
                    *crtc_id = encoder->crtc_id;
                    drmModeFreeEncoder(encoder);
                    drmModeFreeConnector(connector);
                    drmModeFreeResources(resources);
                    return true;
                }
            }
            drmModeFreeConnector(connector);
        }
    }
    
    drmModeFreeResources(resources);
#endif
    return false;
}

/**
 * Create DRM framebuffer
 */
static bool create_drm_framebuffer(int drm_fd, uint32_t width, uint32_t height,
                                  uint32_t *fb_id, uint32_t **framebuffer, 
                                  uint32_t *pitch, size_t *size) {
#ifdef __linux__
    struct drm_mode_create_dumb create_req = {0};
    create_req.width = width;
    create_req.height = height;
    create_req.bpp = 32;
    
    if (drmIoctl(drm_fd, DRM_IOCTL_MODE_CREATE_DUMB, &create_req) < 0) {
        return false;
    }
    
    *pitch = create_req.pitch;
    *size = create_req.size;
    
    // Create framebuffer
    if (drmModeAddFB(drm_fd, width, height, 24, 32, *pitch, create_req.handle, fb_id) < 0) {
        return false;
    }
    
    // Map framebuffer
    struct drm_mode_map_dumb map_req = {0};
    map_req.handle = create_req.handle;
    
    if (drmIoctl(drm_fd, DRM_IOCTL_MODE_MAP_DUMB, &map_req) < 0) {
        return false;
    }
    
    *framebuffer = mmap(0, *size, PROT_READ | PROT_WRITE, MAP_SHARED, drm_fd, map_req.offset);
    if (*framebuffer == MAP_FAILED) {
        return false;
    }
    
    return true;
#else
    return false;
#endif
}

/**
 * Create a simple window using DRM
 */
ug_error_t ug_window_create(uint32_t width, uint32_t height) {
    if (g_window.is_open) {
        return UG_SUCCESS; // Already open
    }
    
#ifdef __linux__
    // Open DRM device
    g_window.drm_fd = open("/dev/dri/card0", O_RDWR | O_CLOEXEC);
    if (g_window.drm_fd < 0) {
        printf("Failed to open DRM device: %s\n", strerror(errno));
        return UG_ERROR_PLATFORM_NOT_SUPPORTED;
    }
    
    // Find display resources
    uint32_t conn_width, conn_height;
    if (!find_drm_resources(g_window.drm_fd, &g_window.connector_id, &g_window.crtc_id, 
                           &conn_width, &conn_height)) {
        close(g_window.drm_fd);
        return UG_ERROR_PLATFORM_NOT_SUPPORTED;
    }
    
    // Use requested size or display size
    g_window.width = (width > 0) ? width : conn_width;
    g_window.height = (height > 0) ? height : conn_height;
    
    // Create framebuffer
    if (!create_drm_framebuffer(g_window.drm_fd, g_window.width, g_window.height,
                               &g_window.fb_id, &g_window.framebuffer, 
                               &g_window.pitch, &g_window.size)) {
        close(g_window.drm_fd);
        return UG_ERROR_PLATFORM_NOT_SUPPORTED;
    }
    
    // Set CRTC to display our framebuffer
    if (drmModeSetCrtc(g_window.drm_fd, g_window.crtc_id, g_window.fb_id, 0, 0,
                      &g_window.connector_id, 1, NULL) < 0) {
        munmap(g_window.framebuffer, g_window.size);
        close(g_window.drm_fd);
        return UG_ERROR_PLATFORM_NOT_SUPPORTED;
    }
    
    g_window.is_open = true;
    return UG_SUCCESS;
#else
    return UG_ERROR_PLATFORM_NOT_SUPPORTED;
#endif
}

/**
 * Get window framebuffer as surface
 */
ug_surface_t* ug_window_get_surface(void) {
    if (!g_window.is_open) {
        return NULL;
    }
    
    ug_surface_t* surface = malloc(sizeof(ug_surface_t));
    if (!surface) {
        return NULL;
    }
    
    surface->pixels = g_window.framebuffer;
    surface->width = g_window.width;
    surface->height = g_window.height;
    surface->stride = g_window.pitch / 4; // Convert bytes to pixels
    surface->size = g_window.size;
    
    return surface;
}

/**
 * Present/flush window contents
 */
void ug_window_present(void) {
    // DRM framebuffer is already displayed, no need to flush
    // Could add page flipping here for double buffering
}

/**
 * Close window
 */
void ug_window_close(void) {
    if (!g_window.is_open) {
        return;
    }
    
#ifdef __linux__
    if (g_window.framebuffer) {
        munmap(g_window.framebuffer, g_window.size);
    }
    
    if (g_window.drm_fd >= 0) {
        close(g_window.drm_fd);
    }
#endif
    
    memset(&g_window, 0, sizeof(g_window));
}

/**
 * Check if window is open
 */
bool ug_window_is_open(void) {
    return g_window.is_open;
}

/**
 * Get window dimensions
 */
void ug_window_get_size(uint32_t *width, uint32_t *height) {
    if (width) *width = g_window.width;
    if (height) *height = g_window.height;
}
