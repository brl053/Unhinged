// ============================================================================
// Persistence Platform - Query Executor Interface
// ============================================================================
//
// @file QueryExecutor.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-10-19
// @description Interface for executing queries with optimization, caching,
//              and routing across multiple database technologies
//
// The QueryExecutor handles query planning, optimization, caching, and
// execution across different database technologies. It provides intelligent
// routing based on query characteristics and data access patterns.
//
// ============================================================================

package com.unhinged.persistence.core

import com.unhinged.persistence.model.*
import kotlinx.coroutines.flow.Flow

/*
 * @llm-type misc.interface
 * @llm-does query executor that handles query planning, optimization,
 * @llm-rule all queries must be processed through this executor for consistency and optim...
 */
interface QueryExecutor {
    
    // ==========================================================================
    // Query Planning and Execution
    // ==========================================================================
    
    /**
     * Execute a named query with automatic optimization
     * 
     * @param queryName Name of the query from configuration
     * @param parameters Query parameters
     * @param context Execution context
     * @return Query results as a flow
     */
    suspend fun <T> executeNamedQuery(
        queryName: String,
        parameters: Map<String, Any>,
        context: ExecutionContext
    ): Flow<T>
    
    /**
     * Execute a raw query with automatic routing
     * 
     * @param querySpec Query specification
     * @param context Execution context
     * @return Query results as a flow
     */
    suspend fun <T> executeQuery(
        querySpec: QuerySpec,
        context: ExecutionContext
    ): Flow<T>
    
    /**
     * Execute a query and return a single result
     * 
     * @param querySpec Query specification
     * @param context Execution context
     * @return Single result or null
     */
    suspend fun <T> executeQuerySingle(
        querySpec: QuerySpec,
        context: ExecutionContext
    ): T?
    
    /**
     * Execute a query and return count of results
     * 
     * @param querySpec Query specification
     * @param context Execution context
     * @return Number of matching records
     */
    suspend fun executeQueryCount(
        querySpec: QuerySpec,
        context: ExecutionContext
    ): Long
    
    // ==========================================================================
    // Query Planning and Optimization
    // ==========================================================================
    
    /**
     * Create an execution plan for a query
     * 
     * @param querySpec Query specification
     * @param context Execution context
     * @return Query execution plan
     */
    suspend fun createExecutionPlan(
        querySpec: QuerySpec,
        context: ExecutionContext
    ): QueryExecutionPlan
    
    /**
     * Optimize a query for better performance
     * 
     * @param querySpec Original query specification
     * @param context Execution context
     * @return Optimized query specification
     */
    suspend fun optimizeQuery(
        querySpec: QuerySpec,
        context: ExecutionContext
    ): QuerySpec
    
    /**
     * Analyze query performance and suggest improvements
     * 
     * @param queryName Query name to analyze
     * @param timeRange Time range for analysis
     * @return Performance analysis and recommendations
     */
    suspend fun analyzeQueryPerformance(
        queryName: String,
        timeRange: TimeRange
    ): QueryPerformanceAnalysis
    
    // ==========================================================================
    // Caching Operations
    // ==========================================================================
    
    /**
     * Execute query with caching strategy
     * 
     * @param querySpec Query specification
     * @param cacheStrategy Caching strategy to use
     * @param context Execution context
     * @return Cached or fresh query results
     */
    suspend fun <T> executeWithCache(
        querySpec: QuerySpec,
        cacheStrategy: CacheStrategy,
        context: ExecutionContext
    ): Flow<T>
    
    /**
     * Invalidate cache for specific query patterns
     * 
     * @param pattern Cache invalidation pattern
     * @param context Execution context
     */
    suspend fun invalidateCache(
        pattern: CacheInvalidationPattern,
        context: ExecutionContext
    )
    
    /**
     * Get cache statistics for query patterns
     * 
     * @param pattern Optional pattern to filter statistics
     * @return Cache performance statistics
     */
    suspend fun getCacheStatistics(
        pattern: String? = null
    ): CacheStatistics
    
    // ==========================================================================
    // Cross-Technology Queries
    // ==========================================================================
    
    /**
     * Execute a query that spans multiple database technologies
     * 
     * @param crossTechQuery Cross-technology query specification
     * @param context Execution context
     * @return Combined results from multiple technologies
     */
    suspend fun <T> executeCrossTechnologyQuery(
        crossTechQuery: CrossTechnologyQuery,
        context: ExecutionContext
    ): Flow<T>
    
    /**
     * Execute a hybrid search combining multiple search technologies
     * 
     * @param hybridQuery Hybrid search specification
     * @param context Execution context
     * @return Ranked and merged search results
     */
    suspend fun <T> executeHybridSearch(
        hybridQuery: HybridSearchQuery,
        context: ExecutionContext
    ): List<HybridSearchResult<T>>
    
    // ==========================================================================
    // Query Routing
    // ==========================================================================
    
    /**
     * Determine the best database technology for a query
     * 
     * @param querySpec Query specification
     * @param context Execution context
     * @return Recommended database technology and reasoning
     */
    suspend fun routeQuery(
        querySpec: QuerySpec,
        context: ExecutionContext
    ): QueryRoutingDecision
    
    /**
     * Get routing statistics and patterns
     * 
     * @param timeRange Time range for statistics
     * @return Query routing analytics
     */
    suspend fun getRoutingStatistics(
        timeRange: TimeRange
    ): QueryRoutingStatistics
    
    // ==========================================================================
    // Batch Operations
    // ==========================================================================
    
    /**
     * Execute multiple queries in batch with optimization
     * 
     * @param queries List of query specifications
     * @param context Execution context
     * @return Batch execution results
     */
    suspend fun executeBatch(
        queries: List<QuerySpec>,
        context: ExecutionContext
    ): List<BatchQueryResult>
    
    /**
     * Execute queries in parallel across multiple technologies
     * 
     * @param parallelQueries Parallel query specifications
     * @param context Execution context
     * @return Combined parallel execution results
     */
    suspend fun <T> executeParallel(
        parallelQueries: List<QuerySpec>,
        context: ExecutionContext
    ): List<Flow<T>>
    
    // ==========================================================================
    // Query Monitoring and Analytics
    // ==========================================================================
    
    /**
     * Get real-time query execution metrics
     * 
     * @return Current query execution metrics
     */
    suspend fun getExecutionMetrics(): QueryExecutionMetrics
    
    /**
     * Get query execution history and patterns
     * 
     * @param timeRange Time range for history
     * @param filters Optional filters for query patterns
     * @return Query execution history
     */
    suspend fun getExecutionHistory(
        timeRange: TimeRange,
        filters: QueryFilters? = null
    ): List<QueryExecutionRecord>
    
    /**
     * Get slow query analysis
     * 
     * @param threshold Minimum execution time threshold
     * @param timeRange Time range for analysis
     * @return Slow query analysis results
     */
    suspend fun getSlowQueryAnalysis(
        threshold: Long,
        timeRange: TimeRange
    ): SlowQueryAnalysis
    
    // ==========================================================================
    // Configuration and Management
    // ==========================================================================
    
    /**
     * Update query execution configuration
     * 
     * @param config New execution configuration
     */
    suspend fun updateConfiguration(config: QueryExecutorConfig)
    
    /**
     * Get current configuration
     * 
     * @return Current query executor configuration
     */
    fun getConfiguration(): QueryExecutorConfig
    
    /**
     * Validate a query specification
     * 
     * @param querySpec Query to validate
     * @return Validation result with any errors or warnings
     */
    suspend fun validateQuery(querySpec: QuerySpec): QueryValidationResult
    
    /**
     * Get supported query capabilities
     * 
     * @return Set of supported query capabilities
     */
    fun getSupportedCapabilities(): Set<QueryCapability>
}

/**
 * Enum defining query capabilities
 */
enum class QueryCapability {
    CACHING,
    CROSS_TECHNOLOGY,
    HYBRID_SEARCH,
    BATCH_EXECUTION,
    PARALLEL_EXECUTION,
    QUERY_OPTIMIZATION,
    PERFORMANCE_ANALYSIS,
    AUTOMATIC_ROUTING,
    REAL_TIME_METRICS,
    SLOW_QUERY_DETECTION
}

/**
 * Cache strategy enumeration
 */
enum class CacheStrategy {
    NONE,           // No caching
    READ_THROUGH,   // Cache on read
    WRITE_THROUGH,  // Cache on write
    WRITE_BEHIND,   // Async cache write
    REFRESH_AHEAD   // Proactive cache refresh
}

/**
 * Query execution plan
 */
data class QueryExecutionPlan(
    val queryId: String,
    val targetTechnology: String,
    val estimatedCost: Long,
    val estimatedLatency: Long,
    val cacheStrategy: CacheStrategy,
    val optimizations: List<QueryOptimization>,
    val reasoning: String
)

/**
 * Query optimization information
 */
data class QueryOptimization(
    val type: OptimizationType,
    val description: String,
    val estimatedImprovement: Float
)

/**
 * Optimization types
 */
enum class OptimizationType {
    INDEX_USAGE,
    QUERY_REWRITE,
    TECHNOLOGY_ROUTING,
    CACHING,
    BATCHING,
    PARALLELIZATION
}
