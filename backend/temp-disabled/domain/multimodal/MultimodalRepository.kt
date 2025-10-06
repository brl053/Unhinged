// ============================================================================
// Multimodal Repository - Data Access Interface
// ============================================================================
//
// @file MultimodalRepository.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description Repository interface for multimodal analysis data access
//
// This interface defines the contract for multimodal data persistence,
// following clean architecture principles. Infrastructure implementations
// provide the actual data access logic.
//
// ============================================================================

package com.unhinged.domain.multimodal

import kotlinx.coroutines.flow.Flow

// ============================================================================
// Repository Interface
// ============================================================================

/**
 * Repository interface for multimodal analysis persistence
 * 
 * Defines the contract for storing and retrieving multimodal analysis results.
 * Infrastructure implementations provide the actual data access logic.
 */
interface MultimodalRepository {
    
    /**
     * Save a multimodal analysis result
     * 
     * @param analysis The analysis to save
     * @return The saved analysis with any generated fields
     */
    suspend fun save(analysis: MultimodalAnalysis): MultimodalAnalysis
    
    /**
     * Find analysis by ID
     * 
     * @param id The analysis ID
     * @return The analysis if found, null otherwise
     */
    suspend fun findById(id: String): MultimodalAnalysis?
    
    /**
     * Find analyses by user ID
     * 
     * @param userId The user ID
     * @param limit Maximum number of results
     * @param offset Offset for pagination
     * @return List of analyses for the user
     */
    suspend fun findByUserId(
        userId: String, 
        limit: Int = 50, 
        offset: Int = 0
    ): List<MultimodalAnalysis>
    
    /**
     * Find analyses by image ID
     * 
     * @param imageId The image ID
     * @return List of analyses for the image
     */
    suspend fun findByImageId(imageId: String): List<MultimodalAnalysis>
    
    /**
     * Find analyses by workflow type
     * 
     * @param workflowType The workflow type
     * @param limit Maximum number of results
     * @param offset Offset for pagination
     * @return List of analyses using the workflow
     */
    suspend fun findByWorkflowType(
        workflowType: WorkflowType,
        limit: Int = 50,
        offset: Int = 0
    ): List<MultimodalAnalysis>
    
    /**
     * Find analyses by analysis type
     * 
     * @param analysisType The analysis type
     * @param limit Maximum number of results
     * @param offset Offset for pagination
     * @return List of analyses of the specified type
     */
    suspend fun findByAnalysisType(
        analysisType: AnalysisType,
        limit: Int = 50,
        offset: Int = 0
    ): List<MultimodalAnalysis>
    
    /**
     * Search analyses by description content
     * 
     * @param query Search query
     * @param limit Maximum number of results
     * @param offset Offset for pagination
     * @return List of matching analyses
     */
    suspend fun searchByDescription(
        query: String,
        limit: Int = 50,
        offset: Int = 0
    ): List<MultimodalAnalysis>
    
    /**
     * Get analyses with confidence above threshold
     * 
     * @param minConfidence Minimum confidence threshold
     * @param limit Maximum number of results
     * @param offset Offset for pagination
     * @return List of high-confidence analyses
     */
    suspend fun findByMinConfidence(
        minConfidence: Double,
        limit: Int = 50,
        offset: Int = 0
    ): List<MultimodalAnalysis>
    
    /**
     * Delete analysis by ID
     * 
     * @param id The analysis ID
     * @return True if deleted, false if not found
     */
    suspend fun delete(id: String): Boolean
    
    /**
     * Delete analyses by user ID
     * 
     * @param userId The user ID
     * @return Number of analyses deleted
     */
    suspend fun deleteByUserId(userId: String): Int
    
    /**
     * Get analysis statistics
     * 
     * @param userId Optional user ID to filter by
     * @return Analysis statistics
     */
    suspend fun getStatistics(userId: String? = null): AnalysisStatistics
    
    /**
     * Stream analyses in real-time
     * 
     * @param userId Optional user ID to filter by
     * @return Flow of new analyses
     */
    fun streamAnalyses(userId: String? = null): Flow<MultimodalAnalysis>
}

// ============================================================================
// Supporting Data Classes
// ============================================================================

/**
 * Statistics about multimodal analyses
 */
data class AnalysisStatistics(
    val totalAnalyses: Long,
    val averageConfidence: Double,
    val averageProcessingTime: Double,
    val analysisTypeBreakdown: Map<AnalysisType, Long>,
    val workflowTypeBreakdown: Map<WorkflowType, Long>,
    val modelUsageBreakdown: Map<String, Long>,
    val dailyAnalysisCount: Map<String, Long> // Date string to count
)
