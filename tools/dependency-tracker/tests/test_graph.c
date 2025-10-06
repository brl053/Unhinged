/**
 * @file test_graph.c
 * @brief Graph operations tests
 */

#include "dependency_tracker.h"

void test_graph_creation(void) {
    DependencyGraph* graph = graph_create();
    TEST_ASSERT_NOT_NULL(graph, "Graph creation should succeed");
    
    if (graph) {
        TEST_ASSERT_EQ(0, graph->node_count, "New graph should have no nodes");
        TEST_ASSERT_EQ(0, graph->edge_count, "New graph should have no edges");
        TEST_ASSERT_NOT_NULL(graph->nodes, "Nodes array should be allocated");
        TEST_ASSERT_NOT_NULL(graph->edges, "Edges array should be allocated");
        
        graph_destroy(graph);
    }
}

void test_node_operations(void) {
    DependencyGraph* graph = graph_create();
    TEST_ASSERT_NOT_NULL(graph, "Graph creation should succeed");
    
    if (graph) {
        GraphNode node = {
            .id = "test-node",
            .name = "Test Node",
            .type = NODE_SERVICE,
            .filepath = "/test/path",
            .dependencies = NULL,
            .dep_count = 0,
            .metadata = NULL
        };
        
        int result = graph_add_node(graph, &node);
        TEST_ASSERT_EQ(DEPTRACK_SUCCESS, result, "Adding node should succeed");
        TEST_ASSERT_EQ(1, graph->node_count, "Graph should have one node");
        
        GraphNode* found = graph_find_node(graph, "test-node");
        TEST_ASSERT_NOT_NULL(found, "Should find added node");
        
        if (found) {
            TEST_ASSERT_STR_EQ("test-node", found->id, "Node ID should match");
            TEST_ASSERT_STR_EQ("Test Node", found->name, "Node name should match");
            TEST_ASSERT_EQ(NODE_SERVICE, found->type, "Node type should match");
        }
        
        graph_destroy(graph);
    }
}

void test_edge_operations(void) {
    DependencyGraph* graph = graph_create();
    TEST_ASSERT_NOT_NULL(graph, "Graph creation should succeed");
    
    if (graph) {
        // Add two nodes first
        GraphNode node1 = {.id = "node1", .name = "Node 1", .type = NODE_SERVICE};
        GraphNode node2 = {.id = "node2", .name = "Node 2", .type = NODE_LIBRARY};
        
        graph_add_node(graph, &node1);
        graph_add_node(graph, &node2);
        
        // Add edge between them
        GraphEdge edge = {
            .from_id = "node1",
            .to_id = "node2",
            .type = DEP_INTERNAL,
            .version_constraint = ">=1.0.0",
            .metadata = NULL
        };
        
        int result = graph_add_edge(graph, &edge);
        TEST_ASSERT_EQ(DEPTRACK_SUCCESS, result, "Adding edge should succeed");
        TEST_ASSERT_EQ(1, graph->edge_count, "Graph should have one edge");
        
        graph_destroy(graph);
    }
}

void run_graph_tests(void) {
    test_run("graph_creation", test_graph_creation);
    test_run("node_operations", test_node_operations);
    test_run("edge_operations", test_edge_operations);
}
