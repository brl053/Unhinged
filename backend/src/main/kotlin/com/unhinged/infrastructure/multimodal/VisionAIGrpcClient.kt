// ============================================================================
// Vision AI gRPC Client - Infrastructure Layer
// ============================================================================
//
// @file VisionAIGrpcClient.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description gRPC client implementation for vision AI service
//
// This implementation communicates with the Python vision-ai service
// via gRPC for efficient binary communication and better performance.
//
// ============================================================================

package com.unhinged.infrastructure.multimodal

import com.unhinged.application.multimodal.VisionInferenceService
import com.unhinged.application.multimodal.VisionInferenceResult
import com.unhinged.application.multimodal.VisionUIElement
import com.unhinged.application.multimodal.VisionElementBounds
import com.unhinged.domain.multimodal.MultimodalProcessingException
import com.unhinged.multimodal.grpc.*
import io.grpc.ManagedChannel
import io.grpc.ManagedChannelBuilder
import io.grpc.StatusException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Component
import javax.annotation.PostConstruct
import javax.annotation.PreDestroy
import kotlin.time.Duration.Companion.seconds
import kotlin.time.toJavaDuration

// ============================================================================
// gRPC Vision AI Client
// ============================================================================

/**
 * gRPC client for Vision AI service
 * 
 * Provides efficient binary communication with the Python vision-ai service
 * for image inference operations. Implements connection pooling, health checks,
 * and proper error handling.
 */
@Component
class VisionAIGrpcClient(
    @Value("\${multimodal.vision.host:localhost}")
    private val host: String,
    @Value("\${multimodal.vision.port:50051}")
    private val port: Int,
    @Value("\${multimodal.vision.timeout-seconds:60}")
    private val timeoutSeconds: Long
) : VisionInferenceService {
    
    private lateinit var channel: ManagedChannel
    private lateinit var stub: VisionServiceGrpcKt.VisionServiceCoroutineStub
    
    @PostConstruct
    fun initialize() {
        channel = ManagedChannelBuilder.forAddress(host, port)
            .usePlaintext()
            .keepAliveTime(30, java.util.concurrent.TimeUnit.SECONDS)
            .keepAliveTimeout(5, java.util.concurrent.TimeUnit.SECONDS)
            .keepAliveWithoutCalls(true)
            .maxInboundMessageSize(16 * 1024 * 1024) // 16MB for large images
            .build()
        
        stub = VisionServiceGrpcKt.VisionServiceCoroutineStub(channel)
            .withDeadlineAfter(timeoutSeconds, java.util.concurrent.TimeUnit.SECONDS)
    }
    
    /**
     * Perform vision inference using gRPC
     */
    override suspend fun infer(
        imageData: ByteArray,
        model: String,
        prompt: String,
        analysisType: String,
        maxTokens: Int,
        temperature: Float
    ): VisionInferenceResult = withContext(Dispatchers.IO) {
        
        try {
            val request = visionInferenceRequest {
                this.imageData = com.google.protobuf.ByteString.copyFrom(imageData)
                this.model = model
                this.prompt = prompt
                this.analysisType = analysisType
                this.maxTokens = maxTokens
                this.temperature = temperature
            }
            
            val response = stub.infer(request)
            
            if (!response.success) {
                throw MultimodalProcessingException(
                    "Vision inference failed: ${response.error}"
                )
            }
            
            VisionInferenceResult(
                description = response.description,
                confidence = response.confidence,
                modelUsed = response.modelUsed,
                processingTime = response.processingTime,
                metadata = response.metadataMap,
                extractedText = response.extractedText.takeIf { it.isNotEmpty() },
                uiElements = response.uiElementsList.map { element ->
                    VisionUIElement(
                        type = element.type,
                        confidence = element.confidence,
                        bounds = element.bounds?.let { bounds ->
                            VisionElementBounds(bounds.x, bounds.y, bounds.width, bounds.height)
                        },
                        properties = element.propertiesMap
                    )
                },
                tags = response.tagsList,
                properties = mapOf(
                    "grpc_success" to response.success.toString(),
                    "response_size" to response.serializedSize.toString()
                )
            )
            
        } catch (e: StatusException) {
            throw MultimodalProcessingException(
                "gRPC vision inference failed: ${e.status.description}",
                e
            )
        } catch (e: Exception) {
            throw MultimodalProcessingException(
                "Vision inference error: ${e.message}",
                e
            )
        }
    }
    
    /**
     * Get available models from vision service
     */
    suspend fun getAvailableModels(): List<ModelInfo> = withContext(Dispatchers.IO) {
        try {
            val request = empty { }
            val response = stub.getAvailableModels(request)
            
            response.modelsList.map { model ->
                ModelInfo(
                    name = model.name,
                    displayName = model.displayName,
                    description = model.description,
                    available = model.available,
                    memoryUsageMb = model.memoryUsageMb,
                    supportedTypes = model.supportedTypesList
                )
            }
        } catch (e: StatusException) {
            throw MultimodalProcessingException(
                "Failed to get available models: ${e.status.description}",
                e
            )
        }
    }
    
    /**
     * Get model performance metrics
     */
    suspend fun getModelMetrics(model: String): ModelMetrics = withContext(Dispatchers.IO) {
        try {
            val request = modelMetricsRequest {
                this.model = model
            }
            val response = stub.getModelMetrics(request)
            
            ModelMetrics(
                model = response.model,
                totalInferences = response.totalInferences,
                averageProcessingTime = response.averageProcessingTime,
                averageConfidence = response.averageConfidence,
                memoryUsageMb = response.memoryUsageMb,
                gpuUtilization = response.gpuUtilization,
                additionalMetrics = response.additionalMetricsMap
            )
        } catch (e: StatusException) {
            throw MultimodalProcessingException(
                "Failed to get model metrics: ${e.status.description}",
                e
            )
        }
    }
    
    /**
     * Check service health
     */
    suspend fun checkHealth(): ServiceHealth = withContext(Dispatchers.IO) {
        try {
            val request = empty { }
            val response = stub.getHealth(request)
            
            ServiceHealth(
                healthy = response.healthy,
                status = response.status,
                details = response.detailsMap,
                uptimeSeconds = response.uptimeSeconds,
                version = response.version
            )
        } catch (e: StatusException) {
            ServiceHealth(
                healthy = false,
                status = "UNAVAILABLE",
                details = mapOf("error" to (e.status.description ?: "Unknown error")),
                uptimeSeconds = 0,
                version = "unknown"
            )
        }
    }
    
    @PreDestroy
    fun shutdown() {
        if (::channel.isInitialized) {
            channel.shutdown()
            try {
                if (!channel.awaitTermination(5, java.util.concurrent.TimeUnit.SECONDS)) {
                    channel.shutdownNow()
                }
            } catch (e: InterruptedException) {
                channel.shutdownNow()
                Thread.currentThread().interrupt()
            }
        }
    }
}

// ============================================================================
// Supporting Data Classes
// ============================================================================

/**
 * Model information
 */
data class ModelInfo(
    val name: String,
    val displayName: String,
    val description: String,
    val available: Boolean,
    val memoryUsageMb: Long,
    val supportedTypes: List<String>
)

/**
 * Model performance metrics
 */
data class ModelMetrics(
    val model: String,
    val totalInferences: Long,
    val averageProcessingTime: Double,
    val averageConfidence: Double,
    val memoryUsageMb: Long,
    val gpuUtilization: Double,
    val additionalMetrics: Map<String, Double>
)

/**
 * Service health information
 */
data class ServiceHealth(
    val healthy: Boolean,
    val status: String,
    val details: Map<String, String>,
    val uptimeSeconds: Long,
    val version: String
)
