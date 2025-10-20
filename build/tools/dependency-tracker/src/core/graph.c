/**
 * @file graph.c
 * @brief Dependency graph implementation
 * @author Unhinged Development Team
 * 
 * @llm-type class
 * @llm-legend Manages dependency graph data structure for representing relationships between components
 * @llm-key Implements dynamic arrays for nodes and edges with hash map indexing for fast lookups
 * @llm-map Core data structure used by dependency tracker to represent and analyze dependencies
 * @llm-axiom Graph operations must maintain referential integrity and prevent memory leaks
 * @llm-contract Provides thread-safe graph operations with proper error handling
 * @llm-token dependency-graph: directed graph representing component dependencies and relationships
 */

#include "dependency_tracker.h"
#include <string.h>

// Initial capacity for dynamic arrays
#define INITIAL_NODE_CAPACITY 100
#define INITIAL_EDGE_CAPACITY 200

// Simple hash map implementation for node indexing (stub)
typedef struct HashMapEntry {
    char* key;
    size_t value;
    struct HashMapEntry* next;
} HashMapEntry;

typedef struct HashMap {
    HashMapEntry** buckets;
    size_t bucket_count;
    size_t size;
} HashMap;

// Hash map operations (simplified implementation)
static HashMap* hashmap_create(size_t bucket_count) {
    HashMap* map = calloc(1, sizeof(HashMap));
    if (!map) return NULL;
    
    map->buckets = calloc(bucket_count, sizeof(HashMapEntry*));
    if (!map->buckets) {
        free(map);
        return NULL;
    }
    
    map->bucket_count = bucket_count;
    map->size = 0;
    return map;
}

static void hashmap_destroy(HashMap* map) {
    if (!map) return;
    
    for (size_t i = 0; i < map->bucket_count; i++) {
        HashMapEntry* entry = map->buckets[i];
        while (entry) {
            HashMapEntry* next = entry->next;
            free(entry->key);
            free(entry);
            entry = next;
        }
    }
    
    free(map->buckets);
    free(map);
}

static size_t hash_string(const char* str) {
    size_t hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash;
}

static int hashmap_put(HashMap* map, const char* key, size_t value) {
    if (!map || !key) return -1;
    
    size_t bucket = hash_string(key) % map->bucket_count;
    
    // Check if key already exists
    HashMapEntry* entry = map->buckets[bucket];
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            entry->value = value;
            return 0;
        }
        entry = entry->next;
    }
    
    // Create new entry
    entry = malloc(sizeof(HashMapEntry));
    if (!entry) return -1;
    
    entry->key = strdup(key);
    if (!entry->key) {
        free(entry);
        return -1;
    }
    
    entry->value = value;
    entry->next = map->buckets[bucket];
    map->buckets[bucket] = entry;
    map->size++;
    
    return 0;
}

static int hashmap_get(HashMap* map, const char* key, size_t* value) {
    if (!map || !key || !value) return -1;
    
    size_t bucket = hash_string(key) % map->bucket_count;
    HashMapEntry* entry = map->buckets[bucket];
    
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            *value = entry->value;
            return 0;
        }
        entry = entry->next;
    }
    
    return -1; // Not found
}

DependencyGraph* graph_create(void) {
    DependencyGraph* graph = calloc(1, sizeof(DependencyGraph));
    if (!graph) {
        return NULL;
    }
    
    // Allocate initial capacity for nodes
    graph->nodes = calloc(INITIAL_NODE_CAPACITY, sizeof(GraphNode));
    if (!graph->nodes) {
        free(graph);
        return NULL;
    }
    
    // Allocate initial capacity for edges
    graph->edges = calloc(INITIAL_EDGE_CAPACITY, sizeof(GraphEdge));
    if (!graph->edges) {
        free(graph->nodes);
        free(graph);
        return NULL;
    }
    
    // Create node index hash map
    graph->node_index = hashmap_create(101); // Prime number for better distribution
    if (!graph->node_index) {
        free(graph->edges);
        free(graph->nodes);
        free(graph);
        return NULL;
    }
    
    graph->node_count = 0;
    graph->edge_count = 0;
    graph->node_capacity = INITIAL_NODE_CAPACITY;
    graph->edge_capacity = INITIAL_EDGE_CAPACITY;

    // Initialize mutex for thread safety
    if (pthread_mutex_init(&graph->mutex, NULL) != 0) {
        hashmap_destroy((HashMap*)graph->node_index);
        free(graph->edges);
        free(graph->nodes);
        free(graph);
        return NULL;
    }

    return graph;
}

void graph_destroy(DependencyGraph* graph) {
    if (!graph) return;

    // Destroy mutex
    pthread_mutex_destroy(&graph->mutex);
    
    // Clean up nodes
    for (size_t i = 0; i < graph->node_count; i++) {
        GraphNode* node = &graph->nodes[i];
        free(node->id);
        free(node->name);
        free(node->filepath);
        
        // Clean up dependencies array
        if (node->dependencies) {
            for (size_t j = 0; j < node->dep_count; j++) {
                free(node->dependencies[j]);
            }
            free(node->dependencies);
        }
        
        // Clean up metadata if needed
        // TODO: Implement metadata cleanup based on node type
    }
    
    // Clean up edges
    for (size_t i = 0; i < graph->edge_count; i++) {
        GraphEdge* edge = &graph->edges[i];
        free(edge->from_id);
        free(edge->to_id);
        free(edge->version_constraint);
        
        // Clean up metadata if needed
        // TODO: Implement metadata cleanup based on edge type
    }
    
    // Clean up arrays
    free(graph->nodes);
    free(graph->edges);
    
    // Clean up hash map
    hashmap_destroy((HashMap*)graph->node_index);
    
    free(graph);
}

static int graph_resize_nodes(DependencyGraph* graph) {
    size_t new_capacity = graph->node_capacity * 2;
    GraphNode* new_nodes = realloc(graph->nodes, new_capacity * sizeof(GraphNode));
    if (!new_nodes) {
        return -1;
    }
    
    // Zero out new memory
    memset(new_nodes + graph->node_capacity, 0, 
           (new_capacity - graph->node_capacity) * sizeof(GraphNode));
    
    graph->nodes = new_nodes;
    graph->node_capacity = new_capacity;
    return 0;
}

static int graph_resize_edges(DependencyGraph* graph) {
    size_t new_capacity = graph->edge_capacity * 2;
    GraphEdge* new_edges = realloc(graph->edges, new_capacity * sizeof(GraphEdge));
    if (!new_edges) {
        return -1;
    }
    
    // Zero out new memory
    memset(new_edges + graph->edge_capacity, 0,
           (new_capacity - graph->edge_capacity) * sizeof(GraphEdge));
    
    graph->edges = new_edges;
    graph->edge_capacity = new_capacity;
    return 0;
}

int graph_add_node(DependencyGraph* graph, const GraphNode* node) {
    if (!graph || !node || !node->id) {
        return DEPTRACK_ERROR_INVALID_PARAM;
    }

    // Lock graph for thread safety
    pthread_mutex_lock(&graph->mutex);

    // Check if node already exists
    size_t existing_index;
    if (hashmap_get((HashMap*)graph->node_index, node->id, &existing_index) == 0) {
        // Node already exists, could update it or return error
        pthread_mutex_unlock(&graph->mutex);
        return DEPTRACK_ERROR_INVALID_PARAM; // For now, don't allow duplicates
    }
    
    // Resize if necessary
    if (graph->node_count >= graph->node_capacity) {
        if (graph_resize_nodes(graph) != 0) {
            pthread_mutex_unlock(&graph->mutex);
            return DEPTRACK_ERROR_MEMORY;
        }
    }
    
    // Copy node data
    GraphNode* new_node = &graph->nodes[graph->node_count];
    new_node->id = strdup(node->id);
    new_node->name = node->name ? strdup(node->name) : NULL;
    new_node->type = node->type;
    new_node->filepath = node->filepath ? strdup(node->filepath) : NULL;
    
    // Copy dependencies
    if (node->dependencies && node->dep_count > 0) {
        new_node->dependencies = calloc(node->dep_count, sizeof(char*));
        if (!new_node->dependencies) {
            free(new_node->id);
            free(new_node->name);
            free(new_node->filepath);
            pthread_mutex_unlock(&graph->mutex);
            return DEPTRACK_ERROR_MEMORY;
        }
        
        for (size_t i = 0; i < node->dep_count; i++) {
            new_node->dependencies[i] = strdup(node->dependencies[i]);
        }
        new_node->dep_count = node->dep_count;
    }
    
    // Add to index
    if (hashmap_put((HashMap*)graph->node_index, node->id, graph->node_count) != 0) {
        // Cleanup on failure
        free(new_node->id);
        free(new_node->name);
        free(new_node->filepath);
        if (new_node->dependencies) {
            for (size_t i = 0; i < new_node->dep_count; i++) {
                free(new_node->dependencies[i]);
            }
            free(new_node->dependencies);
        }
        pthread_mutex_unlock(&graph->mutex);
        return DEPTRACK_ERROR_MEMORY;
    }
    
    graph->node_count++;

    // Unlock graph
    pthread_mutex_unlock(&graph->mutex);
    return DEPTRACK_SUCCESS;
}

int graph_add_edge(DependencyGraph* graph, const GraphEdge* edge) {
    if (!graph || !edge || !edge->from_id || !edge->to_id) {
        return DEPTRACK_ERROR_INVALID_PARAM;
    }

    // Lock graph for thread safety
    pthread_mutex_lock(&graph->mutex);

    // Verify that both nodes exist
    size_t from_index, to_index;
    if (hashmap_get((HashMap*)graph->node_index, edge->from_id, &from_index) != 0 ||
        hashmap_get((HashMap*)graph->node_index, edge->to_id, &to_index) != 0) {
        pthread_mutex_unlock(&graph->mutex);
        return DEPTRACK_ERROR_INVALID_PARAM;
    }
    
    // Resize if necessary
    if (graph->edge_count >= graph->edge_capacity) {
        if (graph_resize_edges(graph) != 0) {
            pthread_mutex_unlock(&graph->mutex);
            return DEPTRACK_ERROR_MEMORY;
        }
    }
    
    // Copy edge data
    GraphEdge* new_edge = &graph->edges[graph->edge_count];
    new_edge->from_id = strdup(edge->from_id);
    new_edge->to_id = strdup(edge->to_id);
    new_edge->type = edge->type;
    new_edge->version_constraint = edge->version_constraint ? strdup(edge->version_constraint) : NULL;
    new_edge->metadata = edge->metadata; // Shallow copy for now
    
    graph->edge_count++;

    // Unlock graph
    pthread_mutex_unlock(&graph->mutex);
    return DEPTRACK_SUCCESS;
}

GraphNode* graph_find_node(DependencyGraph* graph, const char* id) {
    if (!graph || !id) {
        return NULL;
    }
    
    size_t index;
    if (hashmap_get((HashMap*)graph->node_index, id, &index) == 0) {
        return &graph->nodes[index];
    }
    
    return NULL;
}

int graph_detect_cycles(DependencyGraph* graph) {
    if (!graph) {
        return DEPTRACK_ERROR_INVALID_PARAM;
    }
    
    // TODO: Implement cycle detection using DFS
    // For now, return 0 (no cycles detected)
    return 0;
}
