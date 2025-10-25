/**
 * @file platform.c
 * @brief Platform detection and capability discovery
 * 
 * Detects platform capabilities including:
 * - CPU SIMD support (AVX2, NEON)
 * - GPU vendor identification
 * - DRM capabilities
 * - Wayland support
 * - Platform-specific optimizations
 */

#include "unhinged_graphics.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#ifdef __linux__
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#endif

#ifdef _WIN32
#include <windows.h>
#include <intrin.h>
#endif

#ifdef __APPLE__
#include <sys/sysctl.h>
#endif

/* Global platform capabilities */
static ug_platform_caps_t g_platform_caps = {0};
static bool g_caps_initialized = false;

/* CPU feature detection */
static bool detect_avx2_support(void) {
#ifdef __x86_64__
    #ifdef _WIN32
        int cpu_info[4];
        __cpuid(cpu_info, 1);
        
        /* Check for AVX support */
        bool has_avx = (cpu_info[2] & (1 << 28)) != 0;
        if (!has_avx) return false;
        
        /* Check for AVX2 support */
        __cpuidex(cpu_info, 7, 0);
        return (cpu_info[1] & (1 << 5)) != 0;
    #else
        /* Use GCC/Clang builtin */
        #ifdef __AVX2__
            return true;
        #else
            /* Runtime detection via /proc/cpuinfo on Linux */
            #ifdef __linux__
                FILE* cpuinfo = fopen("/proc/cpuinfo", "r");
                if (!cpuinfo) return false;
                
                char line[256];
                bool has_avx2 = false;
                
                while (fgets(line, sizeof(line), cpuinfo)) {
                    if (strstr(line, "flags") && strstr(line, "avx2")) {
                        has_avx2 = true;
                        break;
                    }
                }
                
                fclose(cpuinfo);
                return has_avx2;
            #else
                return false;
            #endif
        #endif
    #endif
#else
    return false;
#endif
}

static bool detect_neon_support(void) {
#ifdef __aarch64__
    /* AArch64 always has NEON */
    return true;
#elif defined(__arm__)
    #ifdef __ARM_NEON
        return true;
    #else
        /* Runtime detection via /proc/cpuinfo on Linux */
        #ifdef __linux__
            FILE* cpuinfo = fopen("/proc/cpuinfo", "r");
            if (!cpuinfo) return false;
            
            char line[256];
            bool has_neon = false;
            
            while (fgets(line, sizeof(line), cpuinfo)) {
                if (strstr(line, "Features") && strstr(line, "neon")) {
                    has_neon = true;
                    break;
                }
            }
            
            fclose(cpuinfo);
            return has_neon;
        #else
            return false;
        #endif
    #endif
#else
    return false;
#endif
}

/* GPU vendor detection */
static const char* detect_gpu_vendor(void) {
#ifdef __linux__
    /* Try to read GPU info from DRM */
    const char* drm_paths[] = {
        "/sys/class/drm/card0/device/vendor",
        "/sys/class/drm/card1/device/vendor",
        NULL
    };
    
    for (int i = 0; drm_paths[i]; i++) {
        FILE* vendor_file = fopen(drm_paths[i], "r");
        if (vendor_file) {
            char vendor_id[16];
            if (fgets(vendor_id, sizeof(vendor_id), vendor_file)) {
                fclose(vendor_file);
                
                /* Convert hex vendor ID to vendor name */
                unsigned int id = strtoul(vendor_id, NULL, 16);
                switch (id) {
                    case 0x8086: return "Intel";
                    case 0x10de: return "NVIDIA";
                    case 0x1002: return "AMD";
                    case 0x1414: return "Microsoft";
                    default: return "Unknown";
                }
            }
            fclose(vendor_file);
        }
    }
    
    /* Fallback: try lspci if available */
    FILE* lspci = popen("lspci | grep -i vga", "r");
    if (lspci) {
        char line[256];
        if (fgets(line, sizeof(line), lspci)) {
            pclose(lspci);
            
            if (strstr(line, "Intel")) return "Intel";
            if (strstr(line, "NVIDIA")) return "NVIDIA";
            if (strstr(line, "AMD") || strstr(line, "ATI")) return "AMD";
        }
        pclose(lspci);
    }
#endif

#ifdef _WIN32
    /* Use Windows API to detect GPU */
    /* This would require additional Windows-specific code */
    return "Unknown";
#endif

#ifdef __APPLE__
    /* Use macOS system profiler */
    return "Apple";
#endif

    return "Unknown";
}

/* DRM capability detection */
static bool detect_drm_support(void) {
#ifdef __linux__
    /* Check if DRM devices exist */
    struct stat st;
    return (stat("/dev/dri/card0", &st) == 0) || (stat("/dev/dri/card1", &st) == 0);
#else
    return false;
#endif
}

/* Wayland support detection */
static bool detect_wayland_support(void) {
#ifdef __linux__
    /* Check if Wayland is running */
    const char* wayland_display = getenv("WAYLAND_DISPLAY");
    if (wayland_display && strlen(wayland_display) > 0) {
        return true;
    }
    
    /* Check if Wayland libraries are available */
    struct stat st;
    return stat("/usr/lib/x86_64-linux-gnu/libwayland-client.so", &st) == 0 ||
           stat("/usr/lib/libwayland-client.so", &st) == 0;
#else
    return false;
#endif
}

/* Platform name detection */
static const char* detect_platform_name(void) {
#ifdef __linux__
    return "Linux";
#elif defined(_WIN32)
    return "Windows";
#elif defined(__APPLE__)
    #ifdef TARGET_OS_MAC
        return "macOS";
    #else
        return "iOS";
    #endif
#elif defined(__FreeBSD__)
    return "FreeBSD";
#elif defined(__OpenBSD__)
    return "OpenBSD";
#elif defined(__NetBSD__)
    return "NetBSD";
#else
    return "Unknown";
#endif
}

/* Initialize platform capabilities */
static void initialize_platform_caps(void) {
    if (g_caps_initialized) {
        return;
    }
    
    /* Detect CPU features */
    g_platform_caps.has_avx2 = detect_avx2_support();
    g_platform_caps.has_neon = detect_neon_support();
    
    /* Detect GPU and platform features */
    g_platform_caps.gpu_vendor = detect_gpu_vendor();
    g_platform_caps.has_drm = detect_drm_support();
    g_platform_caps.has_wayland = detect_wayland_support();
    g_platform_caps.platform_name = detect_platform_name();
    
    g_caps_initialized = true;
}

/* Public API */
ug_platform_caps_t ug_get_platform_caps(void) {
    if (!g_caps_initialized) {
        initialize_platform_caps();
    }
    return g_platform_caps;
}

/* Platform-specific optimization hints */
bool ug_platform_should_use_simd(void) {
    ug_platform_caps_t caps = ug_get_platform_caps();
    return caps.has_avx2 || caps.has_neon;
}

bool ug_platform_should_use_gpu(void) {
    ug_platform_caps_t caps = ug_get_platform_caps();
    return caps.has_drm && (strcmp(caps.gpu_vendor, "Unknown") != 0);
}

size_t ug_platform_get_cache_line_size(void) {
#ifdef __linux__
    long cache_line_size = sysconf(_SC_LEVEL1_DCACHE_LINESIZE);
    if (cache_line_size > 0) {
        return (size_t)cache_line_size;
    }
#endif
    
    /* Default cache line size for most modern CPUs */
    return 64;
}

size_t ug_platform_get_page_size(void) {
#ifdef __linux__
    long page_size = sysconf(_SC_PAGESIZE);
    if (page_size > 0) {
        return (size_t)page_size;
    }
#endif

#ifdef _WIN32
    SYSTEM_INFO si;
    GetSystemInfo(&si);
    return si.dwPageSize;
#endif
    
    /* Default page size */
    return 4096;
}
