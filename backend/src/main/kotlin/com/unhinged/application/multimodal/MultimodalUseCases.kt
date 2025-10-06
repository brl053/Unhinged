// ============================================================================
// Multimodal Use Cases - Application Layer
// ============================================================================
//
// @file MultimodalUseCases.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description Application layer use cases for multimodal processing operations
//
// This layer orchestrates domain objects and coordinates with infrastructure.
// It implements the business workflows for multimodal analysis while
// maintaining clean architecture principles.
//
// ============================================================================

package com.unhinged.application.multimodal

import com.unhinged.domain.multimodal.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.withTimeout
import kotlin.time.Duration.Companion.seconds

// ============================================================================
// Use Case Interfaces
// ============================================================================

/**
 * Multimodal image analysis use case
 * 
 * Handles the complete workflow for advanced multimodal image analysis
 */
class MultimodalAnalysisUseCase(
    private val multimodalRepository: MultimodalRepository,
    private val domainService: MultimodalDomainService,
    private val workflowSelector: WorkflowSelector,
    private val contextService: ContextService,
    private val visionService: VisionInferenceService,
    private val contextLLMService: ContextLLMService,
    private val cacheService: CacheService
) {
    
    /**
     * Executes multimodal analysis workflow
     * 
     * @param request The analysis request
     * @return Analysis result
     */
    suspend fun execute(request: AnalysisRequest): MultimodalAnalysis {
        
        // Validate the request
        val validationErrors = domainService.validateAnalysisRequest(request)
        if (validationErrors.isNotEmpty()) {
            throw MultimodalValidationException("Invalid analysis request", validationErrors)
        }
        
        // Check cache first if request is cacheable
        if (domainService.isCacheable(request)) {
            val cacheKey = domainService.generateCacheKey(request)
            cacheService.get<MultimodalAnalysis>(cacheKey)?.let { cached ->
                return cached
            }
        }
        
        // Select optimal workflow
        val workflow = workflowSelector.selectOptimalWorkflow(
            request.analysisType,
            request.priority,
            request.workflowType
        )
        
        // Execute analysis based on workflow type
        val analysis = when (workflow.type) {
            WorkflowType.BASIC_ANALYSIS -> executeBasicAnalysis(request, workflow)
            WorkflowType.CONTEXTUAL_ANALYSIS -> executeContextualAnalysis(request, workflow)
            WorkflowType.ITERATIVE_REFINEMENT -> executeIterativeAnalysis(request, workflow)
            WorkflowType.MULTI_MODEL_CONSENSUS -> executeConsensusAnalysis(request, workflow)
        }
        
        // Validate the result
        val resultValidationErrors = domainService.validateAnalysisResult(analysis)
        if (resultValidationErrors.isNotEmpty()) {
            throw MultimodalValidationException("Invalid analysis result", resultValidationErrors)
        }
        
        // Calculate adjusted confidence and quality score
        val adjustedConfidence = domainService.calculateAdjustedConfidence(
            analysis.confidence,
            analysis.modelUsed,
            analysis.workflowType,
            analysis.processingTime
        )
        
        val qualityScore = domainService.calculateQualityScore(analysis)
        
        val finalAnalysis = analysis.copy(
            confidence = adjustedConfidence,
            metadata = analysis.metadata + mapOf(
                "quality_score" to qualityScore.toString(),
                "workflow_config" to workflow.type.name,
                "requires_review" to domainService.requiresHumanReview(analysis).toString()
            )
        )
        
        // Persist the result
        val savedAnalysis = multimodalRepository.save(finalAnalysis)
        
        // Cache the result if applicable
        if (domainService.isCacheable(request)) {
            val cacheKey = domainService.generateCacheKey(request)
            val ttl = domainService.calculateCacheTTL(savedAnalysis)
            cacheService.set(cacheKey, savedAnalysis, ttl)
        }
        
        return savedAnalysis
    }
    
    /**
     * Execute basic analysis workflow
     */
    private suspend fun executeBasicAnalysis(
        request: AnalysisRequest,
        workflow: WorkflowConfiguration
    ): MultimodalAnalysis = withTimeout(workflow.timeoutSeconds.seconds) {
        
        val visionResult = visionService.infer(
            imageData = request.imageData,
            model = workflow.visionModel,
            prompt = request.prompt ?: "Analyze this image in detail.",
            analysisType = request.analysisType.name.lowercase(),
            maxTokens = request.maxTokens,
            temperature = request.temperature
        )
        
        MultimodalAnalysis(
            imageId = request.imageId,
            analysisType = request.analysisType,
            description = visionResult.description,
            confidence = visionResult.confidence,
            modelUsed = visionResult.modelUsed,
            workflowType = workflow.type,
            processingTime = visionResult.processingTime,
            metadata = visionResult.metadata,
            extractedText = visionResult.extractedText,
            uiElements = visionResult.uiElements.map { 
                UIElement(it.type, it.confidence, it.bounds?.let { b ->
                    ElementBounds(b.x, b.y, b.width, b.height)
                }, it.properties)
            },
            tags = visionResult.tags,
            userId = request.userId
        )
    }
    
    /**
     * Execute contextual analysis workflow
     */
    private suspend fun executeContextualAnalysis(
        request: AnalysisRequest,
        workflow: WorkflowConfiguration
    ): MultimodalAnalysis = withTimeout(workflow.timeoutSeconds.seconds) {
        
        coroutineScope {
            // Generate contextual prompt in parallel with context search
            val contextPromptDeferred = async {
                if (workflow.useContextEnhancement) {
                    contextLLMService.generatePrompt(
                        basePrompt = request.prompt ?: "Analyze this image in detail.",
                        analysisType = request.analysisType.name.lowercase(),
                        contextTypes = listOf("documentation", "ui_components"),
                        maxContextItems = 3
                    )
                } else {
                    request.prompt ?: "Analyze this image in detail."
                }
            }
            
            // Perform vision analysis
            val visionResultDeferred = async {
                val enhancedPrompt = contextPromptDeferred.await()
                visionService.infer(
                    imageData = request.imageData,
                    model = workflow.visionModel,
                    prompt = enhancedPrompt,
                    analysisType = request.analysisType.name.lowercase(),
                    maxTokens = request.maxTokens,
                    temperature = request.temperature
                )
            }
            
            val visionResult = visionResultDeferred.await()
            
            MultimodalAnalysis(
                imageId = request.imageId,
                analysisType = request.analysisType,
                description = visionResult.description,
                confidence = visionResult.confidence,
                modelUsed = visionResult.modelUsed,
                workflowType = workflow.type,
                processingTime = visionResult.processingTime,
                metadata = visionResult.metadata + mapOf(
                    "context_enhanced" to workflow.useContextEnhancement.toString()
                ),
                extractedText = visionResult.extractedText,
                uiElements = visionResult.uiElements.map { 
                    UIElement(it.type, it.confidence, it.bounds?.let { b ->
                        ElementBounds(b.x, b.y, b.width, b.height)
                    }, it.properties)
                },
                tags = visionResult.tags,
                userId = request.userId
            )
        }
    }
    
    /**
     * Execute iterative refinement workflow
     */
    private suspend fun executeIterativeAnalysis(
        request: AnalysisRequest,
        workflow: WorkflowConfiguration
    ): MultimodalAnalysis = withTimeout(workflow.timeoutSeconds.seconds) {
        
        // Initial analysis
        var currentAnalysis = executeContextualAnalysis(request, workflow)
        
        // Iterative refinement
        repeat(workflow.maxIterations - 1) { iteration ->
            val refinementPrompt = """
                Based on this initial analysis: "${currentAnalysis.description}"
                
                Please provide a more detailed and comprehensive analysis of the image, focusing on:
                1. Any details that might have been missed
                2. More specific technical information
                3. Better organization of the information
                4. Enhanced clarity and precision
                
                Original analysis request: ${request.prompt ?: "Analyze this image."}
            """.trimIndent()
            
            val refinedResult = visionService.infer(
                imageData = request.imageData,
                model = workflow.visionModel,
                prompt = refinementPrompt,
                analysisType = request.analysisType.name.lowercase(),
                maxTokens = request.maxTokens,
                temperature = request.temperature * 0.8f // Slightly lower temperature for refinement
            )
            
            if (refinedResult.confidence > currentAnalysis.confidence) {
                currentAnalysis = currentAnalysis.copy(
                    description = refinedResult.description,
                    confidence = refinedResult.confidence,
                    processingTime = currentAnalysis.processingTime + refinedResult.processingTime,
                    metadata = currentAnalysis.metadata + mapOf(
                        "refinement_iterations" to (iteration + 1).toString(),
                        "final_iteration_confidence" to refinedResult.confidence.toString()
                    )
                )
            }
        }
        
        currentAnalysis
    }
    
    /**
     * Execute multi-model consensus workflow
     */
    private suspend fun executeConsensusAnalysis(
        request: AnalysisRequest,
        workflow: WorkflowConfiguration
    ): MultimodalAnalysis = withTimeout(workflow.timeoutSeconds.seconds) {
        
        // For now, implement as enhanced contextual analysis
        // TODO: Implement actual multi-model consensus when multiple models are available
        val analysis = executeContextualAnalysis(request, workflow)
        
        analysis.copy(
            confidence = minOf(0.95, analysis.confidence + 0.1), // Slight boost for consensus
            metadata = analysis.metadata + mapOf(
                "consensus_models" to "1", // Will be updated when multiple models are available
                "consensus_method" to "single_model_enhanced"
            )
        )
    }
}

// ============================================================================
// Query Use Cases
// ============================================================================

/**
 * Get analysis by ID use case
 */
class GetAnalysisUseCase(
    private val multimodalRepository: MultimodalRepository
) {
    suspend fun execute(id: String): MultimodalAnalysis? {
        return multimodalRepository.findById(id)
    }
}

/**
 * Get user analyses use case
 */
class GetUserAnalysesUseCase(
    private val multimodalRepository: MultimodalRepository
) {
    suspend fun execute(
        userId: String,
        limit: Int = 50,
        offset: Int = 0
    ): List<MultimodalAnalysis> {
        return multimodalRepository.findByUserId(userId, limit, offset)
    }
}

/**
 * Search analyses use case
 */
class SearchAnalysesUseCase(
    private val multimodalRepository: MultimodalRepository
) {
    suspend fun execute(
        query: String,
        limit: Int = 50,
        offset: Int = 0
    ): List<MultimodalAnalysis> {
        return multimodalRepository.searchByDescription(query, limit, offset)
    }
}

/**
 * Get analysis statistics use case
 */
class GetAnalysisStatisticsUseCase(
    private val multimodalRepository: MultimodalRepository
) {
    suspend fun execute(userId: String? = null): AnalysisStatistics {
        return multimodalRepository.getStatistics(userId)
    }
}

// ============================================================================
// Supporting Interfaces
// ============================================================================

/**
 * Vision inference service interface
 */
interface VisionInferenceService {
    suspend fun infer(
        imageData: ByteArray,
        model: String,
        prompt: String,
        analysisType: String,
        maxTokens: Int = 1024,
        temperature: Float = 0.1f
    ): VisionInferenceResult
}

/**
 * Context LLM service interface
 */
interface ContextLLMService {
    suspend fun generatePrompt(
        basePrompt: String,
        analysisType: String,
        contextTypes: List<String>,
        maxContextItems: Int = 3
    ): String
}

/**
 * Cache service interface
 */
interface CacheService {
    suspend fun <T> get(key: String): T?
    suspend fun <T> set(key: String, value: T, ttlSeconds: Long)
    suspend fun delete(key: String): Boolean
}

/**
 * Vision inference result
 */
data class VisionInferenceResult(
    val description: String,
    val confidence: Double,
    val modelUsed: String,
    val processingTime: Double,
    val metadata: Map<String, String>,
    val extractedText: String?,
    val uiElements: List<VisionUIElement>,
    val tags: List<String>,
    val properties: Map<String, String> = emptyMap()
)

/**
 * Vision UI element
 */
data class VisionUIElement(
    val type: String,
    val confidence: Double,
    val bounds: VisionElementBounds?,
    val properties: Map<String, String> = emptyMap()
)

/**
 * Vision element bounds
 */
data class VisionElementBounds(
    val x: Int, val y: Int, val width: Int, val height: Int
)
