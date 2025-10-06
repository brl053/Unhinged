// ============================================================================
// Context LLM gRPC Client - Infrastructure Layer
// ============================================================================
//
// @file ContextLLMGrpcClient.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description gRPC client implementation for context-aware LLM service
//
// This implementation communicates with the Python context-llm service
// via gRPC for efficient prompt generation and context search operations.
//
// ============================================================================

package com.unhinged.infrastructure.multimodal

import com.unhinged.application.multimodal.ContextLLMService
import com.unhinged.domain.multimodal.ContextItem
import com.unhinged.domain.multimodal.ContextType
import com.unhinged.domain.multimodal.MultimodalProcessingException
import com.unhinged.multimodal.grpc.*
import io.grpc.ManagedChannel
import io.grpc.ManagedChannelBuilder
import io.grpc.StatusException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Component
import java.time.Instant
import javax.annotation.PostConstruct
import javax.annotation.PreDestroy

// ============================================================================
// gRPC Context LLM Client
// ============================================================================

/**
 * gRPC client for Context-Aware LLM service
 * 
 * Provides efficient communication with the Python context-llm service
 * for prompt generation, context search, and text generation operations.
 */
@Component
class ContextLLMGrpcClient(
    @Value("\${multimodal.context.host:localhost}")
    private val host: String,
    @Value("\${multimodal.context.port:50052}")
    private val port: Int,
    @Value("\${multimodal.context.timeout-seconds:30}")
    private val timeoutSeconds: Long
) : ContextLLMService {
    
    private lateinit var channel: ManagedChannel
    private lateinit var stub: ContextServiceGrpcKt.ContextServiceCoroutineStub
    
    @PostConstruct
    fun initialize() {
        channel = ManagedChannelBuilder.forAddress(host, port)
            .usePlaintext()
            .keepAliveTime(30, java.util.concurrent.TimeUnit.SECONDS)
            .keepAliveTimeout(5, java.util.concurrent.TimeUnit.SECONDS)
            .keepAliveWithoutCalls(true)
            .maxInboundMessageSize(4 * 1024 * 1024) // 4MB for context data
            .build()
        
        stub = ContextServiceGrpcKt.ContextServiceCoroutineStub(channel)
            .withDeadlineAfter(timeoutSeconds, java.util.concurrent.TimeUnit.SECONDS)
    }
    
    /**
     * Generate enhanced prompt with project context
     */
    override suspend fun generatePrompt(
        basePrompt: String,
        analysisType: String,
        contextTypes: List<String>,
        maxContextItems: Int
    ): String = withContext(Dispatchers.IO) {
        
        try {
            val request = promptGenerationRequest {
                this.basePrompt = basePrompt
                this.analysisType = analysisType
                this.contextTypes.addAll(contextTypes)
                this.maxContextItems = maxContextItems
                this.model = "default" // Use default LLM model
                this.maxTokens = 1000
                this.temperature = 0.3f
            }
            
            val response = stub.generatePrompt(request)
            
            if (!response.success) {
                throw MultimodalProcessingException(
                    "Prompt generation failed: ${response.error}"
                )
            }
            
            response.enhancedPrompt
            
        } catch (e: StatusException) {
            throw MultimodalProcessingException(
                "gRPC prompt generation failed: ${e.status.description}",
                e
            )
        } catch (e: Exception) {
            throw MultimodalProcessingException(
                "Prompt generation error: ${e.message}",
                e
            )
        }
    }
    
    /**
     * Search project context and documentation
     */
    suspend fun searchContext(
        query: String,
        contextTypes: List<String>,
        maxResults: Int = 10,
        minRelevance: Float = 0.0f
    ): List<ContextItem> = withContext(Dispatchers.IO) {
        
        try {
            val request = contextSearchRequest {
                this.query = query
                this.contextTypes.addAll(contextTypes)
                this.maxResults = maxResults
                this.minRelevance = minRelevance
            }
            
            val response = stub.searchContext(request)
            
            response.resultsList.map { item ->
                ContextItem(
                    id = item.id,
                    type = ContextType.valueOf(item.type.uppercase()),
                    title = item.title,
                    content = item.content,
                    filePath = item.filePath,
                    tags = item.tagsList,
                    relevanceScore = item.relevanceScore,
                    lastModified = Instant.ofEpochSecond(item.lastModified)
                )
            }
            
        } catch (e: StatusException) {
            throw MultimodalProcessingException(
                "gRPC context search failed: ${e.status.description}",
                e
            )
        } catch (e: Exception) {
            throw MultimodalProcessingException(
                "Context search error: ${e.message}",
                e
            )
        }
    }
    
    /**
     * Generate text using LLM
     */
    suspend fun generateText(
        prompt: String,
        model: String = "default",
        maxTokens: Int = 500,
        temperature: Float = 0.7f,
        topP: Float = 0.9f,
        stopSequences: List<String> = emptyList()
    ): TextGenerationResult = withContext(Dispatchers.IO) {
        
        try {
            val request = textGenerationRequest {
                this.prompt = prompt
                this.model = model
                this.maxTokens = maxTokens
                this.temperature = temperature
                this.topP = topP
                this.stopSequences.addAll(stopSequences)
            }
            
            val response = stub.generateText(request)
            
            if (!response.success) {
                throw MultimodalProcessingException(
                    "Text generation failed: ${response.error}"
                )
            }
            
            TextGenerationResult(
                text = response.text,
                modelUsed = response.modelUsed,
                tokensGenerated = response.tokensGenerated,
                processingTime = response.processingTime
            )
            
        } catch (e: StatusException) {
            throw MultimodalProcessingException(
                "gRPC text generation failed: ${e.status.description}",
                e
            )
        } catch (e: Exception) {
            throw MultimodalProcessingException(
                "Text generation error: ${e.message}",
                e
            )
        }
    }
    
    /**
     * Get available LLM models
     */
    suspend fun getAvailableModels(): List<LLMModelInfo> = withContext(Dispatchers.IO) {
        try {
            val request = empty { }
            val response = stub.getAvailableModels(request)
            
            response.modelsList.map { model ->
                LLMModelInfo(
                    name = model.name,
                    displayName = model.displayName,
                    description = model.description,
                    available = model.available,
                    provider = model.provider,
                    maxTokens = model.maxTokens,
                    capabilities = model.capabilitiesList
                )
            }
        } catch (e: StatusException) {
            throw MultimodalProcessingException(
                "Failed to get available LLM models: ${e.status.description}",
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
 * Text generation result
 */
data class TextGenerationResult(
    val text: String,
    val modelUsed: String,
    val tokensGenerated: Int,
    val processingTime: Double
)

/**
 * LLM model information
 */
data class LLMModelInfo(
    val name: String,
    val displayName: String,
    val description: String,
    val available: Boolean,
    val provider: String,
    val maxTokens: Int,
    val capabilities: List<String>
)
