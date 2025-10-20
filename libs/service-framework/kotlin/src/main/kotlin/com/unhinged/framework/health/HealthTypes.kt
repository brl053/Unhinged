package com.unhinged.framework.health

import java.time.Instant

/**
 * Health status enumeration matching the protobuf definition
 */
public enum class HealthStatus {
    UNKNOWN,
    HEALTHY,
    DEGRADED,
    UNHEALTHY,
    MAINTENANCE
}

/**
 * Fast heartbeat response (< 10ms)
 */
public data class HeartbeatResponse(
    val alive: Boolean,
    val timestampMs: Long,
    val serviceId: String,
    val version: String,
    val uptimeMs: Long,
    val status: HealthStatus
)

/**
 * Detailed diagnostics request
 */
public data class DiagnosticsRequest(
    val includeMetrics: Boolean = false,
    val includeDependencies: Boolean = false,
    val includeResources: Boolean = false,
    val includeCustomChecks: Boolean = false
)

/**
 * Detailed diagnostics response
 */
public data class DiagnosticsResponse(
    val heartbeat: HeartbeatResponse,
    val dependencies: List<DependencyHealthResult> = emptyList(),
    val resources: ResourceMetrics? = null,
    val customChecks: List<CustomHealthCheckResult> = emptyList(),
    val metadata: Map<String, String> = emptyMap(),
    val lastUpdated: Instant
)

/**
 * Dependency health check result
 */
public data class DependencyHealthResult(
    val name: String,
    val type: String,
    val status: HealthStatus,
    val endpoint: String,
    val responseTimeMs: Long,
    val version: String? = null,
    val lastCheck: Instant,
    val errorMessage: String? = null
)

/**
 * Custom health check result
 */
public data class CustomHealthCheckResult(
    val name: String,
    val status: HealthStatus,
    val message: String,
    val lastCheck: Instant,
    val responseTimeMs: Long,
    val details: Map<String, String> = emptyMap()
)

/**
 * Resource metrics
 */
public data class ResourceMetrics(
    val cpu: CpuMetrics,
    val memory: MemoryMetrics,
    val disk: DiskMetrics? = null,
    val network: NetworkMetrics? = null
)

/**
 * CPU metrics
 */
public data class CpuMetrics(
    val usagePercent: Double,
    val loadAverage1m: Double,
    val coreCount: Int
)

/**
 * Memory metrics
 */
public data class MemoryMetrics(
    val usedBytes: Long,
    val totalBytes: Long,
    val usagePercent: Double,
    val heapUsedBytes: Long,
    val heapMaxBytes: Long
)

/**
 * Disk metrics
 */
public data class DiskMetrics(
    val usedBytes: Long,
    val totalBytes: Long,
    val usagePercent: Double,
    val freeBytes: Long
)

/**
 * Network metrics
 */
public data class NetworkMetrics(
    val bytesSent: Long,
    val bytesReceived: Long,
    val packetsSent: Long,
    val packetsReceived: Long,
    val activeConnections: Int
)
