/**
 * @file linux_drm.c
 * @brief Linux DRM (Direct Rendering Manager) integration
 * 
 * Provides direct GPU access through DRM for high-performance rendering
 * without going through X11 or Wayland compositors.
 */

#ifdef __linux__
#ifdef ENABLE_DRM

#include "unhinged_graphics.h"
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <errno.h>
#include <string.h>

/* DRM device structure */
typedef struct {
    int fd;
    char device_path[256];
    bool is_master;
    uint32_t driver_version_major;
    uint32_t driver_version_minor;
    char driver_name[64];
} ug_drm_device_t;

static ug_drm_device_t g_drm_device = {-1};

/* Initialize DRM device */
ug_error_t ug_drm_init(void) {
    /* Try common DRM device paths */
    const char* drm_paths[] = {
        "/dev/dri/card0",
        "/dev/dri/card1",
        "/dev/dri/renderD128",
        "/dev/dri/renderD129",
        NULL
    };
    
    for (int i = 0; drm_paths[i]; i++) {
        int fd = open(drm_paths[i], O_RDWR | O_CLOEXEC);
        if (fd >= 0) {
            g_drm_device.fd = fd;
            strncpy(g_drm_device.device_path, drm_paths[i], sizeof(g_drm_device.device_path) - 1);
            g_drm_device.device_path[sizeof(g_drm_device.device_path) - 1] = '\0';
            
            /* Try to become DRM master (may fail if X11/Wayland is running) */
            g_drm_device.is_master = (ioctl(fd, DRM_IOCTL_SET_MASTER, 0) == 0);
            
            return UG_SUCCESS;
        }
    }
    
    return UG_ERROR_PLATFORM_NOT_SUPPORTED;
}

/* Cleanup DRM device */
void ug_drm_cleanup(void) {
    if (g_drm_device.fd >= 0) {
        if (g_drm_device.is_master) {
            ioctl(g_drm_device.fd, DRM_IOCTL_DROP_MASTER, 0);
        }
        close(g_drm_device.fd);
        g_drm_device.fd = -1;
    }
}

/* Get DRM device info */
bool ug_drm_is_available(void) {
    return g_drm_device.fd >= 0;
}

const char* ug_drm_get_device_path(void) {
    return g_drm_device.fd >= 0 ? g_drm_device.device_path : NULL;
}

bool ug_drm_is_master(void) {
    return g_drm_device.is_master;
}

/* DRM buffer management */
typedef struct {
    uint32_t handle;
    uint32_t pitch;
    uint64_t size;
    void* map;
} ug_drm_buffer_t;

/* Create DRM framebuffer */
ug_error_t ug_drm_create_framebuffer(int32_t width, int32_t height, ug_drm_buffer_t* buffer) {
    if (!ug_drm_is_available() || !buffer) {
        return UG_ERROR_PLATFORM_NOT_SUPPORTED;
    }
    
    /* Calculate buffer parameters */
    uint32_t bpp = 32;  /* 32 bits per pixel (RGBA) */
    uint32_t pitch = width * (bpp / 8);
    uint64_t size = pitch * height;
    
    /* Create dumb buffer */
    struct drm_mode_create_dumb create_req = {0};
    create_req.width = width;
    create_req.height = height;
    create_req.bpp = bpp;
    
    if (ioctl(g_drm_device.fd, DRM_IOCTL_MODE_CREATE_DUMB, &create_req) < 0) {
        return UG_ERROR_PLATFORM_NOT_SUPPORTED;
    }
    
    /* Map the buffer */
    struct drm_mode_map_dumb map_req = {0};
    map_req.handle = create_req.handle;
    
    if (ioctl(g_drm_device.fd, DRM_IOCTL_MODE_MAP_DUMB, &map_req) < 0) {
        /* Cleanup on failure */
        struct drm_mode_destroy_dumb destroy_req = {0};
        destroy_req.handle = create_req.handle;
        ioctl(g_drm_device.fd, DRM_IOCTL_MODE_DESTROY_DUMB, &destroy_req);
        return UG_ERROR_PLATFORM_NOT_SUPPORTED;
    }
    
    /* Memory map the buffer */
    void* map = mmap(0, create_req.size, PROT_READ | PROT_WRITE, MAP_SHARED,
                     g_drm_device.fd, map_req.offset);
    
    if (map == MAP_FAILED) {
        /* Cleanup on failure */
        struct drm_mode_destroy_dumb destroy_req = {0};
        destroy_req.handle = create_req.handle;
        ioctl(g_drm_device.fd, DRM_IOCTL_MODE_DESTROY_DUMB, &destroy_req);
        return UG_ERROR_OUT_OF_MEMORY;
    }
    
    /* Fill buffer structure */
    buffer->handle = create_req.handle;
    buffer->pitch = create_req.pitch;
    buffer->size = create_req.size;
    buffer->map = map;
    
    return UG_SUCCESS;
}

/* Destroy DRM framebuffer */
void ug_drm_destroy_framebuffer(ug_drm_buffer_t* buffer) {
    if (!buffer || !ug_drm_is_available()) {
        return;
    }
    
    if (buffer->map) {
        munmap(buffer->map, buffer->size);
        buffer->map = NULL;
    }
    
    if (buffer->handle) {
        struct drm_mode_destroy_dumb destroy_req = {0};
        destroy_req.handle = buffer->handle;
        ioctl(g_drm_device.fd, DRM_IOCTL_MODE_DESTROY_DUMB, &destroy_req);
        buffer->handle = 0;
    }
}

/* Get display mode information */
typedef struct {
    uint32_t width;
    uint32_t height;
    uint32_t refresh_rate;
    char name[32];
} ug_display_mode_t;

ug_error_t ug_drm_get_display_modes(ug_display_mode_t* modes, int32_t* count) {
    if (!ug_drm_is_available() || !modes || !count) {
        return UG_ERROR_INVALID_PARAM;
    }
    
    /* Get DRM resources */
    drmModeRes* resources = drmModeGetResources(g_drm_device.fd);
    if (!resources) {
        return UG_ERROR_PLATFORM_NOT_SUPPORTED;
    }
    
    int32_t mode_count = 0;
    int32_t max_modes = *count;
    
    /* Iterate through connectors */
    for (int i = 0; i < resources->count_connectors && mode_count < max_modes; i++) {
        drmModeConnector* connector = drmModeGetConnector(g_drm_device.fd, resources->connectors[i]);
        if (!connector) continue;
        
        if (connector->connection == DRM_MODE_CONNECTED) {
            /* Add modes from this connector */
            for (int j = 0; j < connector->count_modes && mode_count < max_modes; j++) {
                drmModeModeInfo* mode = &connector->modes[j];
                
                modes[mode_count].width = mode->hdisplay;
                modes[mode_count].height = mode->vdisplay;
                modes[mode_count].refresh_rate = mode->vrefresh;
                strncpy(modes[mode_count].name, mode->name, sizeof(modes[mode_count].name) - 1);
                modes[mode_count].name[sizeof(modes[mode_count].name) - 1] = '\0';
                
                mode_count++;
            }
        }
        
        drmModeFreeConnector(connector);
    }
    
    drmModeFreeResources(resources);
    *count = mode_count;
    
    return UG_SUCCESS;
}

/* Check if we can use DRM for direct rendering */
bool ug_drm_can_direct_render(void) {
    return ug_drm_is_available() && g_drm_device.is_master;
}

/* Get GPU memory info */
ug_error_t ug_drm_get_gpu_memory_info(uint64_t* total_memory, uint64_t* available_memory) {
    if (!ug_drm_is_available() || !total_memory || !available_memory) {
        return UG_ERROR_INVALID_PARAM;
    }
    
    /* This is a simplified implementation */
    /* Real implementation would query GPU-specific memory information */
    *total_memory = 0;
    *available_memory = 0;
    
    /* Try to read from sysfs */
    FILE* mem_file = fopen("/sys/class/drm/card0/device/mem_info_vram_total", "r");
    if (mem_file) {
        fscanf(mem_file, "%lu", total_memory);
        fclose(mem_file);
    }
    
    mem_file = fopen("/sys/class/drm/card0/device/mem_info_vram_used", "r");
    if (mem_file) {
        uint64_t used_memory;
        fscanf(mem_file, "%lu", &used_memory);
        *available_memory = *total_memory - used_memory;
        fclose(mem_file);
    }
    
    return UG_SUCCESS;
}

#endif /* ENABLE_DRM */
#endif /* __linux__ */
