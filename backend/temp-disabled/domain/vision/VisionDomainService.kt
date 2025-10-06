// ============================================================================
// Vision Domain Service - Business Logic
// ============================================================================
//
// @file VisionDomainService.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description Domain service for vision processing business logic
//
// This service contains pure business logic for vision operations.
// Infrastructure implementations provide the actual processing capabilities.
//
// ============================================================================

package com.unhinged.domain.vision

import kotlinx.coroutines.flow.Flow
import java.time.Instant

// ============================================================================
// Domain Service Interface
// ============================================================================

/**
 * Core vision processing domain service
 * 
 * Contains pure business logic for vision operations. Infrastructure
 * implementations provide the actual processing capabilities.
 */
interface VisionDomainService {
    
    /**
     * Validates an image analysis request
     * 
     * @param imageData The image data to validate
     * @param options Processing options
     * @return List of validation errors (empty if valid)
     */
    fun validateImageAnalysisRequest(
        imageData: ByteArray,
        options: VisionOptions
    ): List<VisionValidationError>
    
    /**
     * Validates an image analysis result
     * 
     * @param analysis The analysis to validate
     * @return List of validation errors (empty if valid)
     */
    fun validateImageAnalysis(analysis: ImageAnalysis): List<VisionValidationError>
    
    /**
     * Generates session metadata for tracking
     * 
     * @param sessionType Type of vision session
     * @param userId User performing the operation
     * @param additionalMetadata Additional metadata
     * @return Generated metadata map
     */
    fun generateSessionMetadata(
        sessionType: VisionSessionType,
        userId: String,
        additionalMetadata: Map<String, String> = emptyMap()
    ): Map<String, String>
    
    /**
     * Determines optimal processing options based on image characteristics
     * 
     * @param imageData The image data
     * @param userOptions User-specified options
     * @return Optimized processing options
     */
    fun optimizeProcessingOptions(
        imageData: ByteArray,
        userOptions: VisionOptions
    ): VisionOptions
}

// ============================================================================
// Repository Interfaces
// ============================================================================

/**
 * Vision data repository interface
 * 
 * Defines the contract for vision data persistence without
 * specifying implementation details.
 */
interface VisionRepository {
    
    /**
     * Saves an image analysis result
     */
    suspend fun saveImageAnalysis(analysis: ImageAnalysis): ImageAnalysis
    
    /**
     * Retrieves an analysis by ID
     */
    suspend fun getImageAnalysis(id: String): ImageAnalysis?
    
    /**
     * Lists analyses for a user
     */
    suspend fun listImageAnalyses(
        userId: String,
        limit: Int = 50,
        offset: Int = 0
    ): List<ImageAnalysis>
    
    /**
     * Deletes an analysis
     */
    suspend fun deleteImageAnalysis(id: String): Boolean
}

/**
 * Vision session repository interface
 */
interface VisionSessionRepository {
    
    /**
     * Creates a new vision session
     */
    suspend fun createSession(session: VisionSession): VisionSession
    
    /**
     * Retrieves a session by ID
     */
    suspend fun getSession(id: String): VisionSession?
    
    /**
     * Updates session status
     */
    suspend fun updateSessionStatus(id: String, status: VisionSessionStatus): Boolean
    
    /**
     * Lists sessions for a user
     */
    suspend fun listUserSessions(
        userId: String,
        sessionType: VisionSessionType? = null,
        limit: Int = 50,
        offset: Int = 0
    ): List<VisionSession>
    
    /**
     * Deletes a session
     */
    suspend fun deleteSession(id: String): Boolean
}

// ============================================================================
// Processing Service Interface
// ============================================================================

/**
 * Vision processing service interface
 * 
 * Defines the contract for actual vision processing operations.
 * Infrastructure implementations provide the real processing logic.
 */
interface VisionProcessingService {
    
    /**
     * Analyzes an image and generates description
     * 
     * @param imageData The image data to analyze
     * @param options Processing options
     * @return Analysis result
     */
    suspend fun analyzeImage(
        imageData: ByteArray,
        options: VisionOptions = VisionOptions()
    ): ImageAnalysis
    
    /**
     * Generates detailed description of an image
     * 
     * @param imageData The image data
     * @param prompt Optional prompt for guided description
     * @param options Processing options
     * @return Detailed description
     */
    suspend fun describeImage(
        imageData: ByteArray,
        prompt: String? = null,
        options: VisionOptions = VisionOptions()
    ): String
    
    /**
     * Detects objects in an image
     * 
     * @param imageData The image data
     * @param options Processing options
     * @return List of detected objects
     */
    suspend fun detectObjects(
        imageData: ByteArray,
        options: VisionOptions = VisionOptions()
    ): List<DetectedObject>
    
    /**
     * Extracts metadata from image
     * 
     * @param imageData The image data
     * @return Image metadata
     */
    suspend fun extractImageMetadata(imageData: ByteArray): ImageMetadata
    
    /**
     * Checks service health
     * 
     * @return Service health status
     */
    suspend fun checkHealth(): VisionServiceHealth
}

// ============================================================================
// Processing Results
// ============================================================================

/**
 * Vision processing result
 */
sealed class VisionProcessingResult {
    data class AnalysisResult(val analysis: ImageAnalysis) : VisionProcessingResult()
    data class DescriptionResult(val description: String) : VisionProcessingResult()
    data class ObjectDetectionResult(val objects: List<DetectedObject>) : VisionProcessingResult()
    data class MetadataResult(val metadata: ImageMetadata) : VisionProcessingResult()
}

/**
 * Vision service health status
 */
data class VisionServiceHealth(
    val isHealthy: Boolean,
    val visionModelLoaded: Boolean,
    val cudaAvailable: Boolean,
    val version: String,
    val capabilities: List<String>
)

// ============================================================================
// Default Implementation
// ============================================================================

/**
 * Default implementation of VisionDomainService
 */
class DefaultVisionDomainService : VisionDomainService {

    override fun validateImageAnalysisRequest(
        imageData: ByteArray,
        options: VisionOptions
    ): List<VisionValidationError> {
        val errors = mutableListOf<VisionValidationError>()

        // Validate image data
        if (imageData.isEmpty()) {
            errors.add(VisionValidationError("imageData", "Image data cannot be empty", "EMPTY_IMAGE"))
        }

        // Check file size (max 10MB)
        if (imageData.size > 10 * 1024 * 1024) {
            errors.add(VisionValidationError("imageData", "Image size exceeds 10MB limit", "SIZE_LIMIT"))
        }

        // Validate options
        if (options.maxDescriptionLength <= 0) {
            errors.add(VisionValidationError("maxDescriptionLength", "Must be positive", "INVALID_LENGTH"))
        }

        return errors
    }

    override fun validateImageAnalysis(analysis: ImageAnalysis): List<VisionValidationError> {
        val errors = mutableListOf<VisionValidationError>()

        if (analysis.description.isBlank()) {
            errors.add(VisionValidationError("description", "Description cannot be blank", "EMPTY_DESCRIPTION"))
        }

        if (analysis.confidence !in 0.0f..1.0f) {
            errors.add(VisionValidationError("confidence", "Confidence must be between 0.0 and 1.0", "INVALID_CONFIDENCE"))
        }

        return errors
    }

    override fun generateSessionMetadata(
        sessionType: VisionSessionType,
        userId: String,
        additionalMetadata: Map<String, String>
    ): Map<String, String> {
        return mapOf(
            "session_type" to sessionType.name,
            "user_id" to userId,
            "created_at" to Instant.now().toString()
        ) + additionalMetadata
    }

    override fun optimizeProcessingOptions(
        imageData: ByteArray,
        userOptions: VisionOptions
    ): VisionOptions {
        // For now, just return user options
        // In the future, could analyze image characteristics and optimize
        return userOptions
    }
}
