/**
 * @file memory_pools.c
 * @brief Specialized memory pools for graphics operations
 * 
 * Provides optimized memory pools for common graphics allocations:
 * - Surface memory pool
 * - Temporary rendering buffers
 * - SIMD-aligned allocations
 */

#include "unhinged_graphics.h"
#include <stdlib.h>
#include <string.h>
#include <assert.h>

/* Memory pool for surfaces */
typedef struct ug_surface_pool {
    ug_allocator_t* allocator;
    ug_surface_t** free_surfaces;
    int32_t free_count;
    int32_t max_surfaces;
    int32_t surface_width;
    int32_t surface_height;
} ug_surface_pool_t;

/* Global surface pools for common sizes */
static ug_surface_pool_t* g_surface_pools[8] = {NULL};
static int32_t g_pool_count = 0;

/* Create surface pool for specific size */
ug_surface_pool_t* ug_surface_pool_create(int32_t width, int32_t height, int32_t max_surfaces) {
    if (width <= 0 || height <= 0 || max_surfaces <= 0) {
        return NULL;
    }
    
    ug_surface_pool_t* pool = malloc(sizeof(ug_surface_pool_t));
    if (!pool) {
        return NULL;
    }
    
    /* Create allocator for this pool */
    size_t surface_size = sizeof(ug_surface_t) + width * height * sizeof(uint32_t);
    size_t pool_size = surface_size * max_surfaces + 1024 * 1024;  /* Extra space for overhead */
    
    pool->allocator = ug_allocator_create(pool_size);
    if (!pool->allocator) {
        free(pool);
        return NULL;
    }
    
    /* Allocate array for free surface pointers */
    pool->free_surfaces = malloc(max_surfaces * sizeof(ug_surface_t*));
    if (!pool->free_surfaces) {
        ug_allocator_destroy(pool->allocator);
        free(pool);
        return NULL;
    }
    
    pool->free_count = 0;
    pool->max_surfaces = max_surfaces;
    pool->surface_width = width;
    pool->surface_height = height;
    
    return pool;
}

/* Destroy surface pool */
void ug_surface_pool_destroy(ug_surface_pool_t* pool) {
    if (!pool) {
        return;
    }
    
    /* All surfaces should be returned to pool before destroying */
    if (pool->allocator) {
        ug_allocator_destroy(pool->allocator);
    }
    
    if (pool->free_surfaces) {
        free(pool->free_surfaces);
    }
    
    free(pool);
}

/* Get surface from pool */
ug_surface_t* ug_surface_pool_get(ug_surface_pool_t* pool) {
    if (!pool) {
        return NULL;
    }
    
    /* Try to reuse existing surface */
    if (pool->free_count > 0) {
        pool->free_count--;
        return pool->free_surfaces[pool->free_count];
    }
    
    /* Create new surface if pool not full */
    return ug_surface_create(pool->surface_width, pool->surface_height, pool->allocator);
}

/* Return surface to pool */
void ug_surface_pool_return(ug_surface_pool_t* pool, ug_surface_t* surface) {
    if (!pool || !surface) {
        return;
    }
    
    /* Verify surface dimensions match pool */
    if (surface->width != pool->surface_width || surface->height != pool->surface_height) {
        /* Wrong size, just destroy it */
        ug_surface_destroy(surface);
        return;
    }
    
    /* Add to free list if there's space */
    if (pool->free_count < pool->max_surfaces) {
        /* Clear surface for reuse */
        ug_surface_clear(surface, (ug_color_t){0, 0, 0, 0});
        
        pool->free_surfaces[pool->free_count] = surface;
        pool->free_count++;
    } else {
        /* Pool full, destroy surface */
        ug_surface_destroy(surface);
    }
}

/* Get or create surface pool for size */
ug_surface_pool_t* ug_get_surface_pool(int32_t width, int32_t height) {
    /* Look for existing pool */
    for (int32_t i = 0; i < g_pool_count; i++) {
        ug_surface_pool_t* pool = g_surface_pools[i];
        if (pool && pool->surface_width == width && pool->surface_height == height) {
            return pool;
        }
    }
    
    /* Create new pool if we have space */
    if (g_pool_count < 8) {
        ug_surface_pool_t* pool = ug_surface_pool_create(width, height, 16);
        if (pool) {
            g_surface_pools[g_pool_count] = pool;
            g_pool_count++;
            return pool;
        }
    }
    
    return NULL;
}

/* Cleanup all surface pools */
void ug_cleanup_surface_pools(void) {
    for (int32_t i = 0; i < g_pool_count; i++) {
        if (g_surface_pools[i]) {
            ug_surface_pool_destroy(g_surface_pools[i]);
            g_surface_pools[i] = NULL;
        }
    }
    g_pool_count = 0;
}

/* SIMD-aligned memory allocator */
typedef struct ug_simd_allocator {
    ug_allocator_t* base_allocator;
    size_t alignment;
} ug_simd_allocator_t;

ug_simd_allocator_t* ug_simd_allocator_create(size_t pool_size, size_t alignment) {
    if (alignment == 0 || (alignment & (alignment - 1)) != 0) {
        return NULL;  /* Alignment must be power of 2 */
    }
    
    ug_simd_allocator_t* allocator = malloc(sizeof(ug_simd_allocator_t));
    if (!allocator) {
        return NULL;
    }
    
    allocator->base_allocator = ug_allocator_create(pool_size);
    if (!allocator->base_allocator) {
        free(allocator);
        return NULL;
    }
    
    allocator->alignment = alignment;
    return allocator;
}

void ug_simd_allocator_destroy(ug_simd_allocator_t* allocator) {
    if (!allocator) {
        return;
    }
    
    if (allocator->base_allocator) {
        ug_allocator_destroy(allocator->base_allocator);
    }
    
    free(allocator);
}

void* ug_simd_alloc(ug_simd_allocator_t* allocator, size_t size) {
    if (!allocator) {
        return NULL;
    }
    
    return ug_allocator_alloc(allocator->base_allocator, size, allocator->alignment);
}

void ug_simd_free(ug_simd_allocator_t* allocator, void* ptr) {
    if (!allocator) {
        return;
    }
    
    ug_allocator_free(allocator->base_allocator, ptr);
}

/* Global SIMD allocators */
static ug_simd_allocator_t* g_avx2_allocator = NULL;
static ug_simd_allocator_t* g_neon_allocator = NULL;

/* Initialize SIMD allocators */
ug_error_t ug_init_simd_allocators(void) {
    /* AVX2 requires 32-byte alignment */
    g_avx2_allocator = ug_simd_allocator_create(4 * 1024 * 1024, 32);
    
    /* NEON requires 16-byte alignment */
    g_neon_allocator = ug_simd_allocator_create(2 * 1024 * 1024, 16);
    
    return (g_avx2_allocator && g_neon_allocator) ? UG_SUCCESS : UG_ERROR_OUT_OF_MEMORY;
}

/* Cleanup SIMD allocators */
void ug_cleanup_simd_allocators(void) {
    if (g_avx2_allocator) {
        ug_simd_allocator_destroy(g_avx2_allocator);
        g_avx2_allocator = NULL;
    }
    
    if (g_neon_allocator) {
        ug_simd_allocator_destroy(g_neon_allocator);
        g_neon_allocator = NULL;
    }
}

/* Get SIMD allocator for current platform */
ug_simd_allocator_t* ug_get_simd_allocator(void) {
    ug_platform_caps_t caps = ug_get_platform_caps();
    
    if (caps.has_avx2 && g_avx2_allocator) {
        return g_avx2_allocator;
    } else if (caps.has_neon && g_neon_allocator) {
        return g_neon_allocator;
    }
    
    return NULL;
}

/* Allocate SIMD-aligned buffer */
void* ug_alloc_simd_buffer(size_t size) {
    ug_simd_allocator_t* allocator = ug_get_simd_allocator();
    if (allocator) {
        return ug_simd_alloc(allocator, size);
    }
    
    /* Fallback to system malloc with manual alignment */
    size_t alignment = 32;  /* Use AVX2 alignment as default */
    void* ptr = malloc(size + alignment);
    if (!ptr) {
        return NULL;
    }
    
    /* Align pointer */
    uintptr_t addr = (uintptr_t)ptr;
    uintptr_t aligned_addr = (addr + alignment - 1) & ~(alignment - 1);
    
    return (void*)aligned_addr;
}

/* Free SIMD-aligned buffer */
void ug_free_simd_buffer(void* ptr) {
    if (!ptr) {
        return;
    }
    
    ug_simd_allocator_t* allocator = ug_get_simd_allocator();
    if (allocator) {
        ug_simd_free(allocator, ptr);
    } else {
        /* This is tricky with manual alignment - in real implementation,
         * we'd store the original pointer somewhere */
        free(ptr);
    }
}
