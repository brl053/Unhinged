// ============================================================================
// Persistence Platform - Data Lifecycle Management
// ============================================================================
//
// @file DataLifecycleManager.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-10-19
// @description Data lifecycle management system for hot/warm/cold data tiering
//
// This system manages the complete data lifecycle including hot/warm/cold
// tiering, automatic archival, retention policies, and cross-technology
// data movement based on access patterns and age.
//
// ============================================================================

package com.unhinged.persistence.lifecycle

import com.unhinged.persistence.config.LifecycleConfiguration
import com.unhinged.persistence.core.DatabaseProvider
import com.unhinged.persistence.model.*
import com.unhinged.persistence.providers.ProviderRegistry
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import org.slf4j.LoggerFactory
import java.time.Instant
import java.time.temporal.ChronoUnit
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong

/*
 * @llm-type misc.lifecycle-manager
 * @llm-does data lifecycle manager that handles hot/warm/cold data
 */
class DataLifecycleManager(
    private val providerRegistry: ProviderRegistry,
    private val configuration: LifecycleConfiguration
) {
    
    private val logger = LoggerFactory.getLogger(DataLifecycleManager::class.java)
    
    // Lifecycle job management
    private val lifecycleScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var lifecycleJob: Job? = null
    
    // Metrics and tracking
    private val metrics = LifecycleMetrics()
    private val activeOperations = ConcurrentHashMap<String, LifecycleOperation>()
    
    // ==========================================================================
    // Lifecycle Management
    // ==========================================================================
    
    /**
     * Start the data lifecycle management system
     */
    suspend fun start() {
        logger.info("🔄 Starting Data Lifecycle Manager...")
        
        try {
            // Start periodic lifecycle processing
            startLifecycleScheduler()
            
            // Initialize data tier tracking
            initializeDataTierTracking()
            
            logger.info("✅ Data Lifecycle Manager started successfully")
            
        } catch (e: Exception) {
            logger.error("❌ Failed to start Data Lifecycle Manager", e)
            throw e
        }
    }
    
    /**
     * Stop the data lifecycle management system
     */
    suspend fun stop() {
        logger.info("🛑 Stopping Data Lifecycle Manager...")
        
        try {
            // Cancel lifecycle job
            lifecycleJob?.cancel()
            lifecycleJob?.join()
            
            // Cancel all active operations
            activeOperations.values.forEach { operation ->
                operation.cancel()
            }
            activeOperations.clear()
            
            // Cancel lifecycle scope
            lifecycleScope.cancel()
            
            logger.info("✅ Data Lifecycle Manager stopped successfully")
            
        } catch (e: Exception) {
            logger.error("❌ Error stopping Data Lifecycle Manager", e)
            throw e
        }
    }
    
    // ==========================================================================
    // Data Tiering Operations
    // ==========================================================================
    
    /**
     * Move data to hot tier (frequently accessed)
     */
    suspend fun moveToHotTier(
        tableName: String,
        criteria: DataTieringCriteria,
        context: ExecutionContext
    ): TieringResult {
        logger.info("🔥 Moving data to hot tier: $tableName")
        
        val operation = LifecycleOperation(
            operationId = context.requestId,
            type = LifecycleOperationType.MOVE_TO_HOT,
            tableName = tableName,
            startTime = Instant.now()
        )
        
        activeOperations[operation.operationId] = operation
        
        return try {
            val hotProviders = getProvidersForTier(DataTier.HOT)
            val sourceProvider = getProviderForTable(tableName)
            
            if (hotProviders.contains(sourceProvider)) {
                // Data is already in hot tier
                TieringResult(
                    operationId = operation.operationId,
                    success = true,
                    message = "Data already in hot tier",
                    recordsProcessed = 0,
                    executionTime = 0
                )
            } else {
                // Move data to hot tier
                val targetProvider = hotProviders.first()
                moveDataBetweenProviders(sourceProvider, targetProvider, tableName, criteria, context)
            }
            
        } catch (e: Exception) {
            logger.error("Failed to move data to hot tier: $tableName", e)
            TieringResult(
                operationId = operation.operationId,
                success = false,
                message = "Failed to move data: ${e.message}",
                recordsProcessed = 0,
                executionTime = System.currentTimeMillis() - operation.startTime.toEpochMilli()
            )
        } finally {
            activeOperations.remove(operation.operationId)
        }
    }
    
    /**
     * Move data to warm tier (occasionally accessed)
     */
    suspend fun moveToWarmTier(
        tableName: String,
        criteria: DataTieringCriteria,
        context: ExecutionContext
    ): TieringResult {
        logger.info("🌡️ Moving data to warm tier: $tableName")
        
        val operation = LifecycleOperation(
            operationId = context.requestId,
            type = LifecycleOperationType.MOVE_TO_WARM,
            tableName = tableName,
            startTime = Instant.now()
        )
        
        activeOperations[operation.operationId] = operation
        
        return try {
            val warmProviders = getProvidersForTier(DataTier.WARM)
            val sourceProvider = getProviderForTable(tableName)
            
            if (warmProviders.contains(sourceProvider)) {
                TieringResult(
                    operationId = operation.operationId,
                    success = true,
                    message = "Data already in warm tier",
                    recordsProcessed = 0,
                    executionTime = 0
                )
            } else {
                val targetProvider = warmProviders.first()
                moveDataBetweenProviders(sourceProvider, targetProvider, tableName, criteria, context)
            }
            
        } catch (e: Exception) {
            logger.error("Failed to move data to warm tier: $tableName", e)
            TieringResult(
                operationId = operation.operationId,
                success = false,
                message = "Failed to move data: ${e.message}",
                recordsProcessed = 0,
                executionTime = System.currentTimeMillis() - operation.startTime.toEpochMilli()
            )
        } finally {
            activeOperations.remove(operation.operationId)
        }
    }
    
    /**
     * Move data to cold tier (rarely accessed)
     */
    suspend fun moveToColdTier(
        tableName: String,
        criteria: DataTieringCriteria,
        context: ExecutionContext
    ): TieringResult {
        logger.info("🧊 Moving data to cold tier: $tableName")
        
        val operation = LifecycleOperation(
            operationId = context.requestId,
            type = LifecycleOperationType.MOVE_TO_COLD,
            tableName = tableName,
            startTime = Instant.now()
        )
        
        activeOperations[operation.operationId] = operation
        
        return try {
            val coldProviders = getProvidersForTier(DataTier.COLD)
            val sourceProvider = getProviderForTable(tableName)
            
            if (coldProviders.contains(sourceProvider)) {
                TieringResult(
                    operationId = operation.operationId,
                    success = true,
                    message = "Data already in cold tier",
                    recordsProcessed = 0,
                    executionTime = 0
                )
            } else {
                val targetProvider = coldProviders.first()
                moveDataBetweenProviders(sourceProvider, targetProvider, tableName, criteria, context)
            }
            
        } catch (e: Exception) {
            logger.error("Failed to move data to cold tier: $tableName", e)
            TieringResult(
                operationId = operation.operationId,
                success = false,
                message = "Failed to move data: ${e.message}",
                recordsProcessed = 0,
                executionTime = System.currentTimeMillis() - operation.startTime.toEpochMilli()
            )
        } finally {
            activeOperations.remove(operation.operationId)
        }
    }
    
    // ==========================================================================
    // Archival Operations
    // ==========================================================================
    
    /**
     * Archive data based on retention policies
     */
    suspend fun archiveData(
        tableName: String,
        archivalCriteria: ArchivalCriteria,
        context: ExecutionContext
    ): ArchivalResult {
        logger.info("📦 Archiving data: $tableName")
        
        val operation = LifecycleOperation(
            operationId = context.requestId,
            type = LifecycleOperationType.ARCHIVE,
            tableName = tableName,
            startTime = Instant.now()
        )
        
        activeOperations[operation.operationId] = operation
        
        return try {
            val sourceProvider = getProviderForTable(tableName)
            val archiveProvider = getArchiveProvider()
            
            // Query data to archive
            val query = QuerySpec(
                tableName = tableName,
                queryType = QueryType.RANGE_SCAN,
                criteria = buildArchivalCriteria(archivalCriteria),
                limit = configuration.automation.batchSize
            )
            
            var recordsArchived = 0L
            val startTime = System.currentTimeMillis()
            
            // Process data in batches
            sourceProvider.executeQuery<Map<String, Any>>(query, context).collect { record ->
                // Archive record
                archiveProvider.insert("${tableName}_archive", record, context)
                recordsArchived++
                
                // Update metrics
                metrics.recordsArchived.incrementAndGet()
            }
            
            // Remove archived data from source if configured
            if (archivalCriteria.removeAfterArchive) {
                val deletedCount = sourceProvider.delete(tableName, buildArchivalCriteria(archivalCriteria), context)
                logger.info("Removed $deletedCount archived records from source")
            }
            
            val executionTime = System.currentTimeMillis() - startTime
            
            ArchivalResult(
                operationId = operation.operationId,
                success = true,
                recordsArchived = recordsArchived,
                executionTime = executionTime,
                archiveLocation = "data_lake"
            )
            
        } catch (e: Exception) {
            logger.error("Failed to archive data: $tableName", e)
            ArchivalResult(
                operationId = operation.operationId,
                success = false,
                recordsArchived = 0,
                executionTime = System.currentTimeMillis() - operation.startTime.toEpochMilli(),
                archiveLocation = null,
                error = e.message
            )
        } finally {
            activeOperations.remove(operation.operationId)
        }
    }
    
    // ==========================================================================
    // Retention Policy Enforcement
    // ==========================================================================
    
    /**
     * Apply retention policies to data
     */
    suspend fun applyRetentionPolicies(context: ExecutionContext): RetentionResult {
        logger.info("🗑️ Applying retention policies...")
        
        val results = mutableListOf<TableRetentionResult>()
        
        configuration.policies.forEach { (policyName, policy) ->
            policy.appliesTo.forEach { tableName ->
                try {
                    val result = applyRetentionPolicyToTable(tableName, policy, context)
                    results.add(result)
                } catch (e: Exception) {
                    logger.error("Failed to apply retention policy to table: $tableName", e)
                    results.add(
                        TableRetentionResult(
                            tableName = tableName,
                            policyName = policyName,
                            success = false,
                            recordsDeleted = 0,
                            error = e.message
                        )
                    )
                }
            }
        }
        
        val totalDeleted = results.sumOf { it.recordsDeleted }
        val successCount = results.count { it.success }
        
        return RetentionResult(
            totalTablesProcessed = results.size,
            successfulTables = successCount,
            totalRecordsDeleted = totalDeleted,
            tableResults = results
        )
    }
    
    // ==========================================================================
    // Automatic Lifecycle Processing
    // ==========================================================================
    
    private fun startLifecycleScheduler() {
        lifecycleJob = lifecycleScope.launch {
            while (isActive) {
                try {
                    // Parse schedule (simplified - would use cron parser in real implementation)
                    val scheduleDelay = parseScheduleToDelay(configuration.automation.schedule)
                    
                    delay(scheduleDelay)
                    
                    if (isActive) {
                        processAutomaticLifecycle()
                    }
                    
                } catch (e: Exception) {
                    logger.error("Error in lifecycle scheduler", e)
                    delay(60000) // Wait 1 minute before retrying
                }
            }
        }
    }
    
    private suspend fun processAutomaticLifecycle() {
        logger.info("🔄 Processing automatic lifecycle operations...")
        
        val context = ExecutionContext(
            requestId = "lifecycle-${System.currentTimeMillis()}",
            timestamp = Instant.now(),
            metadata = mapOf("source" to "automatic_lifecycle")
        )
        
        try {
            // Apply retention policies
            val retentionResult = applyRetentionPolicies(context)
            logger.info("Retention processing completed: ${retentionResult.totalRecordsDeleted} records deleted")
            
            // Process data tiering
            processDataTiering(context)
            
            // Update metrics
            metrics.lifecycleCycles.incrementAndGet()
            
        } catch (e: Exception) {
            logger.error("Error in automatic lifecycle processing", e)
            metrics.lifecycleErrors.incrementAndGet()
        }
    }
    
    private suspend fun processDataTiering(context: ExecutionContext) {
        logger.info("📊 Processing data tiering...")
        
        // This would analyze access patterns and move data between tiers
        // For now, this is a placeholder implementation
        
        // Example: Move old data to cold tier
        configuration.policies.forEach { (policyName, policy) ->
            policy.rules.forEach { rule ->
                when (rule.action) {
                    "move_to_cold_storage" -> {
                        policy.appliesTo.forEach { tableName ->
                            try {
                                val criteria = DataTieringCriteria(
                                    ageThreshold = parseAge(rule.age ?: "30d"),
                                    accessThreshold = null
                                )
                                moveToColdTier(tableName, criteria, context)
                            } catch (e: Exception) {
                                logger.error("Failed to move data to cold tier: $tableName", e)
                            }
                        }
                    }
                }
            }
        }
    }
    
    // ==========================================================================
    // Helper Methods
    // ==========================================================================
    
    private fun initializeDataTierTracking() {
        logger.info("📊 Initializing data tier tracking...")
        // Initialize tracking of data access patterns
        // This would set up monitoring of query patterns to inform tiering decisions
    }
    
    private fun getProvidersForTier(tier: DataTier): List<DatabaseProvider> {
        return when (tier) {
            DataTier.HOT -> providerRegistry.getProvidersByType(com.unhinged.persistence.core.TechnologyType.CACHE)
            DataTier.WARM -> providerRegistry.getProvidersByType(com.unhinged.persistence.core.TechnologyType.NEWSQL) +
                           providerRegistry.getProvidersByType(com.unhinged.persistence.core.TechnologyType.NOSQL_DOCUMENT)
            DataTier.COLD -> providerRegistry.getProvidersByType(com.unhinged.persistence.core.TechnologyType.OLAP_WAREHOUSE)
        }
    }
    
    private fun getProviderForTable(tableName: String): DatabaseProvider {
        // This would look up the provider based on table configuration
        // For now, return the first available provider
        return providerRegistry.getAllProviders().values.first()
    }
    
    private fun getArchiveProvider(): DatabaseProvider {
        return providerRegistry.getProvidersByType(com.unhinged.persistence.core.TechnologyType.OLAP_WAREHOUSE).first()
    }
    
    private suspend fun moveDataBetweenProviders(
        sourceProvider: DatabaseProvider,
        targetProvider: DatabaseProvider,
        tableName: String,
        criteria: DataTieringCriteria,
        context: ExecutionContext
    ): TieringResult {
        val startTime = System.currentTimeMillis()
        var recordsProcessed = 0L
        
        try {
            // Query data from source
            val query = QuerySpec(
                tableName = tableName,
                queryType = QueryType.RANGE_SCAN,
                criteria = buildTieringCriteria(criteria),
                limit = configuration.automation.batchSize
            )
            
            val records = mutableListOf<Map<String, Any>>()
            sourceProvider.executeQuery<Map<String, Any>>(query, context).collect { record ->
                records.add(record)
                recordsProcessed++
            }
            
            // Insert data into target
            if (records.isNotEmpty()) {
                targetProvider.insertBatch(tableName, records, context)
                
                // Remove data from source if configured
                if (criteria.removeFromSource) {
                    sourceProvider.delete(tableName, buildTieringCriteria(criteria), context)
                }
            }
            
            val executionTime = System.currentTimeMillis() - startTime
            
            return TieringResult(
                operationId = context.requestId,
                success = true,
                message = "Data moved successfully",
                recordsProcessed = recordsProcessed,
                executionTime = executionTime
            )
            
        } catch (e: Exception) {
            logger.error("Failed to move data between providers", e)
            throw e
        }
    }
    
    private suspend fun applyRetentionPolicyToTable(
        tableName: String,
        policy: com.unhinged.persistence.config.LifecyclePolicy,
        context: ExecutionContext
    ): TableRetentionResult {
        var totalDeleted = 0L
        
        policy.rules.forEach { rule ->
            when (rule.action) {
                "delete" -> {
                    val criteria = buildRetentionCriteria(rule)
                    val provider = getProviderForTable(tableName)
                    val deleted = provider.delete(tableName, criteria, context)
                    totalDeleted += deleted
                }
                "archive" -> {
                    // Archive before deletion
                    val archivalCriteria = ArchivalCriteria(
                        ageThreshold = parseAge(rule.age ?: "1y"),
                        removeAfterArchive = true
                    )
                    val result = archiveData(tableName, archivalCriteria, context)
                    totalDeleted += result.recordsArchived
                }
            }
        }
        
        return TableRetentionResult(
            tableName = tableName,
            policyName = policy.toString(),
            success = true,
            recordsDeleted = totalDeleted
        )
    }
    
    private fun buildArchivalCriteria(criteria: ArchivalCriteria): QueryCriteria {
        return QueryCriteria.LessThan("created_at", criteria.ageThreshold)
    }
    
    private fun buildTieringCriteria(criteria: DataTieringCriteria): QueryCriteria {
        return if (criteria.ageThreshold != null) {
            QueryCriteria.LessThan("created_at", criteria.ageThreshold)
        } else {
            QueryCriteria.LessThan("last_accessed", criteria.accessThreshold ?: Instant.now().minus(30, ChronoUnit.DAYS))
        }
    }
    
    private fun buildRetentionCriteria(rule: com.unhinged.persistence.config.LifecycleRule): QueryCriteria {
        return if (rule.age != null) {
            QueryCriteria.LessThan("created_at", parseAge(rule.age))
        } else {
            // Build criteria based on condition
            QueryCriteria.Equals("status", "inactive")
        }
    }
    
    private fun parseAge(ageString: String): Instant {
        // Parse age strings like "7_years", "30_days", "1_month"
        val parts = ageString.split("_")
        val amount = parts[0].toLong()
        val unit = parts[1]
        
        return when (unit) {
            "days", "day" -> Instant.now().minus(amount, ChronoUnit.DAYS)
            "months", "month" -> Instant.now().minus(amount * 30, ChronoUnit.DAYS)
            "years", "year" -> Instant.now().minus(amount * 365, ChronoUnit.DAYS)
            else -> Instant.now().minus(amount, ChronoUnit.DAYS)
        }
    }
    
    private fun parseScheduleToDelay(schedule: String): Long {
        // Parse schedule strings like "daily_at_02:00_utc"
        // For now, return 24 hours for daily schedule
        return when {
            schedule.startsWith("daily") -> 24 * 60 * 60 * 1000L
            schedule.startsWith("hourly") -> 60 * 60 * 1000L
            else -> 24 * 60 * 60 * 1000L
        }
    }
    
    // ==========================================================================
    // Monitoring and Metrics
    // ==========================================================================
    
    fun getLifecycleMetrics(): LifecycleMetrics {
        return metrics
    }
    
    fun getActiveOperations(): List<LifecycleOperation> {
        return activeOperations.values.toList()
    }
}

// ==========================================================================
// Data Classes
// ==========================================================================

enum class DataTier {
    HOT, WARM, COLD
}

enum class LifecycleOperationType {
    MOVE_TO_HOT, MOVE_TO_WARM, MOVE_TO_COLD, ARCHIVE, DELETE
}

data class LifecycleOperation(
    val operationId: String,
    val type: LifecycleOperationType,
    val tableName: String,
    val startTime: Instant,
    var status: String = "running"
) {
    fun cancel() {
        status = "cancelled"
    }
}

data class DataTieringCriteria(
    val ageThreshold: Instant? = null,
    val accessThreshold: Instant? = null,
    val removeFromSource: Boolean = false
)

data class ArchivalCriteria(
    val ageThreshold: Instant,
    val removeAfterArchive: Boolean = false
)

data class TieringResult(
    val operationId: String,
    val success: Boolean,
    val message: String,
    val recordsProcessed: Long,
    val executionTime: Long
)

data class ArchivalResult(
    val operationId: String,
    val success: Boolean,
    val recordsArchived: Long,
    val executionTime: Long,
    val archiveLocation: String?,
    val error: String? = null
)

data class RetentionResult(
    val totalTablesProcessed: Int,
    val successfulTables: Int,
    val totalRecordsDeleted: Long,
    val tableResults: List<TableRetentionResult>
)

data class TableRetentionResult(
    val tableName: String,
    val policyName: String,
    val success: Boolean,
    val recordsDeleted: Long,
    val error: String? = null
)

class LifecycleMetrics {
    val lifecycleCycles = AtomicLong(0)
    val lifecycleErrors = AtomicLong(0)
    val recordsArchived = AtomicLong(0)
    val recordsDeleted = AtomicLong(0)
    val dataMoved = AtomicLong(0)
}
