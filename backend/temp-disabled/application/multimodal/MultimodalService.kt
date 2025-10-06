// ============================================================================
// Multimodal Service - Application Layer Orchestration
// ============================================================================
//
// @file MultimodalService.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description Main application service for multimodal operations
//
// This service orchestrates all multimodal use cases and provides a unified
// interface for the presentation layer. It coordinates between domain services
// and infrastructure implementations.
//
// ============================================================================

package com.unhinged.application.multimodal

import com.unhinged.domain.multimodal.*
import kotlinx.coroutines.flow.Flow
import org.springframework.stereotype.Service

// ============================================================================
// Main Application Service
// ============================================================================

/**
 * Main multimodal application service
 * 
 * Orchestrates all multimodal operations and provides a unified interface
 * for the presentation layer. Coordinates between use cases and handles
 * cross-cutting concerns.
 */
@Service
class MultimodalService(
    private val analysisUseCase: MultimodalAnalysisUseCase,
    private val getAnalysisUseCase: GetAnalysisUseCase,
    private val getUserAnalysesUseCase: GetUserAnalysesUseCase,
    private val searchAnalysesUseCase: SearchAnalysesUseCase,
    private val getStatisticsUseCase: GetAnalysisStatisticsUseCase,
    private val workflowSelector: WorkflowSelector,
    private val contextService: ContextService
) {
    
    /**
     * Analyze image with multimodal AI
     * 
     * @param request Analysis request
     * @return Analysis result
     */
    suspend fun analyzeImage(request: AnalysisRequest): MultimodalAnalysis {
        return analysisUseCase.execute(request)
    }
    
    /**
     * Get analysis by ID
     * 
     * @param id Analysis ID
     * @return Analysis if found
     * @throws MultimodalNotFoundException if not found
     */
    suspend fun getAnalysis(id: String): MultimodalAnalysis {
        return getAnalysisUseCase.execute(id)
            ?: throw MultimodalNotFoundException("Analysis not found: $id")
    }
    
    /**
     * Get analyses for user
     * 
     * @param userId User ID
     * @param limit Maximum results
     * @param offset Pagination offset
     * @return List of user analyses
     */
    suspend fun getUserAnalyses(
        userId: String,
        limit: Int = 50,
        offset: Int = 0
    ): List<MultimodalAnalysis> {
        return getUserAnalysesUseCase.execute(userId, limit, offset)
    }
    
    /**
     * Search analyses by description
     * 
     * @param query Search query
     * @param limit Maximum results
     * @param offset Pagination offset
     * @return List of matching analyses
     */
    suspend fun searchAnalyses(
        query: String,
        limit: Int = 50,
        offset: Int = 0
    ): List<MultimodalAnalysis> {
        return searchAnalysesUseCase.execute(query, limit, offset)
    }
    
    /**
     * Get analysis statistics
     * 
     * @param userId Optional user filter
     * @return Analysis statistics
     */
    suspend fun getStatistics(userId: String? = null): AnalysisStatistics {
        return getStatisticsUseCase.execute(userId)
    }
    
    /**
     * Get available workflows for analysis type
     * 
     * @param analysisType Type of analysis
     * @return List of available workflows
     */
    fun getAvailableWorkflows(analysisType: AnalysisType): List<WorkflowConfiguration> {
        return workflowSelector.getAvailableWorkflows(analysisType)
    }
    
    /**
     * Get default workflow for analysis type
     * 
     * @param analysisType Type of analysis
     * @return Default workflow configuration
     */
    fun getDefaultWorkflow(analysisType: AnalysisType): WorkflowConfiguration {
        return workflowSelector.getDefaultWorkflow(analysisType)
    }
    
    /**
     * Search project context
     * 
     * @param query Search query
     * @param contextTypes Types of context to search
     * @param maxResults Maximum results
     * @return List of context items
     */
    suspend fun searchContext(
        query: String,
        contextTypes: List<ContextType>,
        maxResults: Int = 10
    ): List<ContextItem> {
        return contextService.searchContext(query, contextTypes, maxResults)
    }
    
    /**
     * Get context by type
     * 
     * @param contextType Type of context
     * @param limit Maximum items
     * @return List of context items
     */
    suspend fun getContextByType(
        contextType: ContextType,
        limit: Int = 10
    ): List<ContextItem> {
        return contextService.getContextByType(contextType, limit)
    }
    
    /**
     * Refresh context cache
     * 
     * @return Number of items refreshed
     */
    suspend fun refreshContext(): Int {
        return contextService.refreshContext()
    }
    
    /**
     * Stream analyses in real-time
     * 
     * @param userId Optional user filter
     * @return Flow of new analyses
     */
    fun streamAnalyses(userId: String? = null): Flow<MultimodalAnalysis> {
        // This would be implemented by the repository
        // For now, return empty flow
        return kotlinx.coroutines.flow.emptyFlow()
    }
}

// ============================================================================
// Service Configuration
// ============================================================================

/**
 * Configuration for multimodal service
 */
data class MultimodalServiceConfig(
    val defaultCacheTTL: Long = 3600, // 1 hour
    val maxConcurrentAnalyses: Int = 10,
    val defaultTimeout: Int = 300, // 5 minutes
    val enableCaching: Boolean = true,
    val enableMetrics: Boolean = true,
    val defaultWorkflowType: WorkflowType = WorkflowType.CONTEXTUAL_ANALYSIS,
    val supportedImageFormats: List<String> = listOf("jpeg", "jpg", "png", "webp", "bmp"),
    val maxImageSizeBytes: Long = 10 * 1024 * 1024, // 10MB
    val maxPromptLength: Int = 2000
)

/**
 * Service metrics for monitoring
 */
data class MultimodalServiceMetrics(
    val totalAnalyses: Long,
    val averageProcessingTime: Double,
    val cacheHitRate: Double,
    val errorRate: Double,
    val activeAnalyses: Int,
    val queuedAnalyses: Int
)
