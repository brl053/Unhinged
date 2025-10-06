// ============================================================================
// In-Memory Vision Repository - Infrastructure Layer
// ============================================================================
//
// @file InMemoryVisionRepository.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description In-memory implementation of vision repositories for development
//
// This provides simple in-memory storage for vision data during development.
// In production, this would be replaced with database implementations.
//
// ============================================================================

package com.unhinged.infrastructure.vision

import com.unhinged.domain.vision.*
import java.util.concurrent.ConcurrentHashMap

// ============================================================================
// In-Memory Vision Repository
// ============================================================================

/**
 * In-memory implementation of VisionRepository
 */
class InMemoryVisionRepository : VisionRepository {
    
    private val analyses = ConcurrentHashMap<String, ImageAnalysis>()
    
    override suspend fun saveImageAnalysis(analysis: ImageAnalysis): ImageAnalysis {
        analyses[analysis.id] = analysis
        return analysis
    }
    
    override suspend fun getImageAnalysis(id: String): ImageAnalysis? {
        return analyses[id]
    }
    
    override suspend fun listImageAnalyses(
        userId: String,
        limit: Int,
        offset: Int
    ): List<ImageAnalysis> {
        return analyses.values
            .filter { it.imageId.contains(userId) } // Simple filtering by user
            .sortedByDescending { it.createdAt }
            .drop(offset)
            .take(limit)
    }
    
    override suspend fun deleteImageAnalysis(id: String): Boolean {
        return analyses.remove(id) != null
    }
}

// ============================================================================
// In-Memory Vision Session Repository
// ============================================================================

/**
 * In-memory implementation of VisionSessionRepository
 */
class InMemoryVisionSessionRepository : VisionSessionRepository {
    
    private val sessions = ConcurrentHashMap<String, VisionSession>()
    
    override suspend fun createSession(session: VisionSession): VisionSession {
        sessions[session.id] = session
        return session
    }
    
    override suspend fun getSession(id: String): VisionSession? {
        return sessions[id]
    }
    
    override suspend fun updateSessionStatus(id: String, status: VisionSessionStatus): Boolean {
        val session = sessions[id] ?: return false
        val updatedSession = session.copy(
            status = status,
            updatedAt = java.time.Instant.now()
        )
        sessions[id] = updatedSession
        return true
    }
    
    override suspend fun listUserSessions(
        userId: String,
        sessionType: VisionSessionType?,
        limit: Int,
        offset: Int
    ): List<VisionSession> {
        return sessions.values
            .filter { it.userId == userId }
            .filter { sessionType == null || it.sessionType == sessionType }
            .sortedByDescending { it.createdAt }
            .drop(offset)
            .take(limit)
    }
    
    override suspend fun deleteSession(id: String): Boolean {
        return sessions.remove(id) != null
    }
}
