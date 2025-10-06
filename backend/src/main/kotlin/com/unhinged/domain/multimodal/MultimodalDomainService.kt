// ============================================================================
// Multimodal Domain Service - Business Logic
// ============================================================================
//
// @file MultimodalDomainService.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description Domain service for multimodal processing business logic
//
// This service contains pure business logic for multimodal operations.
// Infrastructure implementations provide the actual processing capabilities.
//
// ============================================================================

package com.unhinged.domain.multimodal

// ============================================================================
// Domain Service Interface
// ============================================================================

/**
 * Core multimodal processing domain service
 * 
 * Contains pure business logic for multimodal operations. Infrastructure
 * implementations provide the actual processing capabilities.
 */
interface MultimodalDomainService {
    
    /**
     * Validates a multimodal analysis request
     * 
     * @param request The analysis request to validate
     * @return List of validation errors (empty if valid)
     */
    fun validateAnalysisRequest(request: AnalysisRequest): List<MultimodalValidationError>
    
    /**
     * Validates a multimodal analysis result
     * 
     * @param analysis The analysis to validate
     * @return List of validation errors (empty if valid)
     */
    fun validateAnalysisResult(analysis: MultimodalAnalysis): List<MultimodalValidationError>
    
    /**
     * Selects optimal workflow configuration for analysis request
     * 
     * @param analysisType Type of analysis to perform
     * @param priority Priority level of the request
     * @param userPreference User's preferred workflow type (optional)
     * @return Optimal workflow configuration
     */
    fun selectOptimalWorkflow(
        analysisType: AnalysisType,
        priority: Priority = Priority.NORMAL,
        userPreference: WorkflowType? = null
    ): WorkflowConfiguration
    
    /**
     * Calculates confidence score based on multiple factors
     * 
     * @param rawConfidence Raw confidence from model
     * @param modelUsed Model that generated the result
     * @param workflowType Workflow used for analysis
     * @param processingTime Time taken for processing
     * @return Adjusted confidence score
     */
    fun calculateAdjustedConfidence(
        rawConfidence: Double,
        modelUsed: String,
        workflowType: WorkflowType,
        processingTime: Double
    ): Double
    
    /**
     * Validates UI elements detected in analysis
     * 
     * @param uiElements List of UI elements to validate
     * @param imageWidth Width of the analyzed image
     * @param imageHeight Height of the analyzed image
     * @return List of validation errors (empty if valid)
     */
    fun validateUIElements(
        uiElements: List<UIElement>,
        imageWidth: Int,
        imageHeight: Int
    ): List<MultimodalValidationError>
    
    /**
     * Determines if analysis result requires human review
     * 
     * @param analysis The analysis result
     * @return True if human review is recommended
     */
    fun requiresHumanReview(analysis: MultimodalAnalysis): Boolean
    
    /**
     * Calculates quality score for analysis result
     * 
     * @param analysis The analysis result
     * @return Quality score between 0.0 and 1.0
     */
    fun calculateQualityScore(analysis: MultimodalAnalysis): Double
    
    /**
     * Generates cache key for analysis request
     * 
     * @param request The analysis request
     * @return Cache key string
     */
    fun generateCacheKey(request: AnalysisRequest): String
    
    /**
     * Determines if analysis request can be cached
     * 
     * @param request The analysis request
     * @return True if result can be cached
     */
    fun isCacheable(request: AnalysisRequest): Boolean
    
    /**
     * Calculates cache TTL for analysis result
     * 
     * @param analysis The analysis result
     * @return TTL in seconds
     */
    fun calculateCacheTTL(analysis: MultimodalAnalysis): Long
    
    /**
     * Validates context items for relevance
     * 
     * @param contextItems List of context items
     * @param analysisType Type of analysis being performed
     * @return Filtered list of relevant context items
     */
    fun filterRelevantContext(
        contextItems: List<ContextItem>,
        analysisType: AnalysisType
    ): List<ContextItem>
    
    /**
     * Merges multiple analysis results for consensus
     * 
     * @param analyses List of analysis results to merge
     * @return Merged consensus result
     */
    fun mergeAnalysisResults(analyses: List<MultimodalAnalysis>): MultimodalAnalysis
    
    /**
     * Calculates processing priority based on request characteristics
     * 
     * @param request The analysis request
     * @return Calculated priority level
     */
    fun calculateProcessingPriority(request: AnalysisRequest): Priority
}

// ============================================================================
// Workflow Selector Interface
// ============================================================================

/**
 * Service for selecting optimal analysis workflows
 */
interface WorkflowSelector {
    
    /**
     * Select optimal workflow configuration
     * 
     * @param analysisType Type of analysis
     * @param priority Request priority
     * @param userPreference User's preferred workflow (optional)
     * @return Optimal workflow configuration
     */
    fun selectOptimalWorkflow(
        analysisType: AnalysisType,
        priority: Priority = Priority.NORMAL,
        userPreference: WorkflowType? = null
    ): WorkflowConfiguration
    
    /**
     * Get available workflows for analysis type
     * 
     * @param analysisType Type of analysis
     * @return List of available workflow configurations
     */
    fun getAvailableWorkflows(analysisType: AnalysisType): List<WorkflowConfiguration>
    
    /**
     * Get default workflow for analysis type
     * 
     * @param analysisType Type of analysis
     * @return Default workflow configuration
     */
    fun getDefaultWorkflow(analysisType: AnalysisType): WorkflowConfiguration
}

// ============================================================================
// Context Service Interface
// ============================================================================

/**
 * Service for managing analysis context
 */
interface ContextService {
    
    /**
     * Search for relevant context items
     * 
     * @param query Search query
     * @param contextTypes Types of context to search
     * @param maxResults Maximum number of results
     * @return List of relevant context items
     */
    suspend fun searchContext(
        query: String,
        contextTypes: List<ContextType>,
        maxResults: Int = 10
    ): List<ContextItem>
    
    /**
     * Get context items by type
     * 
     * @param contextType Type of context
     * @param limit Maximum number of items
     * @return List of context items
     */
    suspend fun getContextByType(
        contextType: ContextType,
        limit: Int = 10
    ): List<ContextItem>
    
    /**
     * Refresh context cache
     * 
     * @return Number of context items refreshed
     */
    suspend fun refreshContext(): Int
}
