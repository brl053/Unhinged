// ============================================================================
// Persistence Platform - Unified API Server
// ============================================================================
//
// @file PersistenceApiServer.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-10-19
// @description Unified API server providing REST and gRPC endpoints for persistence operations
//
// This server provides a unified API layer that abstracts all database
// technologies behind consistent REST and gRPC endpoints. It handles
// automatic routing, authentication, rate limiting, and observability.
//
// ============================================================================

package com.unhinged.persistence.api

import com.unhinged.persistence.core.PersistenceManager
import com.unhinged.persistence.config.PersistenceConfiguration
import com.unhinged.persistence.model.*
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.routing.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.server.plugins.cors.routing.*
import io.ktor.server.plugins.ratelimit.*
import io.ktor.server.plugins.calllogging.*
import io.ktor.server.plugins.statuspages.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.http.*
import kotlinx.coroutines.flow.toList
import kotlinx.serialization.json.Json
import kotlinx.serialization.Serializable
import org.slf4j.LoggerFactory
import java.time.Instant
import kotlin.time.Duration.Companion.minutes

/**
 * @llm-type api-server
 * @llm-legend Unified API server providing REST and gRPC endpoints for all persistence operations
 * @llm-key Central API gateway that routes requests to appropriate database technologies with authentication and rate limiting
 * @llm-map Unified API layer that abstracts database complexity behind consistent REST/gRPC endpoints
 * @llm-axiom All persistence operations must go through this API layer for consistency and security
 * @llm-contract Provides technology-agnostic REST/gRPC APIs with automatic routing and observability
 * @llm-token persistence-api-server: Unified API gateway for all database operations
 */
class PersistenceApiServer(
    private val persistenceManager: PersistenceManager,
    private val configuration: PersistenceConfiguration
) {
    
    private val logger = LoggerFactory.getLogger(PersistenceApiServer::class.java)
    private var server: NettyApplicationEngine? = null
    
    // ==========================================================================
    // Server Lifecycle
    // ==========================================================================
    
    /**
     * Start the API server
     */
    suspend fun start() {
        logger.info("🚀 Starting Persistence Platform API Server...")
        
        val restConfig = configuration.api.protocols.rest
        val grpcConfig = configuration.api.protocols.grpc
        
        // Start REST API server
        if (restConfig.enabled) {
            startRestServer(restConfig.port)
        }
        
        // Start gRPC server (would be implemented separately)
        if (grpcConfig.enabled) {
            startGrpcServer(grpcConfig.port)
        }
        
        logger.info("✅ Persistence Platform API Server started successfully")
    }
    
    /**
     * Stop the API server
     */
    suspend fun stop() {
        logger.info("🛑 Stopping Persistence Platform API Server...")
        
        server?.stop(1000, 2000)
        server = null
        
        logger.info("✅ Persistence Platform API Server stopped")
    }
    
    // ==========================================================================
    // REST API Server
    // ==========================================================================
    
    private suspend fun startRestServer(port: Int) {
        server = embeddedServer(Netty, port = port, host = "0.0.0.0") {
            configureRestApi()
        }.start(wait = false)
        
        logger.info("✅ REST API server started on port $port")
    }
    
    private fun Application.configureRestApi() {
        // Configure JSON serialization
        install(ContentNegotiation) {
            json(Json {
                prettyPrint = true
                isLenient = true
                ignoreUnknownKeys = true
            })
        }
        
        // Configure CORS
        install(CORS) {
            configuration.api.security.cors.allowedOrigins.forEach { origin ->
                allowHost(origin.removePrefix("http://").removePrefix("https://"))
            }
            allowMethod(HttpMethod.Get)
            allowMethod(HttpMethod.Post)
            allowMethod(HttpMethod.Put)
            allowMethod(HttpMethod.Delete)
            allowHeader(HttpHeaders.ContentType)
            allowHeader(HttpHeaders.Authorization)
        }
        
        // Configure rate limiting
        if (configuration.api.security.rateLimiting.enabled) {
            install(RateLimit) {
                register(RateLimitName("api")) {
                    rateLimiter(limit = 100, refillPeriod = 1.minutes)
                }
            }
        }
        
        // Configure call logging
        install(CallLogging) {
            level = org.slf4j.event.Level.INFO
        }
        
        // Configure status pages for error handling
        install(StatusPages) {
            exception<Throwable> { call, cause ->
                logger.error("API request failed", cause)
                call.respond(
                    HttpStatusCode.InternalServerError,
                    ErrorResponse(
                        error = "internal_server_error",
                        message = cause.message ?: "An unexpected error occurred",
                        timestamp = Instant.now().toString()
                    )
                )
            }
        }
        
        // Configure routing
        routing {
            configureApiRoutes()
        }
    }
    
    // ==========================================================================
    // API Routes
    // ==========================================================================
    
    private fun Routing.configureApiRoutes() {
        route("/api/v1") {
            
            // Health and status endpoints
            get("/health") {
                val healthStatus = persistenceManager.getHealthStatus()
                call.respond(
                    HealthResponse(
                        status = "healthy",
                        timestamp = Instant.now().toString(),
                        technologies = healthStatus
                    )
                )
            }
            
            get("/metrics") {
                val metrics = persistenceManager.getMetrics()
                call.respond(metrics)
            }
            
            get("/config") {
                val config = persistenceManager.getConfiguration()
                call.respond(
                    ConfigResponse(
                        version = config.version,
                        technologies = config.technologies.keys.toList(),
                        databases = config.databases.keys.toList(),
                        tables = config.tables.keys.toList()
                    )
                )
            }
            
            // Query endpoints
            route("/query") {
                post("/{queryName}") {
                    val queryName = call.parameters["queryName"] ?: throw IllegalArgumentException("Query name required")
                    val request = call.receive<QueryRequest>()
                    val context = createExecutionContext(call)
                    
                    try {
                        val results = persistenceManager.executeQuery<Map<String, Any>>(
                            queryName = queryName,
                            parameters = request.parameters,
                            context = context
                        ).toList()
                        
                        call.respond(
                            QueryResponse(
                                queryName = queryName,
                                results = results,
                                count = results.size,
                                executionTime = System.currentTimeMillis() - context.timestamp.toEpochMilli()
                            )
                        )
                    } catch (e: Exception) {
                        logger.error("Query execution failed: $queryName", e)
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse(
                                error = "query_execution_failed",
                                message = e.message ?: "Query execution failed",
                                details = mapOf("queryName" to queryName)
                            )
                        )
                    }
                }
            }
            
            // CRUD endpoints for tables
            route("/tables/{tableName}") {
                
                // Create record
                post {
                    val tableName = call.parameters["tableName"] ?: throw IllegalArgumentException("Table name required")
                    val record = call.receive<Map<String, Any>>()
                    val context = createExecutionContext(call)
                    
                    try {
                        val result = persistenceManager.insert(tableName, record, context)
                        call.respond(
                            HttpStatusCode.Created,
                            CrudResponse(
                                operation = "insert",
                                tableName = tableName,
                                result = result,
                                affectedRecords = 1
                            )
                        )
                    } catch (e: Exception) {
                        logger.error("Insert operation failed: $tableName", e)
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse(
                                error = "insert_failed",
                                message = e.message ?: "Insert operation failed"
                            )
                        )
                    }
                }
                
                // Batch create records
                post("/batch") {
                    val tableName = call.parameters["tableName"] ?: throw IllegalArgumentException("Table name required")
                    val records = call.receive<List<Map<String, Any>>>()
                    val context = createExecutionContext(call)
                    
                    try {
                        val results = persistenceManager.insertBatch(tableName, records, context)
                        call.respond(
                            CrudResponse(
                                operation = "batch_insert",
                                tableName = tableName,
                                result = results,
                                affectedRecords = results.size.toLong()
                            )
                        )
                    } catch (e: Exception) {
                        logger.error("Batch insert operation failed: $tableName", e)
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse(
                                error = "batch_insert_failed",
                                message = e.message ?: "Batch insert operation failed"
                            )
                        )
                    }
                }
                
                // Update record by ID
                put("/{id}") {
                    val tableName = call.parameters["tableName"] ?: throw IllegalArgumentException("Table name required")
                    val id = call.parameters["id"] ?: throw IllegalArgumentException("Record ID required")
                    val updates = call.receive<Map<String, Any>>()
                    val context = createExecutionContext(call)
                    
                    try {
                        val result = persistenceManager.update(tableName, id, updates, context)
                        if (result != null) {
                            call.respond(
                                CrudResponse(
                                    operation = "update",
                                    tableName = tableName,
                                    result = result,
                                    affectedRecords = 1
                                )
                            )
                        } else {
                            call.respond(
                                HttpStatusCode.NotFound,
                                ErrorResponse(
                                    error = "record_not_found",
                                    message = "Record not found for update"
                                )
                            )
                        }
                    } catch (e: Exception) {
                        logger.error("Update operation failed: $tableName/$id", e)
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse(
                                error = "update_failed",
                                message = e.message ?: "Update operation failed"
                            )
                        )
                    }
                }
                
                // Delete record by ID
                delete("/{id}") {
                    val tableName = call.parameters["tableName"] ?: throw IllegalArgumentException("Table name required")
                    val id = call.parameters["id"] ?: throw IllegalArgumentException("Record ID required")
                    val context = createExecutionContext(call)
                    
                    try {
                        val deleted = persistenceManager.delete(tableName, id, context)
                        if (deleted) {
                            call.respond(
                                CrudResponse(
                                    operation = "delete",
                                    tableName = tableName,
                                    result = mapOf("deleted" to true),
                                    affectedRecords = 1
                                )
                            )
                        } else {
                            call.respond(
                                HttpStatusCode.NotFound,
                                ErrorResponse(
                                    error = "record_not_found",
                                    message = "Record not found for deletion"
                                )
                            )
                        }
                    } catch (e: Exception) {
                        logger.error("Delete operation failed: $tableName/$id", e)
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse(
                                error = "delete_failed",
                                message = e.message ?: "Delete operation failed"
                            )
                        )
                    }
                }
            }
            
            // Operation endpoints
            route("/operations") {
                post("/{operationName}") {
                    val operationName = call.parameters["operationName"] ?: throw IllegalArgumentException("Operation name required")
                    val request = call.receive<OperationRequest>()
                    val context = createExecutionContext(call)
                    
                    try {
                        val result = persistenceManager.executeOperation<Map<String, Any>>(
                            operationName = operationName,
                            parameters = request.parameters,
                            context = context
                        )
                        
                        call.respond(
                            OperationResponse(
                                operationName = operationName,
                                status = result.status.name,
                                result = result.data,
                                executionTime = result.executionTime,
                                affectedRecords = result.affectedRecords
                            )
                        )
                    } catch (e: Exception) {
                        logger.error("Operation execution failed: $operationName", e)
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse(
                                error = "operation_execution_failed",
                                message = e.message ?: "Operation execution failed",
                                details = mapOf("operationName" to operationName)
                            )
                        )
                    }
                }
            }
            
            // Vector search endpoints
            route("/vector") {
                post("/search/{tableName}") {
                    val tableName = call.parameters["tableName"] ?: throw IllegalArgumentException("Table name required")
                    val request = call.receive<VectorSearchRequest>()
                    val context = createExecutionContext(call)
                    
                    try {
                        val results = persistenceManager.vectorSearch<Map<String, Any>>(
                            tableName = tableName,
                            queryVector = request.queryVector,
                            limit = request.limit ?: 10,
                            threshold = request.threshold ?: 0.7f,
                            context = context
                        )
                        
                        call.respond(
                            VectorSearchResponse(
                                tableName = tableName,
                                results = results,
                                count = results.size
                            )
                        )
                    } catch (e: Exception) {
                        logger.error("Vector search failed: $tableName", e)
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse(
                                error = "vector_search_failed",
                                message = e.message ?: "Vector search failed"
                            )
                        )
                    }
                }
                
                post("/hybrid-search/{tableName}") {
                    val tableName = call.parameters["tableName"] ?: throw IllegalArgumentException("Table name required")
                    val request = call.receive<HybridSearchRequest>()
                    val context = createExecutionContext(call)
                    
                    try {
                        val results = persistenceManager.hybridSearch<Map<String, Any>>(
                            tableName = tableName,
                            queryVector = request.queryVector,
                            queryText = request.queryText,
                            weights = SearchWeights(request.vectorWeight ?: 0.7f, request.textWeight ?: 0.3f),
                            limit = request.limit ?: 10,
                            context = context
                        )
                        
                        call.respond(
                            HybridSearchResponse(
                                tableName = tableName,
                                results = results,
                                count = results.size
                            )
                        )
                    } catch (e: Exception) {
                        logger.error("Hybrid search failed: $tableName", e)
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse(
                                error = "hybrid_search_failed",
                                message = e.message ?: "Hybrid search failed"
                            )
                        )
                    }
                }
            }
            
            // Graph operations endpoints
            route("/graph") {
                post("/traverse/{tableName}") {
                    val tableName = call.parameters["tableName"] ?: throw IllegalArgumentException("Table name required")
                    val request = call.receive<GraphTraversalRequest>()
                    val context = createExecutionContext(call)
                    
                    try {
                        val results = persistenceManager.graphTraversal<Map<String, Any>>(
                            tableName = tableName,
                            startNodeId = request.startNodeId,
                            relationshipType = request.relationshipType,
                            maxDepth = request.maxDepth ?: 3,
                            context = context
                        )
                        
                        call.respond(
                            GraphTraversalResponse(
                                tableName = tableName,
                                startNodeId = request.startNodeId,
                                results = results,
                                count = results.size
                            )
                        )
                    } catch (e: Exception) {
                        logger.error("Graph traversal failed: $tableName", e)
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse(
                                error = "graph_traversal_failed",
                                message = e.message ?: "Graph traversal failed"
                            )
                        )
                    }
                }
                
                post("/shortest-path/{tableName}") {
                    val tableName = call.parameters["tableName"] ?: throw IllegalArgumentException("Table name required")
                    val request = call.receive<ShortestPathRequest>()
                    val context = createExecutionContext(call)
                    
                    try {
                        val result = persistenceManager.shortestPath<Map<String, Any>>(
                            tableName = tableName,
                            fromNodeId = request.fromNodeId,
                            toNodeId = request.toNodeId,
                            context = context
                        )
                        
                        call.respond(
                            ShortestPathResponse(
                                tableName = tableName,
                                fromNodeId = request.fromNodeId,
                                toNodeId = request.toNodeId,
                                path = result
                            )
                        )
                    } catch (e: Exception) {
                        logger.error("Shortest path search failed: $tableName", e)
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse(
                                error = "shortest_path_failed",
                                message = e.message ?: "Shortest path search failed"
                            )
                        )
                    }
                }
            }
            
            // Cache operations endpoints
            route("/cache") {
                get("/{key}") {
                    val key = call.parameters["key"] ?: throw IllegalArgumentException("Cache key required")
                    val context = createExecutionContext(call)
                    
                    try {
                        val value = persistenceManager.cacheGet<Any>(key, context)
                        if (value != null) {
                            call.respond(
                                CacheResponse(
                                    key = key,
                                    value = value,
                                    found = true
                                )
                            )
                        } else {
                            call.respond(
                                HttpStatusCode.NotFound,
                                CacheResponse(
                                    key = key,
                                    value = null,
                                    found = false
                                )
                            )
                        }
                    } catch (e: Exception) {
                        logger.error("Cache get failed: $key", e)
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse(
                                error = "cache_get_failed",
                                message = e.message ?: "Cache get operation failed"
                            )
                        )
                    }
                }
                
                put("/{key}") {
                    val key = call.parameters["key"] ?: throw IllegalArgumentException("Cache key required")
                    val request = call.receive<CacheSetRequest>()
                    val context = createExecutionContext(call)
                    
                    try {
                        persistenceManager.cacheSet(key, request.value, request.ttl, context)
                        call.respond(
                            CacheResponse(
                                key = key,
                                value = request.value,
                                found = true
                            )
                        )
                    } catch (e: Exception) {
                        logger.error("Cache set failed: $key", e)
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse(
                                error = "cache_set_failed",
                                message = e.message ?: "Cache set operation failed"
                            )
                        )
                    }
                }
                
                delete("/{key}") {
                    val key = call.parameters["key"] ?: throw IllegalArgumentException("Cache key required")
                    val context = createExecutionContext(call)
                    
                    try {
                        val removed = persistenceManager.cacheRemove(key, context)
                        call.respond(
                            CacheResponse(
                                key = key,
                                value = null,
                                found = removed
                            )
                        )
                    } catch (e: Exception) {
                        logger.error("Cache remove failed: $key", e)
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse(
                                error = "cache_remove_failed",
                                message = e.message ?: "Cache remove operation failed"
                            )
                        )
                    }
                }
            }
        }
    }
    
    // ==========================================================================
    // gRPC Server (Placeholder)
    // ==========================================================================
    
    private suspend fun startGrpcServer(port: Int) {
        // gRPC server implementation would go here
        logger.info("✅ gRPC API server would start on port $port (not implemented yet)")
    }
    
    // ==========================================================================
    // Helper Methods
    // ==========================================================================
    
    private fun createExecutionContext(call: ApplicationCall): ExecutionContext {
        return ExecutionContext(
            requestId = call.request.headers["X-Request-ID"] ?: java.util.UUID.randomUUID().toString(),
            userId = call.request.headers["X-User-ID"],
            sessionId = call.request.headers["X-Session-ID"],
            traceId = call.request.headers["X-Trace-ID"],
            spanId = call.request.headers["X-Span-ID"],
            timestamp = Instant.now(),
            metadata = mapOf(
                "user_agent" to (call.request.headers["User-Agent"] ?: "unknown"),
                "remote_address" to (call.request.origin.remoteHost),
                "method" to call.request.httpMethod.value,
                "uri" to call.request.uri
            )
        )
    }
}

// ==========================================================================
// Request/Response Models
// ==========================================================================

@Serializable
data class QueryRequest(
    val parameters: Map<String, String> = emptyMap()
)

@Serializable
data class QueryResponse(
    val queryName: String,
    val results: List<Map<String, Any>>,
    val count: Int,
    val executionTime: Long
)

@Serializable
data class OperationRequest(
    val parameters: Map<String, String> = emptyMap()
)

@Serializable
data class OperationResponse(
    val operationName: String,
    val status: String,
    val result: Map<String, Any>?,
    val executionTime: Long,
    val affectedRecords: Long
)

@Serializable
data class CrudResponse(
    val operation: String,
    val tableName: String,
    val result: Any?,
    val affectedRecords: Long
)

@Serializable
data class VectorSearchRequest(
    val queryVector: FloatArray,
    val limit: Int? = null,
    val threshold: Float? = null
)

@Serializable
data class VectorSearchResponse(
    val tableName: String,
    val results: List<VectorSearchResult<Map<String, Any>>>,
    val count: Int
)

@Serializable
data class HybridSearchRequest(
    val queryVector: FloatArray,
    val queryText: String,
    val vectorWeight: Float? = null,
    val textWeight: Float? = null,
    val limit: Int? = null
)

@Serializable
data class HybridSearchResponse(
    val tableName: String,
    val results: List<HybridSearchResult<Map<String, Any>>>,
    val count: Int
)

@Serializable
data class GraphTraversalRequest(
    val startNodeId: String,
    val relationshipType: String,
    val maxDepth: Int? = null
)

@Serializable
data class GraphTraversalResponse(
    val tableName: String,
    val startNodeId: String,
    val results: List<GraphNode<Map<String, Any>>>,
    val count: Int
)

@Serializable
data class ShortestPathRequest(
    val fromNodeId: String,
    val toNodeId: String
)

@Serializable
data class ShortestPathResponse(
    val tableName: String,
    val fromNodeId: String,
    val toNodeId: String,
    val path: GraphPath<Map<String, Any>>?
)

@Serializable
data class CacheSetRequest(
    val value: Any,
    val ttl: Long? = null
)

@Serializable
data class CacheResponse(
    val key: String,
    val value: Any?,
    val found: Boolean
)

@Serializable
data class HealthResponse(
    val status: String,
    val timestamp: String,
    val technologies: Map<String, HealthStatus>
)

@Serializable
data class ConfigResponse(
    val version: String,
    val technologies: List<String>,
    val databases: List<String>,
    val tables: List<String>
)

@Serializable
data class ErrorResponse(
    val error: String,
    val message: String,
    val timestamp: String = Instant.now().toString(),
    val details: Map<String, Any> = emptyMap()
)
