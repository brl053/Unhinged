package platforms.persistence.hooks

import platforms.persistence.api.*
import platforms.persistence.repository.*
import org.slf4j.LoggerFactory
import java.time.Instant

/**
 * CockroachDB Hooks - Utility functions for common operations
 * ==========================================================
 * 
 * React-inspired hooks pattern for reusable CRDB operations.
 * Provides common patterns and utilities for persistence operations.
 */
object CrdbHooks {
    
    private val logger = LoggerFactory.getLogger(CrdbHooks::class.java)
    
    /**
     * Hook for entity existence check
     */
    fun useEntityExists(api: CrdbApi, id: String): Boolean {
        return when (val response = api.getEntity(id)) {
            is ApiResponse.Success -> response.data != null
            is ApiResponse.Error -> {
                logger.warn("Failed to check entity existence for $id: ${response.message}")
                false
            }
        }
    }
    
    /**
     * Hook for safe entity creation (only if not exists)
     */
    fun useCreateIfNotExists(
        api: CrdbApi,
        id: String,
        recordType: String,
        data: String,
        metadata: String? = null
    ): ApiResponse<String> {
        return if (useEntityExists(api, id)) {
            ApiResponse.Error("Entity with ID $id already exists")
        } else {
            api.createEntity(id, recordType, data, metadata)
        }
    }
    
    /**
     * Hook for upsert operation (create or update)
     */
    fun useUpsert(
        api: CrdbApi,
        id: String,
        recordType: String,
        data: String,
        metadata: String? = null
    ): ApiResponse<CrdbEntity> {
        return if (useEntityExists(api, id)) {
            // Update existing
            api.updateEntity(id, data, metadata)
        } else {
            // Create new
            when (val createResponse = api.createEntity(id, recordType, data, metadata)) {
                is ApiResponse.Success -> {
                    // Return the created entity
                    api.getEntity(id) as ApiResponse<CrdbEntity>
                }
                is ApiResponse.Error -> ApiResponse.Error(createResponse.message, createResponse.cause)
            }
        }
    }
    
    /**
     * Hook for safe delete (only if exists)
     */
    fun useDeleteIfExists(api: CrdbApi, id: String): ApiResponse<Boolean> {
        return if (useEntityExists(api, id)) {
            api.deleteEntity(id)
        } else {
            ApiResponse.Success(false) // Already doesn't exist
        }
    }
    
    /**
     * Hook for batch operations
     */
    fun useBatchCreate(
        api: CrdbApi,
        entities: List<Triple<String, String, String>> // id, recordType, data
    ): BatchResult {
        val results = mutableListOf<Pair<String, ApiResponse<String>>>()
        var successCount = 0
        var failureCount = 0
        
        entities.forEach { (id, recordType, data) ->
            val response = api.createEntity(id, recordType, data)
            results.add(id to response)
            
            when (response) {
                is ApiResponse.Success -> successCount++
                is ApiResponse.Error -> failureCount++
            }
        }
        
        return BatchResult(
            total = entities.size,
            successful = successCount,
            failed = failureCount,
            results = results
        )
    }
    
    /**
     * Hook for paginated listing with automatic pagination
     */
    fun usePaginatedList(
        api: CrdbApi,
        pageSize: Int = 50,
        maxPages: Int = 10
    ): PaginatedResult {
        val allEntities = mutableListOf<CrdbEntity>()
        var currentPage = 0
        var hasMore = true
        
        while (hasMore && currentPage < maxPages) {
            val offset = currentPage * pageSize
            
            when (val response = api.listEntities(pageSize, offset)) {
                is ApiResponse.Success -> {
                    val entities = response.data
                    allEntities.addAll(entities)
                    
                    // Check if we got fewer entities than requested (end of data)
                    hasMore = entities.size == pageSize
                    currentPage++
                }
                is ApiResponse.Error -> {
                    logger.error("Failed to fetch page $currentPage: ${response.message}")
                    hasMore = false
                }
            }
        }
        
        return PaginatedResult(
            entities = allEntities,
            totalFetched = allEntities.size,
            pagesFetched = currentPage,
            hasMore = hasMore
        )
    }
    
    /**
     * Hook for entity validation before operations
     */
    fun useValidateEntity(
        id: String,
        recordType: String,
        data: String
    ): ValidationResult {
        val errors = mutableListOf<String>()
        
        // Basic validation rules
        if (id.isBlank()) {
            errors.add("ID cannot be blank")
        }
        
        if (recordType.isBlank()) {
            errors.add("Record type cannot be blank")
        }
        
        if (data.isBlank()) {
            errors.add("Data cannot be blank")
        }
        
        // JSON validation (basic check)
        try {
            if (!data.trim().startsWith("{") || !data.trim().endsWith("}")) {
                errors.add("Data must be valid JSON object")
            }
        } catch (e: Exception) {
            errors.add("Invalid JSON format: ${e.message}")
        }
        
        return ValidationResult(
            isValid = errors.isEmpty(),
            errors = errors
        )
    }
    
    /**
     * Hook for health check
     */
    fun useHealthCheck(api: CrdbApi): HealthCheckResult {
        val startTime = System.currentTimeMillis()
        
        return try {
            // Try to count entities as a health check
            when (val response = api.countEntities()) {
                is ApiResponse.Success -> {
                    val responseTime = System.currentTimeMillis() - startTime
                    HealthCheckResult(
                        healthy = true,
                        responseTimeMs = responseTime,
                        entityCount = response.data,
                        timestamp = Instant.now()
                    )
                }
                is ApiResponse.Error -> {
                    val responseTime = System.currentTimeMillis() - startTime
                    HealthCheckResult(
                        healthy = false,
                        responseTimeMs = responseTime,
                        errorMessage = response.message,
                        timestamp = Instant.now()
                    )
                }
            }
        } catch (e: Exception) {
            val responseTime = System.currentTimeMillis() - startTime
            HealthCheckResult(
                healthy = false,
                responseTimeMs = responseTime,
                errorMessage = "Health check failed: ${e.message}",
                timestamp = Instant.now()
            )
        }
    }
    
    /**
     * Hook for performance metrics
     */
    fun usePerformanceMetrics(api: CrdbApi, operations: Int = 10): PerformanceMetrics {
        val createTimes = mutableListOf<Long>()
        val readTimes = mutableListOf<Long>()
        val updateTimes = mutableListOf<Long>()
        val deleteTimes = mutableListOf<Long>()
        
        repeat(operations) { i ->
            val testId = "perf_test_$i"
            
            // CREATE
            val createStart = System.currentTimeMillis()
            api.createEntity(testId, "perf_test", """{"test": $i}""")
            createTimes.add(System.currentTimeMillis() - createStart)
            
            // READ
            val readStart = System.currentTimeMillis()
            api.getEntity(testId)
            readTimes.add(System.currentTimeMillis() - readStart)
            
            // UPDATE
            val updateStart = System.currentTimeMillis()
            api.updateEntity(testId, """{"test": ${i * 2}}""")
            updateTimes.add(System.currentTimeMillis() - updateStart)
            
            // DELETE
            val deleteStart = System.currentTimeMillis()
            api.deleteEntity(testId)
            deleteTimes.add(System.currentTimeMillis() - deleteStart)
        }
        
        return PerformanceMetrics(
            operations = operations,
            avgCreateTime = createTimes.average(),
            avgReadTime = readTimes.average(),
            avgUpdateTime = updateTimes.average(),
            avgDeleteTime = deleteTimes.average(),
            totalTime = createTimes.sum() + readTimes.sum() + updateTimes.sum() + deleteTimes.sum()
        )
    }
}

// Result types for hooks
data class BatchResult(
    val total: Int,
    val successful: Int,
    val failed: Int,
    val results: List<Pair<String, ApiResponse<String>>>
)

data class PaginatedResult(
    val entities: List<CrdbEntity>,
    val totalFetched: Int,
    val pagesFetched: Int,
    val hasMore: Boolean
)

data class ValidationResult(
    val isValid: Boolean,
    val errors: List<String>
)

data class HealthCheckResult(
    val healthy: Boolean,
    val responseTimeMs: Long,
    val entityCount: Long? = null,
    val errorMessage: String? = null,
    val timestamp: Instant
)

data class PerformanceMetrics(
    val operations: Int,
    val avgCreateTime: Double,
    val avgReadTime: Double,
    val avgUpdateTime: Double,
    val avgDeleteTime: Double,
    val totalTime: Long
)
