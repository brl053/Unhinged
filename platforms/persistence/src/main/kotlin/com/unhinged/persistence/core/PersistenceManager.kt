// ============================================================================
// Persistence Platform - Core Manager Interface
// ============================================================================
//
// @file PersistenceManager.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-10-19
// @description Main interface for the persistence platform that provides
//              unified access to all database technologies
//
// This interface abstracts all database operations behind a single, 
// technology-agnostic API that automatically routes operations to the
// appropriate database technology based on configuration.
//
// ============================================================================

package com.unhinged.persistence.core

import com.unhinged.persistence.config.PersistenceConfiguration
import com.unhinged.persistence.model.*
import kotlinx.coroutines.flow.Flow

/*
 * @llm-type misc.interface
 * @llm-does main persistence platform manager that provides unified
 */
interface PersistenceManager {
    
    /**
     * Initialize the persistence platform with configuration
     */
    suspend fun initialize(config: PersistenceConfiguration)
    
    /**
     * Shutdown the persistence platform gracefully
     */
    suspend fun shutdown()
    
    // ==========================================================================
    // Query Operations
    // ==========================================================================
    
    /**
     * Execute a named query defined in configuration
     * 
     * @param queryName Name of the query from configuration
     * @param parameters Query parameters as key-value pairs
     * @param context Optional execution context for tracing/auth
     * @return Query results as a flow of records
     */
    suspend fun <T> executeQuery(
        queryName: String,
        parameters: Map<String, Any> = emptyMap(),
        context: ExecutionContext? = null
    ): Flow<T>
    
    /**
     * Execute a raw query on a specific table
     * 
     * @param tableName Target table name
     * @param query Query specification
     * @param context Optional execution context
     * @return Query results
     */
    suspend fun <T> executeRawQuery(
        tableName: String,
        query: QuerySpec,
        context: ExecutionContext? = null
    ): Flow<T>
    
    // ==========================================================================
    // CRUD Operations
    // ==========================================================================
    
    /**
     * Insert a record into a table
     * 
     * @param tableName Target table name
     * @param record Record to insert
     * @param context Optional execution context
     * @return Inserted record with generated fields
     */
    suspend fun <T> insert(
        tableName: String,
        record: T,
        context: ExecutionContext? = null
    ): T
    
    /**
     * Insert multiple records in batch
     * 
     * @param tableName Target table name
     * @param records Records to insert
     * @param context Optional execution context
     * @return Inserted records with generated fields
     */
    suspend fun <T> insertBatch(
        tableName: String,
        records: List<T>,
        context: ExecutionContext? = null
    ): List<T>
    
    /**
     * Update a record by primary key
     * 
     * @param tableName Target table name
     * @param id Primary key value
     * @param updates Fields to update
     * @param context Optional execution context
     * @return Updated record or null if not found
     */
    suspend fun <T> update(
        tableName: String,
        id: Any,
        updates: Map<String, Any>,
        context: ExecutionContext? = null
    ): T?
    
    /**
     * Update records matching criteria
     * 
     * @param tableName Target table name
     * @param criteria Update criteria
     * @param updates Fields to update
     * @param context Optional execution context
     * @return Number of updated records
     */
    suspend fun updateWhere(
        tableName: String,
        criteria: QueryCriteria,
        updates: Map<String, Any>,
        context: ExecutionContext? = null
    ): Long
    
    /**
     * Delete a record by primary key
     * 
     * @param tableName Target table name
     * @param id Primary key value
     * @param context Optional execution context
     * @return True if record was deleted
     */
    suspend fun delete(
        tableName: String,
        id: Any,
        context: ExecutionContext? = null
    ): Boolean
    
    /**
     * Delete records matching criteria
     * 
     * @param tableName Target table name
     * @param criteria Delete criteria
     * @param context Optional execution context
     * @return Number of deleted records
     */
    suspend fun deleteWhere(
        tableName: String,
        criteria: QueryCriteria,
        context: ExecutionContext? = null
    ): Long
    
    // ==========================================================================
    // Complex Operations
    // ==========================================================================
    
    /**
     * Execute a named operation defined in configuration
     * 
     * @param operationName Name of the operation from configuration
     * @param parameters Operation parameters
     * @param context Optional execution context
     * @return Operation result
     */
    suspend fun <T> executeOperation(
        operationName: String,
        parameters: Map<String, Any> = emptyMap(),
        context: ExecutionContext? = null
    ): OperationResult<T>
    
    /**
     * Execute a distributed transaction across multiple technologies
     * 
     * @param transactionSpec Transaction specification
     * @param context Optional execution context
     * @return Transaction result
     */
    suspend fun <T> executeTransaction(
        transactionSpec: TransactionSpec,
        context: ExecutionContext? = null
    ): TransactionResult<T>
    
    // ==========================================================================
    // Vector Operations (for AI/ML)
    // ==========================================================================
    
    /**
     * Perform vector similarity search
     * 
     * @param tableName Target table with vector data
     * @param queryVector Query vector
     * @param limit Maximum number of results
     * @param threshold Similarity threshold
     * @param context Optional execution context
     * @return Similar records with similarity scores
     */
    suspend fun <T> vectorSearch(
        tableName: String,
        queryVector: FloatArray,
        limit: Int = 10,
        threshold: Float = 0.7f,
        context: ExecutionContext? = null
    ): List<VectorSearchResult<T>>
    
    /**
     * Perform hybrid search combining vector and text search
     * 
     * @param tableName Target table
     * @param queryVector Query vector
     * @param queryText Query text
     * @param weights Weights for vector vs text search
     * @param limit Maximum number of results
     * @param context Optional execution context
     * @return Hybrid search results
     */
    suspend fun <T> hybridSearch(
        tableName: String,
        queryVector: FloatArray,
        queryText: String,
        weights: SearchWeights = SearchWeights(vector = 0.7f, text = 0.3f),
        limit: Int = 10,
        context: ExecutionContext? = null
    ): List<HybridSearchResult<T>>
    
    // ==========================================================================
    // Graph Operations
    // ==========================================================================
    
    /**
     * Traverse graph relationships
     * 
     * @param tableName Target graph table
     * @param startNodeId Starting node ID
     * @param relationshipType Type of relationship to follow
     * @param maxDepth Maximum traversal depth
     * @param context Optional execution context
     * @return Graph traversal results
     */
    suspend fun <T> graphTraversal(
        tableName: String,
        startNodeId: Any,
        relationshipType: String,
        maxDepth: Int = 3,
        context: ExecutionContext? = null
    ): List<GraphNode<T>>
    
    /**
     * Find shortest path between two nodes
     * 
     * @param tableName Target graph table
     * @param fromNodeId Source node ID
     * @param toNodeId Target node ID
     * @param context Optional execution context
     * @return Shortest path or null if no path exists
     */
    suspend fun <T> shortestPath(
        tableName: String,
        fromNodeId: Any,
        toNodeId: Any,
        context: ExecutionContext? = null
    ): GraphPath<T>?
    
    // ==========================================================================
    // Cache Operations
    // ==========================================================================
    
    /**
     * Get value from cache
     * 
     * @param key Cache key
     * @param context Optional execution context
     * @return Cached value or null if not found
     */
    suspend fun <T> cacheGet(
        key: String,
        context: ExecutionContext? = null
    ): T?
    
    /**
     * Set value in cache
     * 
     * @param key Cache key
     * @param value Value to cache
     * @param ttl Time to live (optional)
     * @param context Optional execution context
     */
    suspend fun cacheSet(
        key: String,
        value: Any,
        ttl: Long? = null,
        context: ExecutionContext? = null
    )
    
    /**
     * Remove value from cache
     * 
     * @param key Cache key
     * @param context Optional execution context
     * @return True if key was removed
     */
    suspend fun cacheRemove(
        key: String,
        context: ExecutionContext? = null
    ): Boolean
    
    // ==========================================================================
    // Health and Monitoring
    // ==========================================================================
    
    /**
     * Get health status of all database technologies
     * 
     * @return Health status for each technology
     */
    suspend fun getHealthStatus(): Map<String, HealthStatus>
    
    /**
     * Get performance metrics
     * 
     * @return Current performance metrics
     */
    suspend fun getMetrics(): PlatformMetrics
    
    /**
     * Get configuration information
     * 
     * @return Current platform configuration
     */
    fun getConfiguration(): PersistenceConfiguration
}
