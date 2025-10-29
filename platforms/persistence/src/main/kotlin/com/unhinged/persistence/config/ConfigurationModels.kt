// ============================================================================
// Persistence Platform - Configuration Models
// ============================================================================
//
// @file ConfigurationModels.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-10-19
// @description Configuration data models for the persistence platform
//
// This file contains all configuration-related data structures that map
// to the YAML configuration file and provide type-safe access to
// persistence platform settings.
//
// ============================================================================

package com.unhinged.persistence.config

import com.unhinged.persistence.core.TechnologyType
import java.time.Duration

// ==========================================================================
// Main Configuration
// ==========================================================================

/*
 * @llm-type model.config
 * @llm-does main persistence platform configuration loaded from yaml
 * @llm-rule configuration must be validated before platform initialization
 */
data class PersistenceConfiguration(
    val version: String,
    val technologies: Map<String, TechnologyConfiguration>,
    val databases: Map<String, DatabaseConfiguration>,
    val tables: Map<String, TableConfiguration>,
    val queries: Map<String, QueryConfiguration>,
    val operations: Map<String, OperationConfiguration>,
    val routing: Map<String, RoutingConfiguration>,
    val sharding: ShardingConfiguration,
    val lifecycle: LifecycleConfiguration,
    val api: ApiConfiguration,
    val aiMlIntegration: AiMlConfiguration,
    val monitoring: MonitoringConfiguration,
    val environments: Map<String, EnvironmentConfiguration>
)

// ==========================================================================
// Technology Configuration
// ==========================================================================

data class TechnologyConfiguration(
    val type: TechnologyType,
    val clusters: List<String>,
    val useCases: List<String>,
    val connectionConfig: ConnectionConfiguration,
    val performanceConfig: PerformanceConfiguration,
    val securityConfig: SecurityConfiguration? = null,
    val customProperties: Map<String, Any> = emptyMap()
)

data class ConnectionConfiguration(
    val hosts: List<String>,
    val port: Int,
    val database: String? = null,
    val username: String? = null,
    val password: String? = null,
    val connectionPool: ConnectionPoolConfiguration,
    val ssl: SslConfiguration? = null,
    val timeout: Duration = Duration.ofSeconds(30)
)

data class ConnectionPoolConfiguration(
    val minSize: Int = 2,
    val maxSize: Int = 10,
    val maxIdleTime: Duration = Duration.ofMinutes(10),
    val maxLifetime: Duration = Duration.ofMinutes(30),
    val validationQuery: String? = null
)

data class SslConfiguration(
    val enabled: Boolean = false,
    val trustStore: String? = null,
    val keyStore: String? = null,
    val verifyHostname: Boolean = true
)

data class PerformanceConfiguration(
    val defaultTtl: Duration? = null,
    val maxMemoryPolicy: String? = null,
    val defaultReplication: Int = 1,
    val consistencyLevel: String = "eventual",
    val compactionStrategy: String? = null,
    val vectorDimensions: List<Int> = emptyList(),
    val distanceMetrics: List<String> = emptyList(),
    val defaultShards: Int = 1,
    val defaultReplicas: Int = 0
)

data class SecurityConfiguration(
    val authentication: AuthenticationConfiguration,
    val authorization: AuthorizationConfiguration? = null,
    val encryption: EncryptionConfiguration? = null
)

data class AuthenticationConfiguration(
    val type: String, // "basic", "jwt", "oauth", "certificate"
    val properties: Map<String, Any> = emptyMap()
)

data class AuthorizationConfiguration(
    val type: String, // "rbac", "abac", "acl"
    val properties: Map<String, Any> = emptyMap()
)

data class EncryptionConfiguration(
    val atRest: Boolean = false,
    val inTransit: Boolean = true,
    val keyManagement: String? = null
)

// ==========================================================================
// Database and Table Configuration
// ==========================================================================

data class DatabaseConfiguration(
    val primaryTechnology: String,
    val backupTechnology: String? = null,
    val retentionPolicy: String? = null,
    val useCase: String,
    val schemaValidation: String = "strict",
    val customProperties: Map<String, Any> = emptyMap()
)

data class TableConfiguration(
    val database: String,
    val technology: String,
    val schema: Map<String, FieldConfiguration>,
    val accessPatterns: List<AccessPattern>,
    val vectorConfig: VectorConfiguration? = null,
    val indexConfig: IndexConfiguration? = null,
    val partitionConfig: PartitionConfiguration? = null
)

data class FieldConfiguration(
    val type: String,
    val primaryKey: Boolean = false,
    val unique: Boolean = false,
    val indexed: Boolean = false,
    val nullable: Boolean = true,
    val encrypted: Boolean = false,
    val defaultValue: Any? = null,
    val validation: FieldValidation? = null
)

data class FieldValidation(
    val required: Boolean = false,
    val minLength: Int? = null,
    val maxLength: Int? = null,
    val pattern: String? = null,
    val customValidator: String? = null
)

data class AccessPattern(
    val type: String,
    val fields: List<String> = emptyList(),
    val threshold: Float? = null,
    val limit: Int? = null,
    val weights: Map<String, Float> = emptyMap()
)

data class VectorConfiguration(
    val model: String,
    val dimensions: Int,
    val distanceMetric: String = "cosine",
    val indexType: String = "hnsw"
)

data class IndexConfiguration(
    val indexes: List<IndexDefinition> = emptyList(),
    val autoIndex: Boolean = true
)

data class IndexDefinition(
    val name: String,
    val fields: List<String>,
    val type: String = "btree",
    val unique: Boolean = false,
    val sparse: Boolean = false
)

data class PartitionConfiguration(
    val strategy: String, // "time_based", "hash_based", "range_based"
    val partitionKey: String,
    val partitionCount: Int? = null,
    val partitionInterval: String? = null
)

// ==========================================================================
// Query and Operation Configuration
// ==========================================================================

data class QueryConfiguration(
    val table: String? = null,
    val tables: List<String> = emptyList(),
    val type: String,
    val parameters: List<String>,
    val cacheStrategy: String = "none",
    val cacheTtl: Duration? = null,
    val security: String? = null,
    val indexes: List<String> = emptyList(),
    val distanceMetric: String? = null,
    val aggregations: List<String> = emptyList()
)

data class OperationConfiguration(
    val type: String,
    val table: String? = null,
    val steps: List<OperationStepConfiguration> = emptyList(),
    val rollbackStrategy: String = "compensating_transactions",
    val timeout: Duration? = null,
    val retryPolicy: RetryPolicyConfiguration? = null,
    val async: Boolean = false,
    val batchSize: Int? = null,
    val sideEffects: List<SideEffectConfiguration> = emptyList(),
    val conditions: List<String> = emptyList(),
    val cascade: List<CascadeConfiguration> = emptyList(),
    val compliance: String? = null
)

data class OperationStepConfiguration(
    val table: String? = null,
    val operation: String,
    val technology: String? = null,
    val service: String? = null
)

data class SideEffectConfiguration(
    val operation: String,
    val technology: String? = null,
    val service: String? = null
)

data class CascadeConfiguration(
    val operation: String,
    val technology: String
)

data class RetryPolicyConfiguration(
    val maxRetries: Int = 3,
    val backoffStrategy: String = "exponential_backoff",
    val initialDelay: Duration = Duration.ofSeconds(1),
    val maxDelay: Duration = Duration.ofSeconds(30)
)

// ==========================================================================
// Routing and Lifecycle Configuration
// ==========================================================================

data class RoutingConfiguration(
    val criteria: String,
    val technologies: List<String>,
    val priority: String
)

data class ShardingConfiguration(
    val strategies: Map<String, ShardingStrategy>,
    val rebalancing: RebalancingConfiguration? = null
)

data class ShardingStrategy(
    val shardKey: String,
    val shardCount: Int? = null,
    val shardInterval: String? = null,
    val hashFunction: String? = null,
    val retentionPolicy: String? = null,
    val regions: List<String> = emptyList()
)

data class RebalancingConfiguration(
    val autoRebalance: Boolean = true,
    val threshold: String = "80%",
    val strategy: String = "gradual_migration",
    val maintenanceWindow: String? = null
)

data class LifecycleConfiguration(
    val policies: Map<String, LifecyclePolicy>,
    val automation: LifecycleAutomation
)

data class LifecyclePolicy(
    val appliesTo: List<String>,
    val rules: List<LifecycleRule>,
    val compliance: String? = null
)

data class LifecycleRule(
    val age: String? = null,
    val condition: String? = null,
    val action: String
)

data class LifecycleAutomation(
    val schedule: String,
    val batchSize: Int = 10000,
    val parallelWorkers: Int = 4,
    val monitoring: String = "enabled"
)

// ==========================================================================
// API and Monitoring Configuration
// ==========================================================================

data class ApiConfiguration(
    val endpoints: Map<String, EndpointConfiguration>,
    val protocols: ProtocolConfiguration,
    val security: ApiSecurityConfiguration
)

data class EndpointConfiguration(
    val operations: List<String>,
    val rateLimit: String,
    val authentication: String,
    val authorization: String? = null,
    val caching: String? = null,
    val cacheTtl: Duration? = null
)

data class ProtocolConfiguration(
    val rest: RestConfiguration,
    val grpc: GrpcConfiguration,
    val graphql: GraphqlConfiguration? = null
)

data class RestConfiguration(
    val enabled: Boolean = true,
    val port: Int = 8090,
    val basePath: String = "/api/v1"
)

data class GrpcConfiguration(
    val enabled: Boolean = true,
    val port: Int = 9090,
    val reflection: Boolean = true
)

data class GraphqlConfiguration(
    val enabled: Boolean = false,
    val port: Int = 8091,
    val playground: Boolean = true
)

data class ApiSecurityConfiguration(
    val authentication: AuthenticationConfiguration,
    val authorization: AuthorizationConfiguration? = null,
    val rateLimiting: RateLimitingConfiguration,
    val cors: CorsConfiguration
)

data class RateLimitingConfiguration(
    val enabled: Boolean = true,
    val storage: String = "redis"
)

data class CorsConfiguration(
    val enabled: Boolean = true,
    val allowedOrigins: List<String> = emptyList()
)

data class AiMlConfiguration(
    val embeddingModels: Map<String, EmbeddingModelConfiguration>,
    val vectorOperations: VectorOperationsConfiguration,
    val modelServing: ModelServingConfiguration
)

data class EmbeddingModelConfiguration(
    val model: String,
    val dimensions: Int,
    val useCases: List<String>
)

data class VectorOperationsConfiguration(
    val defaultLimit: Int = 10,
    val defaultThreshold: Float = 0.7f,
    val maxLimit: Int = 100
)

data class ModelServingConfiguration(
    val embeddingService: ServiceConfiguration,
    val recommendationService: ServiceConfiguration
)

data class ServiceConfiguration(
    val endpoint: String,
    val timeout: Duration = Duration.ofSeconds(5),
    val retryAttempts: Int = 3,
    val batchSize: Int? = null
)

data class MonitoringConfiguration(
    val metrics: List<String>,
    val technologySpecificMetrics: Map<String, List<String>>,
    val alerts: List<AlertConfiguration>,
    val dashboards: List<String>,
    val logging: LoggingConfiguration,
    val tracing: TracingConfiguration,
    val healthChecks: HealthCheckConfiguration
)

data class AlertConfiguration(
    val condition: String,
    val severity: String
)

data class LoggingConfiguration(
    val level: String = "INFO",
    val format: String = "json",
    val destinations: List<String> = listOf("stdout")
)

data class TracingConfiguration(
    val enabled: Boolean = true,
    val samplingRate: Float = 0.1f,
    val exporter: String = "jaeger"
)

data class HealthCheckConfiguration(
    val interval: Duration = Duration.ofSeconds(30),
    val timeout: Duration = Duration.ofSeconds(10),
    val endpoints: List<String> = listOf("/health", "/ready", "/metrics")
)

data class EnvironmentConfiguration(
    val technologies: Map<String, EnvironmentTechnologyConfiguration>
)

data class EnvironmentTechnologyConfiguration(
    val replicas: Int = 1,
    val memory: String = "1GB",
    val cpu: String? = null,
    val storage: String? = null
)
