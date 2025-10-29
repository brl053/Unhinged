// ============================================================================
// Persistence Platform - Core Model Classes
// ============================================================================
//
// @file CoreModels.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-10-19
// @description Core data models and classes used throughout the persistence platform
//
// This file contains the fundamental data structures used by the persistence
// platform interfaces including query specifications, execution contexts,
// results, and configuration models.
//
// ============================================================================

package com.unhinged.persistence.model

import java.time.Instant
import java.util.*

// ==========================================================================
// Execution Context
// ==========================================================================

/*
 * @llm-type model.entity
 * @llm-does execution context that carries request metadata, tracing,
 */
data class ExecutionContext(
    val requestId: String = UUID.randomUUID().toString(),
    val userId: String? = null,
    val sessionId: String? = null,
    val traceId: String? = null,
    val spanId: String? = null,
    val timestamp: Instant = Instant.now(),
    val metadata: Map<String, Any> = emptyMap(),
    val securityContext: SecurityContext? = null,
    val performanceHints: PerformanceHints? = null
)

data class SecurityContext(
    val roles: Set<String> = emptySet(),
    val permissions: Set<String> = emptySet(),
    val tenantId: String? = null,
    val authToken: String? = null
)

data class PerformanceHints(
    val preferredTechnology: String? = null,
    val maxLatency: Long? = null,
    val cachePreference: CachePreference = CachePreference.DEFAULT,
    val consistencyLevel: ConsistencyLevel = ConsistencyLevel.EVENTUAL
)

enum class CachePreference {
    NONE, DEFAULT, AGGRESSIVE, CACHE_ONLY
}

enum class ConsistencyLevel {
    EVENTUAL, STRONG, BOUNDED_STALENESS
}

// ==========================================================================
// Query Models
// ==========================================================================

/**
 * Query specification for database operations
 */
data class QuerySpec(
    val tableName: String,
    val queryType: QueryType,
    val criteria: QueryCriteria? = null,
    val projections: List<String> = emptyList(),
    val orderBy: List<OrderBy> = emptyList(),
    val limit: Int? = null,
    val offset: Int? = null,
    val parameters: Map<String, Any> = emptyMap(),
    val hints: QueryHints? = null
)

/**
 * Query criteria for filtering
 */
sealed class QueryCriteria {
    data class Equals(val field: String, val value: Any) : QueryCriteria()
    data class NotEquals(val field: String, val value: Any) : QueryCriteria()
    data class GreaterThan(val field: String, val value: Any) : QueryCriteria()
    data class LessThan(val field: String, val value: Any) : QueryCriteria()
    data class In(val field: String, val values: List<Any>) : QueryCriteria()
    data class NotIn(val field: String, val values: List<Any>) : QueryCriteria()
    data class Like(val field: String, val pattern: String) : QueryCriteria()
    data class Between(val field: String, val start: Any, val end: Any) : QueryCriteria()
    data class IsNull(val field: String) : QueryCriteria()
    data class IsNotNull(val field: String) : QueryCriteria()
    data class And(val criteria: List<QueryCriteria>) : QueryCriteria()
    data class Or(val criteria: List<QueryCriteria>) : QueryCriteria()
    data class Not(val criteria: QueryCriteria) : QueryCriteria()
    data class FullTextSearch(val fields: List<String>, val query: String) : QueryCriteria()
    data class VectorSimilarity(val field: String, val vector: FloatArray, val threshold: Float) : QueryCriteria()
    data class GeoWithin(val field: String, val geometry: GeoGeometry) : QueryCriteria()
}

data class OrderBy(
    val field: String,
    val direction: SortDirection = SortDirection.ASC
)

enum class SortDirection {
    ASC, DESC
}

data class QueryHints(
    val useIndex: String? = null,
    val forceIndex: Boolean = false,
    val parallelism: Int? = null,
    val timeout: Long? = null
)

// ==========================================================================
// Operation Models
// ==========================================================================

/**
 * Operation specification for complex operations
 */
data class OperationSpec(
    val operationType: OperationType,
    val name: String,
    val steps: List<OperationStep>,
    val rollbackStrategy: RollbackStrategy = RollbackStrategy.COMPENSATING,
    val timeout: Long? = null,
    val retryPolicy: RetryPolicy? = null,
    val metadata: Map<String, Any> = emptyMap()
)

data class OperationStep(
    val stepId: String,
    val stepType: StepType,
    val tableName: String? = null,
    val technology: String? = null,
    val operation: String,
    val parameters: Map<String, Any> = emptyMap(),
    val dependsOn: List<String> = emptyList(),
    val compensatingAction: String? = null
)

enum class StepType {
    DATABASE_OPERATION,
    SERVICE_CALL,
    VALIDATION,
    TRANSFORMATION,
    NOTIFICATION
}

enum class RollbackStrategy {
    NONE,
    COMPENSATING,
    SNAPSHOT_RESTORE,
    CUSTOM
}

data class RetryPolicy(
    val maxAttempts: Int = 3,
    val backoffStrategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL,
    val initialDelay: Long = 1000,
    val maxDelay: Long = 30000,
    val retryableExceptions: Set<String> = emptySet()
)

enum class BackoffStrategy {
    FIXED, LINEAR, EXPONENTIAL, RANDOM
}

// ==========================================================================
// Result Models
// ==========================================================================

/**
 * Operation result with status and data
 */
data class OperationResult<T>(
    val operationId: String,
    val status: OperationStatus,
    val data: T? = null,
    val error: OperationError? = null,
    val executionTime: Long,
    val affectedRecords: Long = 0,
    val metadata: Map<String, Any> = emptyMap()
)

data class OperationError(
    val code: String,
    val message: String,
    val cause: Throwable? = null,
    val retryable: Boolean = false,
    val details: Map<String, Any> = emptyMap()
)

/**
 * Transaction result
 */
data class TransactionResult<T>(
    val transactionId: String,
    val status: TransactionStatus,
    val results: List<T> = emptyList(),
    val error: OperationError? = null,
    val executionTime: Long,
    val participatingTechnologies: Set<String> = emptySet()
)

enum class TransactionStatus {
    COMMITTED, ROLLED_BACK, FAILED, TIMEOUT
}

// ==========================================================================
// Vector and Search Models
// ==========================================================================

/**
 * Vector search result with similarity score
 */
data class VectorSearchResult<T>(
    val data: T,
    val similarity: Float,
    val distance: Float,
    val metadata: Map<String, Any> = emptyMap()
)

/**
 * Hybrid search result combining vector and text search
 */
data class HybridSearchResult<T>(
    val data: T,
    val vectorScore: Float,
    val textScore: Float,
    val combinedScore: Float,
    val metadata: Map<String, Any> = emptyMap()
)

data class SearchWeights(
    val vector: Float = 0.7f,
    val text: Float = 0.3f
) {
    init {
        require(vector + text == 1.0f) { "Search weights must sum to 1.0" }
    }
}

// ==========================================================================
// Graph Models
// ==========================================================================

/**
 * Graph node representation
 */
data class GraphNode<T>(
    val id: Any,
    val labels: Set<String>,
    val properties: T,
    val relationships: List<GraphRelationship> = emptyList()
)

data class GraphRelationship(
    val id: Any,
    val type: String,
    val fromNodeId: Any,
    val toNodeId: Any,
    val properties: Map<String, Any> = emptyMap()
)

data class GraphPath<T>(
    val nodes: List<GraphNode<T>>,
    val relationships: List<GraphRelationship>,
    val totalCost: Double = 0.0,
    val length: Int = relationships.size
)

// ==========================================================================
// Health and Monitoring Models
// ==========================================================================

/**
 * Health status for database technologies
 */
data class HealthStatus(
    val status: HealthState,
    val message: String? = null,
    val lastChecked: Instant = Instant.now(),
    val responseTime: Long? = null,
    val details: Map<String, Any> = emptyMap()
)

enum class HealthState {
    HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN
}

/**
 * Connection status information
 */
data class ConnectionStatus(
    val connected: Boolean,
    val connectionCount: Int = 0,
    val maxConnections: Int = 0,
    val lastConnected: Instant? = null,
    val connectionDetails: Map<String, Any> = emptyMap()
)

// ==========================================================================
// Configuration Models
// ==========================================================================

/**
 * Time range for queries and analytics
 */
data class TimeRange(
    val start: Instant,
    val end: Instant
) {
    init {
        require(start.isBefore(end)) { "Start time must be before end time" }
    }
}

/**
 * Geospatial geometry for location queries
 */
sealed class GeoGeometry {
    data class Point(val latitude: Double, val longitude: Double) : GeoGeometry()
    data class Circle(val center: Point, val radius: Double) : GeoGeometry()
    data class Polygon(val points: List<Point>) : GeoGeometry()
    data class BoundingBox(val southwest: Point, val northeast: Point) : GeoGeometry()
}

// ==========================================================================
// Metrics and Performance Models
// ==========================================================================

/**
 * Platform-wide performance metrics
 */
data class PlatformMetrics(
    val timestamp: Instant = Instant.now(),
    val queryMetrics: QueryMetrics,
    val operationMetrics: OperationMetrics,
    val technologyMetrics: Map<String, TechnologyMetrics>,
    val cacheMetrics: CacheMetrics,
    val resourceMetrics: ResourceMetrics
)

data class QueryMetrics(
    val totalQueries: Long,
    val queriesPerSecond: Double,
    val averageLatency: Double,
    val p50Latency: Double,
    val p95Latency: Double,
    val p99Latency: Double,
    val errorRate: Double,
    val slowQueries: Long
)

data class OperationMetrics(
    val totalOperations: Long,
    val operationsPerSecond: Double,
    val averageLatency: Double,
    val successRate: Double,
    val failureRate: Double,
    val activeOperations: Int,
    val queuedOperations: Int
)

data class TechnologyMetrics(
    val technology: String,
    val connectionCount: Int,
    val activeConnections: Int,
    val queryCount: Long,
    val errorCount: Long,
    val averageResponseTime: Double,
    val throughput: Double,
    val resourceUtilization: ResourceUtilization
)

data class CacheMetrics(
    val hitRate: Double,
    val missRate: Double,
    val evictionRate: Double,
    val totalHits: Long,
    val totalMisses: Long,
    val cacheSize: Long,
    val maxCacheSize: Long
)

data class ResourceMetrics(
    val cpuUsage: Double,
    val memoryUsage: Double,
    val diskUsage: Double,
    val networkIO: NetworkIO,
    val diskIO: DiskIO
)

data class ResourceUtilization(
    val cpu: Double,
    val memory: Double,
    val disk: Double,
    val network: Double
)

data class NetworkIO(
    val bytesIn: Long,
    val bytesOut: Long,
    val packetsIn: Long,
    val packetsOut: Long
)

data class DiskIO(
    val bytesRead: Long,
    val bytesWritten: Long,
    val readsPerSecond: Double,
    val writesPerSecond: Double
)

// ==========================================================================
// Transaction and Handle Models
// ==========================================================================

/**
 * Transaction handle for managing distributed transactions
 */
data class TransactionHandle(
    val transactionId: String,
    val participatingProviders: Set<String>,
    val isolationLevel: IsolationLevel,
    val timeout: Long,
    val startTime: Instant = Instant.now()
)

/**
 * Distributed transaction handle
 */
data class DistributedTransactionHandle(
    val transactionId: String,
    val coordinatorId: String,
    val participants: Map<String, TransactionHandle>,
    val status: TransactionStatus,
    val startTime: Instant = Instant.now()
)

/**
 * Async pipeline handle for monitoring
 */
data class AsyncPipelineHandle(
    val pipelineId: String,
    val pipelineName: String,
    val stages: List<PipelineStage>,
    val startTime: Instant = Instant.now()
)

data class PipelineStage(
    val stageId: String,
    val stageName: String,
    val status: StageStatus,
    val startTime: Instant? = null,
    val endTime: Instant? = null,
    val error: String? = null
)

enum class StageStatus {
    PENDING, RUNNING, COMPLETED, FAILED, SKIPPED
}

/**
 * Pipeline status information
 */
data class PipelineStatus(
    val pipelineId: String,
    val overallStatus: StageStatus,
    val currentStage: String?,
    val completedStages: Int,
    val totalStages: Int,
    val progress: Double,
    val estimatedTimeRemaining: Long?
)
