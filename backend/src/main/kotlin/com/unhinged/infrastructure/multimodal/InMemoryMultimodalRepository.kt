// ============================================================================
// In-Memory Multimodal Repository - Infrastructure Layer
// ============================================================================
//
// @file InMemoryMultimodalRepository.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description In-memory implementation of multimodal repository for development
//
// This provides simple in-memory storage for multimodal data during development.
// In production, this would be replaced with database implementations.
//
// ============================================================================

package com.unhinged.infrastructure.multimodal

import com.unhinged.domain.multimodal.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import org.springframework.stereotype.Repository
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong

// ============================================================================
// In-Memory Multimodal Repository
// ============================================================================

/**
 * In-memory implementation of MultimodalRepository
 * 
 * Provides thread-safe in-memory storage for multimodal analyses during
 * development. Includes real-time streaming capabilities and statistics.
 */
@Repository
class InMemoryMultimodalRepository : MultimodalRepository {
    
    private val analyses = ConcurrentHashMap<String, MultimodalAnalysis>()
    private val analysisStream = MutableSharedFlow<MultimodalAnalysis>()
    private val idCounter = AtomicLong(0)
    
    override suspend fun save(analysis: MultimodalAnalysis): MultimodalAnalysis {
        val savedAnalysis = if (analysis.id.isEmpty()) {
            analysis.copy(id = generateId())
        } else {
            analysis
        }
        
        analyses[savedAnalysis.id] = savedAnalysis
        
        // Emit to stream for real-time updates
        analysisStream.emit(savedAnalysis)
        
        return savedAnalysis
    }
    
    override suspend fun findById(id: String): MultimodalAnalysis? {
        return analyses[id]
    }
    
    override suspend fun findByUserId(
        userId: String,
        limit: Int,
        offset: Int
    ): List<MultimodalAnalysis> {
        return analyses.values
            .filter { it.userId == userId }
            .sortedByDescending { it.createdAt }
            .drop(offset)
            .take(limit)
    }
    
    override suspend fun findByImageId(imageId: String): List<MultimodalAnalysis> {
        return analyses.values
            .filter { it.imageId == imageId }
            .sortedByDescending { it.createdAt }
    }
    
    override suspend fun findByWorkflowType(
        workflowType: WorkflowType,
        limit: Int,
        offset: Int
    ): List<MultimodalAnalysis> {
        return analyses.values
            .filter { it.workflowType == workflowType }
            .sortedByDescending { it.createdAt }
            .drop(offset)
            .take(limit)
    }
    
    override suspend fun findByAnalysisType(
        analysisType: AnalysisType,
        limit: Int,
        offset: Int
    ): List<MultimodalAnalysis> {
        return analyses.values
            .filter { it.analysisType == analysisType }
            .sortedByDescending { it.createdAt }
            .drop(offset)
            .take(limit)
    }
    
    override suspend fun searchByDescription(
        query: String,
        limit: Int,
        offset: Int
    ): List<MultimodalAnalysis> {
        val searchTerms = query.lowercase().split(" ").filter { it.isNotBlank() }
        
        return analyses.values
            .filter { analysis ->
                val description = analysis.description.lowercase()
                searchTerms.any { term -> description.contains(term) }
            }
            .sortedByDescending { analysis ->
                // Simple relevance scoring based on term frequency
                val description = analysis.description.lowercase()
                searchTerms.sumOf { term ->
                    description.split(term).size - 1
                }
            }
            .drop(offset)
            .take(limit)
    }
    
    override suspend fun findByMinConfidence(
        minConfidence: Double,
        limit: Int,
        offset: Int
    ): List<MultimodalAnalysis> {
        return analyses.values
            .filter { it.confidence >= minConfidence }
            .sortedByDescending { it.confidence }
            .drop(offset)
            .take(limit)
    }
    
    override suspend fun delete(id: String): Boolean {
        return analyses.remove(id) != null
    }
    
    override suspend fun deleteByUserId(userId: String): Int {
        val toDelete = analyses.values.filter { it.userId == userId }
        toDelete.forEach { analyses.remove(it.id) }
        return toDelete.size
    }
    
    override suspend fun getStatistics(userId: String?): AnalysisStatistics {
        val filteredAnalyses = if (userId != null) {
            analyses.values.filter { it.userId == userId }
        } else {
            analyses.values
        }
        
        if (filteredAnalyses.isEmpty()) {
            return AnalysisStatistics(
                totalAnalyses = 0,
                averageConfidence = 0.0,
                averageProcessingTime = 0.0,
                analysisTypeBreakdown = emptyMap(),
                workflowTypeBreakdown = emptyMap(),
                modelUsageBreakdown = emptyMap(),
                dailyAnalysisCount = emptyMap()
            )
        }
        
        val analysisTypeBreakdown = filteredAnalyses
            .groupBy { it.analysisType }
            .mapValues { it.value.size.toLong() }
        
        val workflowTypeBreakdown = filteredAnalyses
            .groupBy { it.workflowType }
            .mapValues { it.value.size.toLong() }
        
        val modelUsageBreakdown = filteredAnalyses
            .groupBy { it.modelUsed }
            .mapValues { it.value.size.toLong() }
        
        val dailyAnalysisCount = filteredAnalyses
            .groupBy { 
                it.createdAt.atOffset(ZoneOffset.UTC)
                    .format(DateTimeFormatter.ISO_LOCAL_DATE)
            }
            .mapValues { it.value.size.toLong() }
        
        return AnalysisStatistics(
            totalAnalyses = filteredAnalyses.size.toLong(),
            averageConfidence = filteredAnalyses.map { it.confidence }.average(),
            averageProcessingTime = filteredAnalyses.map { it.processingTime }.average(),
            analysisTypeBreakdown = analysisTypeBreakdown,
            workflowTypeBreakdown = workflowTypeBreakdown,
            modelUsageBreakdown = modelUsageBreakdown,
            dailyAnalysisCount = dailyAnalysisCount
        )
    }
    
    override fun streamAnalyses(userId: String?): Flow<MultimodalAnalysis> {
        return if (userId != null) {
            analysisStream.asSharedFlow()
                .kotlinx.coroutines.flow.filter { it.userId == userId }
        } else {
            analysisStream.asSharedFlow()
        }
    }
    
    /**
     * Generate unique ID for analysis
     */
    private fun generateId(): String {
        return "analysis_${idCounter.incrementAndGet()}_${System.currentTimeMillis()}"
    }
    
    /**
     * Get all analyses (for testing/debugging)
     */
    fun getAllAnalyses(): List<MultimodalAnalysis> {
        return analyses.values.sortedByDescending { it.createdAt }
    }
    
    /**
     * Clear all analyses (for testing)
     */
    fun clear() {
        analyses.clear()
    }
    
    /**
     * Get repository size
     */
    fun size(): Int {
        return analyses.size
    }
}
