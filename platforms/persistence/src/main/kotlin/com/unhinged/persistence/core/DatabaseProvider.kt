// ============================================================================
// Persistence Platform - Database Provider Interface
// ============================================================================
//
// @file DatabaseProvider.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-10-19
// @description Interface that each database technology must implement
//              to integrate with the persistence platform
//
// This interface defines the contract that all database providers must
// implement to enable unified access through the persistence platform.
// Each technology (Redis, CockroachDB, MongoDB, etc.) will have its own
// implementation of this interface.
//
// ============================================================================

package com.unhinged.persistence.core

import com.unhinged.persistence.config.TechnologyConfiguration
import com.unhinged.persistence.model.*
import kotlinx.coroutines.flow.Flow

/*
 * @llm-type misc.interface
 * @llm-does database provider interface that each technology implements
 */
interface DatabaseProvider {
    
    /**
     * Get the technology type this provider supports
     */
    val technologyType: TechnologyType
    
    /**
     * Get the provider name/identifier
     */
    val providerName: String
    
    /**
     * Initialize the provider with configuration
     * 
     * @param config Technology-specific configuration
     */
    suspend fun initialize(config: TechnologyConfiguration)
    
    /**
     * Shutdown the provider gracefully
     */
    suspend fun shutdown()
    
    // ==========================================================================
    // Connection Management
    // ==========================================================================
    
    /**
     * Test connection to the database
     * 
     * @return True if connection is healthy
     */
    suspend fun testConnection(): Boolean
    
    /**
     * Get current connection status
     * 
     * @return Connection health information
     */
    suspend fun getConnectionStatus(): ConnectionStatus
    
    // ==========================================================================
    // Schema Management
    // ==========================================================================
    
    /**
     * Create a database/keyspace/collection space
     * 
     * @param databaseName Database name
     * @param config Database configuration
     */
    suspend fun createDatabase(
        databaseName: String,
        config: DatabaseConfig
    )
    
    /**
     * Create a table/collection/index
     * 
     * @param tableName Table name
     * @param schema Table schema definition
     * @param config Table configuration
     */
    suspend fun createTable(
        tableName: String,
        schema: TableSchema,
        config: TableConfig
    )
    
    /**
     * Drop a table/collection/index
     * 
     * @param tableName Table name
     */
    suspend fun dropTable(tableName: String)
    
    /**
     * Check if table exists
     * 
     * @param tableName Table name
     * @return True if table exists
     */
    suspend fun tableExists(tableName: String): Boolean
    
    // ==========================================================================
    // Query Operations
    // ==========================================================================
    
    /**
     * Execute a query and return results as a flow
     * 
     * @param query Query specification
     * @param context Execution context
     * @return Query results
     */
    suspend fun <T> executeQuery(
        query: QuerySpec,
        context: ExecutionContext
    ): Flow<T>
    
    /**
     * Execute a query and return a single result
     * 
     * @param query Query specification
     * @param context Execution context
     * @return Single result or null
     */
    suspend fun <T> executeQuerySingle(
        query: QuerySpec,
        context: ExecutionContext
    ): T?
    
    /**
     * Execute a query and return count of results
     * 
     * @param query Query specification
     * @param context Execution context
     * @return Number of matching records
     */
    suspend fun executeQueryCount(
        query: QuerySpec,
        context: ExecutionContext
    ): Long
    
    // ==========================================================================
    // CRUD Operations
    // ==========================================================================
    
    /**
     * Insert a single record
     * 
     * @param tableName Target table
     * @param record Record to insert
     * @param context Execution context
     * @return Inserted record with generated fields
     */
    suspend fun <T> insert(
        tableName: String,
        record: T,
        context: ExecutionContext
    ): T
    
    /**
     * Insert multiple records in batch
     * 
     * @param tableName Target table
     * @param records Records to insert
     * @param context Execution context
     * @return Inserted records with generated fields
     */
    suspend fun <T> insertBatch(
        tableName: String,
        records: List<T>,
        context: ExecutionContext
    ): List<T>
    
    /**
     * Update records matching criteria
     * 
     * @param tableName Target table
     * @param criteria Update criteria
     * @param updates Fields to update
     * @param context Execution context
     * @return Number of updated records
     */
    suspend fun update(
        tableName: String,
        criteria: QueryCriteria,
        updates: Map<String, Any>,
        context: ExecutionContext
    ): Long
    
    /**
     * Delete records matching criteria
     * 
     * @param tableName Target table
     * @param criteria Delete criteria
     * @param context Execution context
     * @return Number of deleted records
     */
    suspend fun delete(
        tableName: String,
        criteria: QueryCriteria,
        context: ExecutionContext
    ): Long
    
    // ==========================================================================
    // Transaction Support
    // ==========================================================================
    
    /**
     * Check if provider supports transactions
     * 
     * @return True if transactions are supported
     */
    fun supportsTransactions(): Boolean
    
    /**
     * Begin a transaction
     * 
     * @param context Execution context
     * @return Transaction handle
     */
    suspend fun beginTransaction(context: ExecutionContext): TransactionHandle?
    
    /**
     * Commit a transaction
     * 
     * @param transaction Transaction handle
     */
    suspend fun commitTransaction(transaction: TransactionHandle)
    
    /**
     * Rollback a transaction
     * 
     * @param transaction Transaction handle
     */
    suspend fun rollbackTransaction(transaction: TransactionHandle)
    
    // ==========================================================================
    // Technology-Specific Operations
    // ==========================================================================
    
    /**
     * Execute technology-specific operation
     * 
     * @param operation Operation specification
     * @param context Execution context
     * @return Operation result
     */
    suspend fun <T> executeSpecificOperation(
        operation: SpecificOperation,
        context: ExecutionContext
    ): T?
    
    // ==========================================================================
    // Performance and Monitoring
    // ==========================================================================
    
    /**
     * Get provider-specific metrics
     * 
     * @return Current metrics for this provider
     */
    suspend fun getMetrics(): ProviderMetrics
    
    /**
     * Get health status
     * 
     * @return Current health status
     */
    suspend fun getHealthStatus(): HealthStatus
    
    /**
     * Get configuration information
     * 
     * @return Current provider configuration
     */
    fun getConfiguration(): TechnologyConfiguration
    
    // ==========================================================================
    // Capability Information
    // ==========================================================================
    
    /**
     * Get supported query types for this provider
     * 
     * @return Set of supported query types
     */
    fun getSupportedQueryTypes(): Set<QueryType>
    
    /**
     * Get supported data types for this provider
     * 
     * @return Set of supported data types
     */
    fun getSupportedDataTypes(): Set<DataType>
    
    /**
     * Check if provider supports specific feature
     * 
     * @param feature Feature to check
     * @return True if feature is supported
     */
    fun supportsFeature(feature: DatabaseFeature): Boolean
}

/**
 * Enum defining different database technology types
 */
enum class TechnologyType {
    CACHE,              // Redis
    NEWSQL,             // CockroachDB
    NOSQL_DOCUMENT,     // MongoDB
    VECTOR_DATABASE,    // Weaviate
    SEARCH_ANALYTICS,   // Elasticsearch
    WIDE_COLUMN,        // Cassandra
    GRAPH,              // Neo4j
    OLAP_WAREHOUSE      // Data Lake
}

/**
 * Enum defining database features
 */
enum class DatabaseFeature {
    TRANSACTIONS,
    VECTOR_SEARCH,
    FULL_TEXT_SEARCH,
    GRAPH_TRAVERSAL,
    TIME_SERIES,
    GEOSPATIAL,
    JSON_QUERIES,
    AGGREGATIONS,
    STREAMING,
    REPLICATION,
    SHARDING,
    ENCRYPTION,
    COMPRESSION,
    BACKUP_RESTORE
}

/**
 * Enum defining query types
 */
enum class QueryType {
    POINT_LOOKUP,
    RANGE_SCAN,
    FULL_TEXT_SEARCH,
    VECTOR_SIMILARITY,
    GRAPH_TRAVERSAL,
    AGGREGATION,
    TIME_SERIES,
    GEOSPATIAL,
    DOCUMENT_QUERY
}

/**
 * Enum defining data types
 */
enum class DataType {
    STRING,
    INTEGER,
    LONG,
    FLOAT,
    DOUBLE,
    BOOLEAN,
    DATE,
    TIMESTAMP,
    UUID,
    JSON,
    JSONB,
    VECTOR,
    BINARY,
    TEXT,
    ARRAY,
    MAP
}
