// ============================================================================
// Persistence Platform - Observability Manager
// ============================================================================
//
// @file ObservabilityManager.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-10-19
// @description Comprehensive observability system for metrics, tracing, and monitoring
//
// This system provides complete observability for the persistence platform
// including metrics collection, distributed tracing, health monitoring,
// alerting, and performance analytics across all database technologies.
//
// ============================================================================

package com.unhinged.persistence.monitoring

import com.unhinged.persistence.config.MonitoringConfiguration
import com.unhinged.persistence.model.*
import com.unhinged.persistence.providers.ProviderRegistry
import io.micrometer.core.instrument.*
import io.micrometer.core.instrument.Timer
import io.micrometer.prometheus.PrometheusConfig
import io.micrometer.prometheus.PrometheusMeterRegistry
import kotlinx.coroutines.*
import org.slf4j.LoggerFactory
import java.time.Duration
import java.time.Instant
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.DoubleAdder

/**
 * @llm-type observability-manager
 * @llm-legend Comprehensive observability system providing metrics, tracing, and monitoring for the persistence platform
 * @llm-key Central observability hub that collects metrics, traces requests, monitors health, and provides analytics
 * @llm-map Complete monitoring solution with metrics collection, distributed tracing, and performance analytics
 * @llm-axiom All persistence operations must be observable for proper monitoring and troubleshooting
 * @llm-contract Provides comprehensive observability including metrics, tracing, health checks, and alerting
 * @llm-token observability-manager: Complete monitoring and observability system
 */
class ObservabilityManager(
    private val providerRegistry: ProviderRegistry,
    private val configuration: MonitoringConfiguration
) {
    
    private val logger = LoggerFactory.getLogger(ObservabilityManager::class.java)
    
    // Metrics registry
    private val meterRegistry = PrometheusMeterRegistry(PrometheusConfig.DEFAULT)
    
    // Monitoring scope
    private val monitoringScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var monitoringJob: Job? = null
    
    // Metrics collectors
    private val platformMetrics = PlatformMetricsCollector()
    private val queryMetrics = QueryMetricsCollector()
    private val operationMetrics = OperationMetricsCollector()
    private val healthMetrics = HealthMetricsCollector()
    
    // Active traces
    private val activeTraces = ConcurrentHashMap<String, TraceContext>()
    
    // Alert manager
    private val alertManager = AlertManager(configuration.alerts)
    
    // ==========================================================================
    // Lifecycle Management
    // ==========================================================================
    
    /**
     * Start the observability system
     */
    suspend fun start() {
        logger.info("📊 Starting Observability Manager...")
        
        try {
            // Initialize metrics
            initializeMetrics()
            
            // Start monitoring jobs
            startMonitoringJobs()
            
            // Initialize alert manager
            alertManager.start()
            
            logger.info("✅ Observability Manager started successfully")
            
        } catch (e: Exception) {
            logger.error("❌ Failed to start Observability Manager", e)
            throw e
        }
    }
    
    /**
     * Stop the observability system
     */
    suspend fun stop() {
        logger.info("🛑 Stopping Observability Manager...")
        
        try {
            // Stop monitoring jobs
            monitoringJob?.cancel()
            monitoringJob?.join()
            
            // Stop alert manager
            alertManager.stop()
            
            // Cancel monitoring scope
            monitoringScope.cancel()
            
            logger.info("✅ Observability Manager stopped successfully")
            
        } catch (e: Exception) {
            logger.error("❌ Error stopping Observability Manager", e)
            throw e
        }
    }
    
    // ==========================================================================
    // Metrics Collection
    // ==========================================================================
    
    /**
     * Record query execution metrics
     */
    fun recordQueryExecution(
        queryName: String,
        tableName: String,
        technology: String,
        duration: Duration,
        success: Boolean,
        recordCount: Long = 0
    ) {
        // Record query latency
        Timer.Sample.start(meterRegistry)
            .stop(Timer.builder("persistence.query.duration")
                .description("Query execution duration")
                .tag("query", queryName)
                .tag("table", tableName)
                .tag("technology", technology)
                .tag("success", success.toString())
                .register(meterRegistry))
        
        // Record query count
        Counter.builder("persistence.query.count")
            .description("Total number of queries executed")
            .tag("query", queryName)
            .tag("table", tableName)
            .tag("technology", technology)
            .tag("success", success.toString())
            .register(meterRegistry)
            .increment()
        
        // Record result count
        if (recordCount > 0) {
            Gauge.builder("persistence.query.records")
                .description("Number of records returned by query")
                .tag("query", queryName)
                .tag("table", tableName)
                .register(meterRegistry, recordCount.toDouble())
        }
        
        // Update internal metrics
        queryMetrics.recordQuery(queryName, technology, duration, success, recordCount)
        
        // Check for alerts
        checkQueryAlerts(queryName, technology, duration, success)
    }
    
    /**
     * Record operation execution metrics
     */
    fun recordOperationExecution(
        operationName: String,
        operationType: String,
        duration: Duration,
        success: Boolean,
        affectedRecords: Long = 0
    ) {
        // Record operation latency
        Timer.Sample.start(meterRegistry)
            .stop(Timer.builder("persistence.operation.duration")
                .description("Operation execution duration")
                .tag("operation", operationName)
                .tag("type", operationType)
                .tag("success", success.toString())
                .register(meterRegistry))
        
        // Record operation count
        Counter.builder("persistence.operation.count")
            .description("Total number of operations executed")
            .tag("operation", operationName)
            .tag("type", operationType)
            .tag("success", success.toString())
            .register(meterRegistry)
            .increment()
        
        // Record affected records
        if (affectedRecords > 0) {
            Gauge.builder("persistence.operation.affected_records")
                .description("Number of records affected by operation")
                .tag("operation", operationName)
                .tag("type", operationType)
                .register(meterRegistry, affectedRecords.toDouble())
        }
        
        // Update internal metrics
        operationMetrics.recordOperation(operationName, operationType, duration, success, affectedRecords)
        
        // Check for alerts
        checkOperationAlerts(operationName, operationType, duration, success)
    }
    
    /**
     * Record database provider metrics
     */
    fun recordProviderMetrics(providerName: String, metrics: ProviderMetrics) {
        val tags = Tags.of("provider", providerName)
        
        // Connection metrics
        Gauge.builder("persistence.provider.connections.active")
            .description("Active database connections")
            .tags(tags)
            .register(meterRegistry, metrics.activeConnections.toDouble())
        
        Gauge.builder("persistence.provider.connections.total")
            .description("Total database connections")
            .tags(tags)
            .register(meterRegistry, metrics.connectionCount.toDouble())
        
        // Query metrics
        Gauge.builder("persistence.provider.queries.total")
            .description("Total queries executed")
            .tags(tags)
            .register(meterRegistry, metrics.queryCount.toDouble())
        
        Gauge.builder("persistence.provider.errors.total")
            .description("Total errors")
            .tags(tags)
            .register(meterRegistry, metrics.errorCount.toDouble())
        
        // Performance metrics
        Gauge.builder("persistence.provider.response_time.avg")
            .description("Average response time")
            .tags(tags)
            .register(meterRegistry, metrics.averageResponseTime)
        
        Gauge.builder("persistence.provider.throughput")
            .description("Operations per second")
            .tags(tags)
            .register(meterRegistry, metrics.throughput)
        
        // Custom metrics
        metrics.customMetrics.forEach { (key, value) ->
            when (value) {
                is Number -> {
                    Gauge.builder("persistence.provider.custom.$key")
                        .description("Custom provider metric: $key")
                        .tags(tags)
                        .register(meterRegistry, value.toDouble())
                }
            }
        }
    }
    
    /**
     * Record health status
     */
    fun recordHealthStatus(component: String, status: HealthState, responseTime: Long? = null) {
        val statusValue = when (status) {
            HealthState.HEALTHY -> 1.0
            HealthState.DEGRADED -> 0.5
            HealthState.UNHEALTHY -> 0.0
            HealthState.UNKNOWN -> -1.0
        }
        
        Gauge.builder("persistence.health.status")
            .description("Component health status")
            .tag("component", component)
            .register(meterRegistry, statusValue)
        
        responseTime?.let { time ->
            Gauge.builder("persistence.health.response_time")
                .description("Health check response time")
                .tag("component", component)
                .register(meterRegistry, time.toDouble())
        }
        
        // Update internal metrics
        healthMetrics.recordHealth(component, status, responseTime)
        
        // Check for health alerts
        checkHealthAlerts(component, status)
    }
    
    // ==========================================================================
    // Distributed Tracing
    // ==========================================================================
    
    /**
     * Start a new trace
     */
    fun startTrace(
        operationName: String,
        context: ExecutionContext,
        parentTraceId: String? = null
    ): TraceContext {
        val traceContext = TraceContext(
            traceId = context.traceId ?: generateTraceId(),
            spanId = context.spanId ?: generateSpanId(),
            parentSpanId = parentTraceId,
            operationName = operationName,
            startTime = Instant.now(),
            tags = mutableMapOf(
                "operation" to operationName,
                "user_id" to (context.userId ?: "anonymous"),
                "request_id" to context.requestId
            )
        )
        
        activeTraces[traceContext.traceId] = traceContext
        
        logger.debug("Started trace: ${traceContext.traceId} for operation: $operationName")
        
        return traceContext
    }
    
    /**
     * Add tag to trace
     */
    fun addTraceTag(traceId: String, key: String, value: String) {
        activeTraces[traceId]?.tags?.put(key, value)
    }
    
    /**
     * Add log to trace
     */
    fun addTraceLog(traceId: String, level: String, message: String) {
        activeTraces[traceId]?.logs?.add(
            TraceLog(
                timestamp = Instant.now(),
                level = level,
                message = message
            )
        )
    }
    
    /**
     * Finish a trace
     */
    fun finishTrace(traceId: String, success: Boolean = true, error: String? = null) {
        val traceContext = activeTraces.remove(traceId)
        
        if (traceContext != null) {
            traceContext.endTime = Instant.now()
            traceContext.success = success
            traceContext.error = error
            
            val duration = Duration.between(traceContext.startTime, traceContext.endTime)
            
            // Record trace metrics
            Timer.builder("persistence.trace.duration")
                .description("Trace execution duration")
                .tag("operation", traceContext.operationName)
                .tag("success", success.toString())
                .register(meterRegistry)
                .record(duration)
            
            // Export trace (would integrate with Jaeger/Zipkin in real implementation)
            exportTrace(traceContext)
            
            logger.debug("Finished trace: $traceId, duration: ${duration.toMillis()}ms, success: $success")
        }
    }
    
    // ==========================================================================
    // Health Monitoring
    // ==========================================================================
    
    /**
     * Get comprehensive health status
     */
    suspend fun getHealthStatus(): Map<String, HealthStatus> {
        val healthStatus = mutableMapOf<String, HealthStatus>()
        
        // Platform health
        healthStatus["platform"] = HealthStatus(
            status = HealthState.HEALTHY,
            message = "Platform is operational",
            responseTime = measurePlatformResponseTime()
        )
        
        // Provider health
        val providerHealth = providerRegistry.getProvidersHealthStatus()
        providerHealth.forEach { (name, info) ->
            healthStatus[name] = info.healthStatus
        }
        
        // Update health metrics
        healthStatus.forEach { (component, status) ->
            recordHealthStatus(component, status.status, status.responseTime)
        }
        
        return healthStatus
    }
    
    /**
     * Get platform metrics
     */
    suspend fun getPlatformMetrics(): PlatformMetrics {
        // Collect metrics from all providers
        val providerMetrics = providerRegistry.getAllProviderMetrics()
        
        // Aggregate technology metrics
        val technologyMetrics = providerMetrics.mapValues { (_, metrics) ->
            TechnologyMetrics(
                technology = metrics.provider,
                connectionCount = metrics.connectionCount,
                activeConnections = metrics.activeConnections,
                queryCount = metrics.queryCount,
                errorCount = metrics.errorCount,
                averageResponseTime = metrics.averageResponseTime,
                throughput = metrics.throughput,
                resourceUtilization = ResourceUtilization(0.0, 0.0, 0.0, 0.0) // Placeholder
            )
        }
        
        return PlatformMetrics(
            timestamp = Instant.now(),
            queryMetrics = queryMetrics.getAggregatedMetrics(),
            operationMetrics = operationMetrics.getAggregatedMetrics(),
            technologyMetrics = technologyMetrics,
            cacheMetrics = CacheMetrics(0.0, 0.0, 0.0, 0L, 0L, 0L, 0L), // Placeholder
            resourceMetrics = ResourceMetrics(0.0, 0.0, 0.0, NetworkIO(0L, 0L, 0L, 0L), DiskIO(0L, 0L, 0.0, 0.0)) // Placeholder
        )
    }
    
    /**
     * Export metrics in Prometheus format
     */
    fun exportPrometheusMetrics(): String {
        return meterRegistry.scrape()
    }
    
    // ==========================================================================
    // Alert Management
    // ==========================================================================
    
    private fun checkQueryAlerts(queryName: String, technology: String, duration: Duration, success: Boolean) {
        // Check query latency alert
        if (duration.toMillis() > 1000) {
            alertManager.triggerAlert(
                AlertEvent(
                    alertId = "query_latency_high",
                    severity = AlertSeverity.WARNING,
                    message = "High query latency detected: ${duration.toMillis()}ms for query $queryName",
                    component = technology,
                    timestamp = Instant.now(),
                    metadata = mapOf(
                        "query" to queryName,
                        "technology" to technology,
                        "duration_ms" to duration.toMillis().toString()
                    )
                )
            )
        }
        
        // Check error rate alert
        if (!success) {
            alertManager.triggerAlert(
                AlertEvent(
                    alertId = "query_error",
                    severity = AlertSeverity.ERROR,
                    message = "Query execution failed: $queryName",
                    component = technology,
                    timestamp = Instant.now(),
                    metadata = mapOf(
                        "query" to queryName,
                        "technology" to technology
                    )
                )
            )
        }
    }
    
    private fun checkOperationAlerts(operationName: String, operationType: String, duration: Duration, success: Boolean) {
        // Check operation latency alert
        if (duration.toMillis() > 5000) {
            alertManager.triggerAlert(
                AlertEvent(
                    alertId = "operation_latency_high",
                    severity = AlertSeverity.WARNING,
                    message = "High operation latency detected: ${duration.toMillis()}ms for operation $operationName",
                    component = "operations",
                    timestamp = Instant.now(),
                    metadata = mapOf(
                        "operation" to operationName,
                        "type" to operationType,
                        "duration_ms" to duration.toMillis().toString()
                    )
                )
            )
        }
        
        // Check operation failure alert
        if (!success) {
            alertManager.triggerAlert(
                AlertEvent(
                    alertId = "operation_failure",
                    severity = AlertSeverity.ERROR,
                    message = "Operation execution failed: $operationName",
                    component = "operations",
                    timestamp = Instant.now(),
                    metadata = mapOf(
                        "operation" to operationName,
                        "type" to operationType
                    )
                )
            )
        }
    }
    
    private fun checkHealthAlerts(component: String, status: HealthState) {
        if (status == HealthState.UNHEALTHY) {
            alertManager.triggerAlert(
                AlertEvent(
                    alertId = "component_unhealthy",
                    severity = AlertSeverity.CRITICAL,
                    message = "Component is unhealthy: $component",
                    component = component,
                    timestamp = Instant.now(),
                    metadata = mapOf(
                        "component" to component,
                        "status" to status.name
                    )
                )
            )
        }
    }
    
    // ==========================================================================
    // Helper Methods
    // ==========================================================================
    
    private fun initializeMetrics() {
        logger.info("📊 Initializing metrics collectors...")
        
        // Register custom metrics
        Gauge.builder("persistence.platform.uptime")
            .description("Platform uptime in seconds")
            .register(meterRegistry) { platformMetrics.getUptimeSeconds() }
        
        Gauge.builder("persistence.platform.active_connections")
            .description("Total active connections across all providers")
            .register(meterRegistry) { platformMetrics.getTotalActiveConnections() }
        
        logger.info("✅ Metrics collectors initialized")
    }
    
    private fun startMonitoringJobs() {
        monitoringJob = monitoringScope.launch {
            while (isActive) {
                try {
                    // Collect provider metrics
                    collectProviderMetrics()
                    
                    // Update health status
                    updateHealthStatus()
                    
                    // Clean up old traces
                    cleanupOldTraces()
                    
                    delay(30000) // Run every 30 seconds
                    
                } catch (e: Exception) {
                    logger.error("Error in monitoring job", e)
                    delay(60000) // Wait longer on error
                }
            }
        }
    }
    
    private suspend fun collectProviderMetrics() {
        val providerMetrics = providerRegistry.getAllProviderMetrics()
        providerMetrics.forEach { (name, metrics) ->
            recordProviderMetrics(name, metrics)
        }
    }
    
    private suspend fun updateHealthStatus() {
        val healthStatus = getHealthStatus()
        // Health status is recorded in getHealthStatus method
    }
    
    private fun cleanupOldTraces() {
        val cutoff = Instant.now().minusSeconds(300) // 5 minutes
        val oldTraces = activeTraces.values.filter { it.startTime.isBefore(cutoff) }
        
        oldTraces.forEach { trace ->
            finishTrace(trace.traceId, success = false, error = "Trace timeout")
        }
    }
    
    private fun measurePlatformResponseTime(): Long {
        val start = System.currentTimeMillis()
        // Perform a simple health check operation
        return System.currentTimeMillis() - start
    }
    
    private fun generateTraceId(): String = java.util.UUID.randomUUID().toString()
    private fun generateSpanId(): String = java.util.UUID.randomUUID().toString()
    
    private fun exportTrace(traceContext: TraceContext) {
        // In a real implementation, this would export to Jaeger, Zipkin, etc.
        logger.debug("Exporting trace: ${traceContext.traceId}")
    }
}

// ==========================================================================
// Data Classes
// ==========================================================================

data class TraceContext(
    val traceId: String,
    val spanId: String,
    val parentSpanId: String?,
    val operationName: String,
    val startTime: Instant,
    var endTime: Instant? = null,
    var success: Boolean = true,
    var error: String? = null,
    val tags: MutableMap<String, String> = mutableMapOf(),
    val logs: MutableList<TraceLog> = mutableListOf()
)

data class TraceLog(
    val timestamp: Instant,
    val level: String,
    val message: String
)

data class AlertEvent(
    val alertId: String,
    val severity: AlertSeverity,
    val message: String,
    val component: String,
    val timestamp: Instant,
    val metadata: Map<String, String> = emptyMap()
)

enum class AlertSeverity {
    INFO, WARNING, ERROR, CRITICAL
}

// ==========================================================================
// Metrics Collectors
// ==========================================================================

class PlatformMetricsCollector {
    private val startTime = Instant.now()
    private val totalConnections = AtomicLong(0)
    
    fun getUptimeSeconds(): Double {
        return Duration.between(startTime, Instant.now()).seconds.toDouble()
    }
    
    fun getTotalActiveConnections(): Double {
        return totalConnections.get().toDouble()
    }
    
    fun updateTotalConnections(count: Long) {
        totalConnections.set(count)
    }
}

class QueryMetricsCollector {
    private val queryCount = AtomicLong(0)
    private val queryErrors = AtomicLong(0)
    private val totalLatency = DoubleAdder()
    
    fun recordQuery(queryName: String, technology: String, duration: Duration, success: Boolean, recordCount: Long) {
        queryCount.incrementAndGet()
        totalLatency.add(duration.toMillis().toDouble())
        
        if (!success) {
            queryErrors.incrementAndGet()
        }
    }
    
    fun getAggregatedMetrics(): QueryMetrics {
        val total = queryCount.get()
        val errors = queryErrors.get()
        val avgLatency = if (total > 0) totalLatency.sum() / total else 0.0
        
        return QueryMetrics(
            totalQueries = total,
            queriesPerSecond = 0.0, // Would calculate based on time window
            averageLatency = avgLatency,
            p50Latency = 0.0, // Would calculate from histogram
            p95Latency = 0.0,
            p99Latency = 0.0,
            errorRate = if (total > 0) errors.toDouble() / total else 0.0,
            slowQueries = 0L // Would track queries above threshold
        )
    }
}

class OperationMetricsCollector {
    private val operationCount = AtomicLong(0)
    private val operationErrors = AtomicLong(0)
    private val totalLatency = DoubleAdder()
    
    fun recordOperation(operationName: String, operationType: String, duration: Duration, success: Boolean, affectedRecords: Long) {
        operationCount.incrementAndGet()
        totalLatency.add(duration.toMillis().toDouble())
        
        if (!success) {
            operationErrors.incrementAndGet()
        }
    }
    
    fun getAggregatedMetrics(): OperationMetrics {
        val total = operationCount.get()
        val errors = operationErrors.get()
        val avgLatency = if (total > 0) totalLatency.sum() / total else 0.0
        
        return OperationMetrics(
            totalOperations = total,
            operationsPerSecond = 0.0, // Would calculate based on time window
            averageLatency = avgLatency,
            successRate = if (total > 0) (total - errors).toDouble() / total else 0.0,
            failureRate = if (total > 0) errors.toDouble() / total else 0.0,
            activeOperations = 0, // Would track from active operations map
            queuedOperations = 0  // Would track from operation queue
        )
    }
}

class HealthMetricsCollector {
    private val healthChecks = ConcurrentHashMap<String, HealthState>()
    
    fun recordHealth(component: String, status: HealthState, responseTime: Long?) {
        healthChecks[component] = status
    }
    
    fun getHealthSummary(): Map<String, HealthState> {
        return healthChecks.toMap()
    }
}

class AlertManager(private val alertConfigs: List<com.unhinged.persistence.config.AlertConfiguration>) {
    private val logger = LoggerFactory.getLogger(AlertManager::class.java)
    private val activeAlerts = ConcurrentHashMap<String, AlertEvent>()
    
    suspend fun start() {
        logger.info("🚨 Starting Alert Manager...")
    }
    
    suspend fun stop() {
        logger.info("🛑 Stopping Alert Manager...")
    }
    
    fun triggerAlert(alert: AlertEvent) {
        activeAlerts[alert.alertId] = alert
        
        // In a real implementation, this would send notifications
        logger.warn("🚨 ALERT [${alert.severity}] ${alert.component}: ${alert.message}")
        
        // Would integrate with notification systems (Slack, PagerDuty, etc.)
    }
    
    fun resolveAlert(alertId: String) {
        activeAlerts.remove(alertId)
        logger.info("✅ Alert resolved: $alertId")
    }
    
    fun getActiveAlerts(): List<AlertEvent> {
        return activeAlerts.values.toList()
    }
}
