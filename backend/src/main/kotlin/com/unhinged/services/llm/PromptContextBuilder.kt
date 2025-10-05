// ============================================================================
// PromptContextBuilder - LLM-Native Domain Service
// ============================================================================
// 
// @file PromptContextBuilder.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-04
// @description Domain service for building optimized LLM prompt contexts
// 
// This service encapsulates LLM-specific business logic for:
// - Context window management and token optimization
// - Prompt template construction with dynamic content
// - Session context aggregation for conversation continuity
// - Semantic relevance scoring for document selection
// - Token counting and estimation across different models
// 
// Following Domain-Driven Design principles:
// - Pure business logic for LLM prompt construction
// - No infrastructure concerns (no gRPC, no database)
// - Composable and testable domain operations
// ============================================================================

package com.unhinged.services.llm

import com.unhinged.di.SessionContextOptimizer
import com.unhinged.services.documentstore.mappers.DocumentMapper
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.slf4j.LoggerFactory
import java.time.Instant

/**
 * Domain service for LLM prompt context construction
 * 
 * Handles the complex business logic of building optimal prompts
 * for LLM interactions, including context window management,
 * document relevance scoring, and token optimization.
 * 
 * @param sessionContextOptimizer Document optimization for context windows
 * @param tokenCounter Token counting service for different LLM models
 * 
 * @since 1.0.0
 * @author Unhinged Team
 */
class PromptContextBuilder(
    private val sessionContextOptimizer: SessionContextOptimizer,
    private val tokenCounter: TokenCounter
) {
    
    private val logger = LoggerFactory.getLogger(PromptContextBuilder::class.java)

    // ========================================================================
    // Core Domain Operations
    // ========================================================================

    /**
     * Build optimized prompt context for LLM interaction
     * 
     * This is the main domain operation that coordinates:
     * - System prompt preparation
     * - User message processing
     * - Document context optimization
     * - Token budget management
     * - Final prompt assembly
     * 
     * @param request Context building request with all parameters
     * @return Complete prompt context ready for LLM submission
     */
    suspend fun buildPromptContext(request: PromptContextRequest): PromptContextResult {
        return withContext(Dispatchers.Default) {
            try {
                logger.info("Building prompt context for session ${request.sessionId}")
                
                // 1. Calculate base token usage
                val systemTokens = tokenCounter.countTokens(request.systemPrompt, request.modelType)
                val userTokens = tokenCounter.countTokens(request.userMessage, request.modelType)
                val baseTokens = systemTokens + userTokens
                
                logger.debug("Base tokens: system=$systemTokens, user=$userTokens, total=$baseTokens")
                
                // 2. Calculate available tokens for context
                val availableForContext = request.maxTokens - baseTokens - request.responseTokenBuffer
                
                if (availableForContext <= 0) {
                    return@withContext PromptContextResult.failure(
                        error = "No tokens available for context (base: $baseTokens, max: ${request.maxTokens})",
                        request = request
                    )
                }
                
                // 3. Optimize document context within token budget
                val optimizedDocuments = sessionContextOptimizer.optimizeContextForPrompt(
                    documents = request.documents.map { it.toProto() }, // TODO: Fix domain/proto mixing
                    maxTokens = availableForContext
                )
                
                val contextTokens = optimizedDocuments.sumOf { 
                    tokenCounter.countTokens(it.bodyJson, request.modelType) 
                }
                
                // 4. Build final prompt context
                val promptContext = assemblePromptContext(
                    systemPrompt = request.systemPrompt,
                    userMessage = request.userMessage,
                    documents = optimizedDocuments.map { DocumentMapper.toDomain(it) },
                    contextTemplate = request.contextTemplate
                )
                
                // 5. Final validation
                val totalTokens = baseTokens + contextTokens
                if (totalTokens > request.maxTokens) {
                    logger.warn("Token count exceeded after optimization: $totalTokens > ${request.maxTokens}")
                }
                
                logger.info("Prompt context built successfully: $totalTokens tokens, ${optimizedDocuments.size} documents")
                
                PromptContextResult.success(
                    context = promptContext,
                    tokenUsage = TokenUsage(
                        systemTokens = systemTokens,
                        userTokens = userTokens,
                        contextTokens = contextTokens,
                        totalTokens = totalTokens,
                        availableTokens = request.maxTokens - totalTokens
                    ),
                    documentsIncluded = optimizedDocuments.size,
                    optimizationApplied = request.documents.size > optimizedDocuments.size
                )
                
            } catch (e: Exception) {
                logger.error("Failed to build prompt context: ${e.message}", e)
                PromptContextResult.failure(
                    error = "Context building failed: ${e.message}",
                    request = request
                )
            }
        }
    }

    /**
     * Estimate token usage for a potential prompt without building it
     * 
     * Useful for pre-flight checks and UI feedback
     */
    suspend fun estimateTokenUsage(request: PromptContextRequest): TokenEstimate {
        return withContext(Dispatchers.Default) {
            try {
                val systemTokens = tokenCounter.countTokens(request.systemPrompt, request.modelType)
                val userTokens = tokenCounter.countTokens(request.userMessage, request.modelType)
                val documentTokens = request.documents.sumOf { 
                    tokenCounter.countTokens(it.content, request.modelType) 
                }
                
                val totalEstimate = systemTokens + userTokens + documentTokens
                val wouldExceedLimit = totalEstimate > request.maxTokens
                
                TokenEstimate(
                    systemTokens = systemTokens,
                    userTokens = userTokens,
                    documentTokens = documentTokens,
                    totalEstimate = totalEstimate,
                    maxTokens = request.maxTokens,
                    wouldExceedLimit = wouldExceedLimit,
                    optimizationNeeded = wouldExceedLimit
                )
                
            } catch (e: Exception) {
                logger.error("Failed to estimate token usage: ${e.message}", e)
                TokenEstimate.error("Estimation failed: ${e.message}")
            }
        }
    }

    // ========================================================================
    // Private Domain Logic
    // ========================================================================

    /**
     * Assemble the final prompt context from components
     */
    private fun assemblePromptContext(
        systemPrompt: String,
        userMessage: String,
        documents: List<DocumentMapper.Document>,
        contextTemplate: String
    ): PromptContext {
        
        // Build document context section
        val documentContext = if (documents.isNotEmpty()) {
            buildDocumentContextSection(documents, contextTemplate)
        } else {
            ""
        }
        
        // Assemble final prompt
        val finalSystemPrompt = if (documentContext.isNotBlank()) {
            "$systemPrompt\n\n$documentContext"
        } else {
            systemPrompt
        }
        
        return PromptContext(
            systemPrompt = finalSystemPrompt,
            userMessage = userMessage,
            documentContext = documentContext,
            documentsIncluded = documents.size
        )
    }

    /**
     * Build the document context section using template
     */
    private fun buildDocumentContextSection(
        documents: List<DocumentMapper.Document>,
        template: String
    ): String {
        val contextBuilder = StringBuilder()
        
        contextBuilder.appendLine("## Relevant Context")
        contextBuilder.appendLine()
        
        documents.forEachIndexed { index, document ->
            contextBuilder.appendLine("### Document ${index + 1}: ${document.name}")
            contextBuilder.appendLine("Type: ${document.type}")
            contextBuilder.appendLine("Created: ${document.createdAt}")
            contextBuilder.appendLine()
            contextBuilder.appendLine(document.content)
            contextBuilder.appendLine()
            contextBuilder.appendLine("---")
            contextBuilder.appendLine()
        }
        
        return contextBuilder.toString()
    }
}

// ========================================================================
// Domain Models for Prompt Context
// ========================================================================

/**
 * Request for building prompt context
 */
data class PromptContextRequest(
    val sessionId: String,
    val systemPrompt: String,
    val userMessage: String,
    val documents: List<DocumentMapper.Document>,
    val maxTokens: Int,
    val responseTokenBuffer: Int = 1000,
    val modelType: String = "gpt-4",
    val contextTemplate: String = "default"
)

/**
 * Result of prompt context building
 */
sealed class PromptContextResult {
    data class Success(
        val context: PromptContext,
        val tokenUsage: TokenUsage,
        val documentsIncluded: Int,
        val optimizationApplied: Boolean
    ) : PromptContextResult()
    
    data class Failure(
        val error: String,
        val request: PromptContextRequest
    ) : PromptContextResult()
    
    companion object {
        fun success(
            context: PromptContext,
            tokenUsage: TokenUsage,
            documentsIncluded: Int,
            optimizationApplied: Boolean
        ) = Success(context, tokenUsage, documentsIncluded, optimizationApplied)
        
        fun failure(error: String, request: PromptContextRequest) = Failure(error, request)
    }
}

/**
 * Final assembled prompt context
 */
data class PromptContext(
    val systemPrompt: String,
    val userMessage: String,
    val documentContext: String,
    val documentsIncluded: Int
) {
    /**
     * Get the complete prompt for LLM submission
     */
    fun getCompletePrompt(): String {
        return if (documentContext.isNotBlank()) {
            "$systemPrompt\n\nUser: $userMessage"
        } else {
            "$systemPrompt\n\nUser: $userMessage"
        }
    }
}

/**
 * Token usage breakdown
 */
data class TokenUsage(
    val systemTokens: Int,
    val userTokens: Int,
    val contextTokens: Int,
    val totalTokens: Int,
    val availableTokens: Int
) {
    val utilizationPercentage: Double = 
        if (totalTokens + availableTokens > 0) {
            (totalTokens.toDouble() / (totalTokens + availableTokens)) * 100
        } else 0.0
}

/**
 * Token estimation result
 */
data class TokenEstimate(
    val systemTokens: Int,
    val userTokens: Int,
    val documentTokens: Int,
    val totalEstimate: Int,
    val maxTokens: Int,
    val wouldExceedLimit: Boolean,
    val optimizationNeeded: Boolean,
    val error: String? = null
) {
    companion object {
        fun error(message: String) = TokenEstimate(
            systemTokens = 0,
            userTokens = 0,
            documentTokens = 0,
            totalEstimate = 0,
            maxTokens = 0,
            wouldExceedLimit = false,
            optimizationNeeded = false,
            error = message
        )
    }
}

// ========================================================================
// Token Counter Interface
// ========================================================================

/**
 * Interface for token counting across different LLM models
 */
interface TokenCounter {
    /**
     * Count tokens for specific model
     */
    fun countTokens(text: String, modelType: String): Int
    
    /**
     * Get model-specific token limits
     */
    fun getTokenLimit(modelType: String): Int
}

/**
 * Simple token counter implementation
 */
class SimpleTokenCounter : TokenCounter {
    
    private val modelLimits = mapOf(
        "gpt-4" to 8192,
        "gpt-4-32k" to 32768,
        "gpt-3.5-turbo" to 4096,
        "claude-2" to 100000
    )
    
    override fun countTokens(text: String, modelType: String): Int {
        // Simple estimation: ~4 characters per token for English
        return (text.length / 4).coerceAtLeast(1)
    }
    
    override fun getTokenLimit(modelType: String): Int {
        return modelLimits[modelType] ?: 4096
    }
}
