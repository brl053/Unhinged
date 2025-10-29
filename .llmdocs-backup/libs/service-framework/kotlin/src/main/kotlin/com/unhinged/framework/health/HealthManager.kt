package com.unhinged.framework.health

import kotlinx.coroutines.*
import java.time.Instant
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlin.time.Duration.Companion.seconds

/**
 * Health Manager for Unhinged Service Framework
 * 
 * Provides fast heartbeat responses (< 10ms) and detailed diagnostics (< 1s).
 * Implements caching and background health checking for optimal performance.
 */
public class HealthManager(
    private val serviceId: String,
    private val version: String,
    private val scope: CoroutineScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
) {
    
    private val startTime = System.currentTimeMillis()
    private val lastHeartbeat = AtomicReference(System.currentTimeMillis())
    private val healthStatus = AtomicReference(HealthStatus.HEALTHY)
    private val customChecks = ConcurrentHashMap<String, HealthCheck>()
    private val dependencies = ConcurrentHashMap<String, DependencyHealth>()
    
    // Cached heartbeat response for ultra-fast responses
    private val cachedHeartbeat = AtomicReference<HeartbeatResponse?>(null)
    private val heartbeatCacheTime = AtomicLong(0)
    private val heartbeatCacheTtl = 1000L // 1 second TTL
    
    init {
        // Start background health monitoring
        startBackgroundMonitoring()
        updateCachedHeartbeat()
    }
    
    /**
     * Fast heartbeat response (< 10ms)
     * Returns cached vitals for minimal latency
     */
    public fun getHeartbeat(): HeartbeatResponse {
        val now = System.currentTimeMillis()
        
        // Return cached response if still valid
        if (now - heartbeatCacheTime.get() < heartbeatCacheTtl) {
            cachedHeartbeat.get()?.let { return it }
        }
        
        // Update cache and return
        updateCachedHeartbeat()
        return cachedHeartbeat.get() ?: createHeartbeatResponse()
    }
    
    /**
     * Detailed diagnostics (< 1s)
     * Performs real-time health checks
     */
    public suspend fun getDiagnostics(request: DiagnosticsRequest): DiagnosticsResponse {
        val heartbeat = getHeartbeat()
        
        return DiagnosticsResponse(
            heartbeat = heartbeat,
            dependencies = if (request.includeDependencies) {
                checkDependencies()
            } else emptyList(),
            resources = if (request.includeResources) {
                collectResourceMetrics()
            } else null,
            customChecks = if (request.includeCustomChecks) {
                runCustomChecks()
            } else emptyList(),
            metadata = collectMetadata(),
            lastUpdated = Instant.now()
        )
    }
    
    /**
     * Register a custom health check
     */
    public fun registerHealthCheck(name: String, check: suspend () -> HealthCheckResult) {
        customChecks[name] = HealthCheck(name, check)
    }
    
    /**
     * Register a dependency for health monitoring
     */
    public fun registerDependency(
        name: String,
        type: String,
        endpoint: String,
        checker: suspend () -> DependencyCheckResult
    ) {
        dependencies[name] = DependencyHealth(name, type, endpoint, checker)
    }
    
    /**
     * Update overall service health status
     */
    public fun updateHealthStatus(status: HealthStatus) {
        healthStatus.set(status)
        updateCachedHeartbeat()
    }
    
    private fun updateCachedHeartbeat() {
        val now = System.currentTimeMillis()
        lastHeartbeat.set(now)
        
        val response = createHeartbeatResponse()
        cachedHeartbeat.set(response)
        heartbeatCacheTime.set(now)
    }
    
    private fun createHeartbeatResponse(): HeartbeatResponse {
        val now = System.currentTimeMillis()
        return HeartbeatResponse(
            alive = true,
            timestampMs = now,
            serviceId = serviceId,
            version = version,
            uptimeMs = now - startTime,
            status = healthStatus.get()
        )
    }
    
    private suspend fun checkDependencies(): List<DependencyHealthResult> {
        return dependencies.values.map { dep ->
            try {
                val result = withTimeout(5.seconds) {
                    dep.checker()
                }
                DependencyHealthResult(
                    name = dep.name,
                    type = dep.type,
                    status = if (result.healthy) HealthStatus.HEALTHY else HealthStatus.UNHEALTHY,
                    endpoint = dep.endpoint,
                    responseTimeMs = result.responseTimeMs,
                    version = result.version,
                    lastCheck = Instant.now(),
                    errorMessage = result.errorMessage
                )
            } catch (e: Exception) {
                DependencyHealthResult(
                    name = dep.name,
                    type = dep.type,
                    status = HealthStatus.UNHEALTHY,
                    endpoint = dep.endpoint,
                    responseTimeMs = 0,
                    version = null,
                    lastCheck = Instant.now(),
                    errorMessage = e.message ?: "Unknown error"
                )
            }
        }
    }
    
    private suspend fun runCustomChecks(): List<CustomHealthCheckResult> {
        return customChecks.values.map { check ->
            try {
                val result = withTimeout(10.seconds) {
                    check.checker()
                }
                CustomHealthCheckResult(
                    name = check.name,
                    status = if (result.healthy) HealthStatus.HEALTHY else HealthStatus.UNHEALTHY,
                    message = result.message,
                    lastCheck = Instant.now(),
                    responseTimeMs = result.responseTimeMs,
                    details = result.details
                )
            } catch (e: Exception) {
                CustomHealthCheckResult(
                    name = check.name,
                    status = HealthStatus.UNHEALTHY,
                    message = e.message ?: "Check failed",
                    lastCheck = Instant.now(),
                    responseTimeMs = 0,
                    details = emptyMap()
                )
            }
        }
    }
    
    private fun collectResourceMetrics(): ResourceMetrics {
        val runtime = Runtime.getRuntime()
        val totalMemory = runtime.totalMemory()
        val freeMemory = runtime.freeMemory()
        val usedMemory = totalMemory - freeMemory
        val maxMemory = runtime.maxMemory()
        
        return ResourceMetrics(
            cpu = CpuMetrics(
                usagePercent = 0.0, // TODO: Implement CPU monitoring
                loadAverage1m = 0.0,
                coreCount = runtime.availableProcessors()
            ),
            memory = MemoryMetrics(
                usedBytes = usedMemory,
                totalBytes = totalMemory,
                usagePercent = (usedMemory.toDouble() / totalMemory.toDouble()) * 100.0,
                heapUsedBytes = usedMemory,
                heapMaxBytes = maxMemory
            ),
            disk = null, // TODO: Implement disk monitoring
            network = null // TODO: Implement network monitoring
        )
    }
    
    private fun collectMetadata(): Map<String, String> {
        return mapOf(
            "jvm.version" to System.getProperty("java.version"),
            "jvm.vendor" to System.getProperty("java.vendor"),
            "os.name" to System.getProperty("os.name"),
            "os.arch" to System.getProperty("os.arch"),
            "start.time" to Instant.ofEpochMilli(startTime).toString()
        )
    }
    
    private fun startBackgroundMonitoring() {
        scope.launch {
            while (isActive) {
                delay(30.seconds)
                
                // Update cached heartbeat periodically
                updateCachedHeartbeat()
                
                // TODO: Run background dependency checks
                // TODO: Update overall health status based on checks
            }
        }
    }
    
    public fun shutdown() {
        scope.cancel()
    }
}

// Data classes for health checking
private data class HealthCheck(
    val name: String,
    val checker: suspend () -> HealthCheckResult
)

private data class DependencyHealth(
    val name: String,
    val type: String,
    val endpoint: String,
    val checker: suspend () -> DependencyCheckResult
)

// Result classes
public data class HealthCheckResult(
    val healthy: Boolean,
    val message: String,
    val responseTimeMs: Long = 0,
    val details: Map<String, String> = emptyMap()
)

public data class DependencyCheckResult(
    val healthy: Boolean,
    val responseTimeMs: Long,
    val version: String? = null,
    val errorMessage: String? = null
)
