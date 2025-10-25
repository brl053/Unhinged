/**
 * @file memory.c
 * @brief Custom memory allocators optimized for graphics rendering
 * 
 * Provides high-performance memory allocation with:
 * - Memory pools for reduced fragmentation
 * - Aligned allocation for SIMD operations
 * - Fast allocation/deallocation for rendering
 * - Memory usage tracking and debugging
 */

#include "unhinged_graphics.h"
#include <stdlib.h>
#include <string.h>
#include <assert.h>

/* Memory block header for tracking allocations */
typedef struct ug_memory_block {
    size_t size;
    size_t alignment;
    struct ug_memory_block* next;
    struct ug_memory_block* prev;
    bool is_free;
    uint32_t magic;  /* For corruption detection */
} ug_memory_block_t;

#define UG_MEMORY_MAGIC 0xDEADBEEF
#define UG_MIN_ALIGNMENT 16
#define UG_BLOCK_HEADER_SIZE sizeof(ug_memory_block_t)

/* Memory allocator structure */
struct ug_allocator {
    void* pool_start;
    void* pool_end;
    size_t pool_size;
    size_t bytes_allocated;
    size_t bytes_free;
    ug_memory_block_t* free_list;
    ug_memory_block_t* used_list;
    bool initialized;
};

/* Utility functions */
static inline size_t align_size(size_t size, size_t alignment) {
    return (size + alignment - 1) & ~(alignment - 1);
}

static inline void* align_pointer(void* ptr, size_t alignment) {
    uintptr_t addr = (uintptr_t)ptr;
    return (void*)((addr + alignment - 1) & ~(alignment - 1));
}

static void insert_free_block(ug_allocator_t* allocator, ug_memory_block_t* block) {
    assert(allocator && block);
    
    block->is_free = true;
    block->next = allocator->free_list;
    block->prev = NULL;
    
    if (allocator->free_list) {
        allocator->free_list->prev = block;
    }
    allocator->free_list = block;
}

static void remove_from_free_list(ug_allocator_t* allocator, ug_memory_block_t* block) {
    assert(allocator && block);
    
    if (block->prev) {
        block->prev->next = block->next;
    } else {
        allocator->free_list = block->next;
    }
    
    if (block->next) {
        block->next->prev = block->prev;
    }
    
    block->next = block->prev = NULL;
}

static void insert_used_block(ug_allocator_t* allocator, ug_memory_block_t* block) {
    assert(allocator && block);
    
    block->is_free = false;
    block->next = allocator->used_list;
    block->prev = NULL;
    
    if (allocator->used_list) {
        allocator->used_list->prev = block;
    }
    allocator->used_list = block;
}

static void remove_from_used_list(ug_allocator_t* allocator, ug_memory_block_t* block) {
    assert(allocator && block);
    
    if (block->prev) {
        block->prev->next = block->next;
    } else {
        allocator->used_list = block->next;
    }
    
    if (block->next) {
        block->next->prev = block->prev;
    }
    
    block->next = block->prev = NULL;
}

ug_allocator_t* ug_allocator_create(size_t pool_size) {
    if (pool_size < 1024) {  /* Minimum 1KB */
        return NULL;
    }
    
    /* Allocate allocator structure */
    ug_allocator_t* allocator = malloc(sizeof(ug_allocator_t));
    if (!allocator) {
        return NULL;
    }
    
    /* Allocate memory pool with extra space for alignment */
    size_t actual_pool_size = pool_size + UG_MIN_ALIGNMENT;
    void* raw_pool = malloc(actual_pool_size);
    if (!raw_pool) {
        free(allocator);
        return NULL;
    }
    
    /* Initialize allocator */
    allocator->pool_start = align_pointer(raw_pool, UG_MIN_ALIGNMENT);
    allocator->pool_size = pool_size;
    allocator->pool_end = (char*)allocator->pool_start + pool_size;
    allocator->bytes_allocated = 0;
    allocator->bytes_free = pool_size;
    allocator->free_list = NULL;
    allocator->used_list = NULL;
    allocator->initialized = true;
    
    /* Create initial free block covering entire pool */
    ug_memory_block_t* initial_block = (ug_memory_block_t*)allocator->pool_start;
    initial_block->size = pool_size - UG_BLOCK_HEADER_SIZE;
    initial_block->alignment = UG_MIN_ALIGNMENT;
    initial_block->magic = UG_MEMORY_MAGIC;
    initial_block->next = NULL;
    initial_block->prev = NULL;
    
    insert_free_block(allocator, initial_block);
    
    return allocator;
}

void ug_allocator_destroy(ug_allocator_t* allocator) {
    if (!allocator || !allocator->initialized) {
        return;
    }
    
    /* Free the raw pool (we need to calculate the original pointer) */
    void* raw_pool = (char*)allocator->pool_start - UG_MIN_ALIGNMENT;
    free(raw_pool);
    
    /* Clear allocator structure */
    memset(allocator, 0, sizeof(ug_allocator_t));
    free(allocator);
}

void* ug_allocator_alloc(ug_allocator_t* allocator, size_t size, size_t alignment) {
    if (!allocator || !allocator->initialized || size == 0) {
        return NULL;
    }
    
    /* Ensure minimum alignment */
    if (alignment < UG_MIN_ALIGNMENT) {
        alignment = UG_MIN_ALIGNMENT;
    }
    
    /* Must be power of 2 */
    if ((alignment & (alignment - 1)) != 0) {
        return NULL;
    }
    
    /* Calculate total size needed including alignment padding */
    size_t aligned_size = align_size(size, alignment);
    size_t total_size = UG_BLOCK_HEADER_SIZE + aligned_size + alignment;
    
    /* Find suitable free block */
    ug_memory_block_t* block = allocator->free_list;
    while (block) {
        if (block->magic != UG_MEMORY_MAGIC) {
            /* Memory corruption detected */
            return NULL;
        }
        
        if (block->size >= total_size) {
            break;
        }
        block = block->next;
    }
    
    if (!block) {
        /* No suitable block found */
        return NULL;
    }
    
    /* Remove from free list */
    remove_from_free_list(allocator, block);
    
    /* Calculate aligned user pointer */
    void* user_ptr = align_pointer((char*)block + UG_BLOCK_HEADER_SIZE, alignment);
    
    /* Split block if there's enough space left */
    size_t used_size = (char*)user_ptr - (char*)block + aligned_size;
    if (block->size > used_size + UG_BLOCK_HEADER_SIZE + UG_MIN_ALIGNMENT) {
        /* Create new free block from remainder */
        ug_memory_block_t* new_block = (ug_memory_block_t*)((char*)block + used_size);
        new_block->size = block->size - used_size;
        new_block->alignment = UG_MIN_ALIGNMENT;
        new_block->magic = UG_MEMORY_MAGIC;
        new_block->next = NULL;
        new_block->prev = NULL;
        
        insert_free_block(allocator, new_block);
        
        /* Update current block size */
        block->size = used_size - UG_BLOCK_HEADER_SIZE;
    }
    
    /* Update block info */
    block->alignment = alignment;
    
    /* Add to used list */
    insert_used_block(allocator, block);
    
    /* Update allocator stats */
    allocator->bytes_allocated += block->size;
    allocator->bytes_free -= block->size;
    
    return user_ptr;
}

void ug_allocator_free(ug_allocator_t* allocator, void* ptr) {
    if (!allocator || !allocator->initialized || !ptr) {
        return;
    }
    
    /* Find the block header */
    ug_memory_block_t* block = allocator->used_list;
    while (block) {
        if (block->magic != UG_MEMORY_MAGIC) {
            /* Memory corruption detected */
            return;
        }
        
        void* user_ptr = align_pointer((char*)block + UG_BLOCK_HEADER_SIZE, block->alignment);
        if (user_ptr == ptr) {
            break;
        }
        block = block->next;
    }
    
    if (!block) {
        /* Block not found in used list */
        return;
    }
    
    /* Remove from used list */
    remove_from_used_list(allocator, block);
    
    /* Update allocator stats */
    allocator->bytes_allocated -= block->size;
    allocator->bytes_free += block->size;
    
    /* Add to free list */
    insert_free_block(allocator, block);
    
    /* TODO: Implement block coalescing for better memory utilization */
}
